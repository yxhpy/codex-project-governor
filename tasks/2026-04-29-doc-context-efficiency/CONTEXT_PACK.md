# Context Pack

## Route

- Route: `risky_feature`
- Quality: `strict`
- Reason: deterministic JSON output contracts and cross-skill workflow behavior are changing.

## Must Read

- `skills/context-indexer/scripts/build_context_index.py`
- `skills/context-indexer/scripts/query_context_index.py`
- `skills/context-pack-builder/scripts/build_context_pack.py`
- `skills/task-router/scripts/classify_task.py`
- `skills/gpt55-auto-orchestrator/scripts/select_runtime_plan.py`
- `tests/test_harness_v6.py`
- `tests/test_gpt55_auto_orchestration.py`
- `tests/selftest.py`
- `docs/architecture/API_CONTRACTS.md`
- `docs/architecture/DATA_MODEL.md`

## Related Docs

- `docs/project/CHARTER.md`
- `docs/conventions/CONVENTION_MANIFEST.md`
- `docs/conventions/ITERATION_CONTRACT.md`
- `docs/harness/HARNESS_V6.md`
- `README.md`
- `README.zh-CN.md`
- `docs/zh-CN/USAGE.md`

## Existing Behavior

- File-level context index and memory search exist.
- Query results include confidence, stale files, role weights, must-read files, and token policy.
- Runtime plans already require memory search and prohibit reading all initialization docs.
- Context packs can use the context index as a source when confidence is high enough.

## Required Patterns

- Keep scripts standard-library only.
- Preserve existing top-level JSON fields and add compatible fields instead of renaming.
- Treat stale/superseded memory as lower-priority or avoid-by-default, not as deleted data.
- Prefer route-based doc packs and section-level excerpts before full documents.

## Avoid

- Do not introduce embeddings or vector database dependencies.
- Do not rewrite context indexer from scratch.
- Do not copy plugin-global assets into templates.
- Do not broaden the initializer copied file set unless required.

## Tests

- Add section-level context index/query tests.
- Add route doc pack assertions in router/runtime tests.
- Add context pack token budget and compression policy assertions.
