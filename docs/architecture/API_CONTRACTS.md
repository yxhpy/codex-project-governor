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

### `tools/install_or_update_user_plugin.py`

Input:

- optional `--plugin-dir <path>`
- optional `--marketplace-path <path>`
- optional `--repo-url <url>`
- optional `--ref <git-ref>`
- optional `--apply`
- optional `--skip-selftest`

Behavior:

- Defaults to dry-run planning and writes nothing unless `--apply` is supplied.
- Installs or updates the user-level Project Governor Git checkout used by a local marketplace entry.
- Creates or updates a local marketplace entry with `source: local` pointing at the plugin checkout.
- Stops without modifying files when the plugin directory exists but is not a Git checkout.
- Stops without updating when the existing Git checkout has uncommitted changes.
- With `--apply`, runs `git clone` when missing, otherwise `git fetch --tags origin` and checks out the requested ref.
- Runs `tests/selftest.py` after update unless `--skip-selftest` is supplied.

Output:

- `status`
- `plugin_dir`
- `marketplace_path`
- `repo_url`
- `ref`
- `current_version`
- `target_source` in dry-run mode
- `previous_version` in apply mode
- `marketplace_entry` in apply mode
- `operations`
- `notes` or `next_steps`

The script exits non-zero when blocked or when self-test fails after applying.

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

### `skills/design-md-aesthetic-governor/scripts/design_env_check.py`

Input:

- optional `--project <path>`
- optional `--write-template`

Output:

- `ok`
- `status`
- `mode`
- `env_file`
- `gemini_protocol`
- `stitch_mcp_url`
- `required`
- `provided`
- `missing`
- `template_created`
- `git_exclude_updated`
- `instructions`

The script exits with code `2` when required values are missing. It never prints API key values. `provided` records only whether each required key came from a shell environment variable or project-root `.env-design`. With `--write-template`, it may create a blank `.env-design` template and add `.env-design` to `.git/info/exclude`. Shell environment variable `DESIGN_BASIC_MODE=1` returns `status=basic_mode` and `mode=basic`; legacy `DESIGN_ENV_SKIP=1` and `DESIGN_SERVICE_CONFIG_SKIP=1` are accepted. Basic-mode flags in `.env-design` are not honored. `GEMINI_PROTOCOL` is optional and may be `auto`, `openai`, or `gemini`; `DESIGN_GEMINI_PROTOCOL` is accepted as an alias. `STITCH_MCP_URL` is optional and defaults to `https://stitch.googleapis.com/mcp`; `DESIGN_STITCH_MCP_URL`, `STITCH_MCP_ENDPOINT`, and `DESIGN_STITCH_MCP_ENDPOINT` are accepted aliases.

### `skills/design-md-aesthetic-governor/scripts/design_md_gate.py`

Input:

- `preflight --task <text>`
- optional `--design <path>`
- optional `--inspiration <id>`
- `check`
- optional `--design <path>`

Successful preflight output:

- `ok`
- `timestamp`
- `task`
- `task_is_ui`
- `design_path`
- `design_sha256`
- `lint_summary`
- `design_env`
- `required_final_section`
- `aesthetic_reference`

Generated files:

- `.codex/design-md-governor/read-proof.json`
- `.codex/design-md-governor/lint-report.json`
- `.codex/design-md-governor/DESIGN_MD_READ_REPORT.md`
- `.codex/design-md-governor/design-env-report.json`

Missing Gemini/Stitch design-service configuration exits with code `2` and outputs `ok`, `blocked`, `reason`, and `design_env`. Missing `DESIGN.md` exits with code `2` and creates `docs/design/DESIGN_MD_ADOPTION_PLAN.md`.

### `skills/design-md-aesthetic-governor/scripts/design_service_smoke.py`

Input:

- optional `--project <path>`
- optional `--task <text>`
- optional `--timeout <seconds>`
- optional `--dry-run`

Output:

- `ok`
- `status`
- `design_env` when blocked
- `gemini`
- `stitch`

