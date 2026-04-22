---
name: parallel-feature-builder
description: Implement a feature through a quality-gated subagent pipeline that uses parallel read-only analysis, one bounded implementation writer, test writing, review, and repair.
---

# Parallel Feature Builder

Use after task route, context pack, pattern reuse plan, test plan, and change budget exist.

## Safety rule

Do not let multiple write agents modify overlapping production code. Use parallel read-only subagents first, then one implementation writer, then one bounded test writer.

## Pipeline

1. Spawn read-only `context-scout`, `pattern-reuse-scout`, `risk-scout`, and `test-planner`.
2. Consolidate scope and change budget.
3. Use one implementation writer for the smallest coherent production patch.
4. Use one test writer for tests and fixtures.
5. Run `quality-gate`.
6. Use `repair-loop` only if the gate fails.
7. Run `merge-readiness`.

## Output

Return changed files, reused patterns, tests, gate result, and remaining blockers.
