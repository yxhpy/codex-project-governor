---
name: pg-route
description: Classify a request with Project Governor task-router and retrieve compact project context before implementation.
argument-hint: "<request>"
disable-model-invocation: true
allowed-tools: Bash(python3 *) Read Grep Glob
---

Classify this request and retrieve compact context:

```text
$ARGUMENTS
```

Run:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/task-router/scripts/classify_task.py" --request "$ARGUMENTS"
python3 "${CLAUDE_PLUGIN_ROOT}/skills/context-indexer/scripts/query_context_index.py" --project . --request "$ARGUMENTS" --auto-build
```

Return the route, lane, quality level, change budget, required skills, recommended sections, and whether full documents are needed.
