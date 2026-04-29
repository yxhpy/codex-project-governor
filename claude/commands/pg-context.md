---
name: pg-context
description: Build or query the Project Governor context index and governed memory search for the current project.
argument-hint: "<query>"
disable-model-invocation: true
allowed-tools: Bash(python3 *) Read Grep Glob
---

Use Project Governor context navigation for:

```text
$ARGUMENTS
```

Run a context query first:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/context-indexer/scripts/query_context_index.py" --project . --request "$ARGUMENTS" --auto-build
```

If the user asks about prior failures, decisions, stale memory, or history, also run:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/context-indexer/scripts/query_context_index.py" --project . --request "$ARGUMENTS" --memory-search --auto-build
```

Prefer `recommended_sections` line ranges before opening full documents.
