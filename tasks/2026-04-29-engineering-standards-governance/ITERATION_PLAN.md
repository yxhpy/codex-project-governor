# Iteration Plan: Engineering Standards Governance

## User request

Update Project Governor so governed coding work includes practical engineering standards for backend and frontend code, test planning, boundary tests, mock leakage detection, and reuse-first implementation.

## Current behavior

Project Governor already routes tasks, builds context packs, finds reuse candidates, synthesizes test plans, checks iteration compliance, and runs evidence-aware quality gates. The current deterministic checks do not directly scan project source for file-size risk, long functions, simple complexity signals, production mock leakage, or weak test files.

## Existing patterns to reuse

- Add one focused skill under `skills/<skill>/SKILL.md`.
- Put deterministic, dependency-free Python helpers under `skills/<skill>/scripts/`.
- Keep helper output JSON additive and document the schema in `docs/architecture/API_CONTRACTS.md`.
- Add copied project governance policy and task report templates under `templates/`.
- Surface mandatory template rule changes through `releases/MIGRATIONS.json` and existing AGENTS.md drift handling.
- Cover behavior with focused tests plus `tests/selftest.py` structure checks.

## Files expected to change

- `.codex-plugin/plugin.json`
- `README.md`
- `README.zh-CN.md`
- `CHANGELOG.md`
- `docs/architecture/API_CONTRACTS.md`
- `docs/conventions/CONVENTION_MANIFEST.md`
- `docs/memory/PROJECT_MEMORY.md`
- `docs/quality/ENGINEERING_STANDARDS_POLICY.md`
- `docs/quality/QUALITY_GATE_POLICY.md`
- `docs/quality/TESTING_ACCELERATION_POLICY.md`
- `docs/upgrades/UPGRADE_REGISTER.md`
- `docs/zh-CN/USAGE.md`
- `releases/6.1.0.md`
- `releases/FEATURE_MATRIX.json`
- `releases/MIGRATIONS.json`
- `skills/engineering-standards-governor/SKILL.md`
- `skills/engineering-standards-governor/scripts/check_engineering_standards.py`
- `skills/quality-gate/SKILL.md`
- `skills/test-first-synthesizer/SKILL.md`
- `templates/AGENTS.md`
- `templates/.codex/prompts/engineering-standards-governor.md`
- `templates/docs/quality/ENGINEERING_STANDARDS_POLICY.md`
- `templates/docs/quality/QUALITY_GATE_POLICY.md`
- `templates/docs/quality/TESTING_ACCELERATION_POLICY.md`
- `templates/tasks/_template/ENGINEERING_STANDARDS_REPORT.md`
- `templates/tasks/_template/TEST_PLAN.md`
- `templates/tasks/_template/QUALITY_REPORT.md`
- `tests/selftest.py`
- `tests/test_engineering_standards_governor.py`

## Files not to change

- Application code outside Project Governor governance surfaces.
- Package manifests, lockfiles, or third-party dependencies.
- Existing template paths except additive new templates.
- Existing helper JSON contracts except additive documentation for the new helper.

## New file justification

- `skills/engineering-standards-governor/` is needed because the behavior is broader than implementation-guard and quality-gate: it performs project source scans rather than only evaluating a supplied gate payload.
- `docs/quality/ENGINEERING_STANDARDS_POLICY.md` and its template copy define the durable engineering rules target projects should inherit.
- `templates/tasks/_template/ENGINEERING_STANDARDS_REPORT.md` gives agents a stable report shape for findings, mock inventory, and remediation.
- `templates/.codex/prompts/engineering-standards-governor.md` exposes the skill in initialized project prompt shortcuts.
- `tests/test_engineering_standards_governor.py` covers the new deterministic scanner without inflating existing self-tests.
- `releases/6.1.0.md` documents the capability release.

## Test plan

- Unit-style scanner tests for healthy code, oversized files, long/complex functions, production mock imports, suspicious mock-like production data, and test files without assertions.
- `tests/selftest.py` structure and release metadata checks.
- Python syntax compile for edited scripts and tests.
- Full `make test` if targeted checks pass.

## Risks

- Regex-based source scanning can produce false positives. The first release should report conservative findings with documented thresholds and skip generated/vendor paths.
- Adding mandatory AGENTS.md rules requires migration metadata so existing initialized projects see the drift without losing local edits.

## Acceptance criteria

- Project Governor exposes an engineering standards skill and deterministic checker.
- Initialized projects receive policy/report templates.
- Quality docs and test-first guidance cover boundary, regression, error, integration/contract, and mock-governance cases.
- Release metadata and upgrade register explain the 6.1.0 capability.
- Targeted and full self-tests pass.

## Verification

- `python3 tests/test_engineering_standards_governor.py` passed.
- `python3 tests/selftest.py` passed.
- `python3 tests/test_harness_v6.py` passed.
- `python3 tests/test_gpt55_auto_orchestration.py` passed.
- `python3 tests/test_plugin_upgrade_migrator.py` passed.
- `python3 -m compileall tools skills tests` passed.
- `python3 tools/init_project.py --mode existing --target /tmp/cpg-engineering-standards-smoke --json` passed.
- `python3 skills/engineering-standards-governor/scripts/check_engineering_standards.py --project . --scope diff --diff-base HEAD` passed.
- `python3 skills/harness-doctor/scripts/doctor.py --project . --execution-readiness` passed.
- `git diff --check` passed.
- `make test` passed.
