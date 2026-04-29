# Quality Gate Policy

Use `light`, `standard`, or `strict` gates. Speed never justifies bypassing route guard, tests, weakening assertions, skipping docs, or exceeding change budget silently.

For coding work, include `engineering-standards-governor` before final `quality-gate` unless the route is docs-only or the quality report explains why no source files were relevant.

Standard and strict gates must treat engineering-standards blockers as quality-gate blockers. In strict mode, unresolved engineering-standards warnings also block until accepted with evidence.
