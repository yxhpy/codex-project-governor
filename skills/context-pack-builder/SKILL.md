---
name: context-pack-builder
description: Build a minimal task-specific context pack using automatic subagent activation when needed so Codex can implement faster without repeatedly rediscovering the repository.
---

# Context Pack Builder

Use after `task-router` and before implementation.

## Required subagents

The user should not have to request context scouts manually.

Run `subagent-activation` with workflow `context-pack-builder` unless the route is `micro_patch` with high confidence. For `micro_patch`, skip subagents and read only the explicit target file plus immediate local context.

When subagents are selected, explicitly spawn the selected read-only scouts, wait for all of them, and consolidate their findings into `tasks/<date>-<slug>/CONTEXT_PACK.md`.

## Process

1. Read task route and project conventions.
2. If subagent mode is optional or required, run selected read-only scouts.
3. Search adjacent code, tests, docs, APIs, and components.
4. Mark files as `must_read`, `maybe_read`, or `avoid`.
5. Create `tasks/<date>-<slug>/CONTEXT_PACK.md`.

## Output

Return relevant files, selected/skipped subagents, tests, docs, existing behavior, required patterns, avoid list, and risk notes.
