# Claude Code Compatibility

Project Governor v6.2.0 ships a Claude Code adapter alongside the existing Codex plugin surface.

## What Is Added

- Claude plugin manifest: `.claude-plugin/plugin.json`
- Claude skill entry: `claude/skills/project-governor/SKILL.md`
- Optional slash-command entries: `claude/commands/pg-*.md`
- Claude subagents: `claude/agents/*.md`
- Claude hook config and script: `claude/hooks/`
- Claude marketplace example: `examples/claude-marketplace/.claude-plugin/marketplace.json`
- Target-project `CLAUDE.md` template that imports `AGENTS.md`

## Install For Claude Code

For local development:

```bash
claude plugin validate .
claude --plugin-dir .
```

For distribution, publish a marketplace repository from `examples/claude-marketplace/.claude-plugin/marketplace.json`, then install with:

```text
/plugin marketplace add <your-marketplace-repo-or-path>
/plugin install codex-project-governor@project-governor-claude-marketplace
```

## Project Initialization

Initialize governance files in a target project:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/tools/init_project.py" --mode existing --target . --json
```

Initialized projects receive both:

- `AGENTS.md` as the cross-agent governance source of truth.
- `CLAUDE.md` as the Claude Code entry point, importing `AGENTS.md` with `@AGENTS.md` and telling Claude Code to apply Project Governor automatically for natural project work.

## Automatic Activation

Normal Claude Code users should not need to type `/pg-*` commands before governed work. The plugin skill and `UserPromptSubmit` hook add Project Governor context for natural coding, testing, review, docs, upgrade, initialization, compatibility, quality, memory, and UI requests.

The bundled `/pg-*` commands remain available as optional shortcuts and diagnostics when a user wants to inspect one workflow stage directly.

## Surface Mapping

| Project Governor | Claude Code |
|---|---|
| `.codex-plugin/plugin.json` | `.claude-plugin/plugin.json` |
| `skills/<name>/SKILL.md` | `claude/skills/project-governor/SKILL.md` plus command wrappers |
| `.codex/prompts/*.md` | `claude/commands/pg-*.md` |
| `.codex/agents/*.toml` | `claude/agents/*.md` |
| `.codex/hooks.json` | `claude/hooks/hooks.json` |
| `.mcp.json` | plugin `mcpServers` reference |
| `AGENTS.md` | `CLAUDE.md` importing `AGENTS.md` |

## Maintenance Rules

- Keep Codex and Claude plugin manifests version-aligned.
- Keep Claude agent names and descriptions aligned with `.codex/agents/*.toml`.
- Do not expose the raw Codex skills directory directly as Claude skills; Claude wrappers reference plugin-root scripts with `${CLAUDE_PLUGIN_ROOT}` so installed cache paths work.
- Keep adapter scripts dependency-free.
- Validate with `claude plugin validate .` before release.
