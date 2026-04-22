# ARCHITECT_PLAN_PAP-222 — Implement Multi-Agent System (Scraper, Analyst, Reporter)

## Ticket
PAP-222

## Role
Architect — planning/design only. No application code implemented in this phase.

## Goal
Expand the current lightweight agent layer into a concrete MVP multi-agent system with:
- Scraper Agent
- Data Cleaner Agent
- Analyst Agent
- Report Generator Agent
- Orchestrator task routing
- explicit memory-backed agent role definitions

The implementation must preserve the current repository architecture, avoid introducing external orchestration dependencies, and remain compatible with the existing artifact-backed pipeline.

---

## 1) Current System State

### Existing agent implementation
Current `app/agents/orchestrator.py` is only a static summary layer:
- defines `AgentRole` dataclass
- exposes `AGENT_ROLES`
- exposes `build_agent_summary()`

This means the repo already acknowledges a multi-agent design conceptually, but there is no real:
- task classification
- task routing
- agent execution contract
- shared context object
- report-generation workflow

### Existing system boundaries
The repository already has strong separations that should remain intact:
- `app/scraping/` for source-specific data collection
- `app/pipeline/` for Bronze/Silver/Gold transformations
- `app/analysis/` for KPI, similarity, valuation, and risk outputs
- `app/api/` for read-only artifact-backed responses
- `memory/` for project continuity and operating notes

### Key architectural opportunity
The cleanest PAP-222 implementation is not a distributed agent platform. It is a **small in-process orchestration layer** that coordinates existing modules through explicit roles and task-routing rules.

---

## 2) Design Decision

### Decision summary
Implement PAP-222 as a lightweight orchestration framework under `app/agents/` with:
1. a shared task contract
2. explicit agent role classes/modules
3. an orchestrator that maps task kinds to agent handlers
4. a small memory/role manifest for transparency

### Why this is the right fit
This matches the current repo maturity:
- avoids premature infrastructure complexity
- reuses existing scraper/pipeline/analysis modules
- keeps orchestration inspectable and testable
- gives `/summary` a richer and more truthful agent model
- creates a stable seam for future async/background execution if needed later

### Explicit non-goals for PAP-222
Do **not** in this ticket:
- add Celery, Kafka, Redis, or a job queue
- build a true autonomous LLM-agent runtime
- move scraping/pipeline logic into `app/agents/`
- create external persistence for agent runs beyond current memory/docs
- break current API routes or pipeline entrypoints

---

## 3) Proposed Architecture

## 3.1 Core concept
The multi-agent system should be **orchestration over existing modules**, not duplication of them.

### Proposed flow
1. caller submits a structured task to orchestrator
2. orchestrator determines task kind / route
3. orchestrator invokes the appropriate agent handler(s)
4. agents call existing modules in `app/scraping/`, `app/pipeline/`, `app/analysis/`
5. orchestrator returns a structured result containing:
   - selected route
   - executed steps
   - generated artifacts / outputs
   - summary text where applicable

---

## 3.2 Proposed agent roster

### Scraper Agent
Responsibility:
- collect source data from configured scrapers
- trigger raw + parsed storage through existing scraping modules

This agent should **not** transform data into Silver/Gold itself.

### Data Cleaner Agent
Responsibility:
- invoke Bronze/Silver/Gold transformation pipeline steps
- normalize parsed outputs into table-shaped artifacts
- optionally run the full pipeline when requested

This agent is the bridge between scraping outputs and analysis-ready data.

### Analyst Agent
Responsibility:
- run downstream analytical engines
- gather KPI / similarity / valuation / risk artifacts
- summarize which analysis outputs were produced

This agent should wrap the existing analysis and pipeline outputs rather than re-implement formulas.

### Report Generator Agent
Responsibility:
- build operator-facing summaries from artifact-backed analysis outputs
- generate human-readable summaries of current data and analyses
- prepare structured report payloads for API/UI consumption later

This agent should stay read-only and should not perform scraping or analysis computation directly.

### Orchestrator
Responsibility:
- classify and route tasks
- define execution sequence for composite tasks
- record route metadata for debug/summary use

### Memory / Role Manifest
Responsibility:
- document agent roles, boundaries, and workflow expectations
- provide transparent metadata for `/summary` and future debugging

---

## 4) Proposed File-Level Changes

### New files
1. `app/agents/types.py`
   - shared dataclasses / typed contracts for agent tasks and results
   - e.g. `AgentTask`, `AgentStepResult`, `AgentRunResult`

2. `app/agents/scraper_agent.py`
   - wraps scraping entrypoints
   - returns structured execution metadata

3. `app/agents/data_cleaner_agent.py`
   - wraps pipeline transform entrypoints
   - returns structured artifact metadata

4. `app/agents/analyst_agent.py`
   - wraps downstream analysis generation / collection
   - returns generated artifact references

5. `app/agents/report_generator_agent.py`
   - builds report-friendly summaries from artifacts / orchestrator results

6. `memory/agent_roles.md`
   - explicit role definitions, routing notes, and operating boundaries

### Existing files to update
1. `app/agents/orchestrator.py`
   - replace static-only summary behavior with real routing logic while preserving summary helpers

2. `app/agents/__init__.py`
   - export public orchestrator / task types as appropriate

3. `app/api/routes.py`
   - keep existing `/summary`
   - optionally enrich summary with agent capabilities and supported task kinds
   - do **not** add write/mutation endpoints in PAP-222 unless explicitly required

4. `README.md`
   - document the new multi-agent layer and its boundaries

