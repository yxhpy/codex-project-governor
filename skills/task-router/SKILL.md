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
5. Produce a route-specific documentation pack with primary roles, read order, section budget, stale-doc filtering, and compression policy.
6. Select downstream skills.
7. Produce route guard requirements for fast or constrained routes.
8. Select `subagent_mode`: `none`, `optional`, or `required`.
9. Do not implement code.

## Micro Patch Route

Use `micro_patch` only when all are true:

- the target file, page, component, or area is explicit
- the change is local and low-risk, such as style, copy, typo, spacing, class, label, or color
- expected modified files is at most 1
- expected added files is 0
- no dependency, API, schema, auth, payment, security, or data-model change is required
- the target is not a shared/global component unless the user explicitly intends global impact
- no new component, hook, service, schema, or style system is required

`micro_patch` skips task artifact creation, context packs, pattern reuse, feature-builder, test-first synthesis, subagent audit, evidence manifests, and merge readiness. It still requires direct edit, route guard, and a light quality gate.

## Tiny Patch Route

Use `tiny_patch` for low-risk local bug, UI, docs, or test changes when the target area is clear enough but the patch may touch up to three files or add one local test file. Do not use it for new components/widgets/features, dependencies, public contracts, schema/data changes, shared/global components, refactors, migrations, auth, payment, security, or low-confidence work.

`tiny_patch` skips task artifact creation, context packs, pattern reuse, feature-builder, test-first synthesis, subagent audit, and evidence manifests. It still requires direct edit, route guard, diff-scoped engineering standards, a light quality gate, and inline final-response evidence.

## Subagent Mode

- `none`: `micro_patch` or high-confidence `tiny_patch`. Do not spawn subagents unless route-guard fails.
- `optional`: small UI, bugfix, test-only, or docs-only work where confidence is lower or target impact is uncertain.
- `required`: standard features, risky features, refactors, migrations, dependency upgrades, PR governance, initialization, and broad research.

## Negative Constraints

Phrases such as "do not change API", "don't touch schema", "不要改接口", "不要改 schema", "no new files", or "without adding dependencies" are guardrails, not risk intent. Convert them into route guard requirements.

## Automatic Escalation

Escalate from `micro_patch` when the target is shared/global, when more files are needed, when a new file/dependency/API/schema/style-system change is needed, or when the actual diff exceeds route guard requirements. Escalate from `tiny_patch` when a new component/widget/feature, dependency, public contract, schema/data change, shared/global component, refactor, migration, auth, payment, or security work is needed.

## Output

Return route, lane, quality level, subagent mode, risk signals, negative constraints, required skills, skipped workflow, change budget, route doc pack, route guard requirements, artifact policy, and escalation triggers.
