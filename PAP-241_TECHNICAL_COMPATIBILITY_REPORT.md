# PAP-241 — Technical Compatibility Report

## Ticket
PAP-241

## Scope
This report verifies whether the current target websites can be scraped with the project’s current technical approach and whether they require:
- static HTTP requests
- browser automation
- JavaScript rendering
- special headers/cookies/session handling
- anti-bot mitigation

## Sources tested
- Transfermarkt squad page:
  - `https://www.transfermarkt.com/independiente-del-valle/kader/verein/19309`
- FBref team stats page:
  - `https://fbref.com/en/squads/990519b8/Independiente-del-Valle-Stats`

---

## 1) Transfermarkt result

### Static HTTP viability
Confirmed workable for the tested squad page.

### Evidence
- `HTTP/2 200`
- readable HTML returned via static fetch
- title present in initial HTML
- squad/player text present in initial HTML
- no explicit challenge marker observed

### Rendering requirement
No confirmed JavaScript-render requirement for the tested page class.

### Session / headers / cookies
- browser-like User-Agent was sufficient for the live probe
- no required challenge cookie or access-interstitial was observed in the tested response

### Selector availability
Expected content markers appeared in the initial HTML response, which suggests selectors do not depend on client-side rendering for this page class.

### Compatibility conclusion
**Requests-first is valid** for the tested Transfermarkt page class.

---

## 2) FBref result

### Static HTTP viability
Confirmed blocked in the current environment for the tested page.

### Evidence
- `HTTP/2 403`
- `cf-mitigated: challenge`
- Cloudflare challenge body/title (`Just a moment...`)
- `__cf_bm` cookie observed
- no target content/table markers present in the returned body

### Rendering requirement
The primary blocker is anti-bot challenge behavior, not ordinary content rendering.

### Session / headers / cookies
- browser-like User-Agent alone was insufficient
- Cloudflare challenge headers/cookies indicate session/challenge gating

### Selector availability
Cannot evaluate actual selectors in static HTML because the target content is never returned; only the challenge page is returned.

### Compatibility conclusion
**Requests-only is not valid** for FBref in the current environment.

---

## 3) Technical choice recommendation

### Transfermarkt
- Prefer **requests** first
- Keep **Playwright** as fallback if required fields disappear from static HTML or later page classes prove different
- Do **not** require Puppeteer

### FBref
- Prefer **Playwright validation next** using the current Python stack
- Do **not** add Puppeteer; it would duplicate browser infrastructure without solving the confirmed blocker by itself
- If Playwright still hits challenge pages, treat FBref as a source-access blocker rather than a parser issue

---

## 4) Rendering strategy recommendation

### Transfermarkt
- fetch via static HTTP first
- parse immediately from returned HTML
- use browser automation only as fallback

### FBref
- run browser-based compatibility validation next
- capture challenge-vs-real-content outcome explicitly
- collect final title, page HTML length, expected table-id presence, and failure screenshots if browser access still fails

---

## 5) Root cause summary
The current source stack is not compatibility-uniform:
- Transfermarkt currently appears accessible with static HTTP for the tested squad page
- FBref is currently blocked by Cloudflare challenge behavior before real content is delivered

That means a single fetch strategy is not sufficient for both sources.

---

## 6) Recommended next issue
**PAP-242 - Implement Source Compatibility Probes and Add Browser-Based FBref Access Validation**

Suggested scope:
- keep a reusable compatibility probe helper in repo
- classify static-vs-browser viability per source
- validate whether Playwright can actually reach FBref content beyond the challenge page
- persist probe artifacts/logs for repeatable diagnosis

---

## 7) Files changed in this phase
- `app/scraping/compatibility.py`
- `tests/test_scraping_compatibility.py`
- `PAP-241_TECHNICAL_COMPATIBILITY_REPORT.md`
- `GRUNT_HANDOFF_PAP-241.md`
- `memory/progress.md`
- `memory/decisions.md`
