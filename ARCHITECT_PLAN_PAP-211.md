# ARCHITECT PLAN — PAP-211

## Ticket
Build data pipeline (Raw → Clean → Features).

## Requested Design
- Bronze = raw HTML
- Silver = cleaned tables
- Gold = features

Required output in implementation phase:
- transformation scripts

Memory must be updated with:
- pipeline design

---

## Memory Review Completed
Reviewed before planning:
- `memory/project_context.md`
- `memory/architecture.md`
- `memory/progress.md`
- `memory/decisions.md`

## Current System State
The repo already contains:
- source-specific scraping under `app/scraping/`
- raw HTML persistence and parsed JSON persistence patterns
- DB models for `clubs`, `players`, `matches`, and `stats`
- no explicit transformation pipeline layer yet

Current persistence pattern already implies the first part of the pipeline:
- raw HTML is saved to source-specific directories
- parsed JSON is saved as a scraper output artifact

What is missing is a formal pipeline layer that:
1. treats raw source artifacts as Bronze inputs
2. standardizes cleaned tables as Silver outputs
3. computes model/report-friendly features as Gold outputs

---

## High-Level Recommendation
Add a dedicated pipeline module instead of embedding transformations into scraper files.

### Preferred direction
Create a small pipeline layer under `app/` that is responsible for:
- reading Bronze artifacts from disk
- normalizing them into source-agnostic Silver tables
- deriving reusable Gold features for downstream analysis

This preserves the current architecture by keeping:
- scraping in `app/scraping/`
- transformations in a separate pipeline package
- DB layer in `app/db/`

---

## Recommended File / Module Plan
Suggested additions:
- `app/pipeline/__init__.py`
- `app/pipeline/bronze.py`
  - helpers to discover and load raw/parsed artifacts
- `app/pipeline/silver.py`
  - cleaning/normalization transforms into table-like records
- `app/pipeline/gold.py`
  - feature generation from cleaned records
- `app/pipeline/io.py`
  - read/write helpers for JSON outputs and directory management
- `app/pipeline/run_pipeline.py`
  - high-level orchestration entrypoint for Bronze → Silver → Gold

If Grunt prefers a script-oriented layout, keep the logic in `app/pipeline/` and expose thin runnable scripts only.

---

## Pipeline Layer Design
### Bronze layer
Bronze should represent source-preserving artifacts.

Inputs:
- raw HTML files from Transfermarkt and FBref
- existing parsed JSON artifacts when available

Bronze principles:
- no destructive normalization
- preserve provenance
- retain source path and scrape source
- keep one artifact per captured page/file

Recommended Bronze record shape:
```json
{
  "source": "transfermarkt|fbref",
  "artifact_type": "raw_html|parsed_json",
  "artifact_path": "...",
  "captured_at": "...",
  "slug": "..."
}
```

### Silver layer
Silver should contain cleaned tables with source-specific quirks normalized away.

Recommended Silver tables:
- `silver_players.json`
- `silver_transfers.json`
- `silver_matches.json`
- `silver_player_match_stats.json`
- `silver_player_per90.json`

Silver principles:
- cleaned field names
- normalized null/default handling
- explicit source provenance retained
- rows shaped for DB ingestion or feature generation
- no raw HTML retained in-row

### Gold layer
Gold should contain analysis-ready features.

Recommended Gold outputs for MVP:
- `gold_player_features.json`
- `gold_match_features.json`

Gold principles:
- derived metrics only
- stable schema for downstream analysis
- values computed from Silver, not directly from raw HTML

---

## Transformation Script Recommendation
The implementation phase should produce scripts/functions for three steps.

### 1. Bronze discovery / staging script
Responsibility:
- scan raw and parsed source directories
- produce a Bronze manifest of available artifacts

Suggested output:
- `data/bronze/manifest.json`

### 2. Silver transformation script
Responsibility:
- read parsed scraper payloads
- emit cleaned, table-shaped records

Examples:
- Transfermarkt profile JSON → normalized player rows
- Transfermarkt transfer JSON → normalized transfer rows
- FBref match JSON → normalized match rows
- FBref player match stats JSON → normalized stat rows
- FBref per-90 JSON → cleaned per-90 rows

Suggested outputs:
- `data/silver/players.json`
- `data/silver/transfers.json`
- `data/silver/matches.json`
- `data/silver/player_match_stats.json`
- `data/silver/player_per90.json`

