# Iteration Plan: Skill Catalog Consolidation

## User request

Analyze whether the Project Governor skill set has unnecessary duplication, then continue with a practical first simplification step.

## Existing behavior

The repository currently exposes 35 Codex skills as a flat README table. The underlying system already has an orchestrator, router, quality gate, and internal workflow stages, but public docs do not distinguish primary user entry points from internal or advanced skills.

## Existing patterns to reuse

| Pattern | Source file | How it will be reused |
|---|---|---|
| Skill folder contract | `docs/conventions/PATTERN_REGISTRY.md` | Keep existing `skills/<skill>/SKILL.md` directories intact; do not rename or delete skills in this iteration. |
| Public README positioning | `README.md`, `README.zh-CN.md` | Replace the flat skill list with grouped user-facing categories while preserving all skill names. |
| Self-test gate | `tests/selftest.py` | Validate that catalog metadata stays aligned with actual skill directories. |

## Files expected to change

- `skills/CATALOG.json`
- `README.md`
- `README.zh-CN.md`
- `docs/architecture/API_CONTRACTS.md`
- `docs/architecture/ARCHITECTURE.md`
- `docs/conventions/CONVENTION_MANIFEST.md`
- `tests/selftest.py`

## Files not to change

- `.codex-plugin/plugin.json`
- `.claude-plugin/plugin.json`
- `skills/*/SKILL.md`
- `skills/*/scripts/*`
- `templates/**`
- package manifests, lockfiles, or dependencies

## New files

| File | Why existing files cannot cover it |
|---|---|
| `skills/CATALOG.json` | A machine-readable catalog is needed to distinguish primary, internal, advanced, and deprecated skill visibility without deleting or renaming public skill folders. |

## Dependencies

No new dependencies.

## Tests

- Add self-test validation that `skills/CATALOG.json` covers every skill directory and uses allowed visibility/category values.
- Run `python3 tests/selftest.py`.
- Run `python3 -m compileall tools skills tests`.

## Risks

- Documentation may imply a skill was removed if grouping is too aggressive; keep all skill names visible.
- Catalog metadata can drift from directories; self-test must block missing or extra catalog entries.

## Rollback

Remove `skills/CATALOG.json`, revert the README grouping, and remove the catalog self-test.
