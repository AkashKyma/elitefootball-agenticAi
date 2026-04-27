# GRUNT_HANDOFF_PAP-240 — Structured Logging Handoff for Pedant

## Ticket
PAP-240

## What I changed
Implemented structured logging across the active scrape → parse → store → Silver flow.

### New files
- `app/services/logging_service.py`
- `tests/test_logging_service.py`
- `tests/test_scraping_logging.py`
- `GRUNT_HANDOFF_PAP-240.md`

### Updated files
- `app/config.py`
- `app/main.py`
- `app/services/__init__.py`
- `app/scraping/browser.py`
- `app/scraping/transfermarkt.py`
- `app/scraping/fbref.py`
- `app/scraping/storage.py`
- `app/scraping/parsers.py`
- `app/scraping/fbref_parsers.py`
- `app/pipeline/silver.py`
- `app/db/base.py`
- `README.md`
- `memory/progress.md`
- `memory/decisions.md`

## Root cause addressed
The active scraper pipeline had no shared structured logging layer, so operators could not tell whether execution stopped in fetch, parse, storage, or Silver shaping. Empty artifacts and dependency failures were effectively opaque unless manually re-run in a shell.

## What is now logged
- fetch start / browser launch / goto / render complete / success / failure
- Playwright missing with stack trace
- scrape start / raw save / parsed save / success / failure
- parser start/completion counts and partial-result warnings
- extracted record counts for Transfermarkt + FBref
- file persistence attempts/results in storage
- Silver load/build/write counts and empty-output warnings
- DB seam initialization plus JSON-persistence write attempt/result events

## Important behavior notes
- debug mode is env-gated via `LOG_DEBUG_ENABLED=true`
- file logging is opt-in via `LOG_FILE_ENABLED=true` + `LOG_FILE_PATH=...`
- terminal logs remain the default
- I logged `db.write.*` events around current persistence seams and DB/session setup, but did **not** invent a real DB ingestion path

## Validation run
Executed:
- `python3 -m unittest tests.test_logging_service tests.test_scraping_logging`
- `python3 -m unittest tests.test_api_routes tests.test_tasks`

Results:
- targeted logging tests passed
- additional API/task tests remained skipped where FastAPI is unavailable in the environment

## Pedant review focus
Please check:
1. event naming consistency (`fetch.*`, `scrape.*`, `parse.*`, `storage.*`, `silver.*`, `db.write.*`)
2. whether any log fields are too noisy or too sparse at INFO level
3. whether `app/db/base.py` logging is acceptable or should be reduced
4. whether the `db.write.*` events around file persistence read clearly enough as persistence-attempt/result events rather than real DB inserts
5. whether there are any modules in the scrape path still missing top-level exception logging

## Next recommended issue
`PAP-241 - Wire Concrete IDV Scrape Targets Into full_refresh and Add Scrape Runtime Preflight`
