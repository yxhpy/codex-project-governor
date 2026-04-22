# API Contracts

This repository has no HTTP API routes.

## Plugin Manifest Contract

`.codex-plugin/plugin.json` declares:

- plugin `name`
- semantic `version`
- `description`
- `homepage`
- `repository`
- `license`
- `keywords`
- `skills`
- `mcpServers`
- `interface` metadata, capabilities, and default prompts

Changes to these fields affect plugin discovery and user-facing positioning.

## CLI Contracts

### `tools/init_project.py`

Inputs:

- `--mode {empty,existing}`
- `--target <path>`
- `--profile {clean,legacy-full}`
- `--overwrite`
- `--json`

Behavior:

- Copies files from `templates/`.
- Defaults to the `clean` profile, which copies project-owned governance files, project `.codex/rules`, project `.codex/hooks`, and `.codex/hooks.json` while skipping plugin-global `.codex` runtime assets.
- `--profile legacy-full` copies bundled `.codex` runtime assets for projects that explicitly need the old behavior.
- Preserves existing files unless `--overwrite` is used.
- Skips known application/package paths.
- Writes `.project-governor/INSTALL_MANIFEST.json` for fresh initialization or when overwrite is requested.
- Writes `reports/project-governor/init-report.json`.

JSON output fields:

- `mode`
- `profile`
- `target`
- `created`
- `preserved`
- `skipped`
- `skipped_application`
- `skipped_global`
- `install_manifest`

### `tools/init_existing_project.py`

Compatibility wrapper accepting:

- `<plugin_root>`
- `<repo>`

It forwards to `copy_templates(...)` and prints a one-line summary.

### `skills/convention-miner/scripts/detect_repo_conventions.py`

Input:

- optional repository path

JSON output includes:

- `package_manager`
- `languages`
- `frameworks`
- `source_roots`
- `test_files`
- `file_count`

### `skills/implementation-guard/scripts/check_iteration_compliance.py`

Input JSON fields include:

- `rewrite_pct_by_file`
- `dependency_changes`
- `new_files`
- `justified_new_files`
- `public_contract_changes`
- `approved_contract_changes`

Output:

- `status`
- `findings`

The script exits non-zero when findings are present.

### `skills/style-drift-check/scripts/check_style_drift.py`

Input JSON fields include:

- `new_components`
- `registered_components`
- `raw_colors`
- `new_style_systems`
- `approved_style_systems`

Output:

- `status`
- `findings`

The script exits non-zero when findings are present.

### `skills/upgrade-advisor/scripts/analyze_upgrade_candidates.py`

Input JSON fields include:

- `project_requirements`
- `dependencies[]`

Output includes:

- `status`
- `project_requirements`
- `summary`
- `candidates[]`
- `policy`

### `skills/version-researcher/scripts/research_versions.py`

Input:

- `--manifest <json>`
- `--request <text>`

Manifest fields include:

- `subject`
- `current_version`
- `project_context`
- `candidate_versions[]`

Output includes:

- `subject`
- `current_version`
- `request`
- `detected_needs`
- `versions_behind`
- `candidate_versions[]`
- `overall_recommendation`
- `user_choices`

### `skills/research-radar/scripts/score_research_candidates.py`

Input:

- `--manifest <json>`
- repeated `--need <need>`

Manifest fields include:

- `project`
- `generated_at`
- `project_needs`
- `candidates[]`

Output includes:

- `project`
- `generated_at`
- `needs`
- `candidates[]`
- `summary`
- `user_choices`

### `skills/task-router/scripts/classify_task.py`

Input:

- JSON file path
- optional `--request <text>` when no JSON file is supplied

Output includes:

- `status`
- `request`
- `route`
- `lane`
- `quality_level`
- `quality_gate`
- `confidence`
- `risk_signals`
- `negative_constraints`
- `subagent_mode`
- `required_skills`
- `required_workflow`
- `skipped_workflow`
- `change_budget`
- `route_guard_requirements`
- `escalate_if`
- `escalation_triggers`

### `skills/route-guard/scripts/check_route_guard.py`

Input JSON fields include:

- `route`
- `route_guard_requirements`
- `changes`

Output:

- `status`
- `route`
- `violations`
- `required_action`
- `recommended_route`
- `summary`

The script exits non-zero when route guard violations are present.

### `skills/subagent-activation/scripts/select_subagents.py`

Input JSON fields include:

- `workflow`
- `skill`
- `route`
- `quality_level`
- `quality_gate`
- `confidence`
- `subagent_mode`
- `target_is_shared_component`
- `repair_expected`

