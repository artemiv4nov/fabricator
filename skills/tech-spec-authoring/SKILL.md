---
name: tech-spec-authoring
description: "Compose a Technical Specification (tech-spec.md) in WORK_PATH: a single handoff-ready document that covers goals, proposed solution, implementation details, test plan, and alternatives. After it is written, the implementation skill can proceed directly from it."
---

# tech-spec-authoring

## Purpose
Produce a `tech-spec.md` inside WORK_PATH that fully describes the technical solution — precise enough that the `implementation` skill can execute it without asking clarifying questions.

This is a **Technical Specification** in the Zara Cooper / Stack Overflow sense:
- combines requirements (WHAT) + design (HOW) + test plan
- selectively includes only sections relevant to the task
- **self-contained**: all content is written inline so the document can be shared without access to other WORK_PATH files

## Inputs
- WORK_PATH (must exist and already be set by Fabricator)
- Read all existing WORK_PATH artifacts: `task.md`, `requirements.md` (or `spec.md`), `contracts.md`, `models.md`
- Any additional files referenced within those artifacts that are relevant to the solution

## Output
- `tech-spec.md` in WORK_PATH

## Skill-specific rules
- Write only `tech-spec.md` — do not create other files.
- Include all relevant content inline — do NOT use links to other WORK_PATH files as a substitute for content. `tech-spec.md` must be readable as a standalone document.
- Pseudocode and code sketches MUST follow the repo's primary language conventions.
- Test plan section MUST contain runnable test cases — vague descriptions are not acceptable.
- If a required section cannot be filled (e.g., no known API changes), write `N/A` with a one-line explanation, not an empty heading.

---

## Section-by-section guide

### Header
```
# Technical Specification: <feature or task title>
```
Title comes from `task.md` or user input. No date, no author — that is in git.

---

### 1. Goals / Non-goals / Open questions
Three subsections in one block. Read from task.md / requirements.md and write out the content directly — do NOT say "see task.md".

```markdown
## Goals / Non-goals / Open questions

### Goals
- <what will be implemented — concrete, verifiable>

### Non-goals
- <what is explicitly out of scope — things a reader might reasonably assume are included>

### Open questions
- <unresolved questions that must be answered before or during implementation>
  - If none: write "None."
```

**Rules:**
- Goals must be verifiable: "user can log in with biometrics" is good; "improve UX" is not.
- Non-goals prevent scope creep — be explicit even if obvious.
- Open questions block implementation until resolved; list them here so `implementation` knows what to skip or flag.

---

### 2. Proposed solution
A narrative (2–5 paragraphs or structured bullets) that describes the chosen technical approach.

```markdown
## Proposed solution
<Describe the approach at a level where a senior engineer can understand the direction
without reading the implementation details. Cover:
- what components are involved
- what the main flow looks like end-to-end
- what the key technical decision is and why this approach was chosen>
```

**Rules:**
- This section explains WHY this approach over alternatives (briefly — full alternatives go to section 5).
- Diagrams (ASCII or Mermaid) are encouraged for flows.
- No pseudocode here — that belongs in Implementation details.

---

### 3. Implementation details
The most precise section. Fill only the subsections that apply; mark others `N/A`.
All content must be written inline — do not reference contracts.md or models.md as substitutes.

```markdown
## Implementation details

### Data model / schema changes
<Describe new or modified entities. Show field-level changes — include the full relevant schema here.>
Example:
- Add `biometric_enabled: Boolean` to `UserPreferences`
- New table `BiometricToken(userId, tokenHash, createdAt, expiresAt)`

### API changes
<New endpoints or modified signatures. Include the full relevant contract here.>
Example:
- POST /auth/biometric/enroll  → 201 { tokenId }
- POST /auth/biometric/verify  → 200 { sessionToken } | 401

### Pseudocode / flowcharts
<For non-trivial logic only. Use the repo's primary language syntax for pseudocode.
Keep it minimal: show the decision points, not boilerplate.>

### Error states and failure scenarios
<For each error case: condition → what the system does → what the user sees.>
Example:
- Biometric hardware unavailable → fallback to PIN → show "Use PIN instead" prompt
- Token expired → 401 with code BIOMETRIC_TOKEN_EXPIRED → client clears token, re-enroll flow

### Rollback steps
<Ordered list of steps to revert this change safely if it must be rolled back post-deploy.
Integrate feature flags or migration reversals here.>
Example:
1. Disable feature flag `biometric_auth_enabled`
2. Run migration rollback: `./gradlew migrateDown --target=<prev_version>`
3. Deploy previous release tag
```

---

### 4. Test plan
Concrete and runnable. This section feeds directly into `verification-run`.

```markdown
## Test plan

### Unit tests
<List the specific test cases that MUST be written as part of this implementation.
Pseudocode or actual test stubs are strongly preferred over vague descriptions.>
Example:
```kotlin
@Test fun `enroll returns token when biometrics available`()
@Test fun `enroll throws BiometricUnavailableException when hardware missing`()
@Test fun `verify returns session token for valid unexpired token`()
@Test fun `verify throws TokenExpiredException for expired token`()
```

### Integration / end-to-end tests
<Key flows that must pass at the integration level.>
Example:
- Full enroll → verify flow via API (happy path)
- Enroll → token expiry → re-enroll flow

### Manual verification steps
<Steps a developer or QA can follow to verify the feature works on a device.>
Example:
1. Enable biometrics on device
2. Open app → Settings → Security → Enable biometric login
3. Log out, log back in using biometric prompt
4. Verify session is created and user lands on home screen
```

**Rules:**
- Unit test names must be concrete function signatures or descriptions, not "test the happy path."
- At minimum: one happy-path test + one failure/edge-case test per changed component.
- Do not say "see verify.md" — copy the relevant commands inline.

---

### 5. Alternatives considered
Briefly document what else was evaluated and why it was rejected.

```markdown
## Alternatives considered

### <Alternative name>
- Approach: <one sentence>
- Why rejected: <trade-off or constraint that ruled it out>
```

Minimum: one alternative. If no alternatives were seriously considered, explain why the solution space was constrained.

---

### 6. Security / Privacy *(include only if applicable)*
```markdown
## Security / Privacy
- <What threat or data-privacy concern this change introduces>
- <How it is mitigated>
```

Include when:
- user credentials, tokens, biometrics, or PII are involved
- the change affects authentication, authorization, or encryption
- data is persisted that was not persisted before

Omit entirely if not applicable (do not leave an empty section).

---

### 7. References *(optional)*
If the document was compiled from WORK_PATH artifacts, list them here as a simple appendix — not as links to navigate, but as a provenance record.

```markdown
## References
- task.md, requirements.md, contracts.md, models.md (WORK_PATH)
```

This section is for traceability only. All content that matters must already be inline above.

---

## Coherence gate (before writing)
Check for contradictions with existing WORK_PATH artifacts:
1. Goals here match acceptance criteria in `task.md`?
2. API sketches consistent with `contracts.md`?
3. Data model consistent with `models.md`?
4. Test cases cover acceptance criteria from `task.md`?

If any contradiction found: stop, report the inconsistency, resolve before writing.

## Completion criteria
- `tech-spec.md` exists in WORK_PATH and covers all applicable sections
- Coherence gate passed
- The file is sufficient for `implementation` to proceed without further clarification

Return control to Fabricator.
