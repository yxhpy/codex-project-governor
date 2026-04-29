---
name: pg-doctor
description: Diagnose Project Governor install shape, context freshness, state files, evidence gates, and Claude Code adapter readiness.
argument-hint: "[optional focus]"
disable-model-invocation: true
allowed-tools: Bash(python3 *) Bash(claude plugin validate *) Read Grep Glob
---

Run Project Governor diagnostics for the current project.

Start with:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/harness-doctor/scripts/doctor.py" --project . --execution-readiness
```

When validating this plugin repository itself, also run:

```bash
claude plugin validate "${CLAUDE_PLUGIN_ROOT}"
```

Report blockers, warnings, and closest verified substitute if a command cannot run.
