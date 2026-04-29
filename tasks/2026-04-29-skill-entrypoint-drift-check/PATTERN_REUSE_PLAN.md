# Pattern Reuse Plan: Skill Entrypoint Drift Check

## Scope

Tighten skill entrypoint documentation by making README grouping follow `skills/CATALOG.json` visibility.

## Existing patterns reused

| Need | Existing pattern | Reuse decision |
|---|---|---|
| Skill audience source | `skills/CATALOG.json` | Reuse visibility metadata instead of adding another grouping file. |
| Maintenance validation | `tools/analyze_skill_catalog.py` | Extend the existing analyzer with README drift checks. |
| Focused unit tests | `tests/test_skill_catalog_analyzer.py` | Add drift scenarios beside analyzer health tests. |
| Documentation contracts | `docs/architecture/API_CONTRACTS.md`, `docs/conventions/CONVENTION_MANIFEST.md` | Document the new validation behavior without changing plugin manifests. |

## New helper justification

No new helper is added. The existing analyzer is the correct place because it already owns catalog health and advisory consolidation output.

## Non-goals

- No skill directory rename, deletion, or deprecation.
- No change to plugin discovery metadata.
- No automatic README rewriting.
