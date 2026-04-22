# Subagent Activation Policy

## Purpose

Project Governor should select and spawn subagents automatically after project initialization. Users should not need to memorize subagent names, model choices, or delegation prompts.

## Mode policy

| Mode | Use when | Behavior |
|---|---|---|
| `none` | `micro_patch`, high-confidence docs/copy/style edits | Do not spawn subagents. Use direct edit, route-guard, and light quality gate. |
| `optional` | small UI/bugfix/test tasks with uncertainty | Spawn scouts only if confidence is low, target may be shared/global, or context is missing. |
| `required` | standard features, risky tasks, refactors, migrations, upgrades, PR review, initialization, broad research | Spawn selected read-only subagents and wait before implementation. |

## Model routing

- Use `gpt-5.4-mini` for fast read-only scouts, context discovery, pattern reuse, docs/memory review, and test planning.
- Use `gpt-5.4` for implementation writing, risk review, architecture review, dependency/security review, repair, and final quality review.
- Use `gpt-5.3-codex-spark` only when available and explicitly requested for near-instant text-only iteration.

## Write policy

- Read-only subagents must finish before implementation when mode is `required`.
- Only one write agent may modify production code at a time.
- Test writer may modify tests only.
- Repair agent may run only after quality-gate failure and must stay inside the approved change budget.

## Initialization

Project initialization must copy:

- `.codex/config.toml`
- `.codex/agents/*.toml`
- `.codex/prompts/subagent-activation.md`

These files make subagent roles and model choices project-scoped and reusable.
