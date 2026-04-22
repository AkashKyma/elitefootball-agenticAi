# GRUNT_HANDOFF_PAP-222

## Scope
Implement the PAP-222 multi-agent system described in `ARCHITECT_PLAN_PAP-222.md`.

## What to build
- `app/agents/types.py`
- `app/agents/scraper_agent.py`
- `app/agents/data_cleaner_agent.py`
- `app/agents/analyst_agent.py`
- `app/agents/report_generator_agent.py`
- refactor `app/agents/orchestrator.py`
- update `app/agents/__init__.py`
- add `memory/agent_roles.md`
- add agent/orchestrator tests
- update `README.md`

## Required architectural rules
- Keep existing scraping logic in `app/scraping/`
- Keep existing pipeline logic in `app/pipeline/`
- Keep existing analysis logic in `app/analysis/`
- `app/agents/` should coordinate these modules, not duplicate them
- preserve `/summary` compatibility
- do not introduce distributed infra or background job dependencies

## Recommended implementation shape
### Shared types
Add a small task/result contract:
- `AgentTask`
- `AgentStepResult`
- `AgentRunResult`

### Agents
Each agent should expose a single `run(task)`-style entrypoint and return a structured result containing:
- `agent_name`
- `task_kind`
- `status`
- `summary`
- `artifacts`
- `metadata`

### Orchestrator
Add:
- a central route map
- `supported_task_kinds()`
- `route_task(task)`
- `run_task(task)`
- composite workflow support for `full_refresh`

### Memory
Add `memory/agent_roles.md` describing:
- agent purposes
- boundaries
- route map
- note that orchestration coordinates existing modules

## Tests minimums
- task kind routes to the expected agent
- unsupported task kind fails clearly
- `full_refresh` runs steps in scraper → cleaner → analyst → reporter order
- `build_agent_summary()` still works for `/summary`
- report-generator output is structured and deterministic

## Suggested execution order
1. Add shared types
2. Add individual agent modules
3. Refactor orchestrator
4. Update exports and summary compatibility
5. Add memory role manifest
6. Add tests
7. Update README