The script reads Gemini/Stitch configuration from shell environment variables and project-root `.env-design`, but never prints API key values. `GEMINI_PROTOCOL=openai` uses an OpenAI-compatible `POST <GEMINI_BASE_URL>/v1/chat/completions` request unless the base URL already ends with `/v1` or `/chat/completions`. `GEMINI_PROTOCOL=gemini` uses native Gemini `POST <GEMINI_BASE_URL>/v1beta/models/<GEMINI_MODEL>:generateContent` unless the base URL already includes a version, model, or `:generateContent` suffix. When a gateway serves native Gemini under a subpath such as `/gemini/v1beta`, `GEMINI_BASE_URL` must include that protocol root, for example `https://host/gemini`. `GEMINI_PROTOCOL=auto` chooses native Gemini for official Google Gemini hostnames and OpenAI-compatible chat completions otherwise. Gemini success requires a valid JSON response shape (`choices` for OpenAI-compatible, `candidates` for native Gemini), not just a 2xx status. Stitch smoke uses remote MCP initialization against `STITCH_MCP_URL` / `DESIGN_STITCH_MCP_URL`, falling back to `https://stitch.googleapis.com/mcp`, and sends the API key only in the `X-Goog-Api-Key` header.

### `skills/design-md-aesthetic-governor/scripts/design_service_review.py`

Input:

- required `--task <text>`
- optional `--project <path>`
- optional `--design <path>`
- optional `--timeout <seconds>`
- optional `--write-template`

Output:

- `ok`
- `status`
- `task`
- `design`
- `design_sha256`
- `lint_summary`
- `gemini`
- `stitch`
- `evidence`

The script is the repeatable full-service UI review step. It reads `DESIGN.md`, lints it, sends the task and design summary to Gemini using the configured protocol, initializes Stitch MCP, calls `tools/list`, and writes `.codex/design-md-governor/service-review.json` plus `.codex/design-md-governor/SERVICE_REVIEW.md`. It does not create remote Stitch projects or modify application code.

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
- `router_version`
- `request`
- `intent`
- `route`
- `lane`
- `quality_level`
- `quality_gate`
- `confidence`
- `risk_score`
- `risk_signals`
- `negative_constraints`
- `task_shape`
- `subagent_mode`
- `required_skills`
- `required_workflow`
- `skipped_workflow`
- `change_budget`
- `route_guard_requirements`
- `evidence_required`
- `escalate_if`
- `escalation_triggers`
- `reasons`

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

### `skills/route-guard/scripts/collect_diff_facts.py`

Input:

- optional `--repo <path>`

Output:

- `status`
- `repo`
- `modified_files`
- `added_files`
- `deleted_files`
- `renamed_files`
- `dependencies_added`
- `dependency_files_changed`
- `api_contract_changed`
- `api_files_changed`
- `schema_changed`
- `schema_files_changed`
- `global_style_changed`
- `global_style_files_changed`
- `shared_component_changed`
- `shared_components_changed`
- `new_components_added`
- `rewrite_detected`
- `tests_deleted`
- `assertions_weakened`
- `tests_skipped`
- `test_files_changed`

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

The planner also surfaces tracked `AGENTS.md` rule-template drift. When `.project-governor/INSTALL_MANIFEST.json` records an older `templates/AGENTS.md` hash and the current project `AGENTS.md` does not already match the latest template, `plan_migration.py` emits an operation with `op=review_rule_template_drift`, `path=AGENTS.md`, `migration_id=rule_template_drift`, and normal `three_way_merge` classification. Unmodified installed files can be `replace_from_template`; user-modified files remain `manual_review_or_three_way_merge`.

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
- `router_version`
- `route`
- `lane`
- `quality_gate`
- `classification`
- `risk_score`
- `evidence_required`
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
- `built_at`
- `git`
- `entry_count`
- `entries[]`

Output with `--write`:

- `status`
- `schema`
- `index`
- `brief`
- `entry_count`

With `--write`, the script writes `.project-governor/context/CONTEXT_INDEX.json`, `.project-governor/context/SESSION_BRIEF.md`, and `.project-governor/context/INDEX_REPORT.json`.

Harness v6 writes `schema` as `project-governor-context-index-v2`. Entries include path, size, mtime, hash, language, roles, symbols, imports, headings, tokens, summary, sensitivity, and stale reason. Secret-like content is redacted from summaries.

### `skills/context-indexer/scripts/query_context_index.py`

Input:

- optional `--project <path>`
- required `--request <text>`
- optional `--route <name>`
- optional `--limit <number>`
- optional `--memory-search`
- optional `--auto-build`
- optional `--include-sensitive`
- optional `--format {json,text}`

