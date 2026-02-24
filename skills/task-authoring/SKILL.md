---
name: task-authoring
description: "Create or update a single Task artifact in WORK_PATH (goal, scope, constraints, acceptance criteria, risks, open questions). Use when starting work, clarifying requirements, or when no task definition exists yet."
---

# task-authoring

## Purpose
Produce a clear, testable task definition **without** doing technical design or implementation.
One iteration should result in exactly one updated/created task file in WORK_PATH.

## Inputs (from Fabricator)
- WORK_PATH
- Context Map (constraints + known commands + existing artifacts)
- User intent / goal

## Output (default)
- Create or update: `${WORK_PATH}/task.md`
  Rules:
- If a task file already exists in WORK_PATH, prefer updating it instead of creating a new one.
- If multiple “task-like” files exist, ask user to pick the canonical one.

## Internal loop (keep going until completion)
### 1) Detect / choose target file
- Look for common candidates in WORK_PATH:
    - task.md
    - *task*.md
    - intake.md
    - issue.md
- If found exactly one strong candidate => use it.
- Else ask user for the exact filename (in WORK_PATH).

### 2) Ask minimal intake questions (skip anything already answered)
Required:
- What is the problem / user-visible outcome?
- Scope (in) and out-of-scope (out)
- 1–3 acceptance criteria (how to know “done”)
- Constraints (must / must-not)
- Unknowns / open questions

Recommended (if multi-platform):
- Platforms (list target platforms)
- Any public surfaces? (API/schema/persistence/deeplink)
- Risk level: low / medium / high

### 3) Draft Task content (preview in chat first)
Keep it concise and decidable. Suggested sections:
- Title
- Goal (why)
- Scope / Out of scope
- Constraints (can/can’t)
- Acceptance criteria
- Risks
- Open questions
- References (links to existing artifacts/docs)

## Completion criteria
- Acceptance criteria are explicit and testable
- Scope and constraints are unambiguous
- Open questions are listed (even if unanswered)

Return control to Fabricator.
