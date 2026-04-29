# Iteration Plan

## User request

Modify the Project Governor plugin so agents do not waste tokens reading many documents before locating the relevant project documentation.

## Existing behavior

- `context-indexer` builds file-level entries and query results.
- `query_context_index.py` recommends whole files, not specific sections.
- `task-router` classifies the task route but does not expose a route-specific documentation pack.
- `context-pack-builder` can consume the index, but it does not enforce a token budget or avoid-list for stale/superseded docs.
- `gpt55-auto-orchestrator` already says not to read all initialization docs, but the deterministic plan does not provide a concrete docs manifest or section-level retrieval contract.

## Existing patterns to reuse

| Pattern | Source file | How it will be reused |
|---|---|---|
| Dependency-free deterministic CLI scripts | `skills/context-indexer/scripts/*.py` | Extend existing JSON outputs in place. |
| Route classification and change budgets | `skills/task-router/scripts/classify_task.py` | Add route-to-document-pack metadata without changing route names. |
| Runtime context policy | `skills/gpt55-auto-orchestrator/scripts/select_runtime_plan.py` | Surface the new progressive retrieval policy in runtime plans. |
| Context pack construction | `skills/context-pack-builder/scripts/build_context_pack.py` | Reuse index query results and add budget/compression metadata. |
| Self-test style | `tests/test_harness_v6.py`, `tests/test_gpt55_auto_orchestration.py` | Add narrow tests for section retrieval, doc status filtering, and doc packs. |

## Files expected to change

- `skills/context-indexer/scripts/build_context_index.py`
- `skills/context-indexer/scripts/query_context_index.py`
- `skills/context-pack-builder/scripts/build_context_pack.py`
- `skills/task-router/scripts/classify_task.py`
- `skills/gpt55-auto-orchestrator/scripts/select_runtime_plan.py`
- `skills/*/SKILL.md` for affected workflows
- `docs/architecture/API_CONTRACTS.md`
- `docs/architecture/DATA_MODEL.md`
- `docs/conventions/CONVENTION_MANIFEST.md`
- `docs/project/CHARTER.md`
- `docs/project/ROADMAP.md`
- `docs/memory/PROJECT_MEMORY.md`
- `docs/memory/RISK_REGISTER.md`
- `README.md`
- `README.zh-CN.md`
- `docs/zh-CN/USAGE.md`
- `releases/*`
- `tests/*`

## Files not to change

- Application templates outside context policy unless tests prove they need updates.
- `.mcp.json`
- Managed DESIGN.md assets.
- Package manifests or lockfiles.

## New files

| File | Why existing files cannot cover it |
|---|---|
| `tasks/2026-04-29-doc-context-efficiency/ITERATION_PLAN.md` | Required by the iteration contract for this non-trivial script/API change. |
| `tasks/2026-04-29-doc-context-efficiency/CONTEXT_PACK.md` | Captures the minimal read set and avoid list for this task. |

## Dependencies

No new dependencies.

## Tests

- `python3 tests/test_harness_v6.py`
- `python3 tests/test_gpt55_auto_orchestration.py`
- `python3 tests/selftest.py`
- `python3 -m compileall tools skills tests`
- `make test`

## Risks

- Adding JSON fields can accidentally break downstream consumers if output contracts are not documented.
- Section extraction must avoid leaking secret-like content in summaries.
- Stale-memory filtering should not hide all useful results when no active docs match.

## Rollback

Revert this task directory and the focused changes in context indexer, context pack builder, task router, runtime planner, docs, release metadata, and tests.
