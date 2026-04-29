---
name: pg-memory
description: Search governed project memory and record session learnings for failed commands, repeated mistakes, stale memory, risks, or open questions.
argument-hint: "<memory query or learning>"
disable-model-invocation: true
allowed-tools: Bash(python3 *) Read Grep Glob
---

Handle Project Governor memory for:

```text
$ARGUMENTS
```

Search governed memory first:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/context-indexer/scripts/query_context_index.py" --project . --request "$ARGUMENTS" --memory-search --auto-build
```

If the user asks to record a learning, or a command failed in this session, use:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/memory-compact/scripts/record_session_learning.py" --help
```

Do not write durable memory without date, status, source, and evidence.
