# Iteration Contract

This project must be modified through iteration, not greenfield redevelopment.

## Mandatory behavior

Before implementation, the agent must:

1. Identify existing adjacent code.
2. Identify existing patterns to reuse.
3. Identify existing components, utilities, services, hooks, schemas, tests, and styles.
4. Write or update the task iteration plan by creating `ITERATION_PLAN.slots.json` first, then rendering `ITERATION_PLAN.md`. Prefer `tools/new_governance_artifact.py --render` for the initial skeleton, and patch slots when plans change during execution.
5. Explain why each new file is necessary.
6. Explain why each new dependency is necessary.
7. Keep public API behavior stable unless explicitly asked.
8. Preserve visual and coding style unless the task is specifically a redesign or refactor.

## Forbidden by default

The agent must not:

- rewrite a module from scratch when a smaller patch is possible
- create parallel duplicate components
- introduce new styling systems
- introduce new state management patterns
- introduce new API response shapes
- introduce new directory conventions
- replace existing architecture without an ADR
- add production dependencies without a dependency decision
- silently change user-facing behavior

## Rewrite threshold

A rewrite requires explicit approval when:

- more than 30% of an existing file is replaced
- more than 3 new files are introduced for one feature
- a new dependency is added
- a public API contract changes
- a design token or layout convention changes
- an existing component is duplicated instead of reused

## Required implementation plan

Every non-trivial change must include:

- existing pattern being reused
- files to inspect
- files expected to change
- files not to change
- tests to update
- style constraints
- risks
- rollback path

## Generated artifact updates

Generated governance artifacts should keep model-authored content in structured slots and let deterministic scripts render fixed headings, tables, and default text.

- `ITERATION_PLAN.slots.json` is the source of truth when present.
- `ITERATION_PLAN.md` is the human-readable render output and should include a `generated_from` marker.
- Initial slot files should be created with `tools/new_governance_artifact.py` when possible, then filled or patched with variable content.
- Mid-task plan changes should be expressed as small update patches against the slot file, with revision checks and a change-log entry.
- Agents should not ask the model to regenerate full Markdown templates when only variable fields changed.
