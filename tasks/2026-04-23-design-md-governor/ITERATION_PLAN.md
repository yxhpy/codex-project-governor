# Iteration Plan: DESIGN.md Governor v0.4.7

## Request

Apply `/Users/yxhpy/Downloads/codex-project-governor-v0.4.7-design-md-governor-dropin.zip` into the Project Governor plugin source and validate it.

## Upgrade Advisory

| Package / Tool | Current | Candidate | Behind / isolated by | Requirement relevance | Risk | Recommendation | Why |
|---|---:|---:|---|---|---|---|---|
| Project Governor plugin | 0.4.6 | 0.4.7 | patch-level, user-provided local drop-in zip | required | low | upgrade_required | The provided package adds an additive opt-in `design-md-governor` skill, deterministic standard-library helpers, examples, managed assets, and tests without dependency or target-project migration changes. |

Decision: `upgrade_now`, based on the user-provided local v0.4.7 package and prior repository release workflow.

## Existing Patterns Reused

- Skill workflow layout under `skills/<skill>/SKILL.md`.
- Dependency-free Python helper scripts under `skills/*/scripts/`.
- Prompt templates under `templates/.codex/prompts/`.
- Release notes and feature metadata under `releases/`.
- Standard-library `unittest` tests under `tests/`.
- Upgrade register and project memory entries with evidence-backed dates and statuses.

## Files Inspected

- `docs/project/CHARTER.md`
- `docs/conventions/CONVENTION_MANIFEST.md`
- `docs/conventions/ITERATION_CONTRACT.md`
- `docs/architecture/ARCHITECTURE.md`
- `docs/architecture/API_CONTRACTS.md`
- `docs/upgrades/UPGRADE_POLICY.md`
- `docs/upgrades/UPGRADE_REGISTER.md`
- `README.md`
- `README.zh-CN.md`
- `.codex-plugin/plugin.json`
- `tests/selftest.py`
- `releases/FEATURE_MATRIX.json`
- `releases/MIGRATIONS.json`
- `CHANGELOG.md`
- `Makefile`

## Expected Changes

- Add `design-md-governor` skill, scripts, examples, tests, prompt template, managed assets, release note, and feature-matrix addendum from the zip.
- Update plugin version and public docs to expose the new skill and opt-in DESIGN.md workflow.
- Update release feature metadata and self-test expectations.
- Update the `make test` wrapper to include the new focused test.
- Document the new deterministic helper output contracts.
- Record the applied upgrade and durable project facts.

## Files Not To Change

- Target project application source.
- Existing initialization default behavior.
- Existing migration operations in `releases/MIGRATIONS.json` unless a project migration is required.
- Existing deterministic output schemas for pre-v0.4.7 helpers.

## New Files

| File | Why existing files cannot cover it |
|---|---|
| `skills/design-md-governor/SKILL.md` | New workflow entry point for opt-in DESIGN.md governance. |
| `skills/design-md-governor/scripts/*.py` | Deterministic lint, summarize, and diff helpers for DESIGN.md files. |
| `managed-assets/design-md/*` | Plugin-owned DESIGN.md template and policy assets that should not be auto-copied into projects. |
| `examples/design-md-*.md` | Fixtures for lint, summarize, and regression tests. |
| `templates/.codex/prompts/design-md-governor.md` | Optional prompt entry point for the new skill. |
| `tests/test_design_md_governor.py` | Focused regression coverage for the new helpers. |
| `releases/0.4.7.md` and `releases/FEATURE_MATRIX_ADDENDUM_0.4.7.json` | Release-specific metadata for plugin upgrade discovery. |

## Dependencies

No new dependencies. The helper scripts remain Python standard-library only; the official `@google/design.md` CLI is documented as preferred when available but is not required by this plugin.

## Tests

- `python3 tests/test_design_md_governor.py`
- `python3 tests/selftest.py`
- `python3 -m compileall tools skills tests`
- `make test`
- Init smoke test with `python3 tools/init_project.py --mode existing --target <tmpdir> --json`

## Risks

- The package uses a new top-level `managed-assets/` directory, so architecture and convention docs must make its plugin-owned status explicit.
- The DESIGN.md helper JSON output is a new deterministic contract and should be documented.
- The official npm CLI is optional; tests must cover the bundled fallback so validation remains dependency-free.

## Rollback Path

Revert the v0.4.7 source changes and remove the added `design-md-governor`, `managed-assets/design-md`, examples, tests, release metadata, and manifest/doc updates.
