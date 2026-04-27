# ARCHITECT_PLAN_PAP-241 — Verify Target Website Accessibility, Rendering Requirements, and Blocking Behavior

## Ticket
PAP-241

## Role
Architect — planning/design only. No application code implemented in this phase.

## Goal
Determine whether the target sites used by the current scraping pipeline are technically compatible with the current approach, and explicitly identify whether scraping requires:
- plain HTTP requests
- browser automation
- JavaScript rendering
- special headers/cookies/session handling
- anti-bot mitigation or alternate acquisition strategy

This phase should leave a concrete compatibility report and an implementation plan for the next role without changing scraper architecture yet.

---

## 1) Current Stack and Scope Reviewed

### Current source targets in repo
The active scraping stack currently targets two source families:
- **Transfermarkt** under `app/scraping/transfermarkt.py`
- **FBref** under `app/scraping/fbref.py`

### Current fetch approach
- `app/scraping/browser.py` uses Playwright-driven browser fetches (`page.goto(...); wait_for_load_state("networkidle"); page.content()`).
- Static-HTTP-only fetching is not currently implemented in repo.

### Current parser expectations
- Transfermarkt parser in `app/scraping/parsers.py` expects label-bearing HTML to exist in the fetched document.
- FBref parser in `app/scraping/fbref_parsers.py` expects actual stats HTML tables and already knows how to strip comment wrappers.

### Downstream dependency note
- Transfermarkt currently serves player profile + transfer data.
- FBref is the primary source for match-stat rows that feed Silver/Gold/dashboard analysis.

---

## 2) Live Compatibility Checks Performed

## 2.1 Transfermarkt check
Tested URL:
- `https://www.transfermarkt.com/independiente-del-valle/kader/verein/19309`

### Observed via `web_fetch`
- HTTP status: `200`
- readable content returned successfully
- extracted content included player names, positions, and market-value text directly in HTML

### Observed via `curl`
- `curl -I -L ...` returned `HTTP/2 200`
- no obvious challenge/anti-bot interstitial in the response headers
- body probes found:
  - `<title>Independiente del Valle - Detailed squad 2026 | Transfermarkt`
  - player text such as `Júnior Sornoza`
  - `Market value`
  - no obvious JS bootstrap marker required for the content sample that was tested

### Preliminary conclusion
For the tested Transfermarkt page class, **plain HTTP retrieval appears technically viable** for basic content acquisition. Browser automation is not clearly required just to receive the initial HTML for squad/profile-like content.

---

## 2.2 FBref check
Tested URL:
- `https://fbref.com/en/squads/990519b8/Independiente-del-Valle-Stats`

### Observed via `web_fetch`
- fetch failed with `403`
- response body/title indicated `Just a moment...`

### Observed via `curl`
- `curl -I -L ...` returned `HTTP/2 403`
- response headers included:
  - `cf-mitigated: challenge`
  - `server: cloudflare`
  - `set-cookie: __cf_bm=...`
  - CSP references to `https://challenges.cloudflare.com`
- body probes found:
  - `<title>Just a moment...`
  - no target team text
  - no stats table ids
  - no comment-wrapped table markers from actual FBref content because the challenge page was returned instead

### Preliminary conclusion
For the tested FBref page class, **plain HTTP retrieval is not technically viable in the current environment** because Cloudflare challenge protection blocks access before actual page content is delivered.

---

## 3) Root Cause Found

### Root cause for PAP-241
The two target sources do not have the same compatibility profile:
- **Transfermarkt** currently appears accessible with basic HTTP on the tested page type.
- **FBref** is actively blocked by Cloudflare challenge behavior for the tested page type, so the current environment cannot retrieve actual content with plain HTTP requests.

### Practical impact
This means the team cannot choose one universal fetch method blindly:
- a requests-style fetch path is likely enough for at least some Transfermarkt pages
- FBref currently requires either a browser-based challenge-clearing approach or an alternate acquisition strategy

