# elitefootball-agenticAi

Welcome to our System

## Project Bootstrap
This repository now includes a minimal Python backend scaffold, scraping module, database layer, and a mandatory memory system for future multi-agent work focused on IDV players.

## Memory Workflow
All future tasks MUST:
- read memory before work
- update memory after work

## MVP Dashboard
This repo now targets a lightweight Streamlit dashboard for internal player exploration.

### Pages
- `Player`
- `Compare`

### Run locally
Start the backend first:
```bash
uvicorn app.main:app --reload
```

Then launch the dashboard:
```bash
streamlit run dashboard/Home.py
```

### API URL
The dashboard reads from the backend API and defaults to:
- `http://localhost:8000`

Override with:
- `ELITEFOOTBALL_API_BASE_URL`
