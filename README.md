# elitefootball-agenticAi

Welcome to our System

## Project Bootstrap
This repository now includes a minimal Python backend scaffold, scraping module, database layer, and a mandatory memory system for future multi-agent work focused on IDV players.

## Memory Workflow
All future tasks MUST:
- read memory before work
- update memory after work

## Club Development + Resale Rankings
The pipeline now supports an MVP club-comparison artifact for:
- IDV
- Benfica
- Ajax

### Output artifact
- `data/gold/club_development_rankings.json`

### Notes
- rankings are heuristic and artifact-backed
- outputs include development, resale, overall, and confidence scores
- low-confidence results should be treated as sparse-data indicators, not definitive club truth
