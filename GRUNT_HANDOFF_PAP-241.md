# GRUNT_HANDOFF_PAP-241 — Compatibility Verification Handoff for Pedant

## Ticket
PAP-241

## What I changed
Implemented a reusable static-HTTP compatibility probe and captured the current source compatibility findings in a dedicated report.

### New files
- `app/scraping/compatibility.py`
- `tests/test_scraping_compatibility.py`
- `PAP-241_TECHNICAL_COMPATIBILITY_REPORT.md`
- `GRUNT_HANDOFF_PAP-241.md`

### Updated files
- `app/scraping/__init__.py`
- `memory/progress.md`
- `memory/decisions.md`

## Root cause confirmed
The current sources are not technically uniform:
- Transfermarkt returns usable HTML to static HTTP on the tested squad page
- FBref returns a Cloudflare challenge page (`403`, `cf-mitigated: challenge`) instead of real content on the tested stats page

That means one fetch strategy will not work cleanly for both sources.

## What the probe does
`probe_static_request(...)` captures:
- source / url / method
- status code / final URL / content type / title
- elapsed time / HTML length
- challenge detection
- whether JS is likely required
- selector-like marker counts
- cookies and selected headers
- final classification (`ok_static_html`, `challenge_page`, `selector_missing`, etc.)

## Live findings captured
### Transfermarkt
- classification: `ok_static_html`
- status: `200`
- challenge: `false`
- JS likely required: `false`

### FBref
- classification: `challenge_page`
- status: `403`
- challenge: `true`
- JS likely required: `true`
- challenge cookie seen: `__cf_bm`

## Commands run
- `python3 -m unittest tests.test_scraping_compatibility`
- `PYTHONPATH=. python3 - <<'PY' ... probe_static_request(...) ... PY`

## Pedant review focus
Please review:
1. whether `javascript_likely_required=True` is the right boolean name for the FBref challenge case, since the blocker is really anti-bot gating
2. whether marker hits from challenge pages should be filtered further to avoid incidental strings like `stats` / `fbref`
3. whether the probe classification taxonomy should add a more explicit `access_blocked` vs `challenge_page` distinction
4. whether the probe should write JSON artifacts in a follow-up ticket, or stay in-memory for now

## Next recommended issue
`PAP-242 - Implement Source Compatibility Probes and Add Browser-Based FBref Access Validation`
