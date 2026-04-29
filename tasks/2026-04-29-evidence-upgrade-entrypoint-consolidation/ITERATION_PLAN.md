# Iteration Plan: Evidence and Upgrade Entrypoint Consolidation

## User request

Continue reducing the visible Project Governor skill surface.

## Existing behavior

README recommended entrypoints list `research-radar` and `upgrade-advisor` as separate rows. They are different workflows, but both answer the same user-level question: get evidence and risk before adopting or changing something.

## Existing patterns to reuse

| Pattern | Source file | Reuse decision |
|---|---|---|
| Evidence-before-change workflows | `research-radar`, `upgrade-advisor` | Preserve both skills and references; collapse only the README row. |
| Catalog visibility coverage | `tools/analyze_skill_catalog.py` | Keep both names in the recommended section so drift checks remain exact. |
| README consolidation regression | `tests/test_skill_catalog_analyzer.py` | Add the same style of assertion used for initialization and maintenance consolidation. |

## Files expected to change

- `README.md`
- `README.zh-CN.md`
- `tests/test_skill_catalog_analyzer.py`
- `tasks/2026-04-29-evidence-upgrade-entrypoint-consolidation/ITERATION_PLAN.md`
- `tasks/2026-04-29-evidence-upgrade-entrypoint-consolidation/PATTERN_REUSE_PLAN.md`
- `tasks/2026-04-29-evidence-upgrade-entrypoint-consolidation/TEST_PLAN.md`
- `tasks/2026-04-29-evidence-upgrade-entrypoint-consolidation/ENGINEERING_STANDARDS_REPORT.md`
- `tasks/2026-04-29-evidence-upgrade-entrypoint-consolidation/EVIDENCE_INPUT.json`
- `tasks/2026-04-29-evidence-upgrade-entrypoint-consolidation/ROUTE_GUARD_INPUT.json`
- `tasks/2026-04-29-evidence-upgrade-entrypoint-consolidation/QUALITY_GATE_INPUT.json`
- `tasks/2026-04-29-evidence-upgrade-entrypoint-consolidation/MERGE_READINESS_INPUT.json`

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

- Collapsing evidence and upgrade advice too far could hide the difference between general research and upgrade-specific advisory. Keep both skill names in the row and preserve the detailed sections later in the README.

## Rollback

Restore separate README rows and remove the focused consolidation assertion.
