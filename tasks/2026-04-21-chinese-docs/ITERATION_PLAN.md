# Iteration Plan

## User request

完善中文文档。

## Existing behavior

The repository has an English `README.md`, skill docs, templates, and self-tests. There is no Chinese README or Chinese usage guide for users who want to install and operate the plugin in Chinese.

## Existing patterns to reuse

| Pattern | Source file | How it will be reused |
|---|---|---|
| Root README as public entrypoint | `README.md` | Add a language switch without changing the English structure. |
| Skill catalog table | `README.md` | Mirror the current 13-skill catalog in Chinese. |
| Workflow prompt examples | `README.md`, `templates/.codex/prompts/*.md` | Provide Chinese explanations while keeping prompt commands copyable. |
| Self-test validation | `tests/selftest.py` | Add a lightweight check that Chinese docs and key links exist. |

## Files expected to change

- `README.md`
- `README.zh-CN.md`
- `docs/zh-CN/USAGE.md`
- `tests/selftest.py`

## Files not to change

- `.codex-plugin/plugin.json`
- `skills/`
- `templates/`
- deterministic helper scripts
- package manifests or dependency files

## New files

| File | Why existing files cannot cover it |
|---|---|
| `README.zh-CN.md` | A Chinese GitHub entrypoint is needed for install, skill, workflow, and test guidance. |
| `docs/zh-CN/USAGE.md` | A longer Chinese operator guide keeps the root README readable while covering practical workflows. |
| `tasks/2026-04-21-chinese-docs/ITERATION_PLAN.md` | The repository requires a task plan for non-trivial documentation additions. |

## Dependencies

No new dependencies.

## Tests

- `python3 tests/selftest.py`
- `git diff --check`

## Risks

- Chinese docs can drift from English README and plugin version if not checked.
- Adding docs under `docs/` must not accidentally stage unrelated untracked governance files.

## Rollback

Remove `README.zh-CN.md`, `docs/zh-CN/USAGE.md`, this task plan, and the `test_chinese_docs_exist` self-test; remove the language switch from `README.md`.
