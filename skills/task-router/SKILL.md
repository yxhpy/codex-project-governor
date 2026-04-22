---
name: task-router
description: Classify a user request into the fastest safe Project Governor workflow, including micro-patch routing, negative constraints, route guard requirements, lane, quality level, change budget, and required downstream skills.
---

# Task Router

Use before implementation when speed matters but quality gates must remain intact.

## Routes

- `micro_patch`
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
2. Choose lane: `fast_lane`, `standard_lane`, `risk_lane`, or `refactor_lane`.
3. Choose quality level: `light`, `standard`, or `strict`.
4. Produce a change budget.
5. Select downstream skills.
6. Produce route guard requirements for fast or constrained routes.
7. Do not implement code.

## Micro Patch Route

Use `micro_patch` only when all are true:

- the target file, page, component, or area is explicit
- the change is local and low-risk, such as style, copy, typo, spacing, class, label, or color
- expected modified files is at most 1
- expected added files is 0
- no dependency, API, schema, auth, payment, security, or data-model change is required
- the target is not a shared/global component unless the user explicitly intends global impact
- no new component, hook, service, schema, or style system is required

`micro_patch` skips context packs, pattern reuse, feature-builder, test-first synthesis, and subagent audit. It still requires direct edit, route guard, and a light quality gate.

## Negative Constraints

Phrases such as "do not change API", "don't touch schema", "不要改接口", "不要改 schema", "no new files", or "without adding dependencies" are guardrails, not risk intent. Convert them into route guard requirements.

## Automatic Escalation

Escalate from `micro_patch` when the target is shared/global, when more files are needed, when a new file/dependency/API/schema/style-system change is needed, or when the actual diff exceeds route guard requirements.

## Output

Return route, lane, quality level, risk signals, negative constraints, required skills, skipped workflow, change budget, route guard requirements, and escalation triggers.
