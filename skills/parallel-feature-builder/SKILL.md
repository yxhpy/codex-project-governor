---
name: parallel-feature-builder
description: Implement a feature through a quality-gated subagent pipeline that uses parallel read-only analysis, one bounded implementation writer, test writing, review, and repair.
---

# Parallel Feature Builder

Use after task route, context pack, pattern reuse plan, test plan, and change budget exist.

## Automatic subagent activation

Run `subagent-activation` with workflow `parallel-feature-builder`.

The user should not have to choose implementation or review agents manually. Use selected project-scoped agents from `.codex/agents/` when present.
If the selector returns `subagent_authorization.status=needs_explicit_user_authorization`, ask once for consent before spawning; do not ask the user to name agents.

For `micro_patch`, do not spawn subagents unless route-guard fails, confidence is low, or the target unexpectedly touches shared/global scope.

## Safety rule

Do not let multiple write agents modify overlapping production code. Use parallel read-only subagents first, then one implementation writer, then one bounded test writer.

## Pipeline

1. Run `subagent-activation`.
2. Spawn selected read-only scouts only after authorization is satisfied, then wait for all results.
3. Consolidate scope and change budget.
4. Use one implementation writer for the smallest coherent production patch.
5. Use one test writer for tests and fixtures.
6. Run `quality-gate`.
7. Use `repair-loop` only if the gate fails.
8. Run `merge-readiness`.

## Output

Return changed files, reused patterns, tests, gate result, and remaining blockers.
