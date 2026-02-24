---
name: model-design
description: "Model states/flows/invariants for complex behavior (async, retries, caching, offline). Use when correctness depends on state machines or non-trivial flows."
---

# model-design

## Purpose
Reduce ambiguity in complex behavior by making states and transitions explicit.

## Inputs
- WORK_PATH
- Task + Spec (preferred)
- Context Map constraints (platform differences, limitations)

## Output
Default: `${WORK_PATH}/models.md`
Update if exists.

## Internal loop
### 1) Identify modeling target
Ask (skip answered):
- What entity/process has states? (e.g., auth session, sync, downloads)
- Key events (user actions, network responses, timers)
- Failure modes (timeouts, offline, partial data)

### 2) Draft model (preview)
Include:
- State list + meanings
- Transition table (from -> event -> to)
- Invariants (must always hold)
- Platform-specific notes (only if truly different)
  Optional: Mermaid diagram if the repo accepts it; otherwise plain text.

### 3) Consistency check
- Must not contradict spec
- If contracts exist, ensure model respects contract constraints

### 4) Write discipline
Apply WRITE PLAN protocol.

## Completion criteria
- A developer can implement logic without inventing hidden states

Return control to Fabricator.
