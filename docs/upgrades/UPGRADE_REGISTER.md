# Upgrade Register

Track proposed, approved, deferred, and rejected upgrades.

| Date | Package / Tool | Current | Candidate | Decision | Why | Evidence | Validation | Status |
|---|---:|---:|---|---|---|---|---|
| 2026-04-22 | Project Governor plugin | 0.3.1 | 0.4.0 | applied | Added quality-gated acceleration workflows, deterministic helper scripts, copied-template quality docs, and self-test coverage from the user-provided local patch. | `/Users/yxhpy/Downloads/codex-project-governor-add-quality-gated-acceleration-v0.4.patch`, `.codex-plugin/plugin.json`, `skills/task-router/SKILL.md`, `skills/quality-gate/SKILL.md` | `python3 tests/selftest.py`, `python3 -m compileall tools skills tests`, `make test`, init smoke test | completed |
| 2026-04-21 | Project Governor plugin | 0.1.0 | 0.2.0 | applied | Added upgrade-advisor skill and kept rules compatibility fix. | `.codex-plugin/plugin.json`, `skills/upgrade-advisor/SKILL.md`, commit `721154f` | `python3 -m unittest tests.selftest` | completed |

## Deferred upgrades

| Date | Package / Tool | Current | Candidate | Reason deferred | Revisit when |
|---|---:|---:|---|---|

## Rejected or pinned upgrades

| Date | Package / Tool | Pinned version | Rejected candidate | Reason | Revisit when |
|---|---:|---:|---|---|
