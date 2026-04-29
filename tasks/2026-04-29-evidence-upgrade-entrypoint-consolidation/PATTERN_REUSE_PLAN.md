# Pattern Reuse Plan: Evidence and Upgrade Entrypoint Consolidation

## Scope

Reduce README skill-choice noise by presenting evidence and upgrade advice as one recommended entrypoint row while preserving both workflow skills.

## Existing patterns reused

| Need | Existing pattern | Reuse decision |
|---|---|---|
| Evidence-before-change workflows | `research-radar`, `upgrade-advisor` | Preserve both skills and references; collapse only the README row. |
| Catalog visibility coverage | `tools/analyze_skill_catalog.py` | Keep both names in the recommended section so drift checks remain exact. |
| README consolidation regression | `tests/test_skill_catalog_analyzer.py` | Add the same style of assertion used for initialization and maintenance consolidation. |

## New helper justification

No new helper is needed. The existing analyzer and tests cover README/catalog alignment.

## Non-goals

- No research or upgrade skill rename, deletion, or deprecation.
- No script behavior changes.
- No plugin manifest changes.
