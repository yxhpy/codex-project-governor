---
name: pg-design
description: Run Project Governor DESIGN.md UI/frontend preflight and explain whether full-service or basic mode is configured.
argument-hint: "<ui task>"
disable-model-invocation: true
allowed-tools: Bash(python3 *) Read Grep Glob
---

Prepare UI/frontend work for:

```text
$ARGUMENTS
```

Run:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/design-md-aesthetic-governor/scripts/design_env_check.py" --project .
python3 "${CLAUDE_PLUGIN_ROOT}/skills/design-md-aesthetic-governor/scripts/design_md_gate.py" preflight --task "$ARGUMENTS"
```

Do not edit UI files until `DESIGN.md` exists and the read proof matches the current file hash. `DESIGN_BASIC_MODE=1` may come from shell environment variables or project-root `.env-design`.
