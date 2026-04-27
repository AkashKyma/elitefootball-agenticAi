# GRUNT_HANDOFF_PAP-242 — Extraction Hardening Handoff for Pedant

## Ticket
PAP-242

## What I changed
Implemented source-aware extraction hardening with explicit validation diagnostics.

### New files
- `app/scraping/validation.py`
- `tests/test_scraping_extraction.py`
- `PAP-242_EXTRACTION_REPORT.md`
- `GRUNT_HANDOFF_PAP-242.md`

### Updated files
- `app/scraping/browser.py`
- `app/scraping/parsers.py`
- `app/scraping/fbref_parsers.py`
- `app/scraping/transfermarkt.py`
- `app/scraping/fbref.py`
- `memory/progress.md`
- `memory/decisions.md`

## Root cause confirmed
The extraction failures were caused by:
- generic waits that did not prove content readiness
- brittle Transfermarkt label parsing
- overly broad FBref table targeting
- no post-parse validation seam, allowing semantically empty payloads to look successful

## What now works
- Transfermarkt fixture extraction returns a non-empty profile and transfer row
- FBref fixture extraction returns a non-empty match record, player stat row, and per-90 row
- FBref challenge pages are classified as `challenge_page`
- scrape payloads now include `diagnostics` with `extraction_status`, `missing_required_fields`, `record_counts`, and sample records

## Commands run
- `python3 -m py_compile app/scraping/browser.py app/scraping/parsers.py app/scraping/fbref_parsers.py app/scraping/validation.py app/scraping/transfermarkt.py app/scraping/fbref.py tests/test_scraping_extraction.py`
- `python3 -m unittest tests.test_scraping_extraction tests.test_scraping_logging`
- sample extraction probe via `PYTHONPATH=. python3 - <<'PY' ... PY`

## Pedant review focus
1. Verify `fetch.selector_missing` and `fetch.challenge_detected` are the right event names/levels in `browser.py`
2. Review whether `map_fbref_match_to_db(match_payload)` should still run on challenge-page payloads or be gated by diagnostics status
3. Check if `external_id` should remain populated on challenge pages or be blanked when target content is not reached
4. Review whether additional Transfermarkt labels or FBref table-id families should be captured now or deferred
5. Confirm `sample_records` inside diagnostics are acceptable payload size-wise for persisted artifacts

## Next recommended issue
`PAP-243 - Wire Extraction Diagnostics into full_refresh and Silver Filtering`

Suggested scope:
- propagate diagnostics into orchestrated refresh results
- decide how Silver should treat `challenge_page` / `schema_invalid` payloads
- optionally gate DB mapping previews on successful extraction status
