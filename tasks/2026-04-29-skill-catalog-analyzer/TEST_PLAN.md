# Test Plan: Skill Catalog Analyzer

| Area | Coverage | Command |
|---|---|---|
| Normal behavior | Current repository catalog returns `status: pass`, matching skill/catalog counts, visibility counts, category counts, and consolidation candidates. | `python3 tests/test_skill_catalog_analyzer.py` |
| Boundary behavior | Missing `skills/CATALOG.json` returns structured failure JSON instead of an unhandled exception. | `python3 tests/test_skill_catalog_analyzer.py` |
| Error behavior | `--fail-on-issues` exits nonzero when a skill directory is missing from the catalog. | `python3 tests/test_skill_catalog_analyzer.py` |
| Regression behavior | Existing skill catalog selftest still validates exact catalog-to-directory coverage. | `python3 tests/selftest.py` |
| Integration/contract behavior | CLI contract supports JSON/text formats and is included in `make test`. | `python3 tools/analyze_skill_catalog.py --project . --format json --fail-on-issues`; `python3 tools/analyze_skill_catalog.py --project . --format text`; `make test` |
| Frontend interaction | Not applicable; this is a repository maintenance CLI with no UI. | Not run |
| Not-tested rationale | No automated deletion/deprecation path is tested because the analyzer is advisory-only and intentionally does not edit files. | Not run |
