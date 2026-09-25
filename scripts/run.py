#!/usr/bin/env python3
"""
Btock CLI runner.

Wraps the unchanged scoring engine in scripts/modules/{indicators,scoring}.py
(byte-for-byte copies of modules/indicators.py and modules/scoring.py) with:
  - live Yahoo Finance history downloads (yfinance), one year by default
  - a disk cache (default TTL 900s / 15 minutes) so repeated runs in the same
    window don't re-hit Yahoo Finance
  - bounded exponential backoff on HTTP 429 / rate limiting
  - a JSON report with top-level "results" and "errors": a ticker that fails
    to download or fails to compute a valid score is NEVER reported as a
    signal (no default/fallback HOLD is invented for it) -- it is recorded
    only in "errors".

Usage:
    python scripts/run.py TICKER [TICKER ...]
    echo "AAPL MSFT SCHD" | python scripts/run.py
    python scripts/run.py --tickers-file tickers.txt --output out.json \
        --cache-dir /tmp/btock-cache --ttl 900

Do not pass --refresh for an ordinary scheduled run; it forces a fresh
Yahoo Finance download and bypasses the disk cache entirely.
"""

import argparse
import hashlib
import io
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import pandas as pd  # noqa: E402
import yfinance as yf  # noqa: E402

from modules.indicators import TechnicalIndicators  # noqa: E402
from modules.scoring import ScoringEngine  # noqa: E402

