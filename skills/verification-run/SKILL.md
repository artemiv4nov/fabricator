---
name: verification-run
description: "Execute project-defined checks (build/test/lint) using verify.md in WORK_PATH or commands pointed to by AGENTS/DEVELOPMENT. Show outputs; optionally record evidence.md."
---

# verification-run

## Purpose
Run checks as defined by the project. No guessing.
Never claim a check was run without actual command output.

## Inputs
- WORK_PATH
- Context Map (especially pointers for how to run checks)
- verify.md (preferred), evidence.md (optional)

## Outputs
Default: no files written.
Optional (only if user approves):
- Create/update `${WORK_PATH}/${DEFAULT_EVIDENCE_FILENAME}` (default: evidence.md)

## Internal loop
### 1) Select target and level
Ask (unless already known):
- Target: platform name(s) or Custom
- Level: Quick / Full

### 2) Resolve command source (strict priority)
1) `${WORK_PATH}/${DEFAULT_VERIFY_FILENAME}` (verify.md) if present
2) **`Verification` section in the nearest `AGENTS.md`** — this is the canonical per-repo source;
   it defines two rings: static checks (no device) and dynamic checks (device required)
3) Commands in DEVELOPMENT.md / repo docs (via Context Map)
4) User-provided commands (ask user to paste exact commands)

If commands are still unknown:
- Recommend using `verification-plan` skill to create verify.md
- If user refuses, proceed only with user-provided commands.

### 3) Build a Run Plan (before executing)
Create a short plan:
- command list (in order)
- working directory (if needed)
- expected effect (1 line each)

Run discipline (based on check ring):
- **Quick checks** (linters, compile — fast, no special setup): run immediately without asking APPROVE.
- **Full checks** (instrumentation tests, emulator/device, network): ask APPROVE before running.

### 4) Execute and report
- Run commands sequentially.
- On first failure: stop by default, show output + exit code.
- Ask whether to continue remaining commands or stop.

### 5) Optional evidence
Ask: “Record results to evidence.md?”
If yes:
- Prepare a compact evidence entry:
  - timestamp
  - target + level
  - commands executed
  - results (pass/fail + exit codes)
  - short failure summary if any
- Apply WRITE PLAN protocol.

## Completion criteria
- Requested checks executed (or explicitly skipped)
- Outputs summarized in chat
- Evidence recorded only if user approved

Return control to Fabricator.
