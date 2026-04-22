# Iteration Plan: v0.4.4 Project Hygiene Doctor

## Request

Merge and publish Project Governor v0.4.4 from `/Users/yxhpy/Downloads/codex-project-governor-v0.4.4-project-hygiene-doctor-fixed.patch`.

## Upgrade Advisory

| Package / Tool | Current | Candidate | Behind / isolated by | Requirement relevance | Risk | Recommendation | Why |
|---|---:|---:|---:|---|---|---|---|
| Project Governor plugin | 0.4.3 | 0.4.4 | one patch release by local patch evidence | required by user request | medium: plugin metadata, one new skill, initializer output, release metadata, install manifest template, and tests change | upgrade_required | User requested merging and publishing v0.4.4; the patch adds project hygiene diagnostics and clean initialization without new dependencies. |

Decision: `upgrade_now`.

## Existing Patterns Reused

- Skill workflows live under `skills/<skill>/SKILL.md`.
- Deterministic helpers live under `skills/<skill>/scripts/` and use Python standard library only.
- Copied governance payloads live under `templates/`.
- Release metadata lives under `releases/FEATURE_MATRIX.json`, `releases/MIGRATIONS.json`, and `releases/<version>.md`.
- Public plugin metadata starts at `.codex-plugin/plugin.json`.
- Tests use standard-library `unittest`.

## Expected Changes

- Add `project-hygiene-doctor` skill and deterministic hygiene inspector.
- Add clean initialization profile to `tools/init_project.py` while preserving legacy compatibility through `--profile legacy-full`.
- Add project hygiene policy and prompt templates.
- Update release metadata, changelog, README, API contracts, upgrade register, and tests.
- Publish `v0.4.4` after validation.

## Files Not To Change

- Do not add dependencies, package manifests, lockfiles, services, or runtimes.
- Do not overwrite prior release tags or release history.
- Do not replace the full README with the shorter patch context.
- Do not treat target project application code as part of initialization.

## New File Justification

The hygiene doctor needs a skill entry, one deterministic helper script, a policy template, a prompt template, a release note, focused tests, and this iteration plan. These are governance/plugin surfaces and do not add application runtime code.

## Tests

- `python3 tests/selftest.py`
- `python3 tests/test_project_hygiene_doctor.py`
- `python3 tests/test_smart_routing_guard.py`
- `python3 tests/test_subagent_activation.py`
- `python3 tests/test_plugin_upgrade_migrator.py`
- `python3 -m compileall tools skills tests`
- `make test`
- `python3 tools/init_project.py --mode existing --target <tmpdir> --json`
- `python3 tools/init_project.py --mode existing --profile legacy-full --target <tmpdir> --json`

## Risks

- The provided patch treats `tools/init_project.py` as a new file; merge it into the current initializer rather than replacing blindly.
- The initializer JSON output shape changes, so API contracts and selftests must be updated together.
- Clean initialization should not break users who still need copied `.codex` runtime assets; preserve `--profile legacy-full`.

## Rollback

Revert this task's changed files and restore `.codex-plugin/plugin.json` version `0.4.3`.