5. tests
   - add focused orchestrator/agent tests

---

## 5) Proposed Task Model

## 5.1 Shared task contract
Introduce a structured task model with fields such as:
- `kind`: task type string
- `payload`: dict of task inputs
- `requested_by`: optional caller tag
- `metadata`: optional routing/debug data

### Recommended task kinds
- `scrape_players`
- `clean_data`
- `run_analysis`
- `generate_report`
- `full_refresh`

### Why this matters
A typed task contract keeps orchestration predictable and testable. It also prevents the orchestrator from becoming a pile of ad hoc branching logic.

---

## 5.2 Route map
### Suggested route behavior
- `scrape_players` → Scraper Agent
- `clean_data` → Data Cleaner Agent
- `run_analysis` → Analyst Agent
- `generate_report` → Report Generator Agent
- `full_refresh` → Scraper Agent → Data Cleaner Agent → Analyst Agent → Report Generator Agent

### Important rule
Routing should be explicit via a central map in the orchestrator, not hidden inside individual agent modules.

---

## 6) Agent Contracts

## 6.1 Consistent interface
Each agent module should expose a single entrypoint like:
- `run(task: AgentTask) -> AgentStepResult`

### Required result fields
- `agent_name`
- `task_kind`
- `status`
- `summary`
- `artifacts`
- `metadata`

This gives the orchestrator a uniform way to compose steps.

---

## 6.2 Error behavior
Use safe MVP semantics:
- raise clear exceptions for unsupported task kinds
- return structured partial results for composite routes when possible
- do not swallow failures silently
- keep summary/debug metadata easy to inspect

---

## 7) Integration Plan

## 7.1 Scraper Agent integration
The Scraper Agent should call existing scraping plans/entrypoints only. It should not own parsing logic itself.

Recommended behavior:
- expose configured scraping capability summary
- for MVP, support task routing and structured summaries even if scraping actions are narrow initially
- if concrete scrape entrypoints are still thin, implement a safe wrapper over current `app/scraping/players.py` and source modules rather than inventing a new pipeline

## 7.2 Data Cleaner Agent integration
This agent should own pipeline normalization invocation.

Recommended behavior:
- wrap `build_bronze_manifest`, `build_silver_tables`, and optionally `build_gold_features`
- support both partial and full clean tasks
- return generated artifact paths in structured output

## 7.3 Analyst Agent integration
This agent should own downstream analytical output generation.

Recommended behavior:
- invoke KPI / advanced metrics / similarity / valuation / risk generation through existing functions
- report which artifacts were produced
- avoid direct logic duplication

## 7.4 Report Generator integration
This agent should be read-only and should consume existing artifacts/results.

Recommended behavior:
- summarize available players, analyses, and top outputs
- assemble a small dict payload suitable for future UI or API consumption
- keep outputs textual/structured, not presentation-heavy

---

## 8) Orchestrator Redesign Plan

## 8.1 Preserve compatibility
`build_agent_summary()` should remain available because `/summary` already uses it.

### New responsibilities for orchestrator
Add:
- task route registry
- `route_task(...)`
- `run_task(...)`
- support for composite workflows like `full_refresh`

### Suggested public surface
- `build_agent_summary()`
- `supported_task_kinds()`
- `route_task(task)`
- `run_task(task)`

This keeps the module useful to API summaries and future internal callers.

---

## 9) Memory / Role Manifest Plan

Add `memory/agent_roles.md` with:
- each agent’s purpose
- explicit ownership boundaries
- route map summary
- note that orchestrator coordinates existing modules rather than replacing them

This addresses the ticket’s “Memory: agent roles” requirement without leaking role logic into ad hoc strings across the codebase.

---

## 10) Testing Plan

## Unit tests
Add tests for:
- task routing by kind
- unsupported task handling
- agent summary contents
- composite route ordering for `full_refresh`

## Integration-style tests
Add tests that mock or safely invoke:
- Data Cleaner Agent result shape
- Analyst Agent result shape
- Report Generator Agent output summary

## Regression checks
Ensure:
- `/summary` still works
- current pipeline and analysis modules remain callable directly
- no route requires network access during tests unless explicitly mocked

---

## 11) Implementation Sequence for Grunt

1. Add shared task/result types in `app/agents/types.py`
2. Add `scraper_agent.py`
3. Add `data_cleaner_agent.py`
4. Add `analyst_agent.py`
5. Add `report_generator_agent.py`
6. Refactor `app/agents/orchestrator.py` to support route registry + execution
7. Update `app/agents/__init__.py`
8. Update `/summary` integration only as needed for richer agent/capability output
9. Add `memory/agent_roles.md`
10. Add orchestrator/agent tests
11. Update README

---

## 12) Acceptance Criteria

PAP-222 should be considered complete when:
- there is a real in-process orchestrator with task routing
- scraper/data-cleaner/analyst/report-generator agent modules exist under `app/agents/`
- agent roles are documented in memory
- `/summary` remains functional and reflects the expanded agent model
- tests cover routing, summaries, and at least one composite flow
- implementation reuses existing scraping/pipeline/analysis modules rather than duplicating them

---

## 13) Suggested Handoff Summary

PAP-222 should be implemented as a lightweight orchestration layer, not a distributed multi-agent runtime. The safest architecture is:
- shared task/result types
- explicit agent modules for scraper, cleaner, analyst, and report generation
- an orchestrator with a central route map
- a memory-backed role manifest
- focused tests for routing and result structure

That gives the project a real multi-agent system in code while preserving the current module boundaries and keeping the MVP small enough to evolve safely.
