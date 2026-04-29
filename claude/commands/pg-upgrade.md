---
name: pg-upgrade
description: Plan Project Governor or dependency upgrades in advisory mode before changing versions, manifests, lockfiles, or governance assets.
argument-hint: "<upgrade request>"
disable-model-invocation: true
allowed-tools: Bash(python3 *) Read Grep Glob
---

Analyze this upgrade request in advisory mode:

```text
$ARGUMENTS
```

Read the relevant workflow files from:

- `${CLAUDE_PLUGIN_ROOT}/skills/version-researcher/SKILL.md`
- `${CLAUDE_PLUGIN_ROOT}/skills/upgrade-advisor/SKILL.md`
- `${CLAUDE_PLUGIN_ROOT}/skills/plugin-upgrade-migrator/SKILL.md`

Do not edit manifests, lockfiles, governance files, or application code until the user selects an upgrade path.
