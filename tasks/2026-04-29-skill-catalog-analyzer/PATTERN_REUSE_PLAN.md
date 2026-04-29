# Pattern Reuse Plan: Skill Catalog Analyzer

## Scope

Add a deterministic repository helper that audits `skills/CATALOG.json` and reports advisory consolidation candidates.

## Existing patterns reused

| Need | Existing pattern | Reuse decision |
|---|---|---|
| Dependency-free CLI | `tools/init_project.py`, `skills/*/scripts/*.py` | Use Python standard library only, argparse inputs, JSON output. |
| Structured validation output | `skills/*/scripts/*.py`, `tests/selftest.py` | Emit `schema`, `status`, `issues`, and summary counters instead of prose-only diagnostics. |
| Skill source of truth | `skills/<skill>/SKILL.md`, `skills/CATALOG.json` | Read existing frontmatter and catalog metadata; do not add a second skill metadata source. |
| Focused tests | `tests/test_*.py` | Add `tests/test_skill_catalog_analyzer.py` rather than expanding unrelated test files. |

## New helper justification

`tests/selftest.py` validates catalog consistency but does not produce operator-facing consolidation candidates or text summaries. A separate tool under `tools/` keeps this as repository maintenance functionality rather than adding another public skill.

## Non-goals

- No new runtime dependencies.
- No skill deletion, deprecation, rename, or file movement.
- No changes to plugin manifests or template copy behavior.
