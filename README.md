# Fabricator

A workflow + skill library for agent-assisted software engineering
with [Windsurf](https://windsurf.com) Cascade.

---

## The problem

Most AI-assisted development follows "prompt → code → hope it works".
Spec-Driven Development (SDD) is a big improvement — specs ground the agent,
reduce hallucinations, and force upfront clarity.

But teams using SDD hit two opposite walls:

- **Overkill for simple tasks.** A three-line config fix doesn't need
  a full technical specification. The overhead kills adoption — people start
  skipping specs "just this once", and the discipline erodes.

- **Not enough for complex tasks.** A single spec can't capture everything
  for a multi-component feature: API contracts, state machines, migration plans,
  verification evidence. It either bloats into something unreadable or leaves
  critical gaps.

The root cause is the same: one artifact format for every change.

## The idea

Fabricator treats "spec" as **one possible artifact**, not the only one.

One workflow (`/fabricator`) gives you:
- **Grounding** — the agent reads your AGENTS.md, docs, and repo conventions
  before doing anything
- **Artifact packs** — iteratively choose the minimal sufficient set of artifacts
  for the change at hand (task, requirements, tech-spec, contracts, models,
  verification plan)
- **Evidence-based verification** — no "tests passed" without actual command
  output to prove it

This separation creates a natural **three-layer output**:
- *Session artifacts* (`.fabricator/`) — task definitions, specs, verification
  plans. Disposable scaffolding that exists while you work.
- *Code* — the actual implementation, committed to the repo.
- *Canonical specs* (`/docs/`) — distilled, stable knowledge promoted from
  session artifacts via `canon-spec-publishing`. This is your project's
  accumulating institutional memory — living documentation that grows with
  every task, not just the codebase.

The result: instead of "agent-assisted coding" you get
**agent-assisted engineering**.

## Why it works

**Extensible by design.** Skills are plain Markdown files with optional scripts.
Add a skill for your CI pipeline, deployment process, design review, or anything
else — Fabricator will discover and offer it automatically.

**Works with your existing repo.** No restructuring required. Fabricator reads
what you already have: `AGENTS.md`, `DEVELOPMENT.md`, `/docs/`. It adapts to
your conventions, not the other way around.

**Pure Markdown, minimal dependencies.** The workflow and all skills are plain
`.md` files. Some skills (e.g. `bitbucket-tooling`) optionally use co-located
scripts for API integration.

## Safety model

- **Human-controlled writes** — every file change outside the session folder
  requires a WRITE PLAN + explicit approval
- **Coherence gate** — before writing, the agent checks for contradictions
  with existing artifacts
- **Fail-fast** — if a command fails, the agent stops, shows output, and asks
  what to do
- **No bulk creation** — artifacts appear through interaction, not a wall of
  generated files
- **Grounding over guessing** — the agent must prefer repo docs over assumptions

## The work folder

Fabricator works inside a single **WORK_PATH** — a folder where change-specific
artifacts live. Created on first write, not before.

Typical contents:

| File | Purpose |
|---|---|
| `task.md` | Goal, scope, acceptance criteria, risks |
| `requirements.md` | Technical requirements, constraints, MUST/SHOULD/MAY |
| `tech-spec.md` | Full technical specification with implementation details |
| `contracts.md` | API / schema / storage contracts + compatibility rules |
| `models.md` | State machines, flows, invariants |
| `verify.md` | Verification commands (quick vs full) |
| `evidence.md` | Captured outputs from executed checks |

Not every task needs all of them — that's the point. Fabricator helps you pick
the minimal sufficient set.

## Installation

### Option A: per-project (recommended, shareable in git)

Windsurf discovers workflows from `.windsurf/workflows/` and skills from
`.windsurf/skills/` inside your workspace.

```bash
# From the root of your target project
mkdir -p .windsurf/workflows .windsurf/skills

# Copy or symlink workflow
cp /path/to/fabricator-repo/fabricator.md .windsurf/workflows/fabricator.md

# Copy or symlink skills
cp -R /path/to/fabricator-repo/skills/* .windsurf/skills/
```

### Option B: global (personal install)

Windsurf supports global skills at `~/.codeium/windsurf/skills/`.

```bash
# Skills (global — documented)
ln -s "$(pwd)/skills" ~/.codeium/windsurf/skills

# Workflow (global — create via Windsurf UI for stability,
# or symlink to ~/.codeium/windsurf/global_workflows/)
mkdir -p ~/.codeium/windsurf/global_workflows
ln -s "$(pwd)/fabricator.md" ~/.codeium/windsurf/global_workflows/fabricator.md
```

> **Note:** global workflow paths may change across Windsurf versions.
> The per-project install is the most stable option.

## Usage

Open any project in Windsurf and type in Cascade chat:

```
/fabricator my-task
```

The workflow will:
1. Resolve WORK_PATH (created on first write, not immediately)
2. Ground itself in your repo instructions (AGENTS.md, docs, conventions)
3. Enter an iterative loop: Status → pick a skill → produce artifacts → repeat

### Typical patterns

**New feature:**
`/fabricator login-flow` → task-authoring → artifact-selection →
tech-spec-authoring → contract-design → implementation →
verification-run → git-tooling → PR

**Bug fix (small scope):**
`/fabricator fix-crash` → task-authoring → implementation →
verification-run → git-tooling

**Standardize verification:**
`/fabricator ci-cleanup` → verification-plan → verification-run

**Publish a canonical spec:**
Work in session folder → canon-spec-publishing → update `/docs/**`

## What's included

- **`fabricator.md`** — the core workflow (one entry point)
- **`skills/`** — 12 reusable skills:

| Skill | Purpose |
|---|---|
| `task-authoring` | Create/update task definition |
| `artifact-selection` | Choose the minimal sufficient artifact set |
| `requirements-authoring` | Technical requirements and constraints |
| `tech-spec-authoring` | Full technical specification |
| `contract-design` | API / schema / storage contracts |
| `model-design` | State machines, flows, invariants |
| `verification-plan` | Create verification commands |
| `verification-run` | Execute checks, record evidence |
| `implementation` | Code changes guided by artifacts |
| `git-tooling` | Commit message, commit, push |
| `bitbucket-tooling` | PR operations via Bitbucket (optional) |
| `canon-spec-publishing` | Promote session knowledge to `/docs/` |

Customization points (`FABRICATOR_META`, `FABRICATOR_LEXICON`) are documented
inside `fabricator.md`.

## Philosophy

Fabricator is intentionally not "spec-first". It is "artifact-pack-first":
- Choose the minimal set of artifacts that makes the work safe, testable,
  and understandable.
- Escalate artifact rigor only when risk/scope requires it.
- Keep everything grounded in repository truth and executable verification.

That is the difference between "agent-assisted coding" and
"agent-assisted engineering".

## License

Apache 2.0 — see [LICENSE](LICENSE).
