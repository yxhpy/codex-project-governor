# Iteration Contract

This project must be modified through iteration, not greenfield redevelopment.

## Mandatory behavior

Before implementation, the agent must:

1. Identify existing adjacent code.
2. Identify existing patterns to reuse.
3. Identify existing components, utilities, services, hooks, schemas, tests, and styles.
4. Write or update `tasks/<date>-<slug>/ITERATION_PLAN.md`.
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

## Repository-Specific Thresholds

Treat a change as non-trivial when it:

- changes `.codex-plugin/plugin.json`
- adds, removes, or renames a skill
- changes any script under `tools/` or `skills/*/scripts/`
- changes template file paths under `templates/`
- changes deterministic JSON output shapes
- changes GitHub Actions, marketplace examples, or install instructions
- creates more than one new governance/documentation file outside templates

For trivial documentation typo fixes, a task plan is optional if no public contract changes.
