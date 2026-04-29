# Iteration Plan: Maintenance Entrypoint Consolidation

## User request

Continue reducing the visible Project Governor skill surface.

## Existing behavior

README recommended entrypoints list `clean-reinstall-manager` and `plugin-upgrade-migrator` as separate rows. They both belong to the maintenance category and are usually part of the same user mental model: install/update/reinstall/refresh/migrate Project Governor governance safely.

## Existing patterns to reuse

| Pattern | Source file | Reuse decision |
|---|---|---|
| Backward-compatible skill names | `skills/clean-reinstall-manager/SKILL.md`, `skills/plugin-upgrade-migrator/SKILL.md` | Keep both skill directories and README references. |
| Catalog visibility drift guard | `tools/analyze_skill_catalog.py` | Keep both skill names in the recommended section so catalog coverage remains exact. |
| Focused README consolidation tests | `tests/test_skill_catalog_analyzer.py` | Add a regression assertion beside the init consolidation test. |

## Files expected to change

- `README.md`
- `README.zh-CN.md`
- `tests/test_skill_catalog_analyzer.py`
- `tasks/2026-04-29-maintenance-entrypoint-consolidation/ITERATION_PLAN.md`
- `tasks/2026-04-29-maintenance-entrypoint-consolidation/PATTERN_REUSE_PLAN.md`
- `tasks/2026-04-29-maintenance-entrypoint-consolidation/TEST_PLAN.md`
- `tasks/2026-04-29-maintenance-entrypoint-consolidation/ENGINEERING_STANDARDS_REPORT.md`
- `tasks/2026-04-29-maintenance-entrypoint-consolidation/EVIDENCE_INPUT.json`
- `tasks/2026-04-29-maintenance-entrypoint-consolidation/ROUTE_GUARD_INPUT.json`
- `tasks/2026-04-29-maintenance-entrypoint-consolidation/QUALITY_GATE_INPUT.json`
- `tasks/2026-04-29-maintenance-entrypoint-consolidation/MERGE_READINESS_INPUT.json`

## Files not to change

- `skills/*/SKILL.md`
- `skills/CATALOG.json`
- Plugin manifests
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

- Removing either maintenance skill mention from README would break exact catalog visibility coverage. Keep both names in the consolidated row.

## Rollback

Restore separate README rows and remove the focused consolidation assertion.
