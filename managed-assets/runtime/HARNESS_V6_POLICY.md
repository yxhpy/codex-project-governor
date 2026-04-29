# Harness v6 Runtime Policy

- Use `task-router` as the single route source of truth.
- Use `gpt55-auto-orchestrator` only for runtime planning.
- Use DOCS_MANIFEST and context-index v2 section ranges before reading large docs.
- Use session lifecycle for non-trivial implementation routes.
- Use git-derived route guard facts before quality gate.
- Use engineering standards checks for coding work before quality gate.
- Use evidence manifests before merge readiness.
- Do not copy plugin-global assets into target projects.
