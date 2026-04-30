<!-- generated_from: iteration_plan_v1; source: ITERATION_PLAN.slots.json; revision: 1 -->
# Iteration Plan: Fast Path v2

## User request

节省 Project Governor 小任务链路和 token 开销，同时不降低质量。

## Existing behavior

- `micro_patch` exists but requires an explicit target and high confidence, so simple UI copy requests without a file path often route to `ui_change` and trigger the full standard workflow.
- `templates/AGENTS.md` describes the acceleration pipeline in a way that can make context packs, pattern reuse plans, test-first synthesis, evidence manifests, and merge readiness feel mandatory for every small task.
- Route guard and quality gate policies already provide the safety mechanism needed for small fast-lane work.

## Existing patterns to reuse

| Pattern | Source file | How it will be reused |
| --- | --- | --- |
| Router route/budget/workflow functions | skills/task-router/scripts/task_router_policy.py | Extend the existing workflow metadata instead of adding a new orchestrator. |
| Router shape detection | skills/task-router/scripts/classify_task.py | Relax micro-patch inference for low-risk local copy/style changes while preserving route guard escalation. |
| Policy mirrored between docs and templates | docs/quality/*.md and templates/docs/quality/*.md | Keep project docs and initialized-project templates aligned. |

## Files expected to change

- skills/task-router/scripts/classify_task.py
- skills/task-router/scripts/task_router_config.py
- skills/task-router/scripts/task_router_policy.py
- skills/task-router/SKILL.md
- skills/gpt55-auto-orchestrator/scripts/select_runtime_plan.py
- docs/architecture/API_CONTRACTS.md
- docs/quality/ACCELERATION_POLICY.md
- docs/quality/QUALITY_GATE_POLICY.md
- docs/quality/ROUTE_GUARD_POLICY.md
- docs/zh-CN/USAGE.md
- templates/AGENTS.md
- templates/docs/quality/ACCELERATION_POLICY.md
- templates/docs/quality/QUALITY_GATE_POLICY.md
- templates/docs/quality/ROUTE_GUARD_POLICY.md
- tests/test_smart_routing_guard.py
- tests/test_gpt55_auto_orchestration.py

## Files not to change

- .codex-plugin/plugin.json
- .claude-plugin/plugin.json
- releases/FEATURE_MATRIX.json
- releases/MIGRATIONS.json
- package or dependency manifests

## New files

| File | Why existing files cannot cover it |
| --- | --- |
| tasks/2026-04-30-fast-path-v2/ITERATION_PLAN.slots.json | Required source slot file for this non-trivial repository change. |
| tasks/2026-04-30-fast-path-v2/ITERATION_PLAN.md | Deterministic render output from the iteration plan slots. |
| tasks/2026-04-30-fast-path-v2/IMPLEMENTATION_GUARD_INPUT.json | Task-local validation input for the existing implementation guard. |
| tasks/2026-04-30-fast-path-v2/STYLE_DRIFT_INPUT.json | Task-local validation input proving this non-UI policy change adds no UI style drift. |
| tasks/2026-04-30-fast-path-v2/QUALITY_GATE_INPUT.json | Task-local final quality-gate input that records checks and evidence without changing production contracts. |

## Dependencies

No new dependencies expected unless explicitly approved.

## Tests

- python3 tests/test_smart_routing_guard.py
- python3 tests/test_gpt55_auto_orchestration.py
- python3 tests/selftest.py
- python3 -m unittest discover -s tests -p 'test_*.py'
- python3 -m compileall tools skills tests
- python3 skills/engineering-standards-governor/scripts/check_engineering_standards.py --project . --diff-base HEAD --format json
- python3 skills/implementation-guard/scripts/check_iteration_compliance.py tasks/2026-04-30-fast-path-v2/IMPLEMENTATION_GUARD_INPUT.json
- python3 skills/style-drift-check/scripts/check_style_drift.py tasks/2026-04-30-fast-path-v2/STYLE_DRIFT_INPUT.json
- python3 skills/quality-gate/scripts/run_quality_gate.py tasks/2026-04-30-fast-path-v2/QUALITY_GATE_INPUT.json
- git diff --check

## Risks

- Under-routing real UI behavior changes as micro patches; mitigate with conservative risk terms and route guard budgets.
- Changing deterministic JSON output shape could break consumers; mitigate by only adding optional fields.
- Template wording could imply quality gates are skipped; mitigate by explicitly keeping route guard and light quality gate mandatory.

## Rollback

Revert the router, policy, template, API contract, and test changes for this task; regenerated task artifacts can remain as historical evidence.
