<!-- generated_from: iteration_plan_v1; source: ITERATION_PLAN.slots.json; revision: 1 -->
# Iteration Plan: Release 6.2.3

## User request

Submit the completed slot-based governance artifact workflow as a new Project Governor patch version.

## Existing behavior

- Current public plugin metadata and documentation point at version 6.2.2.
- Release metadata is tracked in CHANGELOG.md, releases/<version>.md, releases/FEATURE_MATRIX.json, README files, tests, and docs/upgrades/UPGRADE_REGISTER.md.
- The completed feature adds deterministic governance artifact rendering and revision-checked slot updates, with context-indexer read-side optimization for generated Markdown.

## Existing patterns to reuse

| Pattern | Source file | How it will be reused |
| --- | --- | --- |
| Patch release ledger | tasks/2026-04-30-release-6-2-2, releases/6.2.2.md, docs/upgrades/UPGRADE_REGISTER.md | Publish a low-risk patch release with feature matrix, release notes, README refs, tests, and upgrade advisory evidence. |
| Version sync | .codex-plugin/plugin.json, .claude-plugin/plugin.json, tests/selftest.py, tests/test_harness_v6.py, tests/test_claude_code_compat.py | Keep Codex and Claude plugin surfaces and version assertions aligned. |
| Slot-rendered plan | tools/render_governance_artifact.py | Use the new artifact renderer for this release task plan. |

## Files expected to change

- .codex-plugin/plugin.json
- .claude-plugin/plugin.json
- examples/claude-marketplace/.claude-plugin/marketplace.json
- README.md
- README.zh-CN.md
- CHANGELOG.md
- releases/6.2.3.md
- releases/FEATURE_MATRIX.json
- docs/upgrades/UPGRADE_REGISTER.md
- docs/memory/PROJECT_MEMORY.md
- tests/selftest.py
- tests/test_harness_v6.py
- tests/test_claude_code_compat.py
- tasks/2026-04-30-release-6-2-3/*

## Files not to change

- Package manifests or lockfiles
- releases/MIGRATIONS.json unless a project migration is required
- Historical release note bodies for older versions
- Deterministic helper output schemas beyond the already documented 6.2.3 feature work

## New files

| File | Why existing files cannot cover it |
| --- | --- |
| releases/6.2.3.md | Each released version has a dedicated release note. |
| tasks/2026-04-30-release-6-2-3/ITERATION_PLAN.slots.json | The release needs a task-local plan and evidence. |
| tasks/2026-04-30-release-6-2-3/UPGRADE_ADVISORY_INPUT.json | Version changes require upgrade-advisor evidence. |
| tasks/2026-04-30-release-6-2-3/QUALITY_REPORT.md | The release needs task-local verification evidence. |

## Dependencies

No new dependencies.

## Tests

- python3 skills/upgrade-advisor/scripts/analyze_upgrade_candidates.py tasks/2026-04-30-release-6-2-3/UPGRADE_ADVISORY_INPUT.json
- python3 tests/test_governance_artifact_renderer.py
- python3 tests/test_harness_v6.py
- python3 tests/test_claude_code_compat.py
- python3 tests/selftest.py
- python3 -m compileall tools skills tests claude
- python3 skills/engineering-standards-governor/scripts/check_engineering_standards.py --project . --scope diff --diff-base origin/main --format text
- python3 skills/quality-gate/scripts/run_quality_gate.py tasks/2026-04-30-release-6-2-3/QUALITY_GATE_INPUT.json
- git diff --check

## Risks

- Codex, Claude, README, feature matrix, and test version strings can drift.: mitigated by targeted version assertions and self-test
- The release touches AGENTS/template rules and must not imply blind initialized-project overwrites.: mitigated by feature matrix migration metadata and upgrade-register notes

## Rollback

Revert the 6.2.3 version bump, release note, feature matrix entry, upgrade register row, README/test version refs, and release task evidence.
