# Iteration Plan: Skill Catalog Analyzer

## User request

Continue optimizing the large Project Governor skill catalog after grouping skills by audience and reducing routing friction.

## Existing behavior

`skills/CATALOG.json` now records visibility and category metadata, and README groups skills by user-facing audience. There is no deterministic helper that reports catalog health, visibility counts, category counts, duplicate summaries, or consolidation candidates.

## Existing patterns to reuse

| Pattern | Source file | How it will be reused |
|---|---|---|
| Deterministic CLI helper | `tools/init_project.py`, `skills/*/scripts/*.py` | Add a stdlib-only CLI with JSON output and optional text output. |
| Skill folder contract | `skills/<skill>/SKILL.md` | Read existing frontmatter and descriptions rather than requiring new skill files. |
| Catalog contract | `skills/CATALOG.json`, `tests/selftest.py` | Reuse the catalog as the source for visibility/category grouping. |
| Focused unittest coverage | `tests/test_*.py` | Add a targeted test file for analyzer output and issue detection. |

## Files expected to change

- `tools/analyze_skill_catalog.py`
- `tests/test_skill_catalog_analyzer.py`
- `docs/architecture/API_CONTRACTS.md`
- `docs/conventions/CONVENTION_MANIFEST.md`
- `Makefile`
- `README.md`
- `README.zh-CN.md`
- `tasks/2026-04-29-skill-catalog-analyzer/PATTERN_REUSE_PLAN.md`
- `tasks/2026-04-29-skill-catalog-analyzer/TEST_PLAN.md`
- `tasks/2026-04-29-skill-catalog-analyzer/ENGINEERING_STANDARDS_REPORT.md`
- `tasks/2026-04-29-skill-catalog-analyzer/EVIDENCE_INPUT.json`
- `tasks/2026-04-29-skill-catalog-analyzer/ROUTE_GUARD_INPUT.json`
- `tasks/2026-04-29-skill-catalog-analyzer/QUALITY_GATE_INPUT.json`
- `tasks/2026-04-29-skill-catalog-analyzer/MERGE_READINESS_INPUT.json`
- `tasks/2026-04-29-skill-catalog-analyzer/SESSION_LEARNING_INPUT.json`

## Files not to change

- `skills/*/SKILL.md`
- `skills/CATALOG.json` unless tests reveal metadata errors
- Plugin manifests
- Template paths
- Package manifests or lockfiles

## New files

| File | Why existing files cannot cover it |
|---|---|
| `tools/analyze_skill_catalog.py` | A repository-level deterministic analyzer is needed to turn catalog metadata into actionable health and consolidation signals without adding another user-facing skill. |
| `tests/test_skill_catalog_analyzer.py` | Focused tests keep analyzer behavior out of the already broad selftest file. |

## Dependencies

No new dependencies.

## Tests

- `python3 tests/test_skill_catalog_analyzer.py`
- `python3 tests/selftest.py`
- `python3 -m compileall tools skills tests`
- `make test`

## Risks

- Heuristic consolidation suggestions may be treated as deletion instructions. The analyzer must emit advisory candidates only.
- Similarity scoring can create false positives. Output must include evidence fields and avoid automatic file edits.

## Rollback

Remove the analyzer script, tests, docs usage, and API contract section.
