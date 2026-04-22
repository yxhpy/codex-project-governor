---
name: plugin-upgrade-migrator
description: Safely upgrade Project Governor by showing new features, planning migrations, preserving project customizations, and applying only safe operations.
---

# Plugin Upgrade Migrator

## Purpose

Upgrade Project Governor safely after a project has already been initialized.

This skill distinguishes plugin source updates from initialized project governance-file migrations.

## Core rule

Never overwrite initialized project governance files blindly.

Before applying anything, show:

1. installed version
2. target/latest version
3. new features since installed version
4. migrations required
5. safe additions
6. user-modified files
7. append-only memory files
8. conflicts and manual review items
9. recommended action

## Required data

- `CHANGELOG.md`
- `releases/FEATURE_MATRIX.json`
- `releases/MIGRATIONS.json`
- `.project-governor/INSTALL_MANIFEST.json` in the target project when present

## Helpers

```bash
python3 skills/plugin-upgrade-migrator/scripts/inspect_installation.py --project /path/to/project
python3 skills/plugin-upgrade-migrator/scripts/compare_features.py --current-version 0.4.1 --target-version 0.4.3 --feature-matrix releases/FEATURE_MATRIX.json
python3 skills/plugin-upgrade-migrator/scripts/plan_migration.py --project /path/to/project --plugin-root /path/to/codex-project-governor --current-version 0.4.1 --target-version 0.4.3
python3 skills/plugin-upgrade-migrator/scripts/apply_safe_migration.py --plan .project-governor/upgrade/0.4.1-to-0.4.3/UPGRADE_PLAN.json --apply
```

## File policies

| File class | Policy |
|---|---|
| plugin source files | replace through git/patch |
| templates | update in plugin only; do not auto-overwrite project copies |
| `AGENTS.md` | three-way merge/manual review |
| `docs/conventions/*.md` | three-way merge/manual review |
| `docs/quality/*.md` | add-if-missing; merge if modified |
| `docs/memory/*.md` | append-only; never overwrite |
| `docs/decisions/*.md` | never overwrite existing decisions |
| `.codex/agents/*.toml` | add-if-missing; merge by agent name if modified |
| `.codex/config.toml` | merge by section/key; never replace blindly |
| `.codex/prompts/*.md` | add-if-missing or three-way merge |
| `tasks/_template/*.md` | add-if-missing or three-way merge |

## Output

Return an upgrade panel with feature diff, migration plan, safe operations, manual-review items, and next choices.


## Project hygiene preflight

Before planning migrations, run `project-hygiene-doctor` when the target project contains `.codex/agents/`, `.codex/prompts/`, `.codex/config.toml`, `.codex-plugin/`, `skills/`, `templates/`, `releases/`, or Project Governor bundled examples/tests. These may indicate plugin-global assets were initialized into a project.
