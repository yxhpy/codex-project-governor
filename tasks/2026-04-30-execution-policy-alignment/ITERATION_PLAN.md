<!-- generated_from: iteration_plan_v1; source: ITERATION_PLAN.slots.json; revision: 1 -->
# Execution Policy Alignment

## User request

Deeply audit risks where new Project Governor features may not be applied in real sessions, especially cases where user-specified execution tools such as gh release publishing are ignored and sessions fall back to conflicting git commands.

## Existing behavior

- Session-learning memory can record failed release commands in .project-governor/state/COMMAND_LEARNINGS.json, but quality-gate does not turn those lessons or explicit user tool choices into blocking command policy.
- The runtime template only records model/context/automation/hygiene policy; it has no project-owned execution policy for release, deploy, publish, or package-manager constraints.
- The release example already appeared in local command learnings: gh/API was the intended publishing path, while later sessions still attempted git push.

## Existing patterns to reuse

| Pattern | Source file | How it will be reused |
| --- | --- | --- |
| Reuse quality-gate's existing JSON-in/JSON-out blocking-finding model. |  |  |
| Reuse templates/.project-governor/runtime as the project-owned location copied into initialized repositories. |  |  |
| Reuse standard-library deterministic scripts and existing unittest subprocess patterns. |  |  |

## Files expected to change

- Add a deterministic execution policy checker under skills/quality-gate/scripts.
- Teach run_quality_gate.py to run the checker when an execution policy context is present.
- Add a default runtime policy that blocks git-push release publishing unless explicitly overridden and requires a gh release/API command.
- Document that user-specified execution tools and forbidden transports must be captured in the task plan/evidence and checked before final response.

## Files not to change

- .codex-plugin/plugin.json
- .claude-plugin/plugin.json
- tools/init_project.py

## New files

| File | Why existing files cannot cover it |
| --- | --- |
| skills/quality-gate/scripts/check_execution_policy.py |  |
| templates/.project-governor/runtime/EXECUTION_POLICY.json |  |
| tests/test_execution_policy.py |  |

## Dependencies

No new dependencies expected unless explicitly approved.

## Tests

- python3 tests/test_execution_policy.py
- python3 tests/test_harness_v6.py
- python3 tests/selftest.py
- python3 -m compileall tools skills tests

## Risks

- Over-broad command blocking could stop legitimate git-only releases, so the default policy is scoped to execution_context=release_publish and supports explicit override.
- Docs-only reminders would not fix the new-session risk, so the quality gate must consume the policy deterministically.

## Rollback

Revert the task-specific changes.
