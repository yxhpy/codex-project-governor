# Iteration Plan: Diagnostics Baseline Cleanup

## Request

Continue optimization review by removing avoidable diagnostics drift after the v6.2.1 release and reducing low-risk engineering-standards baseline blockers in touched helpers.

## Existing Patterns Reused

- `harness-doctor` stays a dependency-free deterministic Python helper.
- Version truth stays in existing release metadata and plugin manifests.
- Engineering standards scanning keeps existing ignore-directory filtering in `standards_core.py`.
- Small complexity fixes use extraction or table-driven scoring without changing deterministic JSON output schemas.
- Tests use existing `unittest` subprocess patterns.

## Files Inspected

- `skills/harness-doctor/scripts/doctor.py`
- `skills/merge-readiness/scripts/check_merge_readiness.py`
- `skills/evidence-manifest/scripts/write_evidence_manifest.py`
- `skills/task-router/scripts/classify_task.py`
- `skills/task-router/scripts/task_router_config.py`
- `skills/task-router/scripts/task_router_policy.py`
- `skills/upgrade-advisor/scripts/analyze_upgrade_candidates.py`
- `skills/quality-gate/scripts/run_quality_gate.py`
- `skills/route-guard/scripts/check_route_guard.py`
- `skills/route-guard/scripts/collect_diff_facts.py`
- `skills/memory-compact/scripts/classify_memory_items.py`
- `skills/memory-compact/scripts/record_session_learning.py`
- `skills/clean-reinstall-manager/scripts/clean_reinstall_orchestrator.py`
- `skills/clean-reinstall-manager/scripts/refresh_project_governance.py`
- `.codex/hooks/design_md_codex_hook.py`
- `templates/.codex/hooks/design_md_codex_hook.py`
- `skills/convention-miner/scripts/detect_repo_conventions.py`
- `skills/gpt55-auto-orchestrator/scripts/select_runtime_plan.py`
- `skills/project-hygiene-doctor/scripts/inspect_project_hygiene.py`
- `skills/context-indexer/scripts/build_context_index.py`
- `skills/context-indexer/scripts/build_context_roles.py`
- `skills/design-md-governor/scripts/lint_design_md.py`
- `skills/design-md-aesthetic-governor/scripts/design_md_lint.py`
- `skills/design-md-aesthetic-governor/scripts/design_service_smoke.py`
- `skills/design-md-aesthetic-governor/scripts/design_service_http.py`
- `skills/design-md-aesthetic-governor/scripts/design_service_review.py`
- `.codex/hooks/check_iteration_compliance.py`
- `templates/.codex/hooks/check_iteration_compliance.py`
- `skills/clean-reinstall-manager/scripts/apply_latest_runtime_mode.py`
- `skills/clean-reinstall-manager/scripts/discover_governed_projects.py`
- `skills/implementation-guard/scripts/check_iteration_compliance.py`
- `skills/pattern-reuse-engine/scripts/find_reuse_candidates.py`
- `skills/plugin-upgrade-migrator/scripts/plan_migration.py`
- `skills/subagent-activation/scripts/select_subagents.py`
- `skills/upgrade-advisor/scripts/analyze_upgrade_candidates.py`
- `skills/version-researcher/scripts/research_versions.py`
- `tools/init_project.py`
- `tools/install_or_update_user_plugin.py`
- `tests/selftest.py`
- `tests/selftest_helpers.py`
- `tests/test_session_learning.py`
- `skills/design-md-aesthetic-governor/scripts/verify_design_usage.py`
- `skills/engineering-standards-governor/scripts/standards_core.py`
- `tests/test_harness_v6.py`
- `tests/test_engineering_standards_governor.py`
- `tests/test_design_md_aesthetic_governor.py`
- `docs/project/CHARTER.md`
- `docs/project/ROADMAP.md`
- `docs/memory/PROJECT_MEMORY.md`
- `.codex-plugin/plugin.json`
- `releases/FEATURE_MATRIX.json`

## Files Expected To Change

