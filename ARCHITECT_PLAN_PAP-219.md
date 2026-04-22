# ARCHITECT PLAN — PAP-219

## Ticket
Build club development + resale analysis for club comparison.

## Requested comparison set
- IDV
- Benfica
- Ajax

## Required output
- rankings

---

## Memory Review Completed
Reviewed before planning:
- `memory/project_context.md`
- `memory/architecture.md`
- `memory/progress.md`
- `memory/decisions.md`

Inspected relevant code/data:
- `app/analysis/valuation_engine.py`
- `app/pipeline/gold.py`
- `data/silver/transfers.json`
- `data/silver/players.json`
- `data/gold/player_valuation.json`

---

## Current System State
The existing system is already organized around:
- Python backend + pipeline
- Silver tables as cleaned source data
- Gold artifacts as derived analysis outputs
- dedicated analysis engines under `app/analysis/`

Relevant existing pieces:
- player features in Gold
- KPI engine in Gold
- valuation engine in Gold
- API layer already established as a read-only surface
- Streamlit dashboard recently added as a thin UI layer

### Important observation
Current checked-in Silver artifacts are extremely sparse:
- `data/silver/players.json` is currently empty
- `data/silver/transfers.json` is currently empty

That means PAP-219 must be planned as a **graceful, artifact-backed ranking engine** that can:
- work when data exists
- degrade safely when data is incomplete
- emit transparent confidence/coverage information

---

## Problem Framing
The user wants to compare clubs on two related dimensions:
1. **development** — how well the club develops talent
2. **resale** — how well the club creates downstream market value / profitable exits

For the MVP, the system should produce a ranking across:
- IDV
- Benfica
- Ajax

Because this repo is analysis-first and artifact-backed, the correct implementation is **not** a database-heavy or UI-first feature. It should be a new downstream club-analysis artifact built from existing Silver/Gold inputs.

---

## Architectural Recommendation
Implement PAP-219 as a new Gold-layer analysis module.

### Recommended placement
- analysis logic under `app/analysis/`
- pipeline integration in `app/pipeline/run_pipeline.py`
- Gold artifact output under `data/gold/`
- optional read-only API exposure later if requested

### Recommended output artifact
- `data/gold/club_development_rankings.json`

### Why this fits the architecture
- matches existing KPI / similarity / valuation pattern
- preserves scraper → silver → gold layering
- avoids embedding business logic in API/UI
- allows dashboard/API to consume a stable derived artifact later

---

## Recommended Feature Scope
### MVP goal
Produce a transparent club ranking across IDV, Benfica, and Ajax using simple, explainable heuristics built from available player/transfer/valuation artifacts.

### Non-goal for MVP
Do **not** attempt to estimate true transfer profit accounting, squad amortization, contract value, or academy ownership economics. The source data is not rich enough for that.

---

## Proposed Output Shape
Create one ranking artifact with one row per target club.

### Suggested top-level structure
```json
{
  "model_version": "club_dev_resale_mvp_v1",
  "rankings": [
    {
      "club_name": "Benfica",
      "overall_score": 78.4,
      "development_score": 82.0,
      "resale_score": 74.8,
      "confidence_score": 68.0,
      "rank": 1,
      "components": {
        "talent_score": 0,
        "minutes_score": 0,
        "valuation_score": 0,
        "export_score": 0,
        "sale_activity_score": 0
      },
      "coverage": {
        "players_considered": 0,
        "transfer_rows": 0,
        "valuation_rows": 0
      }
    }
  ]
}
```

### Why this shape
- simple for APIs and dashboards to consume
- separates overall, development, resale, and confidence
- exposes transparent components for debugging and tuning

---

## Recommended Scoring Model
Use a bounded, additive scoring model similar to valuation.

### 1. Development score
This should capture how strong the club looks as a player-development environment.

#### Recommended components
1. **young-player valuation quality**
   - use player valuation output for players associated with the club
   - give more credit to players in development ages (for example <=24)

2. **young-player performance quality**
   - use KPI / player feature signals for club-associated players
   - reward clubs whose young players accumulate minutes and output

3. **minutes pathway signal**
   - reward clubs giving substantial minutes to young players
   - this is a simple proxy for actual development opportunity

#### Suggested formula
```text
development_score =
  0.40 * youth_valuation_component +
  0.35 * youth_performance_component +
  0.25 * youth_minutes_component
```

### 2. Resale score
This should capture how strong the club looks as a resale/export platform.

#### Recommended components
1. **outbound transfer activity**
   - count outbound transfers from the club in transfer history
   - outbound to stronger or higher-visibility clubs can receive a modest boost

2. **destination-quality / export quality**
   - small static weights for destination-club prestige or league strength
   - keep static lookup tiny and conservative for MVP

3. **player value realization proxy**
   - if currently valued players from the club have strong valuation scores, award a resale-potential signal even if sale history is sparse

#### Suggested formula
```text
resale_score =
  0.45 * outbound_transfer_component +
  0.25 * destination_quality_component +
  0.30 * current_value_realization_component
```

### 3. Overall score
```text
overall_score =
  0.60 * development_score +
  0.40 * resale_score
```

Reasoning:
- "development + resale" should lean slightly toward development because resale without development is noisy in sparse data.

---

## Data Source Recommendation
Use existing artifacts first and enrich conservatively.

### Primary sources
- `data/silver/players.json`
- `data/silver/transfers.json`
- `data/gold/player_valuation.json`
- `data/gold/player_features.json`
- `data/gold/kpi_engine.json`

### Joining recommendation
For MVP, join by:
- `player_name`
- `current_club`
- transfer row club names

