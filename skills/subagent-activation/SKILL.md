---
name: subagent-activation
description: Automatically select Project Governor subagents and model settings from task route, risk, quality level, and downstream skill so users do not need to manually specify subagents.
---

# Subagent Activation

## Purpose

Choose which subagents to spawn, when to spawn them, and which model strategy to use.

This skill is invoked automatically by Project Governor workflows after `task-router` and before any skill that benefits from subagents, such as `context-pack-builder`, `pattern-reuse-engine`, `parallel-feature-builder`, `pr-governance-review`, `init-existing-project`, `research-radar`, and `version-researcher`.

## Core rule

The user should not have to learn or list subagent names.

The main Codex agent must:

1. Determine `subagent_mode`: `none`, `optional`, or `required`.
2. Select project-scoped custom agents from `.codex/agents/` when present.
3. Use fast models for read-heavy subagents and stronger models for implementation/risk/final review.
4. Explicitly spawn selected subagents when mode is `required`.
5. Wait for all read-only subagents before implementation.
6. Consolidate subagent findings into the current task artifact.

## Mode policy

- `none`: `micro_patch`, docs-only, or exact single-file copy/style edits. Do not spawn subagents unless route-guard fails.
- `optional`: normal UI or small bugfix work. Spawn subagents only when confidence is low, repository is large, or the target may be shared/global.
- `required`: standard features, risky features, migrations, refactors, dependency upgrades, PR governance, existing-project initialization, and broad research.

## Model strategy

- `gpt-5.4-mini` with low/medium reasoning: fast read-only scouting, context search, pattern reuse, docs/memory review, and test planning.
- `gpt-5.4` with medium/high reasoning: implementation writing, risk review, architecture review, dependency/security review, repair, and final quality review.
- `gpt-5.3-codex-spark` may be used only when the user has access and explicitly prioritizes near-instant text-only iteration.

## Deterministic helper

```bash
python3 skills/subagent-activation/scripts/select_subagents.py examples/subagent-activation-standard-feature.json
```

The helper returns selected agents, recommended models, explicit spawn instructions, and skipped agents.

## Output

Return:

- subagent mode
- selected agents
- skipped agents
- model strategy
- explicit spawn instruction block
- wait/consolidation rules
- reason for any skipped subagents
