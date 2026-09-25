# Seeking Alpha -> Btock -> Gmail cloud workflow

Status: **the Btock scoring and Gmail-delivery halves of this pipeline are
built, verified end-to-end in GitHub Actions, and scheduled to run every
weekday at 6:00 AM America/Los_Angeles, PC off or on. The Seeking Alpha
scan half is still blocked** (see "Known blocker" below) and stays a
manual input: if no `coverage/YYYY-MM-DD.json` exists for that morning's
date, the scheduled run sends an honest "Seeking Alpha scan did not run"
email instead of fabricating a result. This document says exactly what is
verified, what isn't, and what's still a human's job each morning.

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
3. **Standing approach implemented now**: the Seeking Alpha leg stays
   manual (you, or a future policy-compliant source, supply a coverage
   JSON) while everything downstream is fully unattended -- see
   "Coverage-upload trigger" below.

Even so, **everything except reading seekingalpha.com is fully
automated**, including a weekday schedule (see below) -- the only
remaining manual step is supplying that day's qualifying tickers.

### The three ways a run fires

1. **`workflow_dispatch`** -- manual, for testing (defaults to `test:
   true`, use `test: false` for a real send).
2. **push to `coverage/YYYY-MM-DD.json` on `main`** -- same shape as
   `sa_scraper.py`'s own output (see
   `scripts/fixtures/manual_coverage_example.json`). The
   `scan-from-coverage-upload` job runs immediately: Btock scoring,
   dedup, the dated `results/` record, and a **real** (non-test) email.
   Supply this whenever you have the day's data, no need to wait for the
   schedule.
3. **`schedule`** -- weekdays at 06:00 `America/Los_Angeles` (two cron
   lines bracket PDT/PST since GitHub Actions cron is UTC-only and
   doesn't know about DST; the job itself computes the real ET date, so
   it's safe if both fire near a DST transition). The `scan-scheduled`
   job looks for `coverage/<today's ET date>.json`:
   - **found** -> runs the real pipeline against it, same as trigger 2.
   - **not found** -> sends a real email that says plainly "Seeking
     Alpha scan did not run" rather than a fabricated "no BUY matches".
   Duplicate-send protection (keyed on the ET date) means pushing a
   coverage file *after* the schedule already fired and found nothing is
   not wasted -- trigger 2 still sends the real results for that date.

So the practical daily routine, PC off the whole time: at any point before
6 AM Pacific (or any time after, if you're catching up), produce that
day's `coverage/YYYY-MM-DD.json` (by hand from your own signed-in browser,
or from a future policy-compliant data source) and push it to `main`.
Nothing else needs to happen.

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

## Retiring the local Task Scheduler jobs

Retire the local Windows Task Scheduler jobs ("Seeking Alpha weekday Buy
scan", "Seeking Alpha powered-off PC test") only after several scheduled
cloud runs (with a real coverage file supplied) have been confirmed to
complete and email successfully without the PC being involved.

## If a policy-compliant Seeking Alpha data path ever becomes available

Fill in `SA_STORAGE_STATE_B64` (or whatever the new path needs) and change
`scan-scheduled`'s "Run orchestrator" step to pass `--storage-state
SA_STORAGE_STATE_B64` instead of looking for a coverage file -- everything
else (window math, dedup, scoring, email, dedup-protection) needs no
changes.
