# Agent Roles

## Purpose
This file documents the MVP multi-agent layout introduced for PAP-222.

The system is **not** a distributed autonomous agent platform. It is an in-process orchestration layer that coordinates existing repository modules.

## Agents

### Coordinator / Orchestrator
- owns task routing
- selects execution order
- supports composite workflows such as `full_refresh`

### Scraper Agent
- coordinates scraping entrypoints in `app/scraping/`
- should not own cleaning or analysis logic

### Data Cleaner Agent
- coordinates Bronze/Silver/Gold build steps in `app/pipeline/`
- bridges scraped/parsing outputs into analysis-ready artifacts

### Analyst Agent
- coordinates KPI, advanced metrics, risk, similarity, and valuation generation in `app/analysis/`
- should not duplicate formulas from analysis modules

### Report Generator Agent
- produces operator-facing summaries from artifacts and orchestrator results
- remains read-only

## Supported Task Kinds
- `scrape_players`
- `clean_data`
- `run_analysis`
- `generate_report`
- `full_refresh`

## Default Route Map
- `scrape_players` → Scraper Agent
- `clean_data` → Data Cleaner Agent
- `run_analysis` → Analyst Agent
- `generate_report` → Report Generator Agent
- `full_refresh` → Scraper Agent → Data Cleaner Agent → Analyst Agent → Report Generator Agent

## Boundaries
- scraping stays in `app/scraping/`
- pipeline stays in `app/pipeline/`
- analysis stays in `app/analysis/`
- `app/agents/` coordinates those modules instead of replacing them
