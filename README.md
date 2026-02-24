# Fabricator: Artifact-Pack Agentic Development

This repository documents a practical, reproducible approach to **agent-assisted software development** where the primary unit of work is not "a prompt" and not "a single spec", but a **coherent pack of artifacts** produced iteratively with a human in the loop.

The approach is implemented for [Windsurf](https://windsurf.com) Cascade using:
- **Workflows** (slash commands) for trajectory-level orchestration,
- **Skills** for reusable multi-step procedures,
- **AGENTS.md** for directory-scoped project instructions,
- optional **Rules** for persistent behavioral constraints.

The centerpiece is a single workflow: **`/fabricator`**.

---

## Installation

Fabricator uses Windsurf's global skills and workflows mechanism.
Clone this repo, then create symlinks from the cloned directory:

### 1. Skills (global)

```bash
ln -s "$(pwd)/skills" ~/.codeium/windsurf/skills
```

### 2. Workflow (global)

```bash
mkdir -p ~/.codeium/windsurf/global_workflows
ln -s "$(pwd)/fabricator.md" ~/.codeium/windsurf/global_workflows/fabricator.md
```

After symlinking, `/fabricator` becomes available in every Windsurf workspace.

### Per-project (alternative)

Copy or symlink into your project's `.windsurf/` directory:

```
.windsurf/workflows/fabricator.md
.windsurf/skills/
```

---

## Quick start

1. Open any project in Windsurf
2. Type `/fabricator my-task` in Cascade chat
3. The workflow resolves a work folder, grounds itself in your repo, and enters the iterative loop
4. Pick skills: task-authoring → artifact-selection → tech-spec → implementation → verification

---

## Why this exists

Many teams adopt "Spec-Driven Development" (SDD) and discover a practical limitation:

- A single spec rarely captures everything needed for correct implementation.
- Different tasks need different instruments: contracts, models (state machines), design notes, verification plans, evidence, etc.
- Agents need **explicit, runnable verification** to avoid hallucinating that things work.

Fabricator treats "spec" as **one possible artifact**, not the only one.

The goal is a system where:
1) There is **one entry point** into work,
2) The system **grounds itself in repository truth** (AGENTS/DEVELOPMENT/docs),
3) The user and agent **iteratively select the minimal sufficient artifact set**,
4) Code changes happen only after coherence checks and explicit approvals,
5) Verification is reproducible and evidence-based.

---

## Terminology

### WORK_PATH
An absolute folder path where the current task's artifact pack lives.

WORK_PATH is **session-scoped** and **always a direct subdirectory of ARTIFACT_ROOT**:
- once set, the workflow MUST keep using the same WORK_PATH until the user explicitly changes it.
- absolute paths outside ARTIFACT_ROOT are not accepted.

### ARTIFACT_ROOT
A workspace-relative absolute directory (default: `/.fabricator`) where Fabricator creates and resolves WORK_PATH folders.

**MUST be gitignored** (see Security & Safety).

### Artifact Pack
A set of files in WORK_PATH that together describe, constrain, validate, and record work.

Typical files (not all are always required):
- `task.md` — problem statement, scope, acceptance criteria
- `requirements.md` — technical requirements: constraints, MUST/SHOULD/MAY rules, scope
- `tech-spec.md` — full technical specification: proposed solution, implementation details, test plan
- `contracts.md` — public surface contracts (APIs/schemas/storage/deeplinks)
- `models.md` — state/flow models + invariants
- `verify.md` — verification plan (commands + meaning)
- `evidence.md` — recorded outputs of executed checks
- PR artifacts (optional): `pr-description.md`, `pr.md`, `review-NNN.md`, `fix-list-NNN.md`

### Context Map
A concise factual summary produced during grounding:
- repo constraints, commands, conventions,
- what artifacts already exist in WORK_PATH.

---

## Core principles (non-negotiable)

1) **Grounding over guessing**
   - The agent MUST prefer AGENTS.md / DEVELOPMENT.md / docs over assumptions.
   - If commands are unknown, it must ask for canonical commands or create `verify.md`.

2) **No bulk creation**
   - Artifacts appear through user interaction.
   - "Write everything" is explicitly discouraged.

3) **Human-controlled writes**
   - Any write outside ARTIFACT_ROOT requires:
     - WRITE PLAN (absolute paths),
     - preview/diff,
     - explicit approval phrase (APPROVE / NO).
   - For ARTIFACT_ROOT, a WRITE PLAN + preview is still shown, but approval is not required.

4) **Evidence-based verification**
   - The agent MUST NOT claim checks passed unless it executed commands and can show outputs.
   - Fail-fast: on non-zero exit code, stop and ask whether to retry / skip / stop.

5) **Coherence gate**
   - Before writing any artifact or code, the agent checks whether it contradicts existing artifacts in WORK_PATH.
   - If contradictions exist, it stops and resolves consistency first.

