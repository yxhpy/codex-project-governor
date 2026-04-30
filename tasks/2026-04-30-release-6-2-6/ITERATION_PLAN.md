<!-- generated_from: iteration_plan_v1; source: ITERATION_PLAN.slots.json; revision: 1 -->
# Release 6.2.6

## User request

Publish the Codex and Claude automatic Project Governor entrypoint compatibility work as a new patch release.

## Existing behavior

- Current public metadata and install instructions point at version 6.2.5.
- The completed compatibility work makes Project Governor activate automatically for natural Codex and Claude project requests instead of requiring visible /pg-* or skill invocations.
- The completed validation matrix covers Codex deterministic tests, Codex CLI smoke tests, Claude plugin validation, Claude/DeepSeek CLI smoke tests, and the ai-tryon downstream fixture.
- Release metadata is tracked across plugin manifests, README files, release notes, feature matrix, tests, memory, roadmap, and upgrade register.

## Existing patterns to reuse

| Pattern | Source file | How it will be reused |
| --- | --- | --- |
| Patch release metadata update | tasks/2026-04-30-release-6-2-5/ITERATION_PLAN.slots.json | Reuse the manifest, release note, feature matrix, upgrade register, README, tests, quality evidence, execution-policy, and gh/API publishing pattern. |
| Upgrade advisory gate | skills/upgrade-advisor/scripts/analyze_upgrade_candidates.py | Record 6.2.5 to 6.2.6 as a low-risk patch release with no dependency or runtime service change. |
| Template drift migration | skills/plugin-upgrade-migrator/scripts/plan_migration.py | Surface CLAUDE.md template drift to initialized projects through existing rule-template drift planning. |

## Files expected to change

- Bump Codex and Claude plugin metadata from 6.2.5 to 6.2.6.
- Add releases/6.2.6.md and update releases/FEATURE_MATRIX.json.
- Update README, Chinese README, charter, roadmap, project memory, marketplace example, tests, and upgrade register version references.
- Include the already completed automatic-entrypoint compatibility task evidence in release validation.
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
| releases/6.2.6.md | Each public release has a dedicated release note file. |
| tasks/2026-04-30-release-6-2-6/UPGRADE_ADVISORY_INPUT.json | Release version bumps require an upgrade-advisor evidence input. |
| tasks/2026-04-30-release-6-2-6/EXECUTION_POLICY_INPUT.json | Release publishing must prove gh/GitHub API transport and block plain git push. |
| tasks/2026-04-30-release-6-2-6/QUALITY_GATE_INPUT.json | Quality-gate requires a stable task-local input that records checks and execution context. |
| tasks/2026-04-30-release-6-2-6/QUALITY_REPORT.md | The release needs a concise human-readable validation ledger. |

## Dependencies

No new dependencies expected unless explicitly approved.

## Tests

- python3 skills/upgrade-advisor/scripts/analyze_upgrade_candidates.py tasks/2026-04-30-release-6-2-6/UPGRADE_ADVISORY_INPUT.json
- python3 tests/test_claude_code_compat.py
- python3 tests/test_plugin_upgrade_migrator.py
- python3 tests/test_harness_v6.py
- python3 tests/selftest.py
- python3 -m unittest discover -s tests -p 'test*.py'
- python3 -m compileall tools skills tests claude
- claude plugin validate .
- claude plugin validate examples/claude-marketplace
- codex --ask-for-approval never exec --cd /Users/yxhpy/Desktop/project/codex-project-governor --sandbox read-only --ephemeral --json <natural prompt>
- python3 skills/engineering-standards-governor/scripts/check_engineering_standards.py --project . --scope diff --diff-base HEAD --format json
- python3 skills/quality-gate/scripts/check_execution_policy.py tasks/2026-04-30-release-6-2-6/EXECUTION_POLICY_INPUT.json
- python3 skills/quality-gate/scripts/run_quality_gate.py tasks/2026-04-30-release-6-2-6/QUALITY_GATE_INPUT.json
- git diff --check

## Risks

- Version strings can drift across manifests, README files, marketplace examples, tests, feature matrix, memory, and roadmap.
- Already initialized projects may keep older CLAUDE.md wording until plugin-upgrade-migrator surfaces the safe template update.
- Publishing must respect release_publish execution policy and use gh/GitHub API transport.
- The working tree includes both the compatibility implementation task and release metadata; quality-gate evidence must cover both.

## Rollback

Revert the task-specific changes.
