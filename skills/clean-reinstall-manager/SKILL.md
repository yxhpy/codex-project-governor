---
name: clean-reinstall-manager
description: Generate full user-level plugin reinstall instructions, stop outside project roots to list governed projects, and cleanly refresh initialized project governance files without copying plugin-global assets.
---

# Clean Reinstall Manager

## Purpose

Repair a Project Governor installation or initialized project without polluting target repositories with plugin-level assets.

Use this skill when the user asks to:

- completely uninstall and reinstall the plugin at the user level
- find all projects that were initialized with Project Governor
- run a clean re-initialization for selected projects
- regenerate `AGENTS.md` and governance docs while preserving project-specific edits
- move noisy generated/plugin-global assets into a quarantine trash instead of deleting them

## Core rule

Do not copy plugin-global assets into target projects by default.

If the requested project path is the Project Governor plugin root, stop and do not run project-refresh or quarantine operations against the plugin source tree.

Project directories should contain project-owned state only:

- `AGENTS.md`
- `.project-governor/**`
- `docs/project/**`
- `docs/memory/**`
- `docs/decisions/**`
- `docs/conventions/**`
- `docs/research/**` when the project owns research notes
- `docs/upgrades/**` when the project owns upgrade decisions
- `tasks/_template/**`
- `.codex/rules/**` and `.codex/hooks/**` when project-owned governance requires deterministic checks

Plugin-level runtime assets should remain in the plugin installation unless explicitly requested:

- `.codex/agents/**`
- `.codex/prompts/**`
- `.codex/config.toml`
- `.codex-plugin/**`
- `skills/**`
- `templates/**`
- `managed-assets/**`
- `releases/**`
- bundled plugin `examples/**` and `tests/**`

## Workflow

### 1. User-level full reinstall plan

Always provide a safe reinstall plan. Do not execute destructive removal unless the user explicitly asks and the environment is appropriate.

Use:

```bash
python3 skills/clean-reinstall-manager/scripts/generate_reinstall_instructions.py
```

### 2. If not in a Project Governor project

Stop. Do not modify the current directory.

List discovered governed projects and offer choices:

- ignore
- all
- selected project paths

Use:

```bash
python3 skills/clean-reinstall-manager/scripts/discover_governed_projects.py --root "$HOME"
```

### 3. If in a Project Governor project

Generate a refresh plan:

```bash
python3 skills/clean-reinstall-manager/scripts/refresh_project_governance.py \
  --project . \
  --plugin-root /path/to/codex-project-governor
```

The refresh plan should:

- re-run clean initialization from `templates/`
- add missing project-owned governance templates
- preserve existing project customizations
- merge missing `AGENTS.md` sections when safe
- move plugin-global noise to `.project-governor/trash/<timestamp>/`
- never overwrite memory or decision files
- never delete without explicit `--delete-trash`

### 4. Orchestrated mode

Use:

```bash
python3 skills/clean-reinstall-manager/scripts/clean_reinstall_orchestrator.py \
  --path . \
  --plugin-root /path/to/codex-project-governor
```

If `--path` is not a governed project, it returns discovered projects and exits without modifying anything.

## Output

Return:

- full reinstall commands
- current directory classification
- discovered projects if outside a project
- refresh plan if inside a project
- safe operations
- manual-review operations
- trash/quarantine path
- next user choices
