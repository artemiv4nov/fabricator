---
name: artifact-selection
description: "Select the minimal sufficient artifact set (task/requirements/tech-spec/contracts/models/verify/evidence) for the current change, and recommend the next skills. Use after task intake or when scope/risk changes."
---

# artifact-selection

## Purpose
Choose *which artifacts are required* for this specific situation (not “write everything”).
Output should be actionable: a short plan + next skill recommendations.

## Inputs
- WORK_PATH
- Context Map (from Fabricator grounding)
- Existing artifacts in WORK_PATH (filenames + short summary)
- Task artifact (preferred)

## Output (default)
Update exactly ONE existing anchor file in WORK_PATH:
Priority:
1) packet.md / index.md / status.md (if present)
2) task.md (if present)
3) otherwise: ask user to run task-authoring first (or choose a new anchor filename)

Add/refresh a section titled: **Artifact Plan**

## Internal loop
### 1) Ensure there is a task definition
- If no task-like artifact exists, recommend invoking `task-authoring` and stop this skill.

### 2) Extract signals (facts only)
Determine:
- Public surface impacted? (API/schema/persistence/deeplink/protocol)
- State complexity? (async flows, retries, offline, caching, concurrency)
- Cross-platform parity required? (Android+iOS)
- Security/privacy relevance? (auth, payments, PII, permissions)
- Risk: low/medium/high (use existing label if present; else propose and ask)
- Unknowns blocking implementation?

### 3) Select minimal sufficient artifact set
Heuristics:
- Always: Task + at least one of {Requirements, Verify plan}
- If medium/high risk: add tech-spec before code changes
- If public surface: add Contracts
- If complex state/flows: add Models (state/flow + invariants)
- If architectural tradeoff: recommend requirements-authoring (task-level draft) → canon-spec-publishing (canonical /docs spec)

### 4) Recommend next skills (1–3)
Recommend the “next best moves”, e.g.:
- requirements-authoring
- verification-plan
- contract-design
- model-design
- implementation
- verification-run
- CUSTOM

## Completion criteria
- Artifact Plan exists in the anchor file
- Next skills are recommended

Return control to Fabricator.
