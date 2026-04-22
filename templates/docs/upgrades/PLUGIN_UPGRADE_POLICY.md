# Plugin Upgrade Policy

Project Governor upgrades must preserve local project customizations.

## Rules

- Do not overwrite initialized project governance files blindly.
- Show new features before applying migrations.
- Use `.project-governor/INSTALL_MANIFEST.json` to distinguish unchanged, modified, missing, and custom files.
- Apply only safe additions or unchanged-file replacements automatically.
- Leave user-modified files for three-way merge or manual review.
- Never overwrite `docs/memory/*` or existing `docs/decisions/*`.
- Generate an upgrade plan before applying migrations.
