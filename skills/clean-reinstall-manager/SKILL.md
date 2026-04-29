---
name: clean-reinstall-manager
description: Generate user-level plugin install/update/reinstall instructions, stop outside project roots to list governed projects, and cleanly refresh initialized project governance files without copying plugin-global assets.
---

# Clean Reinstall Manager

## Purpose

Repair a Project Governor installation or initialized project without polluting target repositories with plugin-level assets.

Use this skill when the user asks to:

- install or update the user-level Project Governor Git checkout used by a local marketplace entry
- completely uninstall and reinstall the plugin at the user level
- find all projects that were initialized with Project Governor
- run a clean re-initialization for selected projects
- apply the latest project-owned runtime mode and context index state
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

### 1. User-level install/update or full reinstall plan

Always provide a safe install/update or reinstall plan. Do not execute destructive removal unless the user explicitly asks and the environment is appropriate.

For the common local marketplace case, update the Git checkout and ensure the marketplace entry exists:

```bash
python3 tools/install_or_update_user_plugin.py --ref v6.0.6 --apply
```

This keeps the marketplace source as `local`; it updates the Git checkout that the local entry points at. Built-in Git marketplace upgrade commands do not fetch this local checkout.

For full replacement instructions, use:

```bash
python3 skills/clean-reinstall-manager/scripts/generate_reinstall_instructions.py --ref v6.0.6
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

### 5. Latest runtime mode

Use this for v0.5.0 GPT-5.5 auto orchestration state. It writes only project-owned files under `.project-governor/runtime/` and `.project-governor/context/`.

```bash
python3 skills/clean-reinstall-manager/scripts/apply_latest_runtime_mode.py \
  --path . \
  --plugin-root /path/to/codex-project-governor
```

Add `--apply` only when the user has selected the runtime-mode update path.

## Output

Return:

- full reinstall commands
- user-level install/update commands when the issue is a local marketplace checkout
- current directory classification
- discovered projects if outside a project
- refresh plan if inside a project
- latest runtime-mode plan or apply result
- safe operations
- manual-review operations
- trash/quarantine path
- next user choices