Output:

- `status`
- `subagent_mode`
- `route`
- `workflow`
- `selected_agents`
- `skipped_agents`
- `model_strategy`
- `spawn_instructions`
- `wait_policy`
- `write_policy`

### `skills/plugin-upgrade-migrator/scripts/inspect_installation.py`

Input:

- `--project <path>`

Output:

- `status`
- `project`
- `installed_version`
- `tracked_files`
- `summary`

### `skills/plugin-upgrade-migrator/scripts/compare_features.py`

Input:

- `--current-version <semver>`
- optional `--target-version <semver>`
- `--feature-matrix <json>`

Output:

- `current_version`
- `target_version`
- `versions_behind`
- `new_versions`
- `features`
- `migration_required`
- `migration_ids`

### `skills/plugin-upgrade-migrator/scripts/plan_migration.py`

Input:

- `--project <path>`
- `--plugin-root <path>`
- `--current-version <semver>`
- `--target-version <semver>`
- optional `--output <path>`

Output:

- `status`
- `project`
- `plugin_root`
- `current_version`
- `target_version`
- `operations`
- `summary`
- `recommended_action`

Operations with `op=run_hygiene_check` or `upgrade_policy=diagnostic_only` are diagnostic steps. They must be planned as manual review operations and must not be treated as safe file-copy operations by `apply_safe_migration.py`.

### `skills/plugin-upgrade-migrator/scripts/apply_safe_migration.py`

Input:

- `--plan <json>`
- optional `--apply`

Output:

- `status`
- `plan`
- `applied`
- `skipped`
- `summary`

### `skills/project-hygiene-doctor/scripts/inspect_project_hygiene.py`

Input:

- `--project <path>`
- optional `--plugin-root <path>`
- optional `--apply`

Behavior:

- Detects plugin-global source-like folders in non-plugin target projects.
- Detects `.codex/agents`, `.codex/prompts`, and `.codex/config.toml` assets that should normally remain plugin-owned.
- Never removes memory or decision files.
- With `--apply`, quarantines only unchanged generated global assets under `.project-governor/hygiene-quarantine/`.

Output:

- `status`
- `project`
- `plugin_root`
- `is_plugin_repo`
- `summary`
- `findings`
- `applied`
- `recommendation`

### `skills/context-pack-builder/scripts/build_context_pack.py`

Input:

- repository path
- `--request <text>`
- optional `--limit <number>`

Output includes:

- `status`
- `request_terms`
- `must_read`
- `related_tests`
- `related_docs`
- `maybe_read`
- `avoid`
- `subagents`

### `skills/pattern-reuse-engine/scripts/find_reuse_candidates.py`

Input:

- repository path
- optional `--request <text>`

Output includes:

- `status`
- `required_reuse`
- `reuse_candidates`
- `forbidden_duplicates`

### `skills/quality-gate/scripts/check_change_budget.py`

Input JSON fields include:

- `budget`
- `actual`

Output:

- `status`
- `findings`

The script exits non-zero when the budget fails.

### `skills/quality-gate/scripts/run_quality_gate.py`

Input JSON fields include:

- `level`
- `quality_level`
- `change_budget`
- `actual`
- `checks`
- `commands`
- `route_guard`

Output:

- `status`
- `level`
- `quality_level`
- `findings`
- `blockers`
- `warnings`
- `commands`
- `route_guard`
- `repair_loop_required`
- `summary`

The script exits non-zero when blocking findings are present.

### `skills/merge-readiness/scripts/check_merge_readiness.py`

Input JSON fields include:

- `quality_gate`
- `blockers`
- `warnings`
- `required_docs_missing`
- `approval_required`
- `approval_recorded`
- `open_repair_items`
- `commands_verified`

Output:

- `status`
- `blockers`
- `warnings`
- `commands_verified`
- `required_before_merge`

The script exits non-zero when merge readiness fails.

### `skills/coding-velocity-report/scripts/build_velocity_report.py`

Input JSON fields include:

- `metrics`

Output:

- `status`
- `velocity_score`
- `quality_score`
- `bottlenecks`
- `recommendations`

### `skills/memory-compact/scripts/classify_memory_items.py`

Input:

- JSON list
- JSON object with `items`
- plain text lines

Output:

- array of `{text, classification}` objects

## Error Behavior

No custom error envelope is currently defined for malformed CLI inputs. Standard Python and `argparse` errors are the current behavior.
