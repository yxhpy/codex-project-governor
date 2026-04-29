---
name: pg-quality
description: Run Project Governor engineering standards, route guard, quality gate, and merge-readiness checks for the current change.
argument-hint: "[route or request]"
disable-model-invocation: true
allowed-tools: Bash(python3 *) Bash(git diff *) Bash(git status *) Read Grep Glob
---

Check the current change with Project Governor quality gates.

Run the narrowest relevant checks first:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/engineering-standards-governor/scripts/check_engineering_standards.py" --project .
python3 "${CLAUDE_PLUGIN_ROOT}/skills/harness-doctor/scripts/doctor.py" --project . --execution-readiness
```

If a task route or evidence payload exists, validate route guard, evidence, quality gate, and merge readiness using the matching scripts under `${CLAUDE_PLUGIN_ROOT}/skills/`.

Report blockers before summaries.