---

## 4) Technical Compatibility Report

## Transfermarkt
### Static HTTP requests
- **Confirmed workable** for the tested squad page.
- Response status `200` with usable HTML content.

### JavaScript rendering requirement
- **Not confirmed as required** for the tested page type.
- The relevant content appears in server-returned HTML.

### DOM readiness timing
- For the tested page type, no client-render delay was needed to expose obvious content.
- Current Playwright `networkidle` wait may still be safe, but appears unnecessary for the tested content slice.

### Selectors after client rendering
- Not indicated by current probes.
- Current content sample suggests selectors/labels are present in initial HTML.

### Headers/cookies/session handling
- No special cookie/session requirement was observed for the tested page.
- Browser-like User-Agent was sufficient for probe success.

### Bot protection/challenge behavior
- No explicit challenge page was observed in current checks.
- That does **not** rule out rate-limit or anti-bot escalation under heavier scraping.

### Compatibility verdict
- **Valid with requests-first approach for tested page class**
- Browser automation remains optional for resilience, but is not clearly required by the tested Transfermarkt content path.

---

## FBref
### Static HTTP requests
- **Confirmed blocked** in current environment for the tested page.
- Returns `403` challenge page rather than real content.

### JavaScript rendering requirement
- The primary blocker is **anti-bot challenge**, not ordinary content rendering.
- Whether JS rendering is needed after challenge clearance is secondary right now.

### DOM readiness timing
- Cannot meaningfully evaluate target-selector readiness because the challenge page is returned instead of the destination page.

### Selectors after client rendering
- Current target selectors are unavailable because the scraper never receives the real FBref page body.

### Headers/cookies/session handling
- Response clearly suggests cookie- and challenge-based session gating (`__cf_bm`, Cloudflare challenge resources).
- Basic browser-like headers alone were insufficient.

### Bot protection/challenge behavior
- **Explicitly confirmed**.
- Current environment is seeing Cloudflare challenge behavior.

### Compatibility verdict
- **Requests-only approach is not valid for FBref in the current environment.**
- A browser-driven challenge-clearing path may be required, but success is not guaranteed without validating real browser/session behavior.

---

## 5) Recommendation: requests vs Playwright vs Puppeteer vs other

## Recommended source-specific strategy
### Transfermarkt
**Recommendation:** `requests` or equivalent static HTTP fetch should be the default first-line method for tested squad/profile-style pages.

Why:
- lower operational cost
- fewer runtime dependencies
- less brittle than full browser automation when server-rendered HTML is already present
- avoids requiring Playwright for pages that do not need JS rendering

Fallback:
- keep Playwright as an optional fallback for pages where selectors/content are absent in static HTML or when site behavior changes

### FBref
**Recommendation:** Playwright-class browser automation is the only valid next thing to test inside the current project direction.

Why:
- requests/plain HTTP is already confirmed blocked by Cloudflare challenge
- Puppeteer would be conceptually similar but would add a second browser stack and does not align with current Python architecture
- Playwright is already the chosen stack and is the least disruptive browser option to validate next

Important caveat:
- PAP-241 does **not** confirm that Playwright will definitely solve FBref access
- it only confirms that plain HTTP will not
- browser-session validation is still required in a later implementation phase

### Alternate/contingency option
If Playwright also gets blocked consistently:
- consider a different source for the missing stat classes
- or a managed data/API acquisition path
- or a more specialized browser/session infrastructure

That should be treated as a fallback decision only after a real Playwright-based compatibility test is completed.

---

## 6) Rendering Strategy Recommendation

## Transfermarkt rendering strategy
### Preferred
1. try static HTTP first
2. parse directly from returned HTML
3. fall back to Playwright only when required-field completeness is too low or selector checks fail

### Why
The tested page does not currently justify browser overhead.

