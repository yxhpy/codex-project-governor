# Test Plan

| Case | Required when | Planned coverage | Status |
|---|---|---|---|
| Normal behavior | Release metadata changes | `tests/selftest.py`, `tests/test_harness_v6.py`, `tests/test_claude_code_compat.py`, `make test` | passed |
| Boundary values | Version and feature-matrix current latest can drift | Grep for stale current-release refs and assert `current_latest == 6.2.2` | passed |
| Empty/null/error input | No new input parser behavior | Not applicable; no parser contract changes | not tested |
| Regression | Release consistency and diagnostics cleanup | `python3 -m unittest discover -s tests -p 'test_*.py'` | passed |
| Integration/contract | Plugin manifests, marketplace examples, install refs | Manifest JSON parse, Claude marketplace test, selftest, harness doctor, Claude plugin validation | passed |
| Frontend interaction | No UI/frontend behavior changed | Not applicable | not tested |
| Not tested rationale | Project migration | No `releases/MIGRATIONS.json` entry because initialized-project file migration is not required | recorded |
