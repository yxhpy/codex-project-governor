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
- Copies project-owned runtime templates under `.project-governor/runtime/`.
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

### `skills/design-md-governor/scripts/lint_design_md.py`

Input:

- `file`

Output:

- `status`
- `file`
- `summary`
- `findings`
- `designSystem`

The script exits non-zero when `status=fail`. Findings include `severity`, `path`, `message`, and `rule`.

### `skills/design-md-governor/scripts/summarize_design_md.py`

Input:

- `file`

Output:

- `file`
- `name`
- `version`
- `description`
- `token_counts`
- `colors`
- `typography_tokens`
- `component_tokens`
- `sections`
- `parse_findings`

### `skills/design-md-governor/scripts/diff_design_md.py`

Input:

- `before`
- `after`

Output:

- `before`
- `after`
- `tokens`
- `before_summary`
- `after_summary`
- `regression`

The script exits non-zero when `regression=true`.

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
- Treats the Project Governor plugin repository itself as clean only when `--project` matches `--plugin-root`, or when no `--plugin-root` is supplied and the project manifest identifies the plugin.
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

### `skills/clean-reinstall-manager/scripts/generate_reinstall_instructions.py`

Input:

- optional `--plugin-dir <path>`
- optional `--repo-url <url>`
- optional `--ref <git-ref>`
- optional `--format {json,shell}`

Output:

- `status`
- `plugin_dir`
- `repo_url`
- `ref`
- `destructive_actions`
- `commands`
- `shell`
- `notes`

The default JSON output is instructions only. It does not remove or clone files itself.

### `skills/clean-reinstall-manager/scripts/discover_governed_projects.py`

Input:

- repeated `--root <path>`
- optional `--max-depth <number>`

Output:

- `status`
- `project_count`
- `projects[]`
- `user_choices`

Each project item includes `path`, `evidence`, `is_plugin_source`, and `recommendation`.

### `skills/clean-reinstall-manager/scripts/refresh_project_governance.py`

Input:

- `--project <path>`
- `--plugin-root <path>`
- optional `--apply`
- optional `--delete-trash`
- optional `--force`

Behavior:

- Stops when `--project` matches `--plugin-root` unless `--force` is supplied.
- Adds missing project-owned governance templates from `templates/`.
- Preserves memory and decision files.
- Merges missing markdown sections when headings are absent.
- Quarantines plugin-global noise under `.project-governor/trash/<timestamp>/` by default.
- Deletes noise only when `--delete-trash` is explicitly supplied with `--apply`.

Output:

- `status`
- `project`
- `plugin_root`
- `trash_root`
- `summary`
- `operations`
- `delete_trash`
- `notes`

Stop outputs use `status=not_project_stop` or `status=plugin_root_stop`.

### `skills/clean-reinstall-manager/scripts/clean_reinstall_orchestrator.py`

Input:

- optional `--path <path>`
- required `--plugin-root <path>`
- repeated `--discover-root <path>`
- optional `--select <ignore|all|comma-separated-paths>`
- optional `--apply`
- optional `--delete-trash`

Output:

- `status`
- `current_path`
- `reinstall`
- `discovered_projects` when outside a governed project
- `refresh` when inside a governed target project
- `applied` when selected discovered projects are refreshed
- `user_choices`
- `next_commands`

The orchestrator stops without modifying files when the current path is not a governed project or when it is the plugin root.

### `skills/clean-reinstall-manager/scripts/apply_latest_runtime_mode.py`

Input:

- optional `--path <path>`
- required `--plugin-root <path>`
- repeated `--discover-root <path>`
- optional `--select <current|all|ignore|comma-separated-paths>`
- optional `--apply`

Behavior:

- Detects whether `--path` is a Project Governor project.
- Writes project-owned `.project-governor/runtime/GPT55_RUNTIME_MODE.json` only when `--apply` is used.
- Builds `.project-governor/context/CONTEXT_INDEX.json` and `SESSION_BRIEF.md` only when `--apply` is used and `context-indexer` is installed.
- Does not copy plugin-global `.codex/agents`, `.codex/prompts`, or `.codex/config.toml`.

Output:

- `status`
- `result` for current-project mode
- `discovered_projects` and `user_choices` for stop mode
- `selected_count` and `results` for selected/all mode

### `skills/gpt55-auto-orchestrator/scripts/select_runtime_plan.py`

Input:

- optional JSON file path
- optional `--request <text>`

Input JSON fields include:

- `request`
- optional `available_models`
- optional `prefer_speed`
- optional `route`
- optional `quality_level` or `quality_gate`

Output:

- `status`
- `runtime_version`
- `route`
- `lane`
- `quality_gate`
- `reasons`
- `model_plan`
- `context_budget`
- `context_retrieval`
- `skill_sequence`
- `subagent_mode`
- `subagents`
- `skipped_skills`
- `quality_rules`

### `skills/context-indexer/scripts/build_context_index.py`

Input:

- optional `--project <path>`
- optional `--write`

Output without `--write`:

- `schema`
- `project`
- `entry_count`
- `entries[]`

Output with `--write`:

- `status`
- `index`
- `brief`
- `entry_count`

With `--write`, the script writes `.project-governor/context/CONTEXT_INDEX.json`, `.project-governor/context/SESSION_BRIEF.md`, and `.project-governor/context/INDEX_REPORT.json`.

### `skills/context-indexer/scripts/query_context_index.py`

Input:

- optional `--project <path>`
- required `--request <text>`
- optional `--limit <number>`

Output:

- `status`
- `request`
- `read_all_initialization_docs`
- `recommended_files[]`
- `token_policy`

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
