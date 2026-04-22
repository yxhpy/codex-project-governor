---
name: merge-readiness
description: Decide whether a task or branch is PR-ready by checking blockers, quality gate status, docs, memory, tests, change budget, and unresolved approvals.
---

# Merge Readiness

Use after `quality-gate` and before opening or merging a PR.

## Process

Read task artifacts, quality report, blockers, docs/memory obligations, change budget, and approvals.

## Output

Return `ready` or `not_ready` with blockers, warnings, required approvals, docs updates, and remaining risks.
