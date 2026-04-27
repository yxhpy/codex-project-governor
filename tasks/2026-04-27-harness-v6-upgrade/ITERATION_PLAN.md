# Iteration Plan: Harness v6.0 Upgrade

## Request

Apply the local Downloads package `codex-project-governor-harness-v6.0-clean-upgrade.zip` and upgrade Project Governor from `0.5.0` to `6.0.0`.

## Upgrade Advisory

| Package / Tool | Current | Candidate | Behind / isolated by | Requirement relevance | Risk | Recommendation | Why |
|---|---:|---:|---:|---|---|---|---|
| Project Governor plugin | 0.5.0 | 6.0.0 | 6 major version fields by offline semver comparison; one supplied candidate | required | medium, breaking | upgrade_required | The user explicitly selected the local Downloads v6.0 package, which adds the Harness v6 runtime contract, session lifecycle, evidence manifests, context-index v2, git diff facts, and harness doctor checks. |

Decision: `upgrade_now`.

Evidence:

- `/Users/yxhpy/Downloads/codex-project-governor-harness-v6.0-clean-upgrade.zip`
- `/tmp/cpg-v6-upgrade/HARNESS_V6_UPGRADE.md`
- `/tmp/cpg-v6-upgrade/v6-advisory.json`
- `python3 skills/upgrade-advisor/scripts/analyze_upgrade_candidates.py /tmp/cpg-v6-upgrade/v6-advisory.json`

## Existing Patterns Reused

- Keep deterministic helpers dependency-free Python scripts under `skills/*/scripts/`.
- Add skill docs as `skills/<skill>/SKILL.md` with front matter.
- Add target-project copied assets only under `templates/`.
- Add plugin-owned source material under `managed-assets/`.
- Update `tests/selftest.py` and `Makefile` when adding a new test module.
- Record the upgrade decision in `docs/upgrades/UPGRADE_REGISTER.md`.

## Expected Changes

- Update `.codex-plugin/plugin.json` to `6.0.0` and Harness v6 positioning.
- Add `session-lifecycle`, `evidence-manifest`, and `harness-doctor` skills.
- Upgrade task routing, runtime planning, context indexing, route guard, quality gate, merge readiness, and context pack helper scripts from the v6 package.
- Add Harness v6 docs, release notes, runtime policy, state templates, evidence templates, prompt templates, and tests.
- Update README, Chinese README, changelog, architecture/convention references, API/data-model docs as needed.

## Files Not To Change

- Do not add package manifests, lockfiles, or third-party dependencies.
- Do not delete existing skills or historical release metadata.
- Do not copy generated root `.project-governor` runtime state into source control.
- Do not change application code; this repository is a plugin/template bundle.

## Validation Plan

- `python3 tests/test_harness_v6.py`
- `python3 tests/selftest.py`
- `python3 -m compileall tools skills tests`
- `make test`
- `python3 tools/init_project.py --mode existing --target <tmpdir> --json`
- `python3 skills/harness-doctor/scripts/doctor.py --project . --execution-readiness`

## Risks

- v6 changes deterministic JSON output shapes; API contract docs and tests must be aligned.
- Major-version jump changes public plugin positioning and manifest prompts.
- Context-index v2 and evidence gates may require target projects to refresh copied templates.
- The supplied package is local evidence only; no network latest-version check was performed.

## Rollback

Revert the v6 upgrade commit or restore changed files from git. The local zip remains available in Downloads for reapplication.
