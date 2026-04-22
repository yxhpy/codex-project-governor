# Clean Reinstall Policy

## Purpose

A plugin reinstall must refresh the user-level plugin installation without copying plugin-global assets into initialized projects.

## User-level reinstall

The user-level plugin directory may be removed and recreated:

```bash
PLUGIN_DIR="$HOME/.codex/plugins/codex-project-governor"
BACKUP_DIR="$PLUGIN_DIR.backup.$(date +%Y%m%d-%H%M%S)"
if [ -d "$PLUGIN_DIR" ]; then mv "$PLUGIN_DIR" "$BACKUP_DIR"; fi
git clone --depth 1 https://github.com/yxhpy/codex-project-governor.git "$PLUGIN_DIR"
python3 "$PLUGIN_DIR/tests/selftest.py" || true
```

## Project refresh

Project refresh must preserve project-owned state and quarantine noise.

Do not run target-project refresh against the Project Governor plugin root itself. The plugin root owns `skills/`, `templates/`, `releases/`, `.codex-plugin/`, and bundled runtime assets.

Do not overwrite:

- `docs/memory/**`
- `docs/decisions/**`
- user-modified `AGENTS.md`
- project-specific conventions

Quarantine, rather than delete, plugin-global assets accidentally copied into a project:

- `.codex/agents/**`
- `.codex/prompts/**`
- `.codex/config.toml`
- `.codex-plugin/**`
- `skills/**`
- `templates/**`
- `managed-assets/**`
- `releases/**`

Default trash location:

```text
.project-governor/trash/<timestamp>/
```
