# Pattern Reuse Plan: Maintenance Entrypoint Consolidation

## Scope

Reduce README skill-choice noise by presenting maintenance as one recommended entrypoint row while preserving both maintenance workflow skills.

## Existing patterns reused

| Need | Existing pattern | Reuse decision |
|---|---|---|
| Maintenance workflows | `clean-reinstall-manager`, `plugin-upgrade-migrator` | Preserve both skills and references; collapse only the README row. |
| Catalog visibility coverage | `tools/analyze_skill_catalog.py` | Keep both names in the recommended section so drift checks remain exact. |
| README consolidation regression | `tests/test_skill_catalog_analyzer.py` | Add the same style of assertion used for initialization consolidation. |

## New helper justification

No new helper is needed. The existing analyzer and tests cover README/catalog alignment.

## Non-goals

- No maintenance skill rename, deletion, or deprecation.
- No script behavior changes.
- No plugin manifest changes.
