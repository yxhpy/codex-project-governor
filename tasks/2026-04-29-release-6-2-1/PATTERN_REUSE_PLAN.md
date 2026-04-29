# Pattern Reuse Plan

## Existing Patterns Reused

- Reused plugin manifest version fields for Codex and Claude metadata.
- Reused existing release note, feature matrix, and upgrade register formats.
- Reused existing self-test and Claude compatibility tests for version contract coverage.
- Reused the existing no-migration patch-release pattern for features that only affect plugin source behavior and user-facing metadata.

## New Patterns

No new runtime pattern, dependency, service, template path, or skill directory is introduced.

## Not Reused

`releases/MIGRATIONS.json` is not reused because `6.2.1` does not require initialized project file migration.
