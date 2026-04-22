---
name: project-hygiene-doctor
description: Detect and fix Project Governor plugin assets that were incorrectly initialized into a target project, keeping only project-owned governance files and quarantining safe-to-remove global artifacts.
---

# Project Hygiene Doctor

## Purpose

Keep initialized projects clean.

A target project should contain its own governance rules, docs, task templates, memory files, and install ledger. Plugin source files, bundled skills, release metadata, examples, tests, and default `.codex` runtime assets should remain in the plugin installation unless the project explicitly opts into local overrides.

## Project-owned files

Normally keep these in the target project:

- `AGENTS.md`
- `.project-governor/INSTALL_MANIFEST.json`
- `docs/project/*`
- `docs/conventions/*`
- `docs/quality/*`
- `docs/memory/*`
- `docs/decisions/*`
- `docs/research/*` when project-specific
- `docs/upgrades/*` when project-specific
- `tasks/_template/*`
- `.codex/hooks.json`
- `.codex/rules/*`
- `.codex/hooks/*`

## Plugin-owned files

Normally keep these in the plugin installation:

- `.codex-plugin/*`
- `skills/*`
- `templates/*`
- `releases/*`
- Project Governor bundled `examples/*` and `tests/*` when they were copied from the plugin, not ordinary project examples or application tests.
- default `.codex/agents/*.toml`
- default `.codex/prompts/*.md`
- default `.codex/config.toml`

## Safety rule

Do not delete user files blindly. The default action is diagnosis only. When `--apply` is used, safe generated global assets are quarantined under `.project-governor/hygiene-quarantine/` instead of being permanently deleted.

## Helper

```bash
python3 skills/project-hygiene-doctor/scripts/inspect_project_hygiene.py \
  --project /path/to/project \
  --plugin-root /path/to/codex-project-governor
```

Apply safe quarantine:

```bash
python3 skills/project-hygiene-doctor/scripts/inspect_project_hygiene.py \
  --project /path/to/project \
  --plugin-root /path/to/codex-project-governor \
  --apply
```

Run this before `plugin-upgrade-migrator` if the project has `.codex/agents`, `.codex/prompts`, `.codex/config.toml`, or plugin-looking folders.
