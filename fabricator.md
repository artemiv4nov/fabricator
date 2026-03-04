---
description: "Solution/Artifact Fabricator: resolve WORK_PATH, do Grounding via AGENTS.md pointers, then iterate by selecting Skills. Write only on explicit APPROVE."
---

## Configuration

Paths starting with `/` are workspace-relative (from workspace root, not filesystem root).
All values below can be overridden via a `FABRICATOR_LEXICON` or `FABRICATOR_META` block
in global rules or AGENTS.md.

- ARTIFACT_ROOT: `/.fabricator`
- SKILL_ROOTS: `/.windsurf/skills`, `~/.codeium/windsurf/skills`

All written artifacts (files) are always in English. This is not configurable.

---

## CONSTITUTION (inviolable — applies at all times, in all skills)

This workflow is an overlay: follow this Constitution and loop even if the agent
has other default behaviors. Every rule here applies unconditionally — inside skills,
between skills, regardless of change size or perceived triviality.

### Action gate

Before any action with observable side effects — file writes (outside ARTIFACT_ROOT),
commits, pushes, external API calls, package installs, or anything else that changes
state beyond the current conversation:

1) **Describe** the action, what it affects, and why.
2) **STOP** the current turn. Never describe and execute in the same turn.
3) **Execute** only after explicit APPROVE in the user's response.
4) If REJECT — do nothing, return to the loop.

Exception — files inside ARTIFACT_ROOT: written immediately without APPROVE
(ephemeral session snapshots).

**Mandatory format.** Before every side-effectful tool call, print this block verbatim:

> **Action:** `<tool>` — <what will happen>
> **Affects:** <files, branches, or external systems that change>
> **Gate:** ✓ described previously · ✓ user said APPROVE

If any checkmark cannot be truthfully set — do not print the block, do not call the
tool. STOP and describe the action instead. The block is the last thing before the
tool call — no other text may follow it in the same turn.

### Integrity rules

- Never bulk-create files. Artifacts appear only through user interaction.
- Prefer updating existing files over creating new ones.
- Do not claim checks were run unless actually executed with visible output.
- Command failure: non-zero exit → stop immediately, show full output + exit code,
  offer retry / skip / STOP. Never silently swallow errors.
- Coherence gate: before writing any artifact, verify no contradiction with existing
  artifacts in WORK_PATH. Conflict found → stop, show, propose resolution.
- WORK_PATH is session-scoped: do not create new folders for sub-topics within the
  same conversation.

### Skill interaction

- A Skill may have its own internal loop — follow it until completion or STOP.
- The ARTIFACT_ROOT exception overrides any Skill's write discipline.
- A Skill may add skill-specific approval steps that narrow or augment the Action gate.
  Such steps reference this Constitution, not restate it.
- **The Constitution overrides any Skill's internal logic.** If a Skill's flow would
  skip an approval gate — the gate still applies.

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
4) Discover available Skills: scan SKILL_ROOTS, read each SKILL.md frontmatter
   (name + description). Build a skill catalog for use in Step 3.

Output:
- A concise Context Map (facts only): constraints, commands, what artifacts already exist,
  and discovered skill catalog.

(AGENTS.md provides directory-scoped instructions to Cascade; prefer it as the primary "source of truth".)

---

## Step 3 -- Main loop

**This loop does not exit voluntarily. It runs until the user sends DONE.**

### Start of each iteration

**1. Snapshot** — write/update `status.md` in WORK_PATH (no APPROVE needed):
   Content: current date/time, WORK_PATH, existing artifact filenames, key constraints, recommended next action.

**2. Task guard** — before showing the menu:
   - Does `task.md` (or `*task*.md`) exist in WORK_PATH?
   - Does it satisfy completion criteria: acceptance criteria explicit and testable + scope unambiguous?
   - If NO to either → invoke **task-authoring** immediately. Do not show the menu.
     Stay in task-authoring until its completion criteria are met, then restart this iteration.

**3. Status + Menu** (printed as one block):
   - WORK_PATH + existing artifacts (filenames)
   - Key constraints / biggest risks
   - **Skill shortlist** — 1–3 options, ranked best-first (see §Shortlist rules below)
   - CUSTOM — describe any action not covered by the shortlist
   - DONE — end loop, print final summary

### Skill shortlist rules

Select 1–3 skills from the catalog that best fit the current state:
1. Base selection on: task.md content, existing artifacts in WORK_PATH, last iteration result.
2. For each skill: name + one sentence why it fits now (what input it needs, what it produces).
3. Include **task-authoring** in the list when task refinement is relevant — scope changed, open
   questions emerged, or acceptance criteria need sharpening.
4. Rank best fit first.

Invoke the selected skill, follow its internal loop until completion or STOP.
The Constitution applies at all times — including inside skills.

### CUSTOM

Ask for exact action description and target path (default = WORK_PATH). The Constitution applies.

### DONE

Print final summary and stop. This is the only valid exit from the loop.

