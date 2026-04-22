---
name: quality-gate
description: Run tiered quality checks for speed-safe development, including iteration compliance, style drift, architecture drift, change budget, tests, docs, and memory update requirements.
---

# Quality Gate

Use after implementation and before final response or PR creation.

## Gate levels

- `light`: tiny patches and targeted checks
- `standard`: ordinary features and bug fixes
- `strict`: auth, payment, security, API, data, migrations, dependency upgrades, and refactors

## Checks

change budget, implementation guard, style drift, architecture drift, dependency changes, API contracts, schema changes, tests, docs, and memory updates.

## Output

Create `QUALITY_REPORT.md` and return pass/fail status, blockers, warnings, commands run, and repair-loop input.
