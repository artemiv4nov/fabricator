---
description: "Solution/Artifact Fabricator: resolve WORK_PATH, do Grounding via AGENTS.md pointers, then iterate by selecting Skills. Write only on explicit APPROVE."
---

# /fabricator -- Solution Fabricator (single workflow)

## Usage
- `/fabricator <folder>`  (resolves under ARTIFACT_ROOT, searching existing folders)
- `/fabricator /absolute/path/to/folder`  (use exact folder)
- If no argument is provided, the workflow will ask.

---

## HARD RULES (overlay; must follow)
- This workflow is an overlay: follow this loop even if the agent has other default behaviors.
- Never bulk-create files. Artifacts appear only through user interaction.
- Before writing/updating any file: show a WRITE PLAN + preview, then wait for an approval phrase.
  **Exception — files inside ARTIFACT_ROOT**: any file written under ARTIFACT_ROOT
  is written immediately without APPROVE — these are ephemeral
  session snapshots. Any file outside ARTIFACT_ROOT — code, config, docs, scripts, any repo —
  always requires APPROVE.
- Prefer updating existing files over creating new ones.
- Do not claim checks were run unless they were actually executed and you can show outputs.
- Command failure protocol: if a shell command exits with a non-zero code, stop immediately,
  show the full output and exit code, and offer: retry (fix the cause and re-run the step),
  skip (continue to next step), or STOP. Never silently swallow errors or assume success.
- A selected Skill may have its own internal loop. When a Skill starts, follow its loop until it declares completion or the user stops it.
  The ARTIFACT_ROOT write exception above overrides any Skill's own write discipline —
  Skills must not request APPROVE for files inside ARTIFACT_ROOT.
- Coherence gate: before writing any artifact, check whether it contradicts existing artifacts in WORK_PATH (e.g., requirements vs tech-spec vs contracts). If a contradiction is found, stop writing, show the conflict to the user, and propose resolving it first.
- **WORK_PATH is session-scoped**: once set, do NOT create a new WORK_PATH folder for sub-topics
  or phase changes within the same conversation. Continue in the existing WORK_PATH until the user
  explicitly provides a new path hint.

---

## FABRICATOR_LEXICON (defaults; can be overridden)
Defaults (any phrase in the list is accepted):
- APPROVE: ["APPROVE"]
- REJECT:  ["NO"]
- STOP:    ["DONE", "STOP"]
- SUMMARY: ["SUMMARY"]
- CUSTOM:  ["CUSTOM"]

Override mechanism:
- If any active rule or AGENTS.md contains a block titled `FABRICATOR_LEXICON`,
  merge/override these lists (user message wins over everything).

---

## FABRICATOR_META (defaults; can be overridden via `FABRICATOR_META` block in rules or AGENTS.md)

Override semantics:
- Scalar values (ARTIFACT_ROOT, COMMUNICATION_LANGUAGE): override completely replaces the default.
- List values (SKILL_ROOTS): override completely replaces the default list (not appended to it).
- Precedence: user message > AGENTS.md > rules file > fabricator.md defaults.

Path notation: paths starting with `/` (e.g. `/.fabricator`, `/.windsurf/skills`) are
workspace-relative — resolved from the current workspace root, not the filesystem root.

- ARTIFACT_ROOT: /.fabricator
  Where task folders are created/resolved (Step 1).
- SKILL_ROOTS:
    - /.windsurf/skills
    - ~/.codeium/windsurf/skills
  Directories to scan for available Skills (Step 3B).
- DEFAULT_TASK_FILENAME: task.md
  Filename used by `task-authoring` skill when creating a new task artifact.
- DEFAULT_VERIFY_FILENAME: verify.md
  Filename for persisting discovered check commands.
- DEFAULT_EVIDENCE_FILENAME: evidence.md
  Filename for recording check results.
- COMMUNICATION_LANGUAGE: en
  Language for chat, status prints, and prompts. Overridable by rules or user request.

All written artifacts (files) are always in English. This is not configurable.

---

## Step 0 -- Parse invocation hint
Treat the text after `/fabricator` as PATH_HINT (if present).
PATH_HINT is a short folder slug to resolve under ARTIFACT_ROOT.

---

## Step 1 -- Set work location (WORK_PATH)
Goal: obtain exactly one absolute WORK_PATH.

