# Quality Gate Policy

Use one of these gate levels:

- `light`: tiny patches, docs-only changes, and targeted checks.
- `standard`: ordinary features and bug fixes.
- `strict`: auth, payment, security, API, data, migrations, dependency upgrades, and refactors.

Speed never justifies bypassing route guard, tests, weakening assertions, skipping docs, or exceeding the change budget silently.

For coding work, include `engineering-standards-governor` before final `quality-gate` unless the route is docs-only or the quality report explains why no source files were relevant.

Standard and strict gates must treat engineering-standards blockers as quality-gate blockers. In strict mode, unresolved engineering-standards warnings also block until accepted with evidence.

When a task includes a user-selected execution tool or forbidden transport, include an execution policy check before final response. Add `execution_context` to the quality-gate input, or run `skills/quality-gate/scripts/check_execution_policy.py` directly against the recorded commands.

Default initialized projects include `.project-governor/runtime/EXECUTION_POLICY.json`. The `release_publish` context requires a `gh release` or `gh api` command and blocks plain `git push` unless `execution_policy_override_approved` is explicitly true.
