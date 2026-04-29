---
name: pg-init
description: Initialize Project Governor governance files in the current Claude Code project without modifying application code.
argument-hint: "[existing|empty]"
disable-model-invocation: true
allowed-tools: Bash(python3 *)
---

Initialize Project Governor in the current project.

Use mode `existing` unless the user explicitly passed `empty`.

Run:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/tools/init_project.py" --mode existing --target . --json
```

After it runs, report created, preserved, skipped application files, skipped plugin-global files, and the install manifest path. Do not modify application code.
