---
name: implementation
description: "Implement changes guided by existing artifacts and repo conventions (AGENTS/README/DEVELOPMENT + WORK_PATH). Make small diffs, follow coherence gate, and optionally trigger verification-run."
---

# implementation

## Purpose
Make code changes safely and predictably, grounded in:
- repo instructions (AGENTS/README/DEVELOPMENT),
- existing artifacts in WORK_PATH (task/requirements/tech-spec/contracts/models/verify),
- existing code patterns in the codebase.

This skill does not replace project-specific rules; it follows them.

## Inputs
- WORK_PATH
- Context Map (constraints + commands + conventions)
- Existing artifacts in WORK_PATH (preferably: task + requirements + tech-spec; optionally contracts/models)
- User-selected scope for this iteration (one small unit of work)

## Outputs
- Code changes (files in the repository)
Optional (only if user approves):
- Update task/requirements/tech-spec to reflect decisions already made
- Trigger `verification-run` (recommended)

## Internal loop
### 1) Read-before-write grounding (mandatory)
Before proposing any code edits:
- Read the relevant artifacts in WORK_PATH (task/requirements/tech-spec/contracts/models if present).
- Read the nearest AGENTS.md relevant to the target code directories.
- Find and inspect existing code patterns in the affected area (similar files, similar flows).

### 2) Define a small implementation slice
Ask the user (unless already specified):
- “What is the smallest implementable slice for this iteration?”
Examples:
- one function + unit tests
- one UI state + wiring
- one API client change + parsing

### 3) Coherence gate (pre-change)
Check for contradictions between artifacts:
- requirements vs tech-spec vs contracts vs models
If a conflict exists, stop and propose resolving artifacts first (do not code).

### 4) Action plan for code edits
Before editing:
- List the exact files you will change (absolute repo paths)
- For each file: purpose of change (1 line)
- Provide a short preview approach (e.g., “I will change X and add test Y”)

### 5) Implement minimal diff
- Make the smallest change that satisfies the slice.
- Do not refactor unrelated code.
- Keep changes symmetric across platforms only when required by the task; otherwise keep scope narrow and explicit.

### 6) Optional quick validation
Recommend running `verification-run`:
- Quick level after each slice
- Full level before finishing the task
Do not claim anything passed without outputs.

### 7) Return control
Summarize:
- what changed (files)
- what remains
- suggested next skill(s): verification-run / verification-plan / requirements-authoring / CUSTOM

## Completion criteria
- One slice implemented
- Coherence maintained (no artifact contradictions)
- Next move proposed

Return control to Fabricator.
