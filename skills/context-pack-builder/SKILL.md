---
name: context-pack-builder
description: Build a minimal task-specific context pack so Codex and subagents can implement faster without repeatedly rediscovering the repository.
---

# Context Pack Builder

Use after `task-router` and before implementation.

## Required subagents

For non-trivial tasks, spawn read-only subagents: `context-scout`, `test-scout`, `docs-scout`, and `api-scout` when applicable.

## Process

1. Read task route and project conventions.
2. Search adjacent code, tests, docs, APIs, and components.
3. Mark files as `must_read`, `maybe_read`, or `avoid`.
4. Create `tasks/<date>-<slug>/CONTEXT_PACK.md`.

## Output

Return relevant files, tests, docs, existing behavior, required patterns, avoid list, and risk notes.