Output:

- `status`
- `request`
- `route`
- `search_mode`
- `searched_roles`
- `auto_built`
- `raw_chat_history_search`
- `confidence`
- `read_all_initialization_docs`
- `recommended_files[]`
- `token_policy`
- `stale_files[]`

Default behavior remains general context retrieval. With `--memory-search`, the script searches governed project memory/history surfaces such as `docs/memory/**`, `docs/decisions/**`, `tasks/**`, `.project-governor/state/**`, release notes, upgrade docs, research docs, quality docs, conventions, design docs, and agent instructions. It does not scan raw chat transcripts. With `--auto-build`, a missing context index is built before querying. With `--format text`, the same result is rendered as a concise human-readable list instead of JSON.

### `skills/memory-compact/scripts/record_session_learning.py`

Input:

- optional `--project <path>`
- optional `--input <json-path>`; otherwise reads JSON from stdin
- optional `--task-id <id>`
- optional `--source <text>`
- optional `--apply`

Input JSON may include `items`, `events`, or `learnings`. Each item can include `type`, `command`, `error`, `lesson`, `correct_behavior`, `repeat_count`, `memory`, `path`, `reason`, and `evidence`.

Behavior:

- Defaults to dry-run classification and writes nothing unless `--apply` is supplied.
- Classifies one-off failed commands into `.project-governor/state/COMMAND_LEARNINGS.json`.
- Promotes repeated command/session mistakes to `docs/memory/REPEATED_AGENT_MISTAKES.md` and records them in the command-learning ledger.
- Queues stale, superseded, or bloated memory candidates in `.project-governor/state/MEMORY_HYGIENE.json`.
- Appends unresolved questions to `docs/memory/OPEN_QUESTIONS.md` and risks to `docs/memory/RISK_REGISTER.md`.
- Redacts or skips secret-like candidates and does not store raw secret content.

Output:

- `status`
- `schema`
- `project`
- `task_id`
- `results[]`
- `applied[]`
- `skipped[]`
- `memory_search_followup`

The state ledgers are included in context-index memory search because `.project-governor/state/**` has `memory` and `task_history` roles.

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
- `schema`
- `level`
- `quality_level`
- `findings`
- `blockers`
- `warnings`
- `commands`
- `route_guard`
- `evidence_required`
- `evidence`
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
- `schema`
- `blockers`
- `warnings`
- `commands_verified`
- `evidence_required`
- `evidence_present`
- `required_before_merge`

The script exits non-zero when merge readiness fails.

### `skills/session-lifecycle/scripts/session_lifecycle.py`

Input:

- subcommand `start` or `end`
- optional `--project <path>`
- `start`: optional `--task-id <id>`, `--route <route>`, repeated `--target-file <path>`
- `end`: optional `--status <status>`, `--summary <text>`, `--evidence-path <path>`, repeated `--command <command>`

Output:

- `status`
- `session`

Side effects:

- Ensures `.project-governor/state/FEATURES.json`, `AGENTS.json`, `ISSUES.json`, `COMMAND_LEARNINGS.json`, `MEMORY_HYGIENE.json`, `QUALITY_SCORE.json`, and `PROGRESS.md`.
- Writes `.project-governor/state/SESSION.json`.
- Appends session start/end events to `.project-governor/state/PROGRESS.md`.

### `skills/evidence-manifest/scripts/write_evidence_manifest.py`

Input:

- optional `--project <path>`
- optional `--task-id <id>`
- optional `--route <route>`
- optional `--input <json-path>`
- optional `--output <json-path>`
- optional `--validate`

Output:

- without `--validate`: `status`, `path`, `validation`
- with `--validate`: `status`, `validation`, `manifest`

Default manifest fields:

- `schema`
- `task_id`
- `route`
- `created_at`
- `acceptance_criteria[]`
- `tests[]`
- `reviews`
- `docs_refresh`

### `skills/harness-doctor/scripts/doctor.py`

Input:

- optional `--project <path>`
- optional `--execution-readiness`

Output:

- `status`
- `schema`
- `project`
- `execution_readiness`
- `blockers`
- `warnings`
- `summary`

With `--execution-readiness`, Python compile failures for Harness v6 scripts are blockers. Missing context index and state files remain warnings because a fresh project may not have started a Harness session yet.

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
