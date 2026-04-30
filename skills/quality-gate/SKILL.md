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
- execution policy for user-selected tools/transports
- change budget
- implementation guard
- engineering standards: file size, function complexity, mock leakage, and test hygiene
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

When coding work changes source or tests, attach the `engineering-standards-governor` result as `engineering_standards` in the quality-gate input. Engineering standards blockers fail the gate; warnings fail strict gates unless accepted with evidence.

When the task includes an execution constraint such as “publish with `gh`” or “do not use `git push`”, include `execution_context` in the quality-gate input. For release publishing, use `execution_context=release_publish`; the default runtime policy requires `gh release` or `gh api` and blocks plain `git push` unless `execution_policy_override_approved` is true.
