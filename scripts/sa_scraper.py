#!/usr/bin/env python3
"""
Seeking Alpha "latest-articles" scraper for the Btock cloud workflow.

Authentication model
---------------------
This script never logs in and never receives a password or verification
code. Instead it loads a Playwright `storage_state` (cookies + local
storage) that the account owner exports ONE TIME from their own already
signed-in browser, on their own machine:

    python -m playwright codegen --save-storage=sa_storage_state.json https://seekingalpha.com

(sign in normally in the window that opens, then close it -- codegen writes
the storage state on exit). The resulting JSON is a bearer credential, so it
must be stored as a secret (e.g. the GitHub Actions secret
SA_STORAGE_STATE_B64, base64-encoded) and never committed to the repo or
pasted into chat.

This script cannot be exercised end-to-end without that secret, so its
extraction logic (`_extract_article`) is best-effort against Seeking
Alpha's known page structure and MUST be validated against real,
authenticated pages before the workflow is trusted -- see the
`--dump-html` flag for capturing raw pages to diff selectors against.
"""

import argparse
import base64
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional
from zoneinfo import ZoneInfo

logger = logging.getLogger("btock.sa_scraper")

LATEST_ARTICLES_URL = "https://seekingalpha.com/latest-articles"
ET = ZoneInfo("America/New_York")
QUALIFYING_RATINGS = {"buy", "strong buy"}

# Map Seeking Alpha ticker labels to their Yahoo Finance equivalents where
# they differ. Extend as new mismatches are found.
SA_TO_YAHOO_TICKER_MAP = {
    "BRK.B": "BRK-B",
    "BRK.A": "BRK-A",
    "BF.B": "BF-B",
}


@dataclass
class Article:
    url: str
    published_at: str  # ISO 8601, UTC
    author: str
    sa_tickers: List[str]
    rating: Optional[str]  # article-specific author rating, verbatim
    rating_verified: bool  # True only if read directly off the article page


def sa_to_yahoo(sa_ticker: str) -> str:
    return SA_TO_YAHOO_TICKER_MAP.get(sa_ticker.upper(), sa_ticker.upper())


def load_storage_state(path_or_b64_env: Optional[str]) -> Optional[dict]:
    """Resolve a Playwright storage_state from a file path or a base64 env var."""
    if not path_or_b64_env:
        return None
    p = Path(path_or_b64_env)
    if p.exists():
        return json.loads(p.read_text())
    env_val = os.environ.get(path_or_b64_env)
    if env_val:
        return json.loads(base64.b64decode(env_val).decode("utf-8"))
    return None


def check_signed_in(page) -> bool:
    """Best-effort signed-in check: look for an authenticated-only element
    and the absence of the anonymous "Sign In" call to action."""
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass
    html = page.content()
    has_sign_in_cta = bool(re.search(r"Sign In</", html)) or bool(
        page.locator("a:has-text('Sign In')").first.is_visible()
        if page.locator("a:has-text('Sign In')").count() > 0
        else False
    )
    has_account_marker = page.locator("[data-test-id='user-nav'], [data-test-id='account-menu'], a[href*='/account']").count() > 0
    return has_account_marker and not has_sign_in_cta


def _parse_relative_or_absolute_time(raw: str, reference: datetime) -> Optional[datetime]:
    raw = raw.strip()
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        pass
    m = re.match(r"(\d+)\s*(min|hour|day)s?\s+ago", raw, re.IGNORECASE)
    if m:
        n, unit = int(m.group(1)), m.group(2).lower()
        delta = {"min": timedelta(minutes=n), "hour": timedelta(hours=n), "day": timedelta(days=n)}[unit]
        return reference - delta
    return None


def _extract_article_links(page) -> List[str]:
    hrefs = page.eval_on_selector_all(
        "a[href*='/article/'], a[href*='/news/']",
        "els => els.map(e => e.href)",
    )
    seen, ordered = set(), []
    for h in hrefs:
        if h not in seen:
            seen.add(h)
            ordered.append(h)
    return ordered


def _extract_article(page, url: str, now_ref: datetime, dump_dir: Optional[Path]) -> Optional[Article]:
    """Open a single article page and pull publish time, author, tickers,
    and the article-specific author rating. Returns None if the rating
    cannot be verified (never guesses)."""
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass

    html = page.content()
    if dump_dir is not None:
        dump_dir.mkdir(parents=True, exist_ok=True)
        safe_name = re.sub(r"[^A-Za-z0-9]+", "_", url)[-120:]
        (dump_dir / f"{safe_name}.html").write_text(html)

    time_el = page.locator("time").first
    published_raw = time_el.get_attribute("datetime") if time_el.count() > 0 else None
    published_at = _parse_relative_or_absolute_time(published_raw, now_ref) if published_raw else None

    author_el = page.locator("[data-test-id='author-name'], a[href*='/author/']").first
    author = author_el.inner_text().strip() if author_el.count() > 0 else "UNKNOWN"

    ticker_els = page.locator("[data-test-id='ticker-tag'], a[href^='/symbol/']")
    sa_tickers = []
    for i in range(ticker_els.count()):
        t = ticker_els.nth(i).inner_text().strip().upper()
        if t and t not in sa_tickers:
            sa_tickers.append(t)

    rating = None
    rating_el = page.locator("[data-test-id='article-rating'], [data-test-id='authors-rating']")
    if rating_el.count() > 0:
        rating = rating_el.first.inner_text().strip()
    else:
        m = re.search(r"Rating:\s*(Strong\s+Buy|Buy|Hold|Sell|Strong\s+Sell)", html, re.IGNORECASE)
        if m:
            rating = m.group(1).strip()

    if published_at is None or not sa_tickers:
        logger.warning("Could not verify timestamp/tickers for %s -- excluding from coverage", url)
        return None

    return Article(
        url=url,
        published_at=published_at.astimezone(timezone.utc).isoformat(),
        author=author,
        sa_tickers=sa_tickers,
        rating=rating,
        rating_verified=rating is not None,
    )


