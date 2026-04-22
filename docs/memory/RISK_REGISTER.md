# Risk Register

| Date | Risk | Impact | Likelihood | Mitigation | Owner | Status | Evidence |
|---|---|---|---|---|---|---|---|
| 2026-04-21 | Template path drift breaks downstream initialization expectations. | Target repositories may miss required governance files or tests may stop reflecting real output. | medium | Treat template path changes as public contract changes and update `tests/selftest.py`. | maintainer | open | `tools/init_project.py`, `tests/selftest.py`, `templates/` |
| 2026-04-21 | Hard-coded application path heuristics in `tools/init_project.py` can misclassify unusual repositories. | Initialization may skip or copy files incorrectly for nonstandard layouts. | medium | Keep skip heuristics conservative and document edge cases before changing them. | maintainer | open | `tools/init_project.py` |
| 2026-04-21 | Compatibility wrapper coupling in `tools/init_existing_project.py`. | Old commands may continue working but wrapper behavior can diverge from `init_project.py`. | medium | Keep tests or docs around compatibility behavior before changing the wrapper. | maintainer | open | `tools/init_existing_project.py` |
| 2026-04-21 | Dependency drift if package managers are added casually. | The repo could lose its dependency-free helper-script property and complicate installation. | low | Require upgrade-advisor and a decision record before adding dependencies. | maintainer | open | `docs/upgrades/UPGRADE_POLICY.md`, `README.md` |
| 2026-04-21 | Speculative or stale memory entries contaminate future Codex sessions. | Future agents may make decisions from incorrect facts. | medium | Record uncertain items in `OPEN_QUESTIONS.md` and require evidence for durable facts. | maintainer | open | `AGENTS.md`, `docs/memory/PROJECT_MEMORY.md` |
