# ARCHITECT_PLAN_PAP-240 — Add Structured Logging to Scraper, Parser, and Data Persistence Flow

## Ticket
PAP-240

## Role
Architect — planning/design only. No application code implemented in this phase.

## Goal
Add structured, readable, environment-safe logging across the scrape → parse → store flow so operators can see exactly where execution stopped, why it failed, and whether a run produced empty, partial, or successful outputs.

The implementation must preserve the current architecture:
- scraping concerns remain in `app/scraping/`
- pipeline/data shaping remains in `app/pipeline/`
- database boundaries remain in `app/db/`
- API/dashboard remain consumers, not owners, of scrape-state logic

---

## 1) Current System State

## 1.1 Confirmed current logging posture
A repo-wide grep for `logging`, `getLogger`, `logger.`, `basicConfig`, and `dictConfig` returned no current logging implementation in `app/`, `tests/`, `README.md`, or `memory/`.

### Implication
The current scraper path has effectively **no structured observability layer**. Failures are either:
- raised as exceptions without unified context
- represented indirectly by empty artifacts later in the pipeline
- invisible unless a developer manually inspects source files or reruns code in an interactive shell

---

## 1.2 Current scrape path to instrument
### Fetch/browser
- `app/scraping/browser.py`
  - `BrowserConfig`
  - `fetch_page_html(...)`

### Source-specific orchestration
- `app/scraping/transfermarkt.py`
  - `scrape_transfermarkt_player(...)`
- `app/scraping/fbref.py`
  - `scrape_fbref_page(...)`

### Parsing
- `app/scraping/parsers.py`
  - `parse_player_profile(...)`
  - `parse_transfer_history(...)`
- `app/scraping/fbref_parsers.py`
  - `parse_fbref_match_payload(...)`
  - `parse_fbref_player_match_stats(...)`
  - `parse_fbref_player_per_90(...)`

### Persistence
- `app/scraping/storage.py`
  - `ensure_directory(...)`
  - `save_raw_html(...)`
  - `save_parsed_payload(...)`

### Downstream table shaping / persistence-adjacent flow
- `app/pipeline/silver.py`
  - `_load_json_files(...)`
  - `build_silver_tables(...)`

### Database seam
- `app/db/base.py`
  - engine/session setup only exists today
- there is no active DB write path yet, but the ticket explicitly asks for DB write attempt/result logging

---

## 2) Problem Framing

PAP-239 established that the current scraping pipeline can fail or stall without clear operator visibility. PAP-240 should solve the observability gap, not the scrape-target/runtime gaps themselves.

### What this ticket should make visible
1. when a scrape starts
2. which source/url/slug is being scraped
3. whether page fetch began and completed
4. whether rendered HTML was captured and how large it is
5. what parser ran and what it extracted
6. whether extracted counts are zero, partial, or expected
7. where raw/parsed artifacts were written
8. whether any DB write was attempted (now or later) and whether it succeeded
9. the full stack trace when exceptions occur
10. whether extra debug logging is enabled without forcing noisy logs in normal environments

### Explicit non-goals
Do **not** in PAP-240:
- solve missing target registry / orchestration wiring from PAP-239
- solve Playwright installation/runtime readiness itself
- redesign scraper architecture into a new framework
- introduce third-party observability vendors or external log shipping
- add a full metrics/tracing system

---

## 3) Root Cause Found

### Root cause for this ticket
The scraper pipeline currently lacks a centralized logging layer entirely. As a result, failures in fetch, parsing, storage, or downstream shaping are not visible in a consistent, structured way.

### Why this matters
This is the specific blocker PAP-240 should address: operators cannot distinguish among:
- scrape never started
- scrape started but fetch failed
- fetch succeeded but parser extracted zero rows
- parser succeeded but persistence failed
- files were written but downstream Silver remained empty

Without structured logs, every failure mode looks similar from the outside.

---

## 4) Design Decision

## 4.1 Add a small shared logging package under `app/services/`
Introduce a lightweight application logging helper rather than ad hoc per-module setup.

### Proposed new file
- `app/services/logging_service.py`

### Why this location
- keeps logging cross-cutting but still inside shared services
- avoids polluting scraper modules with setup concerns
- supports reuse by pipeline and DB layers later

### Responsibilities
The service should provide:
- logger configuration/bootstrap
- structured key/value formatting for terminal readability
- environment-safe debug flag support
- optional file logging if configured
- helper wrappers for event logging and exception logging