- `skills/harness-doctor/scripts/doctor.py`
- `skills/merge-readiness/scripts/check_merge_readiness.py`
- `skills/evidence-manifest/scripts/write_evidence_manifest.py`
- `skills/task-router/scripts/classify_task.py`
- `skills/task-router/scripts/task_router_config.py`
- `skills/task-router/scripts/task_router_policy.py`
- `skills/upgrade-advisor/scripts/analyze_upgrade_candidates.py`
- `skills/quality-gate/scripts/run_quality_gate.py`
- `skills/route-guard/scripts/check_route_guard.py`
- `skills/route-guard/scripts/collect_diff_facts.py`
- `skills/memory-compact/scripts/classify_memory_items.py`
- `skills/memory-compact/scripts/record_session_learning.py`
- `skills/clean-reinstall-manager/scripts/clean_reinstall_orchestrator.py`
- `skills/clean-reinstall-manager/scripts/refresh_project_governance.py`
- `.codex/hooks/design_md_codex_hook.py`
- `templates/.codex/hooks/design_md_codex_hook.py`
- `skills/convention-miner/scripts/detect_repo_conventions.py`
- `skills/gpt55-auto-orchestrator/scripts/select_runtime_plan.py`
- `skills/project-hygiene-doctor/scripts/inspect_project_hygiene.py`
- `skills/context-indexer/scripts/build_context_index.py`
- `skills/context-indexer/scripts/build_context_roles.py`
- `skills/design-md-governor/scripts/lint_design_md.py`
- `skills/design-md-aesthetic-governor/scripts/design_md_lint.py`
- `skills/design-md-aesthetic-governor/scripts/design_service_smoke.py`
- `skills/design-md-aesthetic-governor/scripts/design_service_http.py`
- `skills/design-md-aesthetic-governor/scripts/design_service_review.py`
- `.codex/hooks/check_iteration_compliance.py`
- `templates/.codex/hooks/check_iteration_compliance.py`
- `skills/clean-reinstall-manager/scripts/apply_latest_runtime_mode.py`
- `skills/clean-reinstall-manager/scripts/discover_governed_projects.py`
- `skills/implementation-guard/scripts/check_iteration_compliance.py`
- `skills/pattern-reuse-engine/scripts/find_reuse_candidates.py`
- `skills/plugin-upgrade-migrator/scripts/plan_migration.py`
- `skills/subagent-activation/scripts/select_subagents.py`
- `skills/upgrade-advisor/scripts/analyze_upgrade_candidates.py`
- `skills/version-researcher/scripts/research_versions.py`
- `tools/init_project.py`
- `tools/install_or_update_user_plugin.py`
- `tests/selftest.py`
- `tests/selftest_helpers.py`
- `tests/test_session_learning.py`
- `skills/design-md-aesthetic-governor/scripts/verify_design_usage.py`
- `skills/engineering-standards-governor/scripts/standards_core.py`
- `tests/test_harness_v6.py`
- `tests/test_engineering_standards_governor.py`
- `tests/test_design_md_aesthetic_governor.py`
- `docs/project/CHARTER.md`
- `docs/project/ROADMAP.md`
- `docs/conventions/CONVENTION_MANIFEST.md`
- `docs/memory/PROJECT_MEMORY.md`
- `docs/zh-CN/USAGE.md`
- `skills/clean-reinstall-manager/SKILL.md`

## Files Not To Change

- Plugin manifest public fields.
- Template output paths.
- Deterministic JSON output schemas.
- Historical release notes for older versions.

## Tests To Update

- Add a harness-doctor regression test for current manifest version handling.
- Add an engineering-standards regression test that backup snapshots are ignored.
- Extend the DESIGN.md aesthetic smoke test to cover extracted design-usage scanning.
- Re-run clean-reinstall manager tests after helper extraction.
- Re-run DESIGN.md aesthetic hook tests after handler extraction.
- Re-run convention miner selftest coverage after detector extraction.
- Re-run GPT-5.5 auto orchestration tests after runtime policy extraction.
- Re-run project hygiene doctor tests after classification/status extraction.
- Re-run selftest after splitting the acceleration-tools assertions.
- Re-run Harness v6 and GPT-5.5 orchestration tests after context-indexer role/session brief extraction.
- Re-run DESIGN.md governor tests after lint token extraction.
- Re-run DESIGN.md aesthetic tests after aesthetic lint extraction.
- Re-run DESIGN.md aesthetic tests after service smoke extraction.
- Re-run DESIGN.md aesthetic tests after service review extraction.
- Re-run clean-reinstall and hook compile checks after remaining warning cleanup.
- Re-run upgrade, routing, subagent, init, installer, and selftest coverage after helper extraction.
- Re-run session-learning tests after splitting large test setup/assertions.
- Re-run all-scope engineering standards and clear warnings to zero.
- Re-run existing router, upgrade-advisor, evidence-manifest, merge-readiness, and selftest coverage.

## Risks

- Version checks could become too weak if they only trust the manifest under test.
- Broad ignore patterns could hide real source files if applied outside generated backup paths.

## Rollback

Revert this task's edits; existing self-tests should return to the pre-cleanup behavior.

## Verification

- `make test`: pass.
- `python3 -m compileall tools skills tests`: pass.
- `make doctor`: pass.
- `git diff --check`: pass.
- `python3 skills/engineering-standards-governor/scripts/check_engineering_standards.py --scope diff --diff-base HEAD --project . --format text`: pass with 0 warnings.
- `python3 skills/engineering-standards-governor/scripts/check_engineering_standards.py --scope all --project . --format text`: pass with 0 warnings.
- `python3 skills/quality-gate/scripts/run_quality_gate.py <temp-input>`: pass with 0 blockers and 0 warnings.
