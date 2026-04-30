# Quality Gate Policy

Use `light`, `standard`, or `strict` gates. Speed never justifies bypassing route guard, tests, weakening assertions, skipping docs, or exceeding change budget silently.

Fast-route artifact policy:

- `micro_patch`: no task plan, test plan, pattern reuse plan, evidence manifest, session lifecycle, or merge-readiness artifact is required. Require direct edit, route guard, and a light quality gate.
- `tiny_patch`: no task plan, test plan, pattern reuse plan, evidence manifest, session lifecycle, context pack, or subagent audit is required. Require direct edit, route guard, diff-scoped engineering standards when code changed, a light quality gate, merge-readiness, and inline final-response evidence.
- `standard` and `strict`: use file-backed plans, test planning, reuse/evidence artifacts, and merge-readiness according to route requirements.

For coding work, include `engineering-standards-governor` before final `quality-gate` unless the route is `micro_patch`, docs-only, or the quality report explains why no source files were relevant. `tiny_patch` uses diff-scoped engineering standards.

Standard and strict gates must treat engineering-standards blockers as quality-gate blockers. In strict mode, unresolved engineering-standards warnings also block until accepted with evidence.

When a task includes a user-selected execution tool or forbidden transport, include an execution policy check before final response. Add `execution_context` to the quality-gate input, or run `skills/quality-gate/scripts/check_execution_policy.py` directly against the recorded commands.

Default initialized projects include `.project-governor/runtime/EXECUTION_POLICY.json`. The `release_publish` context requires a `gh release` or `gh api` command and blocks plain `git push` unless `execution_policy_override_approved` is explicitly true.
