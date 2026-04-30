# Subagent Activation Policy

## Purpose

Project Governor should select subagents automatically after project initialization. Users should not need to memorize subagent names, model choices, or delegation prompts.

Actual spawning remains subject to the active host runtime. If Codex, Claude Code, or another runtime requires explicit user authorization before subagents can be spawned, Project Governor must surface that status and ask once for consent instead of silently treating selection as permission.

## Mode policy

| Mode | Use when | Behavior |
|---|---|---|
| `none` | `micro_patch`, high-confidence docs/copy/style edits | Do not spawn subagents. Use direct edit, route-guard, and light quality gate. |
| `optional` | small UI/bugfix/test tasks with uncertainty | Spawn scouts only if confidence is low, target may be shared/global, or context is missing. |
| `required` | standard features, risky tasks, refactors, migrations, upgrades, PR review, initialization, broad research | Spawn selected read-only subagents and wait before implementation. |

## Authorization Status

Deterministic planners return `subagent_authorization`:

- `not_required`: no subagents are selected.
- `authorized`: the request or input explicitly authorized Project Governor to use selected subagents.
- `needs_explicit_user_authorization`: subagents are selected, but the host runtime may require user consent before any spawn tool is called.

Accepted explicit inputs include `subagent_authorized=true`, `user_authorized_subagents=true`, `allow_subagents=true`, or the prompt phrase `I authorize Project Governor to use selected subagents for this task.`

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

Clean project initialization does not copy plugin-global `.codex/agents`, `.codex/prompts`, or `.codex/config.toml` into target repositories. Those assets remain plugin-owned unless the user explicitly requests `--profile legacy-full`.

When project-scoped `.codex/agents/` or Claude Code plugin agents are present, use them. Otherwise use the installed plugin's available agent definitions and deterministic selector output.
