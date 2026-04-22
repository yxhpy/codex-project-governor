---
name: quality-gate
description: Run tiered quality checks for speed-safe development, including route guard validation, iteration compliance, style drift, architecture drift, change budget, tests, docs, and memory update requirements.
---

# Quality Gate

Use after implementation and before final response or PR creation.

## Purpose

Centralize task completion checks so faster coding does not degrade quality.

v0.4.1 adds optional route guard integration: if `task-router` chose `micro_patch`, `tiny_patch`, or another fast route, `quality-gate` must verify the actual diff still fits that route before finalization.

## Gate levels

- `light`: tiny patches and targeted checks
- `standard`: ordinary features and bug fixes
- `strict`: auth, payment, security, API, data, migrations, dependency upgrades, and refactors

## Checks

- route guard
- change budget
- implementation guard
- style drift
- architecture drift
- dependency changes
- API contracts
- schema changes
- tests
- docs
- memory updates

## Output

Create `QUALITY_REPORT.md` and return pass/fail status, blockers, warnings, findings, commands run, optional route guard result, and repair-loop input.
