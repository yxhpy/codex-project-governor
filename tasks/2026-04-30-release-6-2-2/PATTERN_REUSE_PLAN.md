# Pattern Reuse Plan

## Existing Patterns Reused

- Reuse the `6.2.1` release workflow: manifests, release note, feature matrix, upgrade register, README install refs, and version contract tests.
- Reuse existing no-migration patch metadata by setting all new `6.2.2` features to `requires_project_migration: false`.
- Reuse the diagnostics cleanup task evidence in `tasks/2026-04-29-harness-doctor-version-cleanup/QUALITY_REPORT.md`.

## New Patterns

No new runtime, dependency, service, template path, migration family, or skill directory is introduced.

## Not Reused

`releases/MIGRATIONS.json` is not reused because `6.2.2` only changes plugin source behavior, docs, tests, and metadata.
