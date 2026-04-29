# Iteration Plan: Router Docs Typo Optimization

## User request

Deep-search remaining skill duplication and continue optimizing the skill experience.

## Existing behavior

The skill catalog is now grouped by audience, but usage docs still show `task-router` as the main acceleration command. The task router also treats some documentation typo/copy requests as heavier UI or standard workflows when no exact file target is provided.

## Existing patterns to reuse

| Pattern | Source file | How it will be reused |
|---|---|---|
| Smart routing guard | `skills/task-router/scripts/classify_task.py` | Add a narrow docs/copy helper rather than rewriting routing. |
| Routing regression tests | `tests/test_smart_routing_guard.py` | Add focused tests for README typo and UI copy classification. |
| GPT orchestration tests | `tests/test_gpt55_auto_orchestration.py` | Add coverage that orchestrator inherits the lighter docs-only route. |
| Orchestrator-first docs | `README.md`, `README.zh-CN.md` | Update usage guidance to recommend `gpt55-auto-orchestrator` first while keeping direct router examples for advanced use. |

## Files expected to change

- `skills/task-router/scripts/classify_task.py`
- `skills/gpt55-auto-orchestrator/scripts/select_runtime_plan.py`
- `tests/test_smart_routing_guard.py`
- `tests/test_gpt55_auto_orchestration.py`
- `README.md`
- `README.zh-CN.md`
- `examples/gpt55-runtime-standard-feature.json`

## Files not to change

- Skill directories or names.
- `skills/CATALOG.json` beyond the existing catalog consolidation.
- Plugin manifests, template paths, package manifests, or lockfiles.

## New files

| File | Why existing files cannot cover it |
|---|---|
| None | This is a focused routing/docs refinement. |

## Dependencies

No new dependencies.

## Tests

- `python3 tests/test_smart_routing_guard.py`
- `python3 tests/test_gpt55_auto_orchestration.py`
- `python3 tests/selftest.py`
- `python3 -m compileall tools skills tests`

## Risks

- Over-broad docs-only detection could misroute UI copy changes. Keep UI-surface terms as `ui_change`.
- Docs guidance could hide useful advanced router diagnostics. Keep direct `task-router` references as advanced/manual path.

## Rollback

Revert the routing helper, remove the new tests, and restore the README usage snippets.
