# Pattern Reuse Plan: Init Entrypoint Consolidation

## Scope

Reduce README skill-choice noise by presenting initialization as one entrypoint row while preserving both existing initialization skills.

## Existing patterns reused

| Need | Existing pattern | Reuse decision |
|---|---|---|
| Initialization modes | `tools/init_project.py --mode empty|existing` | Use one user-facing initialization row with both mode-specific skills. |
| Backward compatibility | `skills/init-empty-project`, `skills/init-existing-project` | Keep both skills and references; only collapse README presentation. |
| Catalog drift guard | `tools/analyze_skill_catalog.py` | Preserve both skill mentions in the recommended section so visibility coverage remains exact. |
| Focused regression test | `tests/test_skill_catalog_analyzer.py` | Assert the consolidated README row exists and the old separate rows do not return. |

## New helper justification

No new helper is needed. This is a documentation consolidation backed by the existing analyzer.

## Non-goals

- No new `init-project` skill directory.
- No skill rename, deletion, deprecation, or manifest change.
- No change to template initialization behavior.