---

## 4.2 Logging style
Use Python’s standard `logging` module only.

### Format requirements
Logs should be both:
- easy to scan in terminal
- machine-ish enough to grep/filter by key fields

Recommended output style:
- timestamp
- level
- logger name
- event name
- key fields

Example terminal line:
```text
2026-04-27T08:25:10Z INFO app.scraping.transfermarkt scrape.start source=transfermarkt slug=player-x url=https://... headless=true
```

Example error line:
```text
2026-04-27T08:25:14Z ERROR app.scraping.browser fetch.failed source=transfermarkt url=https://... error=PlaywrightUnavailableError traceback=...
```

### Why not raw JSON only
Pure JSON logs are less readable during MVP terminal debugging. A structured key/value line format is a better fit now, while still preserving fielded context.

---

## 4.3 Configuration surface
Extend runtime settings in `app/config.py`.

### Proposed new settings
- `log_level: str = os.getenv("LOG_LEVEL", "INFO")`
- `log_debug_enabled: bool = os.getenv("LOG_DEBUG_ENABLED", "false").lower() == "true"`
- `log_file_path: str | None = os.getenv("LOG_FILE_PATH")`
- `log_file_enabled: bool = os.getenv("LOG_FILE_ENABLED", "false").lower() == "true"`

### Behavior
- default terminal logs only
- debug mode opt-in through env var
- file logging enabled only when explicitly configured
- production-safe defaults remain moderate (`INFO`, no file output unless enabled)

---

## 5) Proposed Architecture Changes

## 5.1 New shared logging helper
### `app/services/logging_service.py`
Recommended surface:
- `configure_logging() -> None`
- `get_logger(name: str) -> logging.Logger`
- `log_event(logger, level, event, **fields) -> None`
- `log_exception(logger, event, exc, **fields) -> None`
- `is_debug_enabled() -> bool`

### Internal behavior
- guard against duplicate handler registration
- install a stream handler for terminal logs
- optionally add a file handler when enabled
- normalize booleans/None values consistently
- support `exc_info=True` for stack traces

---

## 5.2 Entry-point bootstrap
Ensure logging is configured once at startup / first import.

### Likely integration points
- `app/main.py` for API app startup
- scraper modules may defensively call `get_logger(...)` only, assuming configuration already exists
- for script-style runs, the helper should still self-bootstrap safely when first used

### Constraint
Avoid repeated `basicConfig(...)` calls from multiple modules.

---

## 6) Module-by-Module Instrumentation Plan

## 6.1 `app/scraping/browser.py`
### Add logs for:
- fetch start
- Playwright missing
- browser launch start/success
- page navigation start
- DOM loaded / network idle reached
- rendered HTML capture success with length
- fetch failure with exception + stack trace
- browser close in finally path when possible

### Additional fields to include
- `source` (passed in from caller, or optional config metadata)
- `url`
- `timeout_ms`
- `headless`
- `delay_seconds`
- `html_length`
- `elapsed_ms`

### Minor signature seam recommended
Consider extending `fetch_page_html(...)` to accept optional logging metadata such as:
- `source: str | None = None`
- `slug: str | None = None`

This avoids duplicating context reconstruction in logs.

---

## 6.2 `app/scraping/transfermarkt.py`
### Add logs for:
- scrape start
- slug derivation
- raw HTML save success/path
- parser start/end for profile
- parser start/end for transfer history
- extracted transfer count
- extracted profile completeness summary (e.g. required field count present)
- parsed payload save success/path
- empty/partial payload warnings
- top-level scrape failure with exception + stack trace
- scrape complete summary

### Empty-result policy
If profile fields are mostly empty or transfers count is zero, log explicitly as:
- `WARNING scrape.empty_result`
- `WARNING parse.partial_result`

Do not fail automatically in this ticket; just make the condition obvious.

---

## 6.3 `app/scraping/fbref.py`
### Add logs for:
- scrape start
- raw HTML save success/path
- match parser start/end
- player-match-stats parser start/end and extracted row count
- per-90 parser start/end and extracted row count
- DB-safe mapping counts
- parsed payload save success/path
- empty-stat warnings
- top-level scrape failure with exception + stack trace
- scrape complete summary

---

## 6.4 `app/scraping/parsers.py`
### Add logs for:
- profile parse start/end
- transfer-history parse start/end
- count of profile fields found vs expected
- count of transfer rows found
- JSON-LD missing / title fallback used (debug-level)
- suspiciously empty output warnings