def collect_articles(
    window_start_utc: datetime,
    window_end_utc: datetime,
    storage_state: Optional[dict],
    max_pages: int = 40,
    dump_dir: Optional[Path] = None,
) -> dict:
    """Paginate latest-articles until every article is older than
    window_start_utc, returning coverage evidence plus the qualifying
    (Buy / Strong Buy, article-specific) articles inside [start, end)."""
    from playwright.sync_api import sync_playwright

    articles: List[Article] = []
    pages_visited = 0
    oldest_seen_utc: Optional[datetime] = None
    inaccessible: List[str] = []
    signed_in = False

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.environ.get("PLAYWRIGHT_CHROMIUM_PATH"))
        context = browser.new_context(storage_state=storage_state) if storage_state else browser.new_context()
        page = context.new_page()

        page.goto(LATEST_ARTICLES_URL, wait_until="domcontentloaded", timeout=30000)
        signed_in = check_signed_in(page)
        if not signed_in:
            browser.close()
            return {
                "signed_in": False,
                "articles": [],
                "pages_visited": 0,
                "coverage_complete": False,
                "inaccessible": [LATEST_ARTICLES_URL],
                "error": "Not signed in -- aborting scan (see storage_state setup in this script's docstring)",
            }

        candidate_links: List[str] = []
        for page_num in range(1, max_pages + 1):
            pages_visited = page_num
            if page_num > 1:
                page.goto(f"{LATEST_ARTICLES_URL}?page={page_num}", wait_until="domcontentloaded", timeout=30000)
                try:
                    page.wait_for_load_state("networkidle", timeout=15000)
                except Exception:
                    pass
            links = _extract_article_links(page)
            if not links:
                logger.warning("No article links found on page %d -- stopping pagination", page_num)
                break
            candidate_links.extend(links)

            oldest_time_el = page.locator("time").last
            if oldest_time_el.count() > 0:
                raw = oldest_time_el.get_attribute("datetime")
                parsed = _parse_relative_or_absolute_time(raw, datetime.now(timezone.utc)) if raw else None
                if parsed is not None:
                    oldest_seen_utc = parsed.astimezone(timezone.utc)

            if oldest_seen_utc is not None and oldest_seen_utc < window_start_utc:
                break
            time.sleep(1.0)  # be polite / avoid rate limiting

        seen_urls = set()
        now_ref = datetime.now(timezone.utc)
        for url in candidate_links:
            if url in seen_urls:
                continue
            seen_urls.add(url)
            try:
                article = _extract_article(page, url, now_ref, dump_dir)
            except Exception as exc:
                logger.warning("Failed to read article %s: %s", url, exc)
                inaccessible.append(url)
                continue
            if article is None:
                inaccessible.append(url)
                continue

            pub = datetime.fromisoformat(article.published_at)
            if pub < window_start_utc:
                continue
            if pub >= window_end_utc:
                continue
            articles.append(article)
            time.sleep(0.5)

        browser.close()

    coverage_complete = oldest_seen_utc is not None and oldest_seen_utc < window_start_utc

    return {
        "signed_in": signed_in,
        "articles": [asdict(a) for a in articles],
        "pages_visited": pages_visited,
        "oldest_seen_utc": oldest_seen_utc.isoformat() if oldest_seen_utc else None,
        "coverage_complete": coverage_complete,
        "inaccessible": inaccessible,
    }


def qualifying_buy_tickers(articles: List[dict]) -> dict:
    """Dedupe the union of SA ticker labels from Buy/Strong-Buy-rated
    articles (article-specific rating only). Returns {sa_label: yahoo_symbol}."""
    mapping = {}
    for a in articles:
        rating = (a.get("rating") or "").strip().lower()
        if rating not in QUALIFYING_RATINGS or not a.get("rating_verified"):
            continue
        for sa_ticker in a.get("sa_tickers", []):
            mapping[sa_ticker] = sa_to_yahoo(sa_ticker)
    return mapping


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="Scan Seeking Alpha latest-articles for a fixed window")
    parser.add_argument("--window-start", required=True, help="ISO 8601 UTC, inclusive")
    parser.add_argument("--window-end", required=True, help="ISO 8601 UTC, exclusive")
    parser.add_argument("--storage-state", help="Path to a Playwright storage_state JSON file, or a env var name holding base64 JSON")
    parser.add_argument("--output", required=True, help="Path to write the coverage/articles JSON report")
    parser.add_argument("--dump-html", help="Optional directory to dump raw article HTML for selector debugging")
    args = parser.parse_args()

    window_start = datetime.fromisoformat(args.window_start.replace("Z", "+00:00"))
    window_end = datetime.fromisoformat(args.window_end.replace("Z", "+00:00"))
    storage_state = load_storage_state(args.storage_state)

    result = collect_articles(
        window_start, window_end, storage_state,
        dump_dir=Path(args.dump_html) if args.dump_html else None,
    )
    result["window_start"] = window_start.isoformat()
    result["window_end"] = window_end.isoformat()
    result["qualifying_tickers"] = qualifying_buy_tickers(result["articles"])

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(result, f, indent=2, default=str)

    logger.info(
        "signed_in=%s pages=%d articles_in_window=%d coverage_complete=%s qualifying_tickers=%d",
        result["signed_in"], result["pages_visited"], len(result["articles"]),
        result["coverage_complete"], len(result["qualifying_tickers"]),
    )
    return 0 if result["signed_in"] else 1


if __name__ == "__main__":
    sys.exit(main())
