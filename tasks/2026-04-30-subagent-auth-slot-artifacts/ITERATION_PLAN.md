<!-- generated_from: iteration_plan_v1; source: ITERATION_PLAN.slots.json; revision: 3 -->
# Iteration Plan: Subagent Authorization and Slot Artifact Workflow

## User request

Investigate and solve two independent issues: why actual projects require explicit authorization before using subagents, and why agents still hand-create plan Markdown even though fixed template content can be rendered deterministically.

## Existing behavior

- Project Governor selects subagent mode and agent names automatically, but host runtimes may still require explicit user authorization before a spawn tool can be used.
- The default clean initialization profile intentionally skips plugin-global .codex/agents, .codex/prompts, and .codex/config.toml assets unless legacy-full is requested.
- Iteration planning already supports ITERATION_PLAN.slots.json plus tools/render_governance_artifact.py, but some entrypoint rules and examples still mention creating ITERATION_PLAN.md directly.
- tools/update_governance_artifact.py can update slots and re-render Markdown, but there is no small helper to create the initial slot artifact skeleton.

## Existing patterns to reuse

| Pattern | Source file | How it will be reused |
| --- | --- | --- |
| Deterministic subagent selection output | skills/subagent-activation/scripts/select_subagents.py | Add an authorization status object without changing existing selected_agents or mode fields. |
| GPT runtime planner JSON contract | skills/gpt55-auto-orchestrator/scripts/select_runtime_plan.py | Surface whether selected subagents still need host-runtime user authorization. |
| Generated governance artifacts rendered from structured slots | tools/render_governance_artifact.py | Add a small initializer helper that writes initial slots and optionally renders Markdown. |
| Standard-library unittest coverage for deterministic helpers | tests/test_governance_artifact_renderer.py and tests/test_subagent_activation.py | Extend targeted tests for the new authorization and artifact-creation behavior. |

## Files expected to change

- skills/subagent-activation/scripts/select_subagents.py: Report host-runtime subagent authorization status.
- skills/gpt55-auto-orchestrator/scripts/select_runtime_plan.py: Expose authorization status in orchestration plans.
- tools/new_governance_artifact.py: Create initial generated-artifact slot files without model-authored Markdown templates.
- skills/*/SKILL.md, docs, README, templates/AGENTS.md: Clarify explicit subagent authorization and slot-first artifact creation rules.
- tests/test_subagent_activation.py, tests/test_gpt55_auto_orchestration.py, tests/test_governance_artifact_renderer.py: Cover the deterministic helper contract changes.
- .codex-plugin/plugin.json: Include the standard subagent consent sentence in the compact Harness default prompt.
- templates/.project-governor/runtime/GPT55_RUNTIME_MODE.json and managed-assets/runtime/GPT55_AUTO_ORCHESTRATION_POLICY.md: Make host-runtime subagent authorization explicit in runtime policy.
- docs/memory/PROJECT_MEMORY.md and docs/memory/RISK_REGISTER.md: Record the durable fact and risk for future sessions.

## Files not to change

- Do not change application code because this repository is a plugin/template bundle.
- Do not change package manifests or add dependencies.
- Do not remove legacy-full initialization support.
- Do not change existing JSON fields in deterministic helper outputs except by adding backward-compatible fields.

## New files

| File | Why existing files cannot cover it |
| --- | --- |
| tools/new_governance_artifact.py | Existing renderer requires a slot file to already exist; a small dependency-free initializer avoids model-generated fixed Markdown and creates the source slots deterministically. |
| tasks/2026-04-30-subagent-auth-slot-artifacts/ITERATION_PLAN.slots.json | The repository requires a task plan for non-trivial implementation; the slot file is the source of truth for the rendered plan. |
| tasks/2026-04-30-subagent-auth-slot-artifacts/{ARTIFACT_CHANGES.jsonl,ITERATION_PLAN.patch*.json,QUALITY_GATE_INPUT.json,QUALITY_REPORT.md} | Task-local evidence files document the slot update history, quality-gate input, and verification result for this non-trivial implementation. |

## Dependencies

No new dependencies expected unless explicitly approved.

## Tests

- python3 tests/test_subagent_activation.py
- python3 tests/test_gpt55_auto_orchestration.py
- python3 tests/test_governance_artifact_renderer.py
- python3 -m compileall tools skills tests
- python3 tests/selftest.py
- python3 skills/quality-gate/scripts/run_quality_gate.py tasks/2026-04-30-subagent-auth-slot-artifacts/QUALITY_GATE_INPUT.json
- python3 tests/test_harness_v6.py
- python3 tests/test_claude_code_compat.py
- git diff --check

## Risks

- Changing deterministic helper output shapes could surprise consumers; keep changes additive and document them in API_CONTRACTS.md.
- Overstating automatic subagent behavior could conflict with host-level Codex authorization rules; docs must say selection is automatic but spawning follows host policy.
- A new artifact initializer could overlap with existing render/update tools; keep it a thin wrapper around the same registry and renderer.

## Rollback

Revert the task-specific script, docs, tests, and generated task-plan files.

## Revision history

- r2: Implementation added default prompt consent and memory evidence updates after confirming host-runtime authorization is part of the actual project entrypoint.
- r3: Record task-local quality and evidence artifacts plus the final verification commands.