### Important constraint
Keep parsing pure enough to remain testable.

Recommended approach:
- light internal module logger is acceptable
- do not turn helper functions into side-effect-heavy code
- focus logs at top-level parse functions, not every regex helper

---

## 6.5 `app/scraping/fbref_parsers.py`
### Add logs for:
- number of HTML tables discovered after comment stripping
- number of candidate stats/summary tables examined
- number of match rows extracted
- number of per-90 rows extracted
- match metadata extraction completeness
- empty parse warnings

### Debug mode only
More verbose counts, such as table IDs seen, should be debug-only to avoid noisy INFO logs.

---

## 6.6 `app/scraping/storage.py`
### Add logs for:
- directory ensure/create
- raw HTML write attempt + path + byte count
- raw HTML write success
- parsed JSON write attempt + path + record summary
- parsed JSON write success
- storage failure with exception + stack trace

### Fields to include
- `directory`
- `path`
- `slug`
- `bytes_written`
- `payload_keys`

---

## 6.7 `app/pipeline/silver.py`
### Add logs for:
- parsed JSON directory scan start/end
- number of files loaded per source
- malformed JSON or unexpected payload type warnings
- final output row counts for:
  - players
  - transfers
  - matches
  - player_match_stats
  - player_per90
- write attempts/results for Silver outputs
- warning when all outputs are empty

### Why include Silver
This is where successful scraping vs downstream emptiness becomes visible. PAP-239 showed empty artifacts can otherwise be mistaken for upstream fetch issues.

---

## 6.8 Database seam
### Current state
There is no active DB write path today.

### Plan for PAP-240
Do **not** invent a full DB ingestion feature. Instead:
- add logging around DB engine/session initialization in `app/db/base.py` only if low-risk and useful
- document that there are currently **no DB write attempts in the active scrape flow**, so PAP-240 should not fabricate fake DB write logs

### Explicit decision
For this ticket, “log DB write attempts and DB write results” should be interpreted as:
- instrument any current persistence writes that exist (file writes do exist)
- add a documented DB logging seam for future ingestion work
- do not create fake or placeholder DB write code merely to log it

---

## 7) Event Taxonomy

Adopt stable event names so grep and future tooling stay sane.

### Recommended events
#### Fetch/browser
- `fetch.start`
- `fetch.playwright_unavailable`
- `fetch.browser_launch`
- `fetch.goto`
- `fetch.render_complete`
- `fetch.success`
- `fetch.failed`

#### Source scrape orchestration
- `scrape.start`
- `scrape.raw_saved`
- `scrape.parsed_saved`
- `scrape.empty_result`
- `scrape.success`
- `scrape.failed`

#### Parsing
- `parse.profile.start`
- `parse.profile.complete`
- `parse.transfers.start`
- `parse.transfers.complete`
- `parse.fbref.match.start`
- `parse.fbref.match.complete`
- `parse.fbref.player_stats.start`
- `parse.fbref.player_stats.complete`
- `parse.fbref.per90.start`
- `parse.fbref.per90.complete`
- `parse.partial_result`

#### Storage
- `storage.ensure_directory`
- `storage.write_raw.start`
- `storage.write_raw.success`
- `storage.write_parsed.start`
- `storage.write_parsed.success`
- `storage.write.failed`

#### Silver pipeline
- `silver.load.start`
- `silver.load.complete`
- `silver.payload.invalid`
- `silver.build.complete`
- `silver.empty_output`
- `silver.write.success`

#### DB seam
- `db.engine.initialized`
- `db.session.created`
- future: `db.write.start`, `db.write.success`, `db.write.failed`

---

## 8) Debug Mode Design

## Environment-safe behavior
Debug mode should increase detail without changing scrape behavior.

### Debug mode should enable
- extra field completeness counts
- HTML table counts / candidate selector counts
- fallback path notes (e.g. JSON-LD absent, title fallback used)
- file paths and byte sizes
- maybe sampled payload key names

### Debug mode should not do
- dump full HTML bodies to logs
- emit sensitive env/config values
- overwhelm normal runs with row-by-row record spam

### Documentation requirement
README should gain a short section showing:
- `LOG_LEVEL=DEBUG`
- `LOG_DEBUG_ENABLED=true`
- optional `LOG_FILE_ENABLED=true`
- optional `LOG_FILE_PATH=...`

---

## 9) File Logging Support

## Requirement interpretation
“saved if project supports file logs” should be implemented minimally and safely.

