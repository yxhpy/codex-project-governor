# Iteration Plan

## User request

Add a lightweight built-in way to search Project Governor memory/history so users do not need to assemble complex shell pipelines. Keep it aligned with the repository's existing context-index v2 system.

## Existing behavior

`context-indexer` already builds `.project-governor/context/CONTEXT_INDEX.json` and queries it for task-specific files. The index marks `docs/memory/**` and `.project-governor/state/**` as memory roles, but there is no explicit memory-search mode, auto-build query path, or user-facing guidance for governance history lookup.

## Existing patterns to reuse

| Pattern | Source file | How it will be reused |
|---|---|---|
| Deterministic, dependency-free Python helpers | `skills/context-indexer/scripts/*.py` | Extend the existing query/build scripts instead of adding a new runtime or dependency. |
| JSON-first CLI contracts | `docs/architecture/API_CONTRACTS.md` | Keep default JSON output stable and document additive fields/options. |
| Context roles and route weights | `query_context_index.py`, `build_context_index.py` | Add a memory-search role filter and task-history role without changing default context search. |
| Standard-library tests | `tests/test_gpt55_auto_orchestration.py`, `tests/test_harness_v6.py` | Add focused tests for memory-search and auto-build behavior. |

## Files expected to change

- `skills/context-indexer/scripts/build_context_index.py`
- `skills/context-indexer/scripts/query_context_index.py`
- `skills/context-indexer/SKILL.md`
- `docs/architecture/API_CONTRACTS.md`
- `README.md`
- `README.zh-CN.md`
- `docs/zh-CN/USAGE.md`
- `tests/test_gpt55_auto_orchestration.py`
- `tests/test_harness_v6.py`

## Files not to change

- `.codex-plugin/plugin.json`
- `tools/init_project.py`
- Template paths under `templates/`
- Application/runtime dependencies

## New files

| File | Why existing files cannot cover it |
|---|---|
| `tasks/2026-04-28-governance-memory-search/ITERATION_PLAN.md` | Required by the iteration contract for script and workflow changes. |

## Dependencies

No new dependencies. Use Python standard library only.

## Tests

- `python3 tests/test_gpt55_auto_orchestration.py`
- `python3 tests/test_harness_v6.py`
- `python3 -m compileall skills/context-indexer tests/test_gpt55_auto_orchestration.py tests/test_harness_v6.py`
- `make test` if focused checks pass.

## Risks

- Changing the query JSON shape can break downstream users. Mitigation: keep existing fields and add only optional fields.
- Searching raw chat history can leak noise or secrets. Mitigation: search governed project memory/docs/tasks, not raw transcripts.
- Auto-build can mutate `.project-governor/context`. Mitigation: require explicit `--auto-build`.

## Rollback

Revert the context-indexer script changes, documentation updates, tests, and this task plan. Existing default context-index behavior should remain compatible throughout.
