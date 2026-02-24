---
name: verification-plan
description: "Create/update verify.md in WORK_PATH: quick vs full checks, Android/iOS commands, prerequisites, and what each check proves. Use when check commands are unclear or need standardization."
---

# verification-plan

## Purpose
Define a reproducible verification plan for this WORK_PATH.
Primary output: verify.md (quick/full, targets, commands, and meaning).

## Inputs
- WORK_PATH
- Context Map (pointers from AGENTS/DEVELOPMENT/docs)
- Task/spec (preferred): to map checks to acceptance criteria

## Output
- Create/update `${WORK_PATH}/verify.md`

## Internal loop
### 1) Discover existing verification knowledge
Look for:
- verify.md in WORK_PATH (update instead of recreating)
- commands explicitly documented in AGENTS.md / DEVELOPMENT.md / docs (from Context Map)
If commands are not documented:
- Ask user for canonical commands (per-platform quick/full).

### 2) Draft verify.md (preview first)
Minimum sections:
- Scope (what this verify plan covers)
- Prerequisites (SDK/tools/env variables, if any)
- Quick checks (fast, local)
- Full checks (slower, pre-PR)
- Targets:
  - Per-platform commands (if applicable)
- What each check proves (1 line per command)
- Mapping to acceptance criteria (if task/spec provides ACs)

### 3) Sanity checks
- Commands are copy/pasteable (explicit working dir if needed)
- No contradictions with repo rules (AGENTS/DEVELOPMENT)
- If both platforms: the plan states whether parity is required and how to validate it

## Completion criteria
- verify.md exists and is actionable
- verification-run can execute it without guessing

Return control to Fabricator.
