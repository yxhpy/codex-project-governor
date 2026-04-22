# Iteration Plan: v0.4.5 Hygiene Self-Inspection Release

## Request

Publish the hygiene self-inspection fix for `codex-project-governor`.

## Upgrade Advisory

| Package / Tool | Current | Candidate | Behind / isolated by | Requirement relevance | Risk | Recommendation | Why |
|---|---:|---:|---:|---|---|---|---|
| Project Governor plugin | 0.4.4 | 0.4.5 | one patch release by local release evidence | required by user request | low: classifier-only bugfix plus release metadata and tests; no output schema or dependency changes | upgrade_required | User requested publishing the fix; v0.4.5 prevents false hygiene findings when this repository is both plugin source and Project Governor-maintained project. |

Decision: `upgrade_now`.

## Existing Patterns Reused

- Skill scripts remain under `skills/<skill>/scripts/`.
- Release notes live under `releases/<version>.md`.
- Release discovery metadata lives in `releases/FEATURE_MATRIX.json`.
- Version-visible public fields are synchronized across `.codex-plugin/plugin.json`, README, tests, changelog, upgrade register, and memory.
- Tests use Python standard-library `unittest`.

## Expected Changes

- Bump plugin version to `0.4.5`.
- Record the bugfix in changelog, release metadata, upgrade register, and project memory.
- Keep the classifier JSON output shape unchanged.
- Keep `releases/MIGRATIONS.json` unchanged because no project migration is required.

## Files Not To Change

- Do not modify template paths or copied template payloads.
- Do not add dependencies, package manifests, lockfiles, services, or runtimes.
- Do not overwrite prior release tags or release history.
- Do not change deterministic helper output schemas.

## New File Justification

- `releases/0.4.5.md` documents the patch release.
- This task plan records the required upgrade decision, scope, verification, risk, and rollback path for a non-trivial version publish.

## Tests

- `python3 tests/test_project_hygiene_doctor.py`
- `python3 tests/selftest.py`
- `python3 tests/test_plugin_upgrade_migrator.py`
- `python3 -m compileall skills tests`
- `python3 skills/project-hygiene-doctor/scripts/inspect_project_hygiene.py --project . --plugin-root .`
- `python3 skills/plugin-upgrade-migrator/scripts/compare_features.py --current-version 0.4.4 --target-version 0.4.5 --feature-matrix releases/FEATURE_MATRIX.json`
- `python3 skills/plugin-upgrade-migrator/scripts/plan_migration.py --project . --plugin-root . --current-version 0.4.4 --target-version 0.4.5`

## Risks

- A release tag already exists for `v0.4.4`; do not retag or overwrite it.
- GitHub CLI authentication may need repair before the GitHub Release can be created.

## Rollback

Revert this task's changed files and restore `.codex-plugin/plugin.json` version `0.4.4`.
