---
name: pr-governance-review
description: Run a governance review of a branch against main using subagents for iteration compliance, style drift, architecture drift, tests, dependencies, security, and memory updates.
---

# PR Governance Review

Use before opening a PR or during review.

## Required subagents

Run `subagent-activation` with workflow `pr-governance-review`.

Explicitly spawn selected read-only subagents, one per review dimension:

1. `iteration-compliance-reviewer`
2. `style-drift-reviewer`
3. `architecture-drift-reviewer`
4. `test-planner`
5. `dependency-risk-reviewer`
6. `docs-memory-reviewer`
7. `quality-reviewer` when the branch has broad impact or strict quality requirements

Each subagent must:

- compare the branch against the merge base or main branch
- avoid writing files
- cite evidence paths
- report blocking issues, warnings, and recommended patches
- distinguish confirmed defects from subjective suggestions

## Main agent consolidation

Wait for all subagents. Then return:

```markdown
# PR Governance Review

## Blocking

- [ ] <issue>

## Warnings

- [ ] <issue>

## Dimension results

| Dimension | Result | Notes |
|---|---|---|

## Required patches

- <patch>

## Docs / memory updates

- <update>
```
