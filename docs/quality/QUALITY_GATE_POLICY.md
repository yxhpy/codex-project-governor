# Quality Gate Policy

Use one of these gate levels:

- `light`: tiny patches, docs-only changes, and targeted checks.
- `standard`: ordinary features and bug fixes.
- `strict`: auth, payment, security, API, data, migrations, dependency upgrades, and refactors.

Speed never justifies bypassing route guard, tests, weakening assertions, skipping docs, or exceeding the change budget silently.
