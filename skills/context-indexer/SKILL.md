---
name: context-indexer
description: Build and query a compact project context index so Codex can avoid reading all initialization docs in every session.
---

# Context Indexer

## Purpose

Replace repeated full-document session starts with a small project index and task-specific context retrieval.

Use this skill automatically before `context-pack-builder`, `parallel-feature-builder`, `research-radar`, `upgrade-advisor`, and `design-md-governor` when the project has a `.project-governor/` directory.

## Project-owned outputs

This skill writes only project-owned runtime state:

```text
.project-governor/context/CONTEXT_INDEX.json
.project-governor/context/SESSION_BRIEF.md
.project-governor/context/INDEX_REPORT.json
```

It does not copy plugin-global assets into the project.

## Process

1. Build or refresh `CONTEXT_INDEX.json` when missing or stale.
2. Build `SESSION_BRIEF.md` as a compact startup document.
3. Query the index for the user's request.
4. Read only the returned files before implementation.
5. Escalate to broader scanning only when the index is insufficient.
6. For memory/history questions, use `--memory-search` so retrieval stays on governed project memory, decisions, tasks, release notes, and state files instead of raw chat transcripts.

## Deterministic helpers

```bash
python3 skills/context-indexer/scripts/build_context_index.py --project . --write
python3 skills/context-indexer/scripts/query_context_index.py --project . --request "dashboard widget"
python3 skills/context-indexer/scripts/query_context_index.py --project . --request "why did we choose Stripe redirect" --memory-search --auto-build
python3 skills/context-indexer/scripts/query_context_index.py --project . --request "checkout decision history" --memory-search --format text
```

## Output

Return a ranked list of files and docs with roles, reasons, and recommended token budget.

Memory search mode is read-only and intentionally searches curated governance artifacts, not raw conversation history. Durable facts still belong in `docs/memory/`, decisions in `docs/decisions/`, and required team rules in `AGENTS.md`.
