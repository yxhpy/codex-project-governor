---
name: pattern-reuse-engine
description: Find existing components, services, hooks, schemas, tests, and style patterns that must be reused before creating new implementation patterns.
---

# Pattern Reuse Engine

Use before implementation when a change could introduce components, services, hooks, schemas, API clients, state, styles, or tests.

## Process

1. Read `PATTERN_REGISTRY.md` and `COMPONENT_REGISTRY.md`.
2. Search adjacent implementation.
3. Identify reusable patterns and forbidden duplicates.
4. Create `PATTERN_REUSE_PLAN.md`.

## Output

Return reusable patterns, evidence paths, required reuse rules, forbidden duplicate patterns, and allowed new files with justification.
