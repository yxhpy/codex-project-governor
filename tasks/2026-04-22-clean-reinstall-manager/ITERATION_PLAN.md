# Iteration Plan: Clean Reinstall Manager v0.4.6

## Request

Apply `/Users/yxhpy/Downloads/codex-project-governor-v0.4.6-clean-reinstall-manager-additive.patch`, validate it, and publish the plugin release.

## Upgrade Advisory

| Package / Tool | Current | Candidate | Behind / isolated by | Requirement relevance | Risk | Recommendation | Why |
|---|---:|---:|---|---|---|---|---|
| Project Governor plugin | 0.4.5 | 0.4.6 | patch-level, user-provided local patch | required | medium | upgrade_required | User requested upgrade and publish; patch adds a new governance skill and copied templates without new dependencies. |

Decision: `upgrade_now`, based on explicit user request.

## Existing Patterns Reused

- Skill workflow layout under `skills/<skill>/SKILL.md`.
- Dependency-free Python helper scripts under `skills/*/scripts/`.
- Template prompts under `templates/.codex/prompts/`.
- Release notes and feature metadata under `releases/`.
- Standard-library `unittest` tests under `tests/`.

## Files Inspected

- `docs/project/CHARTER.md`
- `docs/conventions/CONVENTION_MANIFEST.md`
- `docs/conventions/ITERATION_CONTRACT.md`
- `docs/architecture/ARCHITECTURE.md`
- `docs/upgrades/UPGRADE_POLICY.md`
- `docs/upgrades/UPGRADE_REGISTER.md`
- `README.md`
- `.codex-plugin/plugin.json`
- `tests/selftest.py`
- `releases/FEATURE_MATRIX.json`
- `releases/MIGRATIONS.json`
- `CHANGELOG.md`

## Expected Changes

- Add `clean-reinstall-manager` skill, scripts, tests, example, release note, feature metadata addendum, and copied governance templates from the patch.
- Update plugin version and public docs to expose the new skill.
- Update release feature/migration metadata and self-test expectations if needed.
- Record the applied upgrade in `docs/upgrades/UPGRADE_REGISTER.md`.

## Files Not To Change

- Application source in target repositories.
- Existing deterministic output schemas except for adding this new release surface.
- Existing skill behavior outside the new skill unless a test requires a narrow integration update.

## Tests

- `python3 tests/selftest.py`
- `python3 tests/test_clean_reinstall_manager.py`
- `python3 -m compileall tools skills tests`
- `make test`
- Init smoke test with `python3 tools/init_project.py --mode existing --target <tmpdir> --json`

## Risks

- New release metadata might be present only as an addendum and not integrated into the main feature matrix.
- Public manifest version and README may not be updated by the additive patch.
- Clean reinstall orchestration must avoid destructive behavior and keep scripts dependency-free.

## Rollback Path

Revert the release commit and delete tag `v0.4.6` if publication occurs before a validation failure is discovered.