This is acceptable because existing analysis already tolerates name-based joins.

### Important constraint
Because the current system has only partial club provenance and sparse artifacts, club association logic must be explicit and conservative.

---

## Club Association Recommendation
Introduce a small normalization layer for club names.

### Recommended helper behavior
Normalize club aliases into canonical club keys:
- `idv` / `independiente del valle` → `IDV`
- `benfica` / `sl benfica` → `Benfica`
- `ajax` / `afc ajax` → `Ajax`

### Why
This ranking depends on club grouping. Without normalization, results will fragment or undercount.

### Recommended file placement
- helper functions inside new analysis module or a small shared analysis helper

---

## Sparse-Data Strategy
This is the most important implementation constraint.

### Required behavior
If data is missing, the system should still emit rankings for:
- IDV
- Benfica
- Ajax

But rankings must include:
- low or zero scores when appropriate
- coverage counts
- confidence score
- optional notes/warnings if evidence is weak

### Confidence recommendation
Build a simple confidence score from coverage:
- player rows available
- valuation rows available
- transfer rows available

Example:
```text
confidence_score = min(100, player_coverage + valuation_coverage + transfer_coverage)
```
with each component bounded.

### Why this matters
Without confidence, empty artifacts could produce misleading rankings that look authoritative.

---

## Recommended New Analysis Module
### Suggested file
- `app/analysis/club_development.py`

### Suggested functions
- `normalize_club_name(...)`
- `build_club_development_rankings(...)`
- helper scoring functions for:
  - development components
  - resale components
  - confidence / coverage

### Inputs
A dict of Silver/Gold tables, similar to existing engines.

### Output
A list of ranking rows plus output path metadata.

---

## Pipeline Integration Recommendation
Integrate this into the existing pipeline runner exactly like KPI/similarity/valuation.

### Likely integration points
- `app/pipeline/run_pipeline.py`
- possibly helper references in `app/pipeline/gold.py` if that is the existing convention

### Pipeline behavior
After player features / KPI / valuation are available:
1. load required Silver/Gold tables
2. run club development + resale ranking builder
3. write `data/gold/club_development_rankings.json`

### Ordering recommendation
Run **after valuation**, because valuation is an input to the club model.

---

## API Recommendation
The ticket only requires rankings, not API work, so API exposure is optional unless requested explicitly.

### Architect recommendation
Do **not** require new API routes in PAP-219 unless the implementation needs a minimal read path for verification.

If a route is added later, suggested route:
- `GET /clubs/development`

But this should be treated as follow-up scope unless explicitly required.

---

## Testing Recommendation
Add focused engine tests only.

### Suggested test file
- `tests/test_club_development.py`

### Required test cases
1. **produces rankings for all requested clubs**
   - even when one or more clubs have no data

2. **sorts by overall score descending**

3. **handles empty artifacts gracefully**
   - emits rows with low scores and low confidence instead of crashing

4. **normalizes club aliases correctly**

5. **uses transfer rows to improve resale score when present**

6. **uses valuation/KPI/player features to improve development score when present**

7. **coverage/confidence fields reflect observed evidence**

### Do not require yet
- API integration tests
- dashboard tests
- browser-based UI validation

---

## Documentation Recommendation
After implementation, update README to describe:
- new club-ranking artifact
- what development/resale scores mean
- that the MVP ranking is heuristic and artifact-backed
- that results are confidence-sensitive when source coverage is sparse

---

## Recommended Memory Updates During Implementation
### `memory/progress.md`
Add:
- implemented club development + resale ranking engine for IDV, Benfica, and Ajax

### `memory/decisions.md`
Add:
- club comparison should be implemented as a Gold-layer heuristic ranking artifact
- rankings must include confidence/coverage because current source data can be sparse
- club name normalization is required for reliable grouping across artifacts

### `memory/architecture.md`
Add:
- club-comparison analysis is a downstream engine parallel to KPI, similarity, and valuation

---

## Risks / Watchouts
- current artifacts may not contain enough Benfica/Ajax data to produce meaningful rankings yet
- club names may vary across source payloads and silently break grouping without normalization
- transfer histories may lack directionality or destination richness, forcing conservative heuristics
- over-weighting sparse transfer data can make results unstable
- current repository scope is IDV-first, so cross-club comparisons should be framed as MVP heuristic rankings, not definitive scouting truth

---

## Recommended MVP Heuristic Details
To keep implementation transparent, use small bounded component scores.

### Development component suggestions
- youth valuation component: `0..40`
- youth performance component: `0..35`
- youth minutes component: `0..25`

### Resale component suggestions
- outbound transfer activity: `0..45`
- destination quality: `0..25`
- current value realization proxy: `0..30`

### Confidence component suggestions
- player evidence: `0..35`
- valuation evidence: `0..35`
- transfer evidence: `0..30`

This keeps all outputs easy to debug.

---

## Expected Files for Grunt Phase
Likely changes:
- `app/analysis/club_development.py`
- `app/pipeline/run_pipeline.py`
- possibly `app/pipeline/gold.py` if pipeline conventions require a helper hook
- `tests/test_club_development.py`
- `README.md`
- `memory/progress.md`
- `memory/decisions.md`
- `memory/architecture.md`
- `GRUNT_HANDOFF_PAP-219.md`

---

## Artifact for Next Role
Grunt should implement a new Gold-layer club development + resale ranking engine for IDV, Benfica, and Ajax that consumes existing Silver/Gold artifacts, writes `data/gold/club_development_rankings.json`, includes overall/development/resale/confidence scores plus coverage details, and handles sparse or missing data without crashing or pretending the evidence is complete.