logging.basicConfig(
    level=os.environ.get("BTOCK_LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("btock.run")

DEFAULT_TTL_SECONDS = 900
DEFAULT_PERIOD = "1y"
MAX_RETRIES = 4
BACKOFF_BASE_SECONDS = 30  # 30s, 60s, 120s, 240s -- bounded, respects rate limits


@dataclass
class FetchResult:
    ticker: str
    data: Optional[pd.DataFrame] = None
    error: Optional[str] = None
    cache_hit: bool = False
    cache_age_seconds: Optional[float] = None
    source: str = "yfinance"
    last_observation: Optional[str] = None


def _cache_path(cache_dir: Path, ticker: str, period: str) -> Path:
    key = hashlib.sha256(f"{ticker.upper()}|{period}".encode("utf-8")).hexdigest()[:24]
    return cache_dir / f"{ticker.upper()}_{key}.json"


def _read_cache(path: Path, ttl_seconds: int) -> Optional[Tuple[pd.DataFrame, float]]:
    if not path.exists():
        return None
    age = time.time() - path.stat().st_mtime
    if age > ttl_seconds:
        return None
    try:
        with open(path, "r") as f:
            payload = json.load(f)
        df = pd.read_json(io.StringIO(payload["data"]), orient="split")
        df.index = pd.to_datetime(df.index)
        return df, age
    except Exception as exc:  # corrupt cache entry -- treat as miss
        logger.warning("Cache read failed for %s: %s", path, exc)
        return None


def _write_cache(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"data": df.to_json(orient="split", date_format="iso")}
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(payload, f)
    tmp.replace(path)


def _is_rate_limited(exc: Exception) -> bool:
    text = str(exc).lower()
    return "429" in text or "too many requests" in text or "rate limit" in text


def fetch_ticker_history(
    ticker: str,
    period: str,
    cache_dir: Optional[Path],
    ttl_seconds: int,
    refresh: bool,
) -> FetchResult:
    """Fetch OHLCV history for one ticker via the unchanged yfinance path,
    with a disk cache and bounded backoff on rate limiting."""

    cache_file = _cache_path(cache_dir, ticker, period) if cache_dir else None

    if not refresh and cache_file is not None:
        cached = _read_cache(cache_file, ttl_seconds)
        if cached is not None:
            df, age = cached
            last_obs = df.index[-1].isoformat() if len(df) else None
            return FetchResult(
                ticker=ticker,
                data=df,
                cache_hit=True,
                cache_age_seconds=round(age, 1),
                last_observation=last_obs,
            )

    last_exc: Optional[Exception] = None
    for attempt in range(MAX_RETRIES):
        try:
            stock = yf.Ticker(ticker.upper())
            data = stock.history(period=period, auto_adjust=False)
            if data is None or data.empty:
                return FetchResult(ticker=ticker, error="No data returned by Yahoo Finance (empty history)")
            required = ["Open", "High", "Low", "Close", "Volume"]
            if not all(col in data.columns for col in required):
                return FetchResult(ticker=ticker, error=f"Missing required OHLCV columns: {list(data.columns)}")

            if cache_file is not None:
                try:
                    _write_cache(cache_file, data)
                except Exception as exc:
                    logger.warning("Failed to write cache for %s: %s", ticker, exc)

            last_obs = data.index[-1].isoformat() if len(data) else None
            return FetchResult(ticker=ticker, data=data, cache_hit=False, last_observation=last_obs)

        except Exception as exc:
            last_exc = exc
            if _is_rate_limited(exc) and attempt < MAX_RETRIES - 1:
                delay = BACKOFF_BASE_SECONDS * (2 ** attempt)
                logger.warning(
                    "Rate limited fetching %s (attempt %d/%d); backing off %ds",
                    ticker, attempt + 1, MAX_RETRIES, delay,
                )
                time.sleep(delay)
                continue
            break

    return FetchResult(ticker=ticker, error=f"Yahoo Finance download failed: {last_exc}")


def analyze_ticker(
    ticker: str,
    fetch: FetchResult,
    weights: Dict[str, float],
    buy_threshold: float,
    sell_threshold: float,
) -> Dict:
    if fetch.error is not None:
        raise ValueError(fetch.error)

    data = fetch.data
    if data is None or len(data) < 200:
        raise ValueError(
            f"Insufficient history for indicator calculation: {0 if data is None else len(data)} rows (need >= 200)"
        )

    ti = TechnicalIndicators()
    raw_indicators = ti.calculate_all_indicators(data)
    if not raw_indicators:
        raise ValueError("Indicator calculation returned no values (see warnings above for the underlying cause)")

    engine = ScoringEngine()
    engine.set_thresholds(buy_threshold, sell_threshold)
    analysis = engine.analyze_ticker(raw_indicators, weights)

    latest_close = float(data["Close"].iloc[-1])

    return {
        "ticker": ticker.upper(),
        "signal": analysis["signal"],
        "weighted_score": analysis["final_weighted_score"],
        "category_scores": {
            "momentum": analysis["momentum_score"],
            "trend": analysis["trend_score"],
            "volatility": analysis["volatility_score"],
            "strength": analysis["strength_score"],
            "support_resistance": analysis["support_resistance_score"],
        },
        "latest_close": latest_close,
        "last_observation": fetch.last_observation,
        "source": fetch.source,
        "cache_hit": fetch.cache_hit,
        "cache_age_seconds": fetch.cache_age_seconds,
        "history_rows": len(data),
        "note": "latest_close is the last history bar's close, not a live quote; an intraday bar may be incomplete.",
    }


def parse_weights(raw: Optional[str], default: Dict[str, float]) -> Dict[str, float]:
    if not raw:
        return dict(default)
    weights = dict(default)
    for part in raw.split(","):
        if not part.strip():
            continue
        key, _, value = part.partition("=")
        key = key.strip()
        if key not in weights:
            raise ValueError(f"Unknown weight category: {key!r} (expected one of {sorted(weights)})")
        weights[key] = float(value)
    return weights


def read_tickers(args: argparse.Namespace) -> List[str]:
    tickers: List[str] = []
    if args.tickers:
        tickers.extend(args.tickers)
    if args.tickers_file:
        with open(args.tickers_file) as f:
            tickers.extend(f.read().split())
    if not tickers and not sys.stdin.isatty():
        piped = sys.stdin.read().split()
        tickers.extend(piped)
    seen = set()
    ordered_unique = []
    for t in tickers:
        u = t.strip().upper()
        if u and u not in seen:
            seen.add(u)
            ordered_unique.append(u)
    return ordered_unique


def main() -> int:
    default_weights = {
        "momentum": 0.30,
        "trend": 0.40,
        "volatility": 0.05,
        "strength": 0.05,
        "support_resistance": 0.20,
    }

    parser = argparse.ArgumentParser(description="Btock CLI scan runner")
    parser.add_argument("tickers", nargs="*", help="Ticker symbols (Yahoo Finance format, e.g. BRK-B)")
    parser.add_argument("--tickers-file", help="Path to a file with whitespace-separated tickers")
    parser.add_argument("--period", default=DEFAULT_PERIOD, help="yfinance history period (default: 1y)")
    parser.add_argument("--output", required=True, help="Path to write the JSON report")
    parser.add_argument("--cache-dir", required=True, help="Disk cache directory (must be outside the source tree)")
    parser.add_argument("--ttl", type=int, default=DEFAULT_TTL_SECONDS, help="Cache TTL in seconds (default: 900)")
    parser.add_argument("--refresh", action="store_true", help="Bypass the disk cache and force a fresh download")
    parser.add_argument("--weights", help="Override weights, e.g. 'momentum=0.3,trend=0.4,volatility=0.05,strength=0.05,support_resistance=0.2'")
    parser.add_argument("--buy-threshold", type=float, default=0.5)
    parser.add_argument("--sell-threshold", type=float, default=-0.5)
    args = parser.parse_args()

    tickers = read_tickers(args)
    if not tickers:
        parser.error("No tickers provided (via positional args, --tickers-file, or stdin)")

    weights = parse_weights(args.weights, default_weights)

    output_path = Path(args.output).resolve()
    cache_dir = Path(args.cache_dir).resolve()
    source_dir = SCRIPT_DIR.resolve()
    if source_dir == cache_dir or source_dir in cache_dir.parents or cache_dir in source_dir.parents:
        logger.warning("cache-dir %s overlaps the installed source directory %s", cache_dir, source_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    results: Dict[str, Dict] = {}
    errors: Dict[str, str] = {}

    for ticker in tickers:
        logger.info("Fetching %s (period=%s, refresh=%s)", ticker, args.period, args.refresh)
        fetch = fetch_ticker_history(ticker, args.period, cache_dir, args.ttl, args.refresh)
        try:
            results[ticker] = analyze_ticker(ticker, fetch, weights, args.buy_threshold, args.sell_threshold)
            logger.info(
                "%s -> %s (score=%.4f, cache_hit=%s)",
                ticker, results[ticker]["signal"], results[ticker]["weighted_score"], fetch.cache_hit,
            )
        except Exception as exc:
            errors[ticker] = str(exc)
            logger.error("%s -> ERROR: %s", ticker, exc)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "period": args.period,
        "weights": weights,
        "buy_threshold": args.buy_threshold,
        "sell_threshold": args.sell_threshold,
        "cache_dir": str(cache_dir),
        "ttl_seconds": args.ttl,
        "refresh": args.refresh,
        "requested_tickers": tickers,
        "results": results,
        "errors": errors,
    }

    with open(output_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    logger.info("Wrote report to %s (%d results, %d errors)", output_path, len(results), len(errors))
    return 0


if __name__ == "__main__":
    sys.exit(main())
