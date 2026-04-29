# Iteration Plan: Default Prompt Consolidation

## Request

Continue reducing user-visible skill noise by consolidating the Codex plugin `defaultPrompt` list.

## Existing Patterns Reused

- `.codex-plugin/plugin.json` remains the source for Codex plugin metadata and default prompts.
- `README.md` and `README.zh-CN.md` already group skills into recommended, internal, and advanced surfaces.
- `tests/selftest.py` already validates plugin manifest shape and is the right place to guard default prompt size.
- `docs/architecture/API_CONTRACTS.md` documents the plugin manifest public contract.

## Expected Changes

- Replace the long skill-by-skill `defaultPrompt` list with concise scenario-level prompts.
- Keep prompts aligned with the README recommended entry points and avoid exposing internal workflow stages as default UI choices.
- Add self-test coverage to keep the prompt list compact and user-facing.
- Document the prompt policy in README and API contracts.

## Files Not To Change

- Do not rename, delete, or deprecate any skill.
- Do not change `.claude-plugin/plugin.json`; this change targets Codex plugin UI defaults only.
- Do not change template payload paths.
- Do not add dependencies.

## Test Plan

- `python3 -m json.tool .codex-plugin/plugin.json`
- `python3 tests/selftest.py`
- `python3 tools/analyze_skill_catalog.py --project . --format json --fail-on-issues`
- `python3 tests/test_skill_catalog_analyzer.py`
- `python3 -m compileall tools skills tests`
- `git diff --check`
- `python3 skills/engineering-standards-governor/scripts/check_engineering_standards.py --project . --diff-base main`
- `make test`

## Risks

- Over-compressing prompts could hide important workflows from users. The replacement keeps initialization, governed change execution, maintenance, evidence/upgrades, memory, design/UI, and PR review as explicit scenarios.
- Changing public plugin metadata requires README and test updates.

## Rollback

Restore the previous `defaultPrompt` array and remove the self-test prompt-count expectations.
