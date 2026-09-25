# Seeking Alpha -> Btock -> Gmail cloud workflow

Status as of this build: **the Btock scoring and Gmail-delivery halves of
this pipeline are built and verified. The Seeking Alpha scan half is
built but currently blocked, and the recurring schedule has deliberately
NOT been created** (see "Known blocker" below). This document says
exactly what is verified, what isn't, and what a human needs to do to
finish activating it.

## Components

- `run.py` -- CLI scan runner. Wraps byte-for-byte copies of
  `modules/indicators.py` and `modules/scoring.py` (diff them against
  `scripts/modules/*` yourself to confirm) with live `yfinance` downloads,
  a 900s-default disk cache, bounded backoff on HTTP 429, and a JSON
  report whose `errors` are never reported as a `HOLD` signal.
  **Verified**: live downloads, cache hit/age reporting, `--refresh`,
  stdin ticker input, and error handling were all exercised against real
  Yahoo Finance data during this build.
- `sa_scraper.py` -- Playwright-based Seeking Alpha `latest-articles`
  scanner. Paginates a `[window_start, window_end)` interval, and for
  each article records URL, timestamp, author, ticker labels, and the
  **article-specific** author rating (never the aggregate/Quant rating).
  **Not verified end-to-end** -- see "Known blocker".
- `orchestrate.py` -- computes the fixed 15-hour ET window
  (6:00 PM previous day -> 9:00 AM run day, DST-aware via `zoneinfo`),
  dedupes qualifying tickers (mapping `BRK.B` -> `BRK-B` etc.), runs
  `run.py`, writes a dated JSON record to `--results-dir`, and sends one
  email per run identifier with duplicate-send protection.
  **Verified end-to-end** using `--manual-coverage-file` (a coverage
  JSON in `sa_scraper.py`'s own output shape) standing in for a live SA
  scan -- including the "SA scan failed, don't claim no-matches" and
  duplicate-skip code paths.
- `mailer.py` -- sends the report over SMTP using a Gmail App Password
  (`GMAIL_SENDER_ADDRESS` / `GMAIL_APP_PASSWORD`). Independent of this
  session's own connected Gmail account -- a GitHub Actions runner can't
  call that MCP tool, so it needs its own credential.

## Known blocker: Seeking Alpha bot protection

A direct test from a headless Chromium browser against
`https://seekingalpha.com/latest-articles` returned **HTTP 403 with a
PerimeterX CAPTCHA challenge**, before any sign-in was attempted. This is
Seeking Alpha detecting and blocking automated/headless clients outright
-- it is not a login problem. Defeating PerimeterX (stealth browser
fingerprint spoofing, CAPTCHA-solving services, residential proxy
rotation, etc.) would mean bypassing a site's access controls, which this
build will not do.

Practical options going forward, in order of preference:
1. **A legitimate Seeking Alpha data API**, if one exists on your account
   tier, that returns article-level author ratings without scraping the
   HTML site.
2. **A human-in-the-loop run**: you run `sa_scraper.py` yourself, from a
   real (non-headless) browser profile on a residential IP, save the
   `storage_state`, and only the download/scoring/email steps run
   unattended in the cloud. This still may not survive PerimeterX's
   fingerprinting of automation, even non-headless.
3. Accept that the Seeking Alpha leg stays manual (you supply the
   qualifying-ticker list via `--manual-coverage-file`) while everything
   downstream (Btock scoring, dedup, dated records, email) runs
   unattended in GitHub Actions.

Until one of these is confirmed working end-to-end, the GitHub Actions
workflow (`.github/workflows/seeking-alpha-scan.yml`) is **manual-dispatch
only** -- no `schedule:` trigger -- exactly per the "leave the schedule
inactive if a gate fails" instruction.

## Required GitHub repo secrets (set in the GitHub UI, never in chat)

| Secret | Purpose |
| --- | --- |
| `GMAIL_SENDER_ADDRESS` | Gmail address the report is sent from |
| `GMAIL_APP_PASSWORD` | [App Password](https://myaccount.google.com/apppasswords) for that address (requires 2-Step Verification) |
| `SA_STORAGE_STATE_B64` | Only if/when option 1 or 2 above is confirmed workable: base64 of a Playwright `storage_state` JSON exported from your own signed-in browser (`python -m playwright codegen --save-storage=state.json https://seekingalpha.com`, sign in, close the window) |

## Running it yourself

```bash
pip install -r scripts/requirements.txt

# Btock scoring only, against real Yahoo Finance data:
python scripts/run.py AAPL MSFT BRK-B --output out.json --cache-dir /tmp/btock-cache

# Full pipeline against a manually supplied article list (no live SA access needed):
python scripts/orchestrate.py \
  --manual-coverage-file scripts/fixtures/manual_coverage_example.json \
  --results-dir results --cache-dir /tmp/btock-cache --test --dry-run
```

## Activating the schedule once every gate passes

1. Confirm a live, policy-compliant Seeking Alpha coverage path (see
   above) and run the workflow via `workflow_dispatch` with `test: true`,
   `dry_run: false` and confirm the resulting email and `results/*.json`
   record look right.
2. Add a `schedule:` trigger to
   `.github/workflows/seeking-alpha-scan.yml`. GitHub Actions cron is UTC
   only and does not itself understand `America/Los_Angeles` or DST, so
   use two cron lines bracketing both offsets and let `orchestrate.py`'s
   own `--cutoff-et` default (today 09:00 ET) decide whether it's
   actually a run day/time, e.g.:
   ```yaml
   on:
     schedule:
       - cron: "0 16 * * 1-5"  # 09:00 PDT / 16:00 UTC (Mar-Nov)
       - cron: "0 17 * * 1-5"  # 09:00 PST / 17:00 UTC (Nov-Mar)
   ```
3. Retire the local Windows Task Scheduler jobs ("Seeking Alpha weekday
   Buy scan", "Seeking Alpha powered-off PC test") only after several
   scheduled cloud runs have been confirmed to complete and email
   successfully without the PC being involved.
