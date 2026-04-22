# Route Guard Policy

## Purpose

Route Guard ensures that a patch still matches the route selected before implementation.

It is especially important for `micro_patch`, `tiny_patch`, and `fast_lane` work. A small edit should not silently turn into a broad shared-component, API, schema, dependency, or global-style change.

## Micro Patch Requirements

Default `micro_patch` budget:

- max modified files: 1
- max added files: 0
- dependencies: not allowed
- API changes: not allowed
- schema changes: not allowed
- global style/token changes: not allowed
- shared component changes: not allowed
- new components/hooks/services/schemas: not allowed

## Negative Constraints

User constraints such as "do not change API" or "不要新增文件" must be converted into hard route guard requirements.

## Failure Behavior

If route guard fails, stop under the original fast route, report violations, and reroute before continuing.