## FBref rendering strategy
### Preferred
1. use browser automation validation as the next compatibility experiment
2. explicitly capture:
   - final URL
   - response status chain if available
   - screenshot on failure
   - cookies/session state after navigation
   - whether real table IDs appear after challenge resolution
3. if blocked, classify as anti-bot challenge failure rather than ordinary parse failure

### Why
The current blocker is access protection, not parser logic.

---

## 7) Implementation Plan for the Next Role

## Step 1 — Add a compatibility probe utility under `app/scraping/`
Introduce a small, source-aware probe layer rather than mixing diagnostics into main scraper entrypoints immediately.

### Proposed new module
- `app/scraping/compatibility.py`

### Responsibilities
- test static HTTP fetch viability
- inspect response status, headers, cookies, title/body markers
- classify outcomes such as:
  - `ok_static_html`
  - `challenge_page`
  - `login_wall`
  - `empty_body`
  - `selector_missing`
  - `timeout`

---

## Step 2 — Probe Transfermarkt with static HTTP first
For a concrete tested URL:
- fetch via `requests`
- check status code
- inspect body markers used by current parsers
- record whether required labels exist in raw HTML

### Success condition
- required labels appear in initial HTML without browser rendering

---

## Step 3 — Probe FBref with static HTTP and classify challenge behavior
For a concrete tested URL:
- fetch via `requests`
- record status and challenge headers/body markers
- store a probe artifact/report

### Success condition
- challenge behavior is classified explicitly instead of surfacing later as a generic parse failure

---

## Step 4 — Add browser-based compatibility validation for FBref
Use the current Playwright path to test whether a real browser session can reach actual content.

### Capture
- navigation success/failure
- visible page title
- HTML length
- presence of expected table ids / comment-wrapped tables
- screenshot on failure
- challenge markers if still present

### Important boundary
This should remain a **probe/diagnostic step**, not yet a full scraper redesign.

---

## Step 5 — Add source-specific fetch-mode decisions
After compatibility probing:
- Transfermarkt pages can be marked `static_preferred`
- FBref pages can be marked `browser_required` or `browser_blocked`

This decision data should live near the scraping boundary, not in downstream pipeline code.

---

## Step 6 — Document exact operating guidance
README / memory should explain:
- Transfermarkt: requests-first
- FBref: currently blocked on plain HTTP, browser validation required
- if browser validation fails, treat as source-access blocker and do not blame parsers

---

## 8) Affected Files / Modules (planned)

### New
- `app/scraping/compatibility.py`
- `tests/test_scraping_compatibility.py`
- possibly a dedicated artifact/report under repo root or `memory/`

### Update
- `app/scraping/browser.py`
- `app/scraping/transfermarkt.py`
- `app/scraping/fbref.py`
- `README.md`
- `memory/progress.md`
- `memory/decisions.md`

Potentially:
- `requirements.txt` if `requests` probing needs explicit reaffirmation (already present today)

---

## 9) Success Criteria Interpretation

PAP-241 should be considered successful when the repo/documentation can answer, concretely:
- Which source works with plain HTTP right now?
- Which source is blocked by challenge behavior?
- Which source requires browser-based validation?
- Is the current Playwright choice still valid?

### Current best answer from this planning phase
- **Transfermarkt:** current technical choice can be simplified; requests-first is valid for the tested page type.
- **FBref:** current technical choice must be browser-oriented if kept at all; requests-only is invalid in the current environment due to explicit Cloudflare challenge behavior.

---

## 10) Next Recommended Issue

**Recommended next issue:**
`PAP-242 - Implement Source Compatibility Probes and Add Browser-Based FBref Access Validation`

Suggested scope:
- add a compatibility probe helper
- classify static-vs-browser viability per source
- validate whether Playwright can actually reach FBref content beyond the Cloudflare challenge
- persist probe artifacts/logs for repeatable diagnosis

---

## 11) Files Changed In This Phase

Planning + memory only:
- `ARCHITECT_PLAN_PAP-241.md`
- `memory/progress.md`
- `memory/decisions.md`
