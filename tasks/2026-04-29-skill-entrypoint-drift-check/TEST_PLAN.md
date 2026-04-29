# Test Plan: Skill Entrypoint Drift Check

| Area | Coverage | Command |
|---|---|---|
| Normal behavior | Current catalog and README skill groups return `status: pass` with no issues. | `python3 tools/analyze_skill_catalog.py --project . --format json --fail-on-issues` |
| Boundary behavior | Missing catalog still returns structured failure JSON. | `python3 tests/test_skill_catalog_analyzer.py` |
| Error behavior | README group drift reports missing and extra skill group issues. | `python3 tests/test_skill_catalog_analyzer.py` |
| Regression behavior | Existing catalog-to-skill directory coverage still passes. | `python3 tests/selftest.py` |
| Integration/contract behavior | Analyzer remains in `make test` and README grouping is documented in API/convention contracts. | `make test` |
| Frontend interaction | Not applicable; this is documentation and CLI validation. | Not run |
| Not-tested rationale | Automatic README generation is not tested because this change validates drift only and does not rewrite docs. | Not run |