### Proposed behavior
- terminal logging always available
- file logging optional via env vars
- if file logging is enabled but path is missing/unwritable, log one warning and continue with terminal logging

### Recommended default path behavior
Prefer explicit `LOG_FILE_PATH`; avoid silently inventing rotating infra in MVP.

---

## 10) Testing Plan

Add focused tests around log-emitting behavior without making tests brittle on exact timestamps.

### Proposed test files
- `tests/test_logging_service.py`
- `tests/test_scraping_logging.py`
- optionally extend parser/storage tests once they exist

### What to test
1. logging helper configures stream handler once
2. file logging can be enabled through env configuration
3. fetch-layer missing-Playwright path logs a structured failure event
4. storage write helpers log write attempt and success
5. transfermarkt/fbref scrape functions log extracted counts
6. empty-result conditions produce warning-level log events
7. exception paths include `exc_info`

### Testing technique
- use `unittest` + `assertLogs`
- mock Playwright/browser interactions
- avoid brittle full-line snapshot tests; assert event names and key fields instead

---

## 11) Implementation Order

### Step 1
Create shared logging helper in `app/services/logging_service.py` and extend `app/config.py` with logging env settings.

### Step 2
Bootstrap logging safely in `app/main.py` and make logger retrieval available to modules.

### Step 3
Instrument `app/scraping/browser.py` for fetch lifecycle + exception logging.

### Step 4
Instrument `app/scraping/transfermarkt.py` and `app/scraping/fbref.py` for scrape lifecycle and extracted-count summaries.

### Step 5
Instrument parser modules for top-level parse counts/completeness summaries.

### Step 6
Instrument `app/scraping/storage.py` for write attempts/results.

### Step 7
Instrument `app/pipeline/silver.py` to log parsed-input counts and empty-output warnings.

### Step 8
Add tests for logging behavior.

### Step 9
Document debug mode and include an example failure log in `README.md`.

---

## 12) Affected Files / Modules

### New
- `app/services/logging_service.py`
- `tests/test_logging_service.py`
- `tests/test_scraping_logging.py`

### Update
- `app/config.py`
- `app/main.py`
- `app/scraping/browser.py`
- `app/scraping/transfermarkt.py`
- `app/scraping/fbref.py`
- `app/scraping/parsers.py`
- `app/scraping/fbref_parsers.py`
- `app/scraping/storage.py`
- `app/pipeline/silver.py`
- `README.md`
- `memory/progress.md`
- `memory/decisions.md`

### Optional / only if low-risk
- `app/db/base.py`

---

## 13) Example Failure Log Output

```text
2026-04-27T08:25:10Z INFO app.scraping.transfermarkt scrape.start source=transfermarkt slug=junior-sornoza url=https://www.transfermarkt.com/... headless=true
2026-04-27T08:25:10Z INFO app.scraping.browser fetch.start source=transfermarkt slug=junior-sornoza url=https://www.transfermarkt.com/... timeout_ms=30000 headless=true
2026-04-27T08:25:10Z ERROR app.scraping.browser fetch.playwright_unavailable source=transfermarkt slug=junior-sornoza url=https://www.transfermarkt.com/... error=PlaywrightUnavailableError message="Playwright is not installed. Install dependencies and run `playwright install` before scraping."
Traceback (most recent call last):
  ...
2026-04-27T08:25:10Z ERROR app.scraping.transfermarkt scrape.failed source=transfermarkt slug=junior-sornoza url=https://www.transfermarkt.com/... stage=fetch
```

Example empty-result warning:
```text
2026-04-27T08:26:14Z WARNING app.scraping.fbref scrape.empty_result source=fbref slug=idv-vs-liga-de-quito player_match_stats_count=0 per90_count=0 match_found=false
```

---

## 14) Recommended Fix Order After PAP-240

PAP-240 should land before broader scrape-debugging work, but after this ticket the next highest-value issue remains the PAP-239 follow-up:

### Next recommended issue
`PAP-241 - Wire Concrete IDV Scrape Targets Into full_refresh and Add Scrape Runtime Preflight`

Why next:
- structured logs will reveal where the flow stops
- PAP-241 will make the orchestrated refresh actually perform scrapes and fail clearly when runtime prerequisites are missing

---

## 15) Files Changed In This Phase

Planning + memory only:
- `ARCHITECT_PLAN_PAP-240.md`
- `memory/progress.md`
- `memory/decisions.md`
