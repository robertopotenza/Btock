#!/usr/bin/env python3
"""
Seeking Alpha -> Btock -> Gmail orchestrator.

Ties together (in order):
  1. window computation: a fixed 15-hour publication window, 6:00 PM ET on
     the previous calendar day through 9:00 AM ET on the run day,
     [start, end) with an inclusive start and exclusive end.
  2. Seeking Alpha coverage: either a live scan via sa_scraper.py (needs a
     working storage_state -- see that script's docstring; live scraping
     is currently blocked by Seeking Alpha's PerimeterX bot protection for
     ANY headless/automated client, see README) or, for testing this half
     of the pipeline independently, a manually supplied qualifying-tickers
     file in the same shape sa_scraper.py produces.
  3. scripts/run.py: the unchanged Btock scoring engine, run as a
     subprocess against the deduped, Yahoo-mapped ticker set.
  4. a dated result record written to --results-dir (committed back to the
     repo by the caller/workflow -- that's this project's durable cloud
     storage).
  5. one email per cutoff, with duplicate-send protection keyed on the
     run identifier.

This script deliberately never invents a result: if Seeking Alpha coverage
could not be established, the email says so explicitly instead of reporting
"no BUY matches".
"""

import argparse
import json
import logging
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from sa_scraper import qualifying_buy_tickers, sa_to_yahoo  # noqa: E402

