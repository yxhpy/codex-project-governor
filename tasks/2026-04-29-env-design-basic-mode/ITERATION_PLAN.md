# Iteration Plan: .env-design Basic Mode

Date: 2026-04-29
Status: completed
Source: User report that Windows Codex PreToolUse did not inherit later shell `DESIGN_BASIC_MODE=1` and ignored project `.env-design`.

## Goal

Allow `DESIGN_BASIC_MODE=1` in project-root `.env-design` to satisfy the DESIGN.md UI gate and PreToolUse hook without requiring the Codex hook process to inherit a shell variable set after startup.

## Existing Pattern Reused

- Reuse `skills/design-md-aesthetic-governor/scripts/design_env_check.py` as the authoritative environment checker.
- Preserve `.env-design` parsing rules and secret-safe reporting.
- Mirror the same local `.env-design` check inside `templates/.codex/hooks/design_md_codex_hook.py` because hooks run standalone.
- Keep deterministic scripts dependency-free.

## Files Inspected

- `docs/project/CHARTER.md`
- `docs/conventions/CONVENTION_MANIFEST.md`
- `docs/conventions/ITERATION_CONTRACT.md`
- `docs/architecture/ARCHITECTURE.md`
- `README.md`
- `.codex-plugin/plugin.json`
- `skills/design-md-aesthetic-governor/SKILL.md`
- `skills/design-md-aesthetic-governor/scripts/design_env_check.py`
- `skills/design-md-aesthetic-governor/scripts/design_md_gate.py`
- `templates/.codex/hooks/design_md_codex_hook.py`
- `.codex/hooks/design_md_codex_hook.py`
- `tests/test_design_md_aesthetic_governor.py`

## Expected Changes

- `design_env_check.py` reads `.env-design` before deciding whether basic mode is enabled.
- The PreToolUse hook honors `.env-design` basic-mode flags.
- `.env-design` template includes a commented basic-mode line.
- Docs and API contract explain that `DESIGN_BASIC_MODE=1` may come from shell environment or project `.env-design`.
- Tests cover `.env-design` basic mode for the checker, preflight, and hook.

## Files Not To Change

- Application source files outside governance/plugin surfaces.
- Package manifests, lockfiles, or dependency setup.
- DESIGN.md token or UI implementation rules beyond the basic-mode configuration semantics.

## Tests

- `python3 tests/test_design_md_aesthetic_governor.py`
- `python3 tests/selftest.py`
- `python3 -m compileall tools skills tests`
- `make test`

## Risks

- Hook and skill checker could drift if only one side is updated.
- Basic mode is a deliberate weaker design-service path, so docs must keep `.env-design` local and uncommitted.

## Rollback

Revert the script, hook, docs, and test changes in this task directory if `.env-design` basic mode should not be supported.
