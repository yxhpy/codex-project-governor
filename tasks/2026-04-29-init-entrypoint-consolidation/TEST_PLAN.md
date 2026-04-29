# Test Plan: Init Entrypoint Consolidation

| Area | Coverage | Command |
|---|---|---|
| Normal behavior | Analyzer still sees both initialization skills in the recommended README section. | `python3 tools/analyze_skill_catalog.py --project . --format json --fail-on-issues` |
| Regression behavior | README contains a single consolidated initialization row and no old separate init rows. | `python3 tests/test_skill_catalog_analyzer.py` |
| Catalog coverage | Skill catalog still exactly matches skill directories. | `python3 tests/selftest.py` |
| Syntax/format | Python helpers and tests compile; markdown diff has no whitespace errors. | `python3 -m compileall tools skills tests`; `git diff --check` |
| Integration | Consolidation test remains part of the full test wrapper. | `make test` |
| Frontend interaction | Not applicable; this is documentation and test coverage only. | Not run |
| Not-tested rationale | No init smoke test is needed because this change does not alter `tools/init_project.py` or template copy behavior. | Not run |