logging.basicConfig(level="INFO", format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("btock.orchestrate")

ET = ZoneInfo("America/New_York")
WINDOW_HOURS = 15
RECIPIENT = "eng.potenza@gmail.com"


@dataclass
class Window:
    start_utc: datetime
    end_utc: datetime
    cutoff_et: datetime

    def describe(self) -> str:
        start_et = self.start_utc.astimezone(ET)
        end_et = self.end_utc.astimezone(ET)
        return (
            f"[{start_et.isoformat()} , {end_et.isoformat()}) America/New_York "
            f"([{self.start_utc.isoformat()} , {self.end_utc.isoformat()}) UTC)"
        )


def compute_window(cutoff_et_naive: Optional[str]) -> Window:
    """cutoff_et_naive: 'YYYY-MM-DDTHH:MM:SS' wall-clock in America/New_York.
    Defaults to today's date at 09:00 local ET wall-clock time."""
    if cutoff_et_naive:
        naive = datetime.fromisoformat(cutoff_et_naive)
    else:
        now_et = datetime.now(ET)
        naive = now_et.replace(hour=9, minute=0, second=0, microsecond=0).replace(tzinfo=None)

    cutoff_et = naive.replace(tzinfo=ET)
    end_utc = cutoff_et.astimezone(timezone.utc)
    start_utc = (cutoff_et - timedelta(hours=WINDOW_HOURS)).astimezone(timezone.utc)
    return Window(start_utc=start_utc, end_utc=end_utc, cutoff_et=cutoff_et)


def run_id_for(window: Window) -> str:
    return window.cutoff_et.strftime("%Y-%m-%d")


def load_manual_coverage(path: Path) -> dict:
    """Load a manually supplied coverage file in sa_scraper.py's output
    shape, for testing the Btock+email half of the pipeline while live SA
    scraping is blocked."""
    with open(path) as f:
        data = json.load(f)
    data.setdefault("qualifying_tickers", qualifying_buy_tickers(data.get("articles", [])))
    return data


def run_btock(tickers: List[str], output_path: Path, cache_dir: Path, ttl: int) -> dict:
    if not tickers:
        return {"results": {}, "errors": {}, "requested_tickers": []}
    cmd = [
        sys.executable, str(SCRIPT_DIR / "run.py"),
        *tickers,
        "--output", str(output_path),
        "--cache-dir", str(cache_dir),
        "--ttl", str(ttl),
    ]
    logger.info("Running: %s", " ".join(cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"scripts/run.py failed (exit {proc.returncode}): {proc.stderr[-4000:]}")
    with open(output_path) as f:
        return json.load(f)


def compose_email(
    window: Window,
    run_id: str,
    coverage: dict,
    btock_report: dict,
    sa_to_yahoo_map: Dict[str, str],
    test: bool,
) -> str:
    buys = []
    for ticker, r in btock_report.get("results", {}).items():
        if r.get("signal") == "BUY":
            buys.append(r)
    buys.sort(key=lambda r: r["weighted_score"], reverse=True)

    lines = []
    lines.append(f"Window (America/New_York, [start, end)): {window.describe()}")
    lines.append(f"Run identifier: {run_id}{'  (TEST)' if test else ''}")
    lines.append("")

    if not coverage.get("signed_in", False):
        lines.append("*** SEEKING ALPHA SCAN DID NOT RUN OR FAILED SIGN-IN CHECK ***")
        lines.append(f"Reason: {coverage.get('error', 'unknown')}")
        lines.append("The list below (if any) reflects manually supplied or partial data only.")
        lines.append("This is NOT a verified 'no BUY matches' result.")
        lines.append("")
    elif not coverage.get("coverage_complete", False):
        lines.append("*** WARNING: Seeking Alpha coverage of the full window is NOT confirmed complete ***")
        lines.append(f"Pages visited: {coverage.get('pages_visited')}; oldest article seen: {coverage.get('oldest_seen_utc')}")
        lines.append("")

    inaccessible = coverage.get("inaccessible", [])
    if inaccessible:
        lines.append(f"{len(inaccessible)} article page(s) could not be read / rating not verifiable:")
        for u in inaccessible[:20]:
            lines.append(f"  - {u}")
        lines.append("")

    lines.append(f"Deduplicated qualifying tickers (Buy/Strong Buy, article-specific): {len(sa_to_yahoo_map)}")
    for sa_label, yahoo in sorted(sa_to_yahoo_map.items()):
        note = f" -> {yahoo}" if yahoo != sa_label else ""
        lines.append(f"  - {sa_label}{note}")
    lines.append("")

    if buys:
        lines.append(f"Successful Btock BUY signals ({len(buys)}), sorted by descending weighted score:")
        for r in buys:
            lines.append(
                f"  {r['ticker']:<8} score={r['weighted_score']:+.4f}  "
                f"close={r['latest_close']:.2f}  as_of={r['last_observation']}  "
                f"cache_hit={r['cache_hit']}"
            )
    else:
        lines.append("No successful Btock BUY signals this run.")
    lines.append("")

    errors = btock_report.get("errors", {})
    if errors:
        lines.append(f"Btock calculation/download failures ({len(errors)}) -- NOT reported as HOLD:")
        for ticker, err in errors.items():
            lines.append(f"  {ticker}: {err}")
        lines.append("")

    non_buy = {
        t: r for t, r in btock_report.get("results", {}).items() if r.get("signal") != "BUY"
    }
    if non_buy:
        lines.append(f"Other successful signals (not BUY, for reference): {', '.join(sorted(non_buy))}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Seeking Alpha -> Btock -> Gmail orchestrator")
    parser.add_argument("--cutoff-et", help="Wall-clock ET cutoff 'YYYY-MM-DDTHH:MM:SS' (default: today 09:00 ET)")
    parser.add_argument("--storage-state", help="Playwright storage_state path/env for a live SA scan")
    parser.add_argument("--manual-coverage-file", help="Pre-collected coverage JSON (sa_scraper.py output shape) for testing without live SA access")
    parser.add_argument("--results-dir", required=True, help="Durable results directory (e.g. results/ in the repo)")
    parser.add_argument("--cache-dir", required=True, help="Btock disk cache dir, outside the source tree")
    parser.add_argument("--ttl", type=int, default=900)
    parser.add_argument("--test", action="store_true", help="Use the test email subject and run-id suffix")
    parser.add_argument("--dry-run", action="store_true", help="Do everything except send the email")
    args = parser.parse_args()

    window = compute_window(args.cutoff_et)
    run_id = run_id_for(window) + ("-test" if args.test else "")
    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    record_path = results_dir / f"{run_id}.json"

    if record_path.exists():
        existing = json.loads(record_path.read_text())
        if existing.get("gmail_message_id"):
            logger.info("Run %s already sent (message id %s) -- skipping duplicate send", run_id, existing["gmail_message_id"])
            return 0

    if args.manual_coverage_file:
        coverage = load_manual_coverage(Path(args.manual_coverage_file))
    elif args.storage_state:
        from sa_scraper import collect_articles, load_storage_state
        storage_state = load_storage_state(args.storage_state)
        coverage = collect_articles(window.start_utc, window.end_utc, storage_state)
        coverage["qualifying_tickers"] = qualifying_buy_tickers(coverage["articles"])
    else:
        coverage = {
            "signed_in": False,
            "articles": [],
            "pages_visited": 0,
            "coverage_complete": False,
            "inaccessible": [],
            "qualifying_tickers": {},
            "error": "Neither --storage-state nor --manual-coverage-file was provided",
        }

    sa_to_yahoo_map: Dict[str, str] = coverage.get("qualifying_tickers", {})
    yahoo_tickers = sorted(set(sa_to_yahoo_map.values()))

    btock_output = results_dir / f"{run_id}-btock.json"
    btock_report = run_btock(yahoo_tickers, btock_output, Path(args.cache_dir), args.ttl)

    email_body = compose_email(window, run_id, coverage, btock_report, sa_to_yahoo_map, args.test)
    subject = f"Seeking Alpha CLOUD {'test ' if args.test else ''}— {window.cutoff_et.date().isoformat()}"

    record = {
        "run_id": run_id,
        "cutoff_et": window.cutoff_et.isoformat(),
        "window_start_utc": window.start_utc.isoformat(),
        "window_end_utc": window.end_utc.isoformat(),
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "coverage": coverage,
        "sa_to_yahoo_map": sa_to_yahoo_map,
        "btock_report": btock_report,
        "subject": subject,
        "recipient": RECIPIENT,
        "email_body": email_body,
        "gmail_message_id": None,
    }

    if args.dry_run:
        logger.info("Dry run -- not sending email. Record written to %s", record_path)
        record_path.write_text(json.dumps(record, indent=2, default=str))
        print(email_body)
        return 0

    from mailer import send_email
    message_id = send_email(RECIPIENT, subject, email_body)
    record["gmail_message_id"] = message_id
    record_path.write_text(json.dumps(record, indent=2, default=str))
    logger.info("Sent %s to %s (message id %s), record at %s", subject, RECIPIENT, message_id, record_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