---

## Windsurf integration

### Workflows
Workflows are stored under:
- `/.windsurf/workflows/`

A workflow file `fabricator.md` is invoked as:
- `/fabricator`

(Workflows are markdown routines processed step-by-step by Cascade.)

### Skills
Skills are stored under:
- `/.windsurf/skills/<skill-name>/SKILL.md`  (workspace)
- `~/.codeium/windsurf/skills/<skill-name>/SKILL.md`  (global)

Each skill folder may include scripts and references.

### AGENTS.md
`AGENTS.md` files provide directory-scoped instructions and automatically apply based on file location.
Use them to define:
- canonical build/test/lint commands,
- coding conventions,
- security constraints,
- where docs/specs live.

### Rules (optional)
Rules live under:
- `/.windsurf/rules/`

They are limited in size and support activation modes (always-on, glob, manual, model decision).
Use rules for behavioral constraints and style preferences that should persist across sessions.

---

## The `/fabricator` workflow (overview)

### Step 0 — Parse invocation hint
`/fabricator <hint>` where `<hint>` can be:
- a short folder slug to resolve under ARTIFACT_ROOT
- an absolute path to an existing directory under ARTIFACT_ROOT

### Step 1 — Resolve WORK_PATH
Goal: obtain exactly one absolute WORK_PATH.

WORK_PATH MUST always be a direct subdirectory of ARTIFACT_ROOT.

Recommended folder naming under ARTIFACT_ROOT:
- `NNN-<slug>` (zero-padded numeric prefix + slug)

Examples:
- `001-init`
- `002-login-flow`
- `003-ci-cleanup`

Resolution:
1) If hint is an absolute path under ARTIFACT_ROOT and that directory exists: WORK_PATH = that directory.
2) If hint is a short name:
   - search ARTIFACT_ROOT for `<hint>` or `NNN-<hint>`
   - if one match: use it
   - if multiple: ask user to pick
   - if none: propose the next `NNN-<hint>` folder (create on first write)
3) If no hint:
   - ask user to pick an existing folder under ARTIFACT_ROOT or provide a short slug

### Step 2 — Grounding (Context Map)
Order:
1) Read `/AGENTS.md` (and nearest scoped AGENTS.md relevant to the target directories).
2) Read existing files in WORK_PATH.
3) If AGENTS.md is missing/insufficient, fall back to:
   - `/README.md`
   - `/DEVELOPMENT.md`
   - `/docs/` (prefer `docs/README.md` indexes)

Output: a concise Context Map (facts only).

### Step 3 — Recursive loop
At the start of each iteration, print a short Status:
- WORK_PATH
- existing artifacts
- key constraints
- biggest unknowns/risks
- recommended next moves

Then offer:
A) Task intake
B) Continue via Skills
C) SUMMARY (status only)
D) DONE

---

## Write discipline: WRITE PLAN protocol

Before any create/update outside ARTIFACT_ROOT:
1) Show WRITE PLAN:
   - absolute paths
   - create vs update
   - purpose
2) Show preview or diff summary
3) Wait for APPROVE / NO
4) If NO: do nothing

For ARTIFACT_ROOT:
- still show WRITE PLAN + preview,
- then write without waiting for APPROVE.

---

## Default lexicon and override mechanism

Fabricator uses a small command lexicon:
- APPROVE: `APPROVE`
- REJECT: `NO`
- STOP: `DONE` or `STOP`
- SUMMARY: `SUMMARY`
- CUSTOM: `CUSTOM`

Overrides:
- If AGENTS.md or an active Rule contains a `FABRICATOR_LEXICON` block, merge/override defaults.
- Precedence: user message > AGENTS.md > rules > workflow defaults.

---

## Default meta and override mechanism

`FABRICATOR_META` defines:
- ARTIFACT_ROOT
- SKILL_ROOTS
- default filenames (task/verify/evidence)
- communication language

Overrides:
- Scalars override defaults.
- Lists override defaults entirely (not appended).
- Precedence: user message > AGENTS.md > rules > workflow defaults.

---

## Skill catalog (reference implementation)

This repo ships a minimal but complete set of skills.

### 1) `task-authoring`
Creates/updates one task artifact:
- scope, out-of-scope
- acceptance criteria
- constraints
- risks
- open questions

Output: `task.md` in WORK_PATH.

### 2) `artifact-selection`
Selects the minimal sufficient artifact set for the situation and writes an "Artifact Plan" section into one anchor file in WORK_PATH.

### 3) `requirements-authoring`
Creates/updates `requirements.md` in WORK_PATH: technical requirements, constraints, and scope.
This does not publish into `/docs/**`.