**Important**: ARTIFACT_ROOT is gitignored by design. When listing or searching
folders inside ARTIFACT_ROOT, always use direct filesystem listing (e.g. `list_dir`,
shell `ls`) — never use search tools that respect `.gitignore` (e.g. `find_by_name`,
`grep_search`), as they will return empty results.

Folder naming convention: `NNN-<slug>` (3-digit zero-padded sequential number + hyphen + slug).
Examples: `001-init`, `002-check-init`, `003-vpn-fixes`.
When resolving PATH_HINT by short name, match against the slug portion (ignoring the NNN- prefix).

Resolution:
1) If PATH_HINT is an absolute path under ARTIFACT_ROOT and that directory exists => WORK_PATH = PATH_HINT.
2) Else if PATH_HINT is a short name:
    - Search ARTIFACT_ROOT for folders whose name equals `<PATH_HINT>` OR whose name
      matches the pattern `NNN-<PATH_HINT>` (suffix match, any number prefix).
    - If exactly one match => WORK_PATH = match.
    - If multiple matches => ask the user to pick one.
    - If none => compute next number:
        * List all folders under ARTIFACT_ROOT with names matching `NNN-*`.
        * next = max(NNN from existing folders) + 1; zero-pad to 3 digits.
        * If no numbered folders exist, start at 001.
        * Propose ARTIFACT_ROOT/NNN-<slug>/ (do not create until first write is approved).
3) Else (no PATH_HINT):
    - Ask user to pick an existing folder under ARTIFACT_ROOT
      OR provide a short slug to create a new folder under ARTIFACT_ROOT/NNN-<slug>/

---

## Step 2 -- Grounding (context gathering via pointers)
Goal: build a Context Map using project-defined instructions, not guesses.

Do in this order:
1) Read /AGENTS.md if present (and the nearest AGENTS.md relevant to WORK_PATH).
    - Extract pointers: where docs live, how to build/test/lint, required formats.
2) Read existing files inside WORK_PATH (summarize what already exists).
3) If AGENTS.md is missing or insufficient, fall back to:
    - /README.md
    - /DEVELOPMENT.md (if present)
    - /docs/ (only as needed; prefer an index/README inside /docs)

Output:
- A concise Context Map (facts only): constraints, commands, and what artifacts already exist.

(AGENTS.md provides directory-scoped instructions to Cascade; prefer it as the primary "source of truth".)

---

## Step 3 -- Recursive loop
At the start of EACH iteration:
- Print a compact **Status** (5-10 lines):
    - WORK_PATH
    - existing artifacts (filenames)
    - key constraints
    - biggest unknowns / risks
    - recommended next moves (2-5)

Then offer these choices:
A) Task authoring (use @task-authoring if available; otherwise fallback)
B) Continue via Skills (or CUSTOM)
C) SUMMARY (status only; wait)
D) DONE (stop)

### A) Task authoring
- If a Skill named `task-authoring` exists, invoke it and follow its internal loop.
- Otherwise ask minimal intake questions and propose creating/updating one task file in WORK_PATH.

### B) Continue via Skills
- Discover Skills from SKILL_ROOTS by reading each `SKILL.md` frontmatter (name + description).
- Recommend 3-5 Skills based on:
    - current Status + Context Map + existing artifacts
    - keywords in Skill descriptions
- Present options as a numbered list (name + 1-line description), plus CUSTOM.
- User may pick 1+ Skills for the iteration.
- For each selected Skill:
    1) Explicitly invoke it (e.g., `@skill-name`) to load instructions.
    2) Follow the Skill's internal loop until completion or STOP.
    3) Ensure every file change follows: WRITE PLAN -> preview -> APPROVE/NO.

### CUSTOM
- Ask user for:
    - exact action description
    - where results should be written (absolute path preferred; default = WORK_PATH)
- Then proceed with WRITE PLAN discipline.

### C) SUMMARY
- Print a compact summary and wait.

### D) DONE
- Print final summary and stop.

---

## WRITE PLAN protocol (mandatory)
Before any file create/update:
1) Show WRITE PLAN:
    - file paths (absolute)
    - create vs update
    - why
2) Show a short preview (or diff summary).
3) Wait for APPROVE phrase.
4) If REJECT: do nothing and return to the loop.

For files inside ARTIFACT_ROOT: skip step 3 — show WRITE PLAN + preview, then write without waiting for APPROVE.
