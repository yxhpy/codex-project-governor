# Plugin Upgrade Policy

Project Governor upgrades must preserve local project customizations.

## Rules

- Do not overwrite initialized project governance files blindly.
- Show new features before applying migrations.
- Use `.project-governor/INSTALL_MANIFEST.json` to distinguish unchanged, modified, missing, and custom files.
- Apply only safe additions or unchanged-file replacements automatically.
- Leave user-modified files for three-way merge or manual review.
- Surface `AGENTS.md` template drift during upgrade planning so newly added mandatory rules are visible to already initialized projects.
- Surface missing required `.project-governor/runtime/*` policy files during upgrade planning so new quality gates can run in already initialized projects.
- Never overwrite `docs/memory/*` or existing `docs/decisions/*`.
- Generate an upgrade plan before applying migrations.
