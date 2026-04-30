<!-- generated_from: iteration_plan_v1; source: ITERATION_PLAN.slots.json; revision: 1 -->
# Release 6.2.5

## User request

Publish the Fast Path v2 routing and artifact-policy changes as a new Project Governor patch version.

## Existing behavior

- Current public metadata and install instructions point at version 6.2.4.
- The completed Fast Path v2 work adds tiny_patch routing, explicit artifact_policy output, and lighter micro/tiny/docs/test artifact requirements.
- Template quality policy files and AGENTS.md now describe when inline evidence is enough and when file-backed artifacts remain required.
- Release metadata is tracked across plugin manifests, README files, release notes, feature matrix, migration metadata, tests, memory, roadmap, and upgrade register.

## Existing patterns to reuse

| Pattern | Source file | How it will be reused |
| --- | --- | --- |
| Patch release metadata update | tasks/2026-04-30-release-6-2-4/ITERATION_PLAN.slots.json | Reuse the manifest, release note, feature matrix, upgrade register, README, tests, quality evidence, and gh/API publishing pattern. |
| Upgrade advisory gate | skills/upgrade-advisor/scripts/analyze_upgrade_candidates.py | Record 6.2.4 to 6.2.5 as a low-risk patch release with no dependency or runtime service change. |
| Template drift migration | releases/MIGRATIONS.json | Surface AGENTS.md and quality-policy template changes to initialized projects through plugin-upgrade-migrator. |

## Files expected to change

- Bump Codex and Claude plugin metadata from 6.2.4 to 6.2.5.
- Add releases/6.2.5.md and update releases/FEATURE_MATRIX.json.
- Update README, Chinese README, charter, roadmap, project memory, marketplace example, tests, and upgrade register version references.
- Add migration metadata and test coverage so initialized projects can see Fast Path v2 template policy updates.
- Run upgrade-advisor, targeted tests, full selftest/unittest, compileall, engineering standards, quality-gate, and execution-policy checks before publishing.
- Publish using gh/GitHub API transport and avoid plain git push.

## Files not to change

- Package manifests or lockfiles
- Historical release note bodies for older versions
- Application code outside governance plugin surfaces
- Deterministic helper output schemas unless API contracts and tests are updated

## New files

| File | Why existing files cannot cover it |
| --- | --- |
| releases/6.2.5.md | Each public release has a dedicated release note file. |
| tasks/2026-04-30-release-6-2-5/UPGRADE_ADVISORY_INPUT.json | Release version bumps require an upgrade-advisor evidence input. |
| tasks/2026-04-30-release-6-2-5/EXECUTION_POLICY_INPUT.json | Release publishing must prove gh/GitHub API transport and block plain git push. |
| tasks/2026-04-30-release-6-2-5/QUALITY_GATE_INPUT.json | Quality-gate requires a stable task-local input that records checks and execution context. |
| tasks/2026-04-30-release-6-2-5/QUALITY_REPORT.md | The release needs a concise human-readable validation ledger. |

## Dependencies

No new dependencies expected unless explicitly approved.

## Tests

- python3 skills/upgrade-advisor/scripts/analyze_upgrade_candidates.py tasks/2026-04-30-release-6-2-5/UPGRADE_ADVISORY_INPUT.json
- python3 tests/test_smart_routing_guard.py
- python3 tests/test_gpt55_auto_orchestration.py
- python3 tests/test_plugin_upgrade_migrator.py
- python3 tests/test_harness_v6.py
- python3 tests/test_claude_code_compat.py
- python3 tests/selftest.py
- python3 -m unittest discover -s tests -p 'test_*.py'
- python3 -m compileall tools skills tests claude
- python3 skills/engineering-standards-governor/scripts/check_engineering_standards.py --project . --scope diff --diff-base HEAD --format json
- python3 skills/quality-gate/scripts/check_execution_policy.py tasks/2026-04-30-release-6-2-5/EXECUTION_POLICY_INPUT.json
- python3 skills/quality-gate/scripts/run_quality_gate.py tasks/2026-04-30-release-6-2-5/QUALITY_GATE_INPUT.json
- git diff --check

## Risks

- Version strings can drift across manifests, README files, marketplace examples, tests, feature matrix, memory, and roadmap.
- Fast Path v2 could accidentally remove required gates from non-trivial work if route tests are incomplete.
- Initialized projects may miss updated artifact-policy rules unless migration metadata surfaces template drift.
- Publishing must respect release_publish execution policy and use gh/GitHub API transport.

## Rollback

Revert the task-specific changes.
