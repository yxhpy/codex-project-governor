# Project Hygiene Policy

A target project initialized by Project Governor should contain project-owned governance files, not the plugin's global runtime implementation assets.

## Project-owned assets

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

## Plugin-owned assets

- `.codex-plugin/*`
- `skills/*`
- `templates/*`
- `releases/*`
- Project Governor bundled `examples/*` and `tests/*` when they were copied from the plugin, not ordinary project examples or application tests.
- default `.codex/agents/*.toml`
- default `.codex/prompts/*.md`
- default `.codex/config.toml`

## Cleanup rules

- Do not delete user customizations.
- Quarantine safe generated global assets instead of permanently deleting them.
- Never overwrite or remove memory and decision files.
- Treat untracked `.codex/agents`, prompts, and config files as possible project overrides and require manual review.
