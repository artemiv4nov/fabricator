---
name: requirements-authoring
description: "Create/update a requirements document (requirements.md) inside WORK_PATH capturing technical requirements, constraints, and scope. Does NOT publish to /docs. No writes without APPROVE."
---

# requirements-authoring

## Purpose
Create or update a **requirements document** inside the current WORK_PATH.
This document captures technical requirements (constraints, scope, MUST/SHOULD/MAY rules) — what the system must do, without designing the solution.

This skill must NOT write to `/docs/**`.

## Inputs
- WORK_PATH (must be an absolute path)
- Optional: desired filename (default: `requirements.md`)
- Task context (from fabricator grounding / existing artifacts)

## Output (in WORK_PATH only)
- `requirements.md` (or user-chosen name)
- Optional links/placeholders to sibling artifacts:
  - `contracts.md`, `models.md`, `verify.md`, `evidence.md`
  (create only if user explicitly requests)

## Constraints
- If there is an existing canonical spec in `/docs/**` relevant to this task, link to it instead of duplicating it.

## Internal loop
### 1) Discover existing requirements
- Check WORK_PATH for existing `requirements.md` (update instead of recreating).
- Read task.md and other WORK_PATH artifacts for context.

### 2) Draft requirements (preview first)
Follow the suggested structure below. Keep it concise and pack-friendly.

### 3) Write discipline
Apply WRITE PLAN protocol.

## Suggested structure (small, pack-friendly)
- Context (1 paragraph)
- Goal / Non-goals (bullet)
- Constraints (MUST/SHOULD/MAY bullets, only if needed)
- Interfaces / contracts (links or short bullets; full contract goes to `contracts.md`)
- Data / model notes (links; full model goes to `models.md`)
- Checks (do not list every test; point to repo-level FULL SUITE command or to `verify.md` if it exists)

## Completion criteria
- `requirements.md` exists in WORK_PATH and captures scope, constraints, and acceptance criteria

Return control to Fabricator.
