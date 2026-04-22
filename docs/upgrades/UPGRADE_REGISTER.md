# Upgrade Register

Track proposed, approved, deferred, and rejected upgrades.

| Date | Package / Tool | Current | Candidate | Decision | Why | Evidence | Validation | Status |
|---|---:|---:|---|---|---|---|---|
| 2026-04-22 | Project Governor plugin | 0.4.3 | 0.4.4 | applied | Added project hygiene doctor, clean initialization profile, hygiene policy/prompt templates, release metadata, and tests from the user-provided local patch. | `/Users/yxhpy/Downloads/codex-project-governor-v0.4.4-project-hygiene-doctor-fixed.patch`, `.codex-plugin/plugin.json`, `skills/project-hygiene-doctor/SKILL.md`, `tools/init_project.py`, `releases/FEATURE_MATRIX.json`, `releases/MIGRATIONS.json` | `python3 tests/selftest.py`, `python3 tests/test_project_hygiene_doctor.py`, `python3 tests/test_smart_routing_guard.py`, `python3 tests/test_subagent_activation.py`, `python3 tests/test_plugin_upgrade_migrator.py`, `python3 -m compileall tools skills tests`, `make test`, clean and legacy init smoke tests | completed |
| 2026-04-22 | Project Governor plugin | 0.4.2 | 0.4.3 | applied | Added plugin upgrade migrator with release feature matrix, migration metadata, install manifest template, safe migration helpers, and tests. | `/Users/yxhpy/Downloads/codex-project-governor-v0.4.3-plugin-upgrade-migrator.patch`, `.codex-plugin/plugin.json`, `skills/plugin-upgrade-migrator/SKILL.md`, `releases/FEATURE_MATRIX.json`, `releases/MIGRATIONS.json` | `python3 tests/selftest.py`, `python3 tests/test_smart_routing_guard.py`, `python3 tests/test_subagent_activation.py`, `python3 tests/test_plugin_upgrade_migrator.py`, `python3 -m compileall tools skills tests`, `make test`, init smoke test | completed |
| 2026-04-22 | Project Governor plugin | 0.4.1 | 0.4.2 | applied | Added explicit subagent activation with project-scoped `.codex/agents`, model-routing policy, deterministic selector, templates, examples, and tests. | `/Users/yxhpy/Downloads/codex-project-governor-v0.4.2-explicit-subagent-activation.patch`, `.codex-plugin/plugin.json`, `skills/subagent-activation/SKILL.md`, `templates/.codex/agents/context-scout.toml` | `python3 tests/selftest.py`, `python3 tests/test_smart_routing_guard.py`, `python3 tests/test_subagent_activation.py`, `python3 -m compileall tools skills tests`, `make test`, init smoke test | completed |
| 2026-04-22 | Project Governor plugin | 0.4.0 | 0.4.1 | applied | Added smart routing guard with `micro_patch`, negative constraint parsing, route guard validation, quality-gate integration, templates, and targeted tests. | `/Users/yxhpy/Downloads/codex-project-governor-v0.4.1-smart-routing-guard.patch`, `.codex-plugin/plugin.json`, `skills/task-router/SKILL.md`, `skills/route-guard/SKILL.md`, `skills/quality-gate/SKILL.md` | `python3 tests/selftest.py`, `python3 tests/test_smart_routing_guard.py`, `python3 -m compileall tools skills tests`, `make test`, init smoke test | completed |
| 2026-04-22 | Project Governor plugin | 0.3.1 | 0.4.0 | applied | Added quality-gated acceleration workflows, deterministic helper scripts, copied-template quality docs, and self-test coverage from the user-provided local patch. | `/Users/yxhpy/Downloads/codex-project-governor-add-quality-gated-acceleration-v0.4.patch`, `.codex-plugin/plugin.json`, `skills/task-router/SKILL.md`, `skills/quality-gate/SKILL.md` | `python3 tests/selftest.py`, `python3 -m compileall tools skills tests`, `make test`, init smoke test | completed |
| 2026-04-21 | Project Governor plugin | 0.1.0 | 0.2.0 | applied | Added upgrade-advisor skill and kept rules compatibility fix. | `.codex-plugin/plugin.json`, `skills/upgrade-advisor/SKILL.md`, commit `721154f` | `python3 -m unittest tests.selftest` | completed |

## Deferred upgrades

| Date | Package / Tool | Current | Candidate | Reason deferred | Revisit when |
|---|---:|---:|---|---|

## Rejected or pinned upgrades

| Date | Package / Tool | Pinned version | Rejected candidate | Reason | Revisit when |
|---|---:|---:|---|---|
