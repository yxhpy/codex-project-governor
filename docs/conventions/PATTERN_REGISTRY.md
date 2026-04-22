# Pattern Registry

| Pattern | Source file | Rule |
|---|---|---|
| Plugin manifest contract | `.codex-plugin/plugin.json` | Keep plugin identity, version, skill path, MCP path, capabilities, and default prompts aligned with README and tests. |
| Skill folder contract | `skills/<skill>/SKILL.md` | Every skill directory must include `SKILL.md` with frontmatter `name` and `description`. |
| Deterministic CLI helper | `tools/init_project.py`, `skills/*/scripts/*.py` | Use stdlib-only Python CLIs with explicit JSON inputs and outputs where possible. |
| Template payload source | `templates/` | Treat path changes as public behavior changes because `tools/init_project.py` copies this tree into target repositories. |
| Self-test gate | `tests/selftest.py` | Cover manifest shape, required templates, skill metadata, and deterministic helper output contracts. |
| Local marketplace examples | `examples/*-marketplace/marketplace.json` | Keep personal and repo-scoped install examples aligned with README install instructions. |
