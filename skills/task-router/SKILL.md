---
name: task-router
description: Classify a user request into the fastest safe Project Governor workflow, lane, quality level, change budget, and required downstream skills.
---

# Task Router

Use before implementation when speed matters but quality gates must remain intact.

## Routes

- `tiny_patch`
- `standard_feature`
- `risky_feature`
- `refactor`
- `migration`
- `dependency_upgrade`
- `ui_change`
- `test_only`
- `docs_only`

## Process

1. Classify the request.
2. Choose lane: `fast`, `standard`, `risk`, or `refactor`.
3. Choose quality level: `light`, `standard`, or `strict`.
4. Produce a change budget.
5. Select downstream skills.
6. Do not implement code.

## Output

Return route, lane, quality level, risk signals, required skills, change budget, and escalation triggers.
