---
name: route-guard
description: Verify that the actual diff still fits the route chosen by task-router, especially micro_patch and fast_lane changes.
---

# Route Guard

## Purpose

Prevent a fast route from silently becoming a broad or risky implementation.

Use this skill after implementation and before `quality-gate`, especially when the route is `micro_patch`, `tiny_patch`, `docs_only`, `test_only`, or `fast_lane`.

## Checks

Route Guard verifies modified file count, added file count, dependency changes, API contract changes, schema changes, global style or design token changes, shared component changes, new components/hooks/services/schemas, deleted tests, weakened assertions, skipped tests, and rewrite threshold.

## Required behavior

If the route guard fails, stop implementation, report violations, recommend rerouting, and do not continue under the original fast route.
