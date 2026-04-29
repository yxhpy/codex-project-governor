# Iteration Plan: Init Entrypoint Consolidation

## User request

Continue reducing the visible Project Governor skill surface.

## Existing behavior

README recommended entrypoints list `init-empty-project` and `init-existing-project` as separate rows, although they are modes of the same initialization job. The underlying deterministic helper already exposes this as `tools/init_project.py --mode empty|existing`.

## Existing patterns to reuse

| Pattern | Source file | Reuse decision |
|---|---|---|
| Backward-compatible skill names | `skills/init-empty-project/SKILL.md`, `skills/init-existing-project/SKILL.md` | Keep both skill directories and catalog entries. |
| Unified implementation mode | `tools/init_project.py --mode empty|existing` | Present initialization as one user choice with two modes. |
| README/catalog drift validation | `tools/analyze_skill_catalog.py` | Keep both skill names mentioned in the recommended section so analyzer coverage remains exact. |
| Focused analyzer tests | `tests/test_skill_catalog_analyzer.py` | Add a test that the README initialization entry is visually consolidated while preserving both skill references. |

## Files expected to change

- `README.md`
- `README.zh-CN.md`
- `tests/test_skill_catalog_analyzer.py`
- `tasks/2026-04-29-init-entrypoint-consolidation/ITERATION_PLAN.md`
- `tasks/2026-04-29-init-entrypoint-consolidation/PATTERN_REUSE_PLAN.md`
- `tasks/2026-04-29-init-entrypoint-consolidation/TEST_PLAN.md`
- `tasks/2026-04-29-init-entrypoint-consolidation/ENGINEERING_STANDARDS_REPORT.md`
- `tasks/2026-04-29-init-entrypoint-consolidation/EVIDENCE_INPUT.json`
- `tasks/2026-04-29-init-entrypoint-consolidation/ROUTE_GUARD_INPUT.json`
- `tasks/2026-04-29-init-entrypoint-consolidation/QUALITY_GATE_INPUT.json`
- `tasks/2026-04-29-init-entrypoint-consolidation/MERGE_READINESS_INPUT.json`
- `tasks/2026-04-29-init-entrypoint-consolidation/SESSION_LEARNING_INPUT.json`

## Files not to change

- `skills/*/SKILL.md`
- Plugin manifests
- Template paths
- Package manifests or lockfiles

## Dependencies

No new dependencies.

## Tests

- `python3 tools/analyze_skill_catalog.py --project . --format json --fail-on-issues`
- `python3 tests/test_skill_catalog_analyzer.py`
- `python3 tests/selftest.py`
- `python3 -m compileall tools skills tests`
- `git diff --check`
- `make test`

## Risks

- Removing either skill name from README would break exact catalog visibility coverage. Keep both names in the single initialization row.

## Rollback

Restore separate README rows and remove the focused consolidation assertion.