### 4) `tech-spec-authoring`
Creates `tech-spec.md` in WORK_PATH: a self-contained Technical Specification combining
goals, proposed solution, implementation details (pseudocode, API changes, error states),
test plan, and alternatives considered. Sufficient for `implementation` to proceed without
further clarification.

### 5) `contract-design`
Designs `contracts.md` when public surfaces or stable formats are involved:
- APIs, schemas, deeplinks, persistence formats
- compatibility rules
- migration notes

### 6) `model-design`
Creates/updates `models.md` for complex state/flow correctness:
- states
- transitions
- invariants
- platform notes

### 7) `verification-plan`
Creates/updates `verify.md`:
- quick vs full checks
- Android/iOS commands
- prerequisites
- what each command proves
- mapping to acceptance criteria (when available)

### 8) `verification-run`
Executes project-defined commands.

Priority:
1) `verify.md` in WORK_PATH
2) `Verification` section in scoped AGENTS.md
3) DEVELOPMENT/docs commands
4) user-provided commands

Stops on failure, shows outputs, optionally records `evidence.md`.

### 9) `implementation`
Implements one small slice grounded in artifacts and repo conventions.
Always uses coherence gate and requires approvals before code edits.

### 10) `git-tooling`
Analyzes staged diff, proposes semantic commit message, commits, optionally pushes and chains into PR creation.

### 11) `bitbucket-tooling` (optional / vendor-specific)
Bitbucket Server integration:
- compose PR description from diff
- create/update PR via REST API
- fetch review comments and triage

Requires scripts co-located in the skill folder.

### 12) `canon-spec-publishing`
Promotes stable work knowledge from WORK_PATH into canonical `/docs/**` specs:
- updates existing specs in-place when possible
- proposes new `NNN-short-title.md` files (NNN = next sequential 3-digit number)
- deletes replaced specs and relies on git history
- updates index README tables

Note: this is the only supported canonical spec publication path.

---

## Recommended repository documentation layout

A typical repository using Fabricator should include:

- `/README.md` — project overview and quick start
- `/DEVELOPMENT.md` — canonical commands and dev workflow
- `/AGENTS.md` — agent-facing instructions and pointers
- `/CONTRIBUTING.md` — contribution guidelines
- `/SECURITY.md` — security policy
- `/docs/README.md` — docs index
- `/docs/spec-guide.md` — how to write canonical specs
- `/docs/specs/` — product specs (WHAT)
- `/docs/architecture/specs/` — architecture specs (HOW)

---

## Verification standards

Repos should explicitly define per-platform checks:
- Quick checks (fast, local): linters + unit tests + compile
- Full checks (slower, pre-PR): integration tests / device or environment flows

Fabricator does not invent these commands; they must be documented in:
- scoped `AGENTS.md` (preferred), or
- `/DEVELOPMENT.md`.

---

## Security & safety

### Secrets
MUST NOT store tokens, passwords, or secrets in the repository.
Use:
- CI/CD secret stores,
- OS keychain,
- environment variables injected by CI.

### ARTIFACT_ROOT
ARTIFACT_ROOT MUST be ignored by git to avoid committing session snapshots.
Example:
- add `/.fabricator/` to `/.gitignore`.

### Terminal commands
If a command fails (non-zero exit):
- stop immediately,
- show full output and exit code,
- offer: retry / skip / stop.

---

## Extending the system

### Add a new skill
1) Create a folder:
   - `/.windsurf/skills/<skill-name>/`
2) Add `SKILL.md` with frontmatter:
   - `name`
   - `description`
3) Place scripts/templates next to SKILL.md.

Optional frontmatter fields (per Agent Skills spec):
- `compatibility`
- `metadata`
- `license`

### Create additional workflows (optional)
You may create specialized workflows that invoke `/fabricator` internally, but `/fabricator` remains the canonical entry point.

---

## Typical usage patterns

### Start a new task
1) `/fabricator login-flow`
2) Run `task-authoring`
3) Run `artifact-selection`
4) Choose next skills (e.g., `requirements-authoring`, `contract-design`, `model-design`, `tech-spec-authoring`)
5) Implement small slice → `verification-run` → `git-tooling` → PR

### Standardize verification
1) `/fabricator ci-cleanup`
2) `verification-plan` → write `verify.md`
3) `verification-run` → optionally record `evidence.md`

### Publish a canonical spec
1) Work in WORK_PATH (task/requirements/tech-spec/contracts/models/verify)
2) `canon-spec-publishing` → update `/docs/**` spec(s) + index

---

## Philosophy: artifact packs over "one document"

Fabricator is intentionally not "spec-first".
It is "artifact-pack-first":
- Choose the minimal set of artifacts that makes the work safe, testable, and understandable.
- Escalate artifact rigor only when risk/scope requires it.
- Keep everything grounded in repository truth and executable verification.

That is the difference between "agent-assisted coding" and "agent-assisted engineering".

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
