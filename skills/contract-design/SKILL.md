---
name: contract-design
description: "Define interface/persistence contracts (APIs, schemas, deeplinks, storage formats) + compatibility rules. Use when public surfaces or stable formats are involved."
---

# contract-design

## Purpose
Make interface boundaries explicit and testable.
This skill can target:
- HTTP API / GraphQL / gRPC
- deeplink formats
- persistence schema / storage format
- event contracts (analytics/events)

## Inputs
- WORK_PATH
- Task + Spec (preferred)
- Context Map (how the project expresses contracts, if known)

## Output
Default: `${WORK_PATH}/contracts.md`
If the project already uses OpenAPI/proto/schema files, ask user which format to use and where to write.

## Internal loop
### 1) Select contract type
Ask:
- What boundary is changing? Who consumes it?
- Backward compatibility required? Versioning strategy?
- Migration needed (for persistence)?

### 2) Draft contract (preview)
Minimum sections (even in markdown):
- Contract scope (producer/consumer)
- Data shapes (fields + types + required/optional)
- Constraints/invariants (validation rules)
- Compatibility rules (what is allowed to change, what is breaking)
- Migration/rollout notes (if persistence)
- Verification hooks (how to validate contract correctness)

### 3) Consistency check
- Must align with spec rules and acceptance criteria
- Must not conflict with existing contracts in WORK_PATH

## Completion criteria
- Contract is precise enough that a consumer can implement against it

Return control to Fabricator.
