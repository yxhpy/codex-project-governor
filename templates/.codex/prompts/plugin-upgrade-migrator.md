Use @project-governor plugin-upgrade-migrator.

Upgrade Project Governor safely.

Rules:
- Show what is new before applying anything.
- Do not overwrite user-modified project files.
- Use feature matrix and migrations metadata.
- Generate an upgrade plan.
- Apply only safe add-if-missing or unchanged-file operations.
- Leave memory files append-only and decision files untouched.
- Report conflicts and manual review items.
