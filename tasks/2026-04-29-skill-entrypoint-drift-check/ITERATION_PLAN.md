# Iteration Plan: Skill Entrypoint Drift Check

## User request

Continue optimizing the large Project Governor skill surface after adding the catalog and analyzer.

## Existing behavior

`skills/CATALOG.json` records skill visibility, and README groups skills by audience. The analyzer checks catalog health but does not verify that README skill sections still match catalog visibility. `design-md-aesthetic-governor` remains in the main recommended table even though it is a specialized UI gate and is documented separately.

## Existing patterns to reuse

| Pattern | Source file | Reuse decision |
|---|---|---|
| Skill catalog source of truth | `skills/CATALOG.json` | Treat visibility as the source for README grouping. |
| Deterministic maintenance CLI | `tools/analyze_skill_catalog.py` | Extend the analyzer rather than adding another script. |
| Focused tests | `tests/test_skill_catalog_analyzer.py` | Add drift detection coverage beside analyzer tests. |
| Documentation grouping | `README.md`, `README.zh-CN.md` | Keep compatibility docs while reducing main-entry noise. |

## Files expected to change

- `skills/CATALOG.json`
- `tools/analyze_skill_catalog.py`
- `tests/test_skill_catalog_analyzer.py`
- `README.md`
- `README.zh-CN.md`
- `docs/architecture/API_CONTRACTS.md`
- `docs/conventions/CONVENTION_MANIFEST.md`
- `tasks/2026-04-29-skill-entrypoint-drift-check/PATTERN_REUSE_PLAN.md`
- `tasks/2026-04-29-skill-entrypoint-drift-check/TEST_PLAN.md`
- `tasks/2026-04-29-skill-entrypoint-drift-check/ENGINEERING_STANDARDS_REPORT.md`
- `tasks/2026-04-29-skill-entrypoint-drift-check/EVIDENCE_INPUT.json`
- `tasks/2026-04-29-skill-entrypoint-drift-check/ROUTE_GUARD_INPUT.json`
- `tasks/2026-04-29-skill-entrypoint-drift-check/QUALITY_GATE_INPUT.json`
- `tasks/2026-04-29-skill-entrypoint-drift-check/MERGE_READINESS_INPUT.json`

## Files not to change

- `skills/*/SKILL.md`
- Plugin manifests
- Template paths
- Package manifests or lockfiles

## New files

| File | Why existing files cannot cover it |
|---|---|
| `tasks/2026-04-29-skill-entrypoint-drift-check/ITERATION_PLAN.md` | Records this non-trivial documentation/contract iteration separately from the analyzer implementation. |

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

- Overly strict README parsing could fail on unrelated prose changes. Keep parsing scoped to the three skill grouping sections.
- Reclassifying a skill visibility must not rename, delete, or move the skill directory.

## Rollback

Revert catalog visibility changes, README grouping edits, analyzer drift checks, and the focused tests.
