---
name: iteration-planner
description: Plan a feature, fix, or refactor as an iteration on existing patterns instead of a greenfield rewrite.
---

# Iteration Planner

Use before implementing any non-trivial feature, bug fix, migration, or refactor.

## Required reading

1. `AGENTS.md`
2. `docs/conventions/CONVENTION_MANIFEST.md`
3. `docs/conventions/ITERATION_CONTRACT.md`
4. `docs/conventions/PATTERN_REGISTRY.md`
5. `docs/conventions/COMPONENT_REGISTRY.md`
6. Relevant nested `AGENTS.md` files
7. Adjacent existing code

## Process

1. Restate the user request.
2. Identify current behavior and adjacent implementation.
3. Identify existing patterns to reuse.
4. Identify files expected to change and files explicitly not to change.
5. Justify every new file.
6. Reject new dependencies unless clearly necessary.
7. Identify tests and validation commands.
8. Create `tasks/<yyyy-mm-dd>-<slug>/ITERATION_PLAN.md` from the template.
9. Do not implement until the plan is complete.

## Anti-greenfield checks

Flag the plan if it:

- duplicates an existing component or service
- creates a new styling approach
- creates a parallel state management pattern
- changes API response shapes without a decision record
- changes public behavior without documenting it
- adds dependencies without alternatives and risk analysis
- replaces large parts of a module instead of making a smaller patch

## Output

Return the path to the iteration plan and a summary of:

- existing patterns reused
- minimal patch boundary
- risks
- tests
- open questions
