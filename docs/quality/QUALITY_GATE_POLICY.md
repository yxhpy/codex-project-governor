# Quality Gate Policy

Use one of these gate levels:

- `light`: tiny patches, docs-only changes, and targeted checks.
- `standard`: ordinary features and bug fixes.
- `strict`: auth, payment, security, API, data, migrations, dependency upgrades, and refactors.

Speed never justifies bypassing route guard, tests, weakening assertions, skipping docs, or exceeding the change budget silently.

For coding work, include `engineering-standards-governor` before final `quality-gate` unless the route is docs-only or the quality report explains why no source files were relevant.

Standard and strict gates must treat engineering-standards blockers as quality-gate blockers. In strict mode, unresolved engineering-standards warnings also block until accepted with evidence.
