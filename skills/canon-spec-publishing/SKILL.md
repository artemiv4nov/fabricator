---
name: canon-spec-publishing
description: "Promote a task artifact pack into a canonical spec under /docs/specs or /docs/architecture/specs, following /docs/spec-guide.md lifecycle (active-only, delete replaced). No writes without APPROVE."
---

# canon-spec-publishing

## Purpose
Turn stable knowledge from WORK_PATH into a **canonical spec** in `/docs/**`.

## Inputs
- WORK_PATH (absolute)
- Spec kind: product | architecture
- Target: update existing canonical spec OR create a new one

## Output
- Created or updated canonical spec file in `/docs/specs/` or `/docs/architecture/specs/`
- Updated spec index README (if present)

## Constraints
- Read `/docs/spec-guide.md` if present and follow it as the single source of truth.
  If absent: apply default conventions (self-contained canonical spec, active-only,
  delete replaced specs, rely on git history for old versions).
- Keep only active specs in `/docs/**` (delete replaced specs, rely on git history).

## Internal loop
1) Grounding:
   - Read `/docs/spec-guide.md` if present
   - Read relevant `/docs/**/specs/README.md` index if present
   - Read WORK_PATH artifacts (requirements/tech-spec/contracts/models/evidence)

2) Decide publish target:
   - Search for an existing canonical spec that matches the same domain.
   - If found: propose an update-in-place.
   - If not found: propose a new `NNN-short-title.md` in the correct folder.
     Compute NNN:
     * List all `NNN-*.md` files in the target folder.
     * next = max(NNN from existing files) + 1; zero-pad to 3 digits.
     * If no numbered files exist, start at `001`.
     * Propose the full path; do not create until APPROVE.

3) Compose canonical spec:
   - Canonical spec must be self-contained.
   - It may *summarize* contracts/models and link to stable internal docs if needed.
   - Do not copy volatile check outputs; keep checks at repo-level.

4) Coherence gate:
   - If contradictions with existing canonical specs exist, stop and propose resolution.
   - Update spec index README if it exists.

## Completion criteria
- Canonical spec created or updated in `/docs/**`
- No contradictions with existing specs

Return control to Fabricator.
