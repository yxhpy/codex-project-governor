---
name: pattern-reuse-engine
description: Find existing components, services, hooks, schemas, tests, and style patterns that must be reused before creating new implementation patterns.
---

# Pattern Reuse Engine

Use before implementation when a change could introduce components, services, hooks, schemas, API clients, state, styles, or tests.

## Automatic subagent activation

Run `subagent-activation` with workflow `pattern-reuse-engine` when the route is not `micro_patch` or when the target may be shared/global.

Use `pattern-reuse-scout` for read-only reuse discovery when selected. Do not ask the user to name the scout.

## Process

1. Read `PATTERN_REGISTRY.md` and `COMPONENT_REGISTRY.md`.
2. Run selected read-only scouts when subagent mode is optional or required.
3. Search adjacent implementation.
4. Identify reusable patterns and forbidden duplicates.
5. Create `PATTERN_REUSE_PLAN.md`.

## Output

Return reusable patterns, evidence paths, required reuse rules, forbidden duplicate patterns, and allowed new files with justification.