### 3. Gold feature generation script
Responsibility:
- compute derived features from Silver outputs

Suggested examples:
- player goal involvement rate
- minutes-normalized attacking contribution
- card risk indicators
- shot contribution indicators
- match-level score differential feature

Suggested outputs:
- `data/gold/player_features.json`
- `data/gold/match_features.json`

---

## Source-to-Pipeline Mapping Recommendation
### Transfermarkt inputs
Use parsed Transfermarkt outputs to populate Silver:
- `profile` → player-clean table rows
- `transfers` → transfer-clean table rows

### FBref inputs
Use parsed FBref outputs to populate Silver:
- `match` → match-clean table rows
- `player_match_stats` → player-match-stats clean rows
- `player_per_90` → player-per90 clean rows

This allows the pipeline to consume source-specific parsed outputs without forcing parsers to become transformation scripts.

---

## Normalization Rules for Silver
Recommended rules:
- trim and normalize string whitespace
- preserve `source`
- preserve source identifiers/slug where available
- coerce numeric fields safely
- standardize missing values to `null`
- keep one record shape per table
- do not mix match-level rows and player-level rows in the same output

Examples:
- `minutes`, `goals`, `assists`, `shots` → numeric or null
- `market_value`, `fee` remain strings for MVP unless a reliable parser is introduced
- per-90 metric bags may stay nested initially if full column expansion is premature

---

## Feature Design Recommendation (Gold)
Keep Gold intentionally modest for MVP.

### Player features
Suggested derived fields:
- `goal_contributions = goals + assists`
- `goal_contribution_per_90` when enough fields exist
- `shot_involvement_flag`
- `discipline_risk_score = yellow_cards + (red_cards * 2)`
- `minutes_bucket`

### Match features
Suggested derived fields:
- `score_difference = home_score - away_score`
- `is_draw`
- `total_goals`
- `idv_involved_flag` if club normalization supports it

### Per-90 features
For MVP, preserve cleaned per-90 rows in Silver and only promote a small subset to Gold if they can be consistently derived.

---

## Non-Breaking Architecture Guidance
Do not break existing boundaries.

Specifically:
- do not move scraper logic into pipeline files
- do not overload DB models with feature logic
- do not turn API routes into batch transformation runners
- keep source-specific parsing separate from source-agnostic transforms

---

## Recommended Memory Updates During Implementation
### `memory/progress.md`
Add:
- pipeline module created
- Bronze/Silver/Gold transformation scripts added
- feature outputs scaffolded

### `memory/decisions.md`
Add:
- Bronze/Silver/Gold layer definitions
- which source outputs feed which Silver tables
- Gold feature scope kept intentionally narrow for MVP

### `memory/architecture.md`
Add:
- pipeline layer location
- relationship between scraping outputs and transformation scripts

---

## Risks / Watchouts
- coupling feature generation directly to scraper internals
- mixing raw HTML with cleaned table outputs
- generating Gold directly from source payloads instead of Silver
- overdesigning schemas before real data variation is observed
- forcing per-source quirks into a single messy transform function

---

## QA Checklist for Pedant
Pedant should verify:
- pipeline code stays out of scraper modules except for consumption of parsed outputs
- Bronze/Silver/Gold responsibilities are separated
- transformation scripts write stable outputs under `data/bronze`, `data/silver`, and `data/gold`
- Silver outputs are table-shaped and source-cleaned
- Gold outputs are derived from Silver, not raw HTML directly
- memory includes explicit pipeline design decisions

---

## Files Expected to Change in Grunt Phase
Most likely:
- `app/pipeline/__init__.py`
- `app/pipeline/io.py`
- `app/pipeline/bronze.py`
- `app/pipeline/silver.py`
- `app/pipeline/gold.py`
- `app/pipeline/run_pipeline.py`
- `memory/progress.md`
- `memory/decisions.md`
- `memory/architecture.md`
- `GRUNT_HANDOFF_PAP-211.md`

---

## Artifact for Next Role
Grunt should implement a lightweight `app/pipeline/` module that reads existing raw/parsed scraper artifacts, stages a Bronze manifest, writes cleaned Silver table outputs, derives small MVP-safe Gold feature outputs, and updates memory with explicit pipeline design decisions and next steps.
