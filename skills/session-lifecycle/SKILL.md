---
name: session-lifecycle
description: Start and end Harness v6 sessions by maintaining .project-governor/state, progress logs, stale-session metadata, and evidence handoff information.
---

# Session Lifecycle

Use this skill for all non-trivial routes before implementation and before final response.

Session start:

- creates `.project-governor/state/SESSION.json`
- initializes `FEATURES.json`, `AGENTS.json`, `ISSUES.json`, `QUALITY_SCORE.json`, and `PROGRESS.md`
- records git status and active target files
- records target-file metadata for later collision checks

Session end:

- appends a handoff entry to `PROGRESS.md`
- records evidence path and verification commands
- updates session status

Micro patches and docs-only edits may skip full lifecycle state, but should still record evidence-lite when useful.
