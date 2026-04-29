# codex-project-governor

[中文文档](README.zh-CN.md) | English

`codex-project-governor` is a Codex and Claude Code plugin for making projects self-governing across agent sessions. Harness v6.2.3 initializes governance files, mines conventions from existing repositories, forces iteration-first development, renders generated governance artifacts from structured slots, routes work through one source of truth, plans GPT-5.5-era runtime execution, builds context-index v2 with `DOCS_MANIFEST.json`, section-level retrieval, route-specific doc packs, generated-artifact slot indexing, governed memory search, session state, session-learning ledgers, and evidence manifests, activates project-scoped subagents, advises on upgrades, adds diff-derived route guards, enforces engineering standards for source size, function complexity, mock leakage, test planning, and reuse-first coding, supports safe plugin upgrade migrations with AGENTS.md/CLAUDE.md rule-template drift detection, clean user-level Git install/update for local marketplaces, Claude Code commands/agents/hooks, opt-in DESIGN.md governance, DESIGN.md-gated UI coding, and scheduled memory compaction.

The core idea is simple: the project should carry durable memory and rules in version-controlled files, while Codex or Claude Code acts as an executor, reviewer, and compactor.

## What it provides

- Codex plugin manifest at `.codex-plugin/plugin.json`.
- Claude Code plugin manifest at `.claude-plugin/plugin.json`.
- Claude Code adapter under `claude/` with `pg-*` slash commands, subagents, hooks, and a plugin skill wrapper.
- 35+ bundled Codex skills under `skills/`.
- Governance templates under `templates/`.
- Plugin-owned managed assets under `managed-assets/`.
- Deterministic helper scripts for user-level plugin install/update, initialization, generated governance artifact rendering and updates, task routing, GPT-5.5 runtime planning, context-index v2, docs manifest generation, section-level context queries, session lifecycle state, session learning capture, evidence manifests, git diff fact collection, project hygiene inspection, clean reinstall management, DESIGN.md linting/summarization/diffing, DESIGN.md UI read-proof gates, iteration checks, style drift checks, engineering standards checks, convention mining, upgrade advisory analysis, release research, research scoring, route guard checks, subagent activation, plugin upgrade migration planning, context pack construction, pattern reuse discovery, quality gates, merge readiness checks, velocity reporting, and memory classification.
- Local marketplace examples for Codex repo-scoped and personal plugin installation.
- Claude Code marketplace example under `examples/claude-marketplace/`.
- Cron, launchd, and GitHub Actions examples for scheduled memory compaction.
- Self-tests that validate plugin structure and core deterministic scripts.

## Skills

Most users should start with `gpt55-auto-orchestrator`. The other skills are still available, but many are workflow stages that the orchestrator, router, or quality gate invokes automatically. The machine-readable grouping lives in `skills/CATALOG.json`.

The Codex plugin default prompts are intentionally compact scenario prompts, not a full list of skills. They should stay aligned with the recommended entry points below and avoid exposing internal workflow stages as default UI choices.

To audit catalog health, resolved entrypoint consolidations, and remaining advisory consolidation candidates, run:

```bash
python3 tools/analyze_skill_catalog.py --project . --format text
```

### Recommended entry points

| Skill | Use when |
|---|---|
| `gpt55-auto-orchestrator` | You want Project Governor to choose the route, context budget, subagents, model plan, and quality gates automatically. |
| Initialization: `init-empty-project` / `init-existing-project` | You need governance files for an empty or existing repository without touching application code. |
| Maintenance: `clean-reinstall-manager` / `plugin-upgrade-migrator` | You need user-level install/update/reinstall, clean project refresh, or safe migration after a plugin update. |
| Evidence and upgrades: `research-radar` / `upgrade-advisor` | You need evidence, risk, or upgrade choices before adopting capabilities or changing dependencies, tools, SDKs, runtimes, or governance assets. |
| `design-md-governor` | You need to adopt, lint, summarize, or diff a project-owned `DESIGN.md`. |
| `quality-gate` | You need to run or inspect the final task completion gate. |
| `memory-compact` | You need to compact recent activity into durable memory, risks, questions, or command learnings. |
| `pr-governance-review` | You need a multi-dimension governance review before or during PR review. |

### Internal workflow stages

These skills normally run as part of a selected workflow rather than as user-facing commands: `task-router`, `subagent-activation`, `context-indexer`, `context-pack-builder`, `iteration-planner`, `pattern-reuse-engine`, `test-first-synthesizer`, `parallel-feature-builder`, `implementation-guard`, `route-guard`, `engineering-standards-governor`, `repair-loop`, `merge-readiness`, `session-lifecycle`, and `evidence-manifest`.

### Advanced and diagnostic tools

Use these directly only when you need a specific audit, diagnostic, UI gate, release research, or retrospective artifact: `convention-miner`, `design-md-aesthetic-governor`, `style-drift-check`, `architecture-drift-check`, `project-hygiene-doctor`, `harness-doctor`, `version-researcher`, `release-retro`, and `coding-velocity-report`.

## Install locally for yourself

Use the installer/updater to clone the plugin and write the local marketplace entry:

```bash
curl -fsSL https://raw.githubusercontent.com/yxhpy/codex-project-governor/main/tools/install_or_update_user_plugin.py \
  -o /tmp/install_or_update_user_plugin.py
python3 /tmp/install_or_update_user_plugin.py --ref v6.2.3 --apply
```

The generated `~/.agents/plugins/marketplace.json` entry remains a local marketplace pointer:

```json
{
  "name": "personal-codex-plugins",
  "interface": {
    "displayName": "Personal Codex Plugins"
  },
  "plugins": [
    {
      "name": "codex-project-governor",
      "source": {
        "source": "local",
        "path": "./.codex/plugins/codex-project-governor"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Developer Tools"
    }
  ]
}
```

Restart Codex, open `/plugins`, choose the personal marketplace, and install **Project Governor**.

### Upgrade a local marketplace install

Codex sees the entry above as `source: local`, so built-in Git marketplace upgrade commands do not fetch the plugin checkout. Update the Git checkout directly, then restart Codex:

```bash
curl -fsSL https://raw.githubusercontent.com/yxhpy/codex-project-governor/main/tools/install_or_update_user_plugin.py \
  -o /tmp/install_or_update_user_plugin.py
python3 /tmp/install_or_update_user_plugin.py --ref v6.2.3 --apply
```

After v6.2.3 is installed, the same helper is available from the plugin checkout:

```bash
python3 ~/.codex/plugins/codex-project-governor/tools/install_or_update_user_plugin.py --ref v6.2.3 --apply
```

For a manual equivalent that works when the helper is not present:

```bash
PLUGIN_DIR="${CODEX_PROJECT_GOVERNOR_PLUGIN_DIR:-$HOME/.codex/plugins/codex-project-governor}"
git -C "$PLUGIN_DIR" fetch --tags origin
git -C "$PLUGIN_DIR" checkout --detach v6.2.3
python3 "$PLUGIN_DIR/tests/selftest.py"
```

After updating the plugin itself, use `plugin-upgrade-migrator` inside initialized projects when project governance files need migration.

## Install for Claude Code

Validate the plugin from a local checkout:

```bash
claude plugin validate .
```

Load this checkout directly during development:

```bash
claude --plugin-dir .
```

For distribution, publish a marketplace repository using `examples/claude-marketplace/.claude-plugin/marketplace.json`, then users can add that marketplace and install:

```text
/plugin marketplace add <your-marketplace-repo-or-path>
/plugin install codex-project-governor@project-governor-claude-marketplace
```

The Claude adapter exposes:

- `/pg-init` to initialize governance files.
- `/pg-route` and `/pg-context` for route and context retrieval.
- `/pg-quality` for engineering standards and readiness checks.
- `/pg-memory` for governed memory search and session learning.
- `/pg-upgrade`, `/pg-design`, and `/pg-doctor` for upgrade, UI, and diagnostics workflows.

See `docs/compat/CLAUDE_CODE.md` for the component mapping and maintenance rules.

## Install repo-scoped for a project team

From the target repository:

```bash
mkdir -p plugins .agents/plugins
git clone https://github.com/yxhpy/codex-project-governor.git plugins/codex-project-governor
cp plugins/codex-project-governor/examples/repo-marketplace/marketplace.json .agents/plugins/marketplace.json
```

Restart Codex, open `/plugins`, choose the repository marketplace, and install **Project Governor**.

The repo-scoped entry is also `source: local`. Teams should update the checkout at `plugins/codex-project-governor` with Git or a project-owned submodule/worktree policy, then restart Codex and run `plugin-upgrade-migrator` for project governance migrations.

## Use

### Use Harness v6.2.3

Harness v6.2.3 makes `task-router` the single route source of truth and lets the runtime planner, docs manifest, section-level context index, governed memory search, session-learning ledgers, session state, route guard, quality gate, evidence manifest, DESIGN.md UI gate, and merge-readiness checks share one contract.

```text
Use Project Governor Harness v6.2.3 to plan this change with DOCS_MANIFEST, section-level context retrieval, governed memory search, session state, evidence, route guard checks, and DESIGN.md UI gates when relevant.
```

Core validation commands:

```bash
python3 skills/context-indexer/scripts/build_context_index.py --project . --write
python3 skills/harness-doctor/scripts/doctor.py --project . --execution-readiness
python3 skills/evidence-manifest/scripts/write_evidence_manifest.py --project . --task-id demo --route standard_feature --validate
```

### Initialize an empty project

```text
Use @project-governor init-empty-project.

Create a Codex-governed project foundation.

Project:
- Name: <name>
- Product goal: <goal>
- Primary users: <users>
- Preferred stack: <stack>

Do not write application code.
Create only governance docs, memory docs, task templates, AGENTS.md, and Codex prompts.
```

### Initialize an existing project

```text
Use @project-governor init-existing-project.

Initialize this existing repository for strict iterative development.

Do not modify application code.
Infer conventions from the existing codebase.
Spawn read-only subagents for architecture, style, components, tests, API contracts, dependencies, product docs, and memory candidates.
Create governance files only.
```

You can also run the deterministic template initializer directly:

```bash
python3 tools/init_project.py --mode existing --target /path/to/your/repo
```

### Plan a change as an iteration

```text
Use @project-governor iteration-planner.

Request:
<your feature, bug fix, or refactor>

Treat this as an iteration, not a rewrite.
Find existing adjacent code and patterns first.
Create an ITERATION_PLAN.slots.json and render ITERATION_PLAN.md with the deterministic artifact renderer when available.
Do not implement until the plan is complete.
```

Generated task artifacts should keep model-authored content in structured slots while deterministic scripts render fixed Markdown headings, tables, and defaults:

```bash
python3 tools/render_governance_artifact.py --input tasks/<task-id>/ITERATION_PLAN.slots.json --output tasks/<task-id>/ITERATION_PLAN.md
python3 tools/update_governance_artifact.py --input tasks/<task-id>/ITERATION_PLAN.slots.json --patch tasks/<task-id>/ITERATION_PLAN.patch.json --render-output tasks/<task-id>/ITERATION_PLAN.md --change-log tasks/<task-id>/ARTIFACT_CHANGES.jsonl
```

When a plan changes during execution, update the slot file with a small patch and re-render the Markdown instead of asking the model to rewrite the full template.


### Accelerate a feature with quality gates

```text
Use @project-governor gpt55-auto-orchestrator.

Request:
<your feature, bug fix, or refactor>

Choose the fastest safe workflow, context budget, model plan, subagents, and quality gates.
```

The orchestrator uses `task-router` as the route source of truth, then selects the needed internal stages. Standard work may use `context-pack-builder`, `pattern-reuse-engine`, `test-first-synthesizer`, `parallel-feature-builder`, `engineering-standards-governor`, `quality-gate`, `repair-loop`, and `merge-readiness`.

For explicit local style, copy, spacing, or typo edits, the router can choose `micro_patch` or `docs_only`. These routes skip heavy workflows and subagents, then run the light quality path.

Use `task-router` directly only when you need to inspect route classification, lane, quality level, change budget, or route guard requirements without starting the full orchestrated workflow.

### Check engineering standards

```text
Use @project-governor engineering-standards-governor.

Check source size, function complexity, production mock leakage, test assertions, boundary-test planning, and reuse-first compliance before quality-gate completion.
```

Run the deterministic checker on a whole project or the current branch diff:

```bash
python3 skills/engineering-standards-governor/scripts/check_engineering_standards.py --project .
python3 skills/engineering-standards-governor/scripts/check_engineering_standards.py --project . --diff-base main
```

### Use GPT-5.5 auto orchestration

```text
Use @project-governor gpt55-auto-orchestrator.

Automatically choose the workflow, model plan, context budget, subagents, and quality gate for this request.
Query the context index before reading large initialization docs.
```

For initialized projects, build or refresh the compact context index:

```bash
python3 skills/context-indexer/scripts/build_context_index.py --project . --write
python3 skills/context-indexer/scripts/query_context_index.py --project . --request "dashboard widget"
python3 skills/context-indexer/scripts/query_context_index.py --project . --request "why did we choose this checkout flow" --memory-search --auto-build
```

`build_context_index.py --write` generates `.project-governor/context/DOCS_MANIFEST.json`; `query_context_index.py` returns `recommended_sections`, `must_read_sections`, `progressive_read_plan`, and `avoid_docs` before recommending full files.

Memory search mode reads governed project artifacts such as `docs/memory/`, `docs/decisions/`, `tasks/`, release notes, and `.project-governor/state/`. It does not scan raw chat transcripts.

### Record session learnings

For non-trivial sessions, query memory before repeating known command paths, and record failures before final response:

```bash
python3 skills/context-indexer/scripts/query_context_index.py --project . --request "<task request> command failures repeated mistakes stale memory" --memory-search --auto-build --format text
python3 skills/memory-compact/scripts/record_session_learning.py --project . --input /path/to/session-learning.json --apply
```

The learning recorder classifies one-off command failures into `.project-governor/state/COMMAND_LEARNINGS.json`, promotes repeated mistakes to `docs/memory/REPEATED_AGENT_MISTAKES.md`, and queues stale memory in `.project-governor/state/MEMORY_HYGIENE.json`. These state files are indexed by memory search, so new sessions can find the lesson without the user asking to remember it.

### Review a PR with subagents

```text
Use @project-governor pr-governance-review.

Review this branch against main.
Spawn one read-only subagent for each dimension:
- iteration compliance
- style drift
- architecture drift
- tests
- dependency risk
- docs and memory

Return blocking issues, warnings, and required patches.
```


### Advise on upgrades before implementation

```text
Use @project-governor upgrade-advisor.

Request:
<your feature, bug fix, migration, or maintenance goal>

Advisory only. Do not edit manifests or install packages.
Show which dependencies/tools are behind, how many versions they are isolated from the candidate, which upgrades are relevant to this request, and whether to upgrade now, plan a separate upgrade iteration, defer, or pin.
```

You can also run the offline deterministic helper after collecting candidate versions:

```bash
python3 skills/upgrade-advisor/scripts/analyze_upgrade_candidates.py examples/upgrade-candidates.json
python3 skills/version-researcher/scripts/research_versions.py --manifest examples/version-research-manifest.json --request "Need better memory and subagent governance"
python3 skills/research-radar/scripts/score_research_candidates.py --manifest examples/research-candidates.json --need memory --need subagents --need research
```

### Upgrade an initialized Project Governor project

```text
Use @project-governor plugin-upgrade-migrator.

Show what is new, plan a safe migration, and do not overwrite my project customizations.
```

The migrator uses `CHANGELOG.md`, `releases/FEATURE_MATRIX.json`, `releases/MIGRATIONS.json`, and `.project-governor/INSTALL_MANIFEST.json` when present. It applies only safe add-if-missing or unchanged-file operations automatically; user-modified governance files remain manual review or three-way merge work.

Because `AGENTS.md` carries mandatory project behavior, the migrator also surfaces `AGENTS.md` template drift when the latest plugin template differs from the installed template hash. This lets unchanged projects receive new rules automatically while keeping locally edited `AGENTS.md` files in manual review.

### Inspect project hygiene

As of v0.4.4, initialization defaults to a clean profile. It copies project-owned governance files only and skips plugin-global `.codex/agents`, `.codex/prompts`, and `.codex/config.toml` assets unless `--profile legacy-full` is requested.

```bash
python3 skills/project-hygiene-doctor/scripts/inspect_project_hygiene.py --project /path/to/project --plugin-root /path/to/codex-project-governor
```

Safe generated global assets are quarantined instead of deleted:

```bash
python3 skills/project-hygiene-doctor/scripts/inspect_project_hygiene.py --project /path/to/project --plugin-root /path/to/codex-project-governor --apply
```

### Clean reinstall or refresh governed projects

Use `clean-reinstall-manager` when a plugin reinstall or project refresh is needed without polluting target repositories with plugin-global assets.

Install or update the user-level plugin checkout and local marketplace entry:

```bash
python3 tools/install_or_update_user_plugin.py --ref v6.2.3 --apply
```

Generate user-level reinstall commands:

```bash
python3 skills/clean-reinstall-manager/scripts/generate_reinstall_instructions.py --ref v6.2.3
```

Discover governed projects from outside a project:

```bash
python3 skills/clean-reinstall-manager/scripts/discover_governed_projects.py --root "$HOME"
```

Plan a safe refresh inside a governed project:

```bash
python3 skills/clean-reinstall-manager/scripts/refresh_project_governance.py --project . --plugin-root /path/to/codex-project-governor
```

### Govern DESIGN.md design systems

Use `design-md-governor` when a project has, or is considering, a project-owned `DESIGN.md` file for visual identity, design tokens, UI rationale, and implementation constraints.

```text
Use @project-governor design-md-governor.

Detect whether DESIGN.md exists.
Lint and summarize it if present.
Recommend an adoption plan if missing.
Do not create or overwrite DESIGN.md unless the user explicitly opts in.
```

Dependency-free fallback helpers:

```bash
python3 skills/design-md-governor/scripts/lint_design_md.py DESIGN.md
python3 skills/design-md-governor/scripts/summarize_design_md.py DESIGN.md
python3 skills/design-md-governor/scripts/diff_design_md.py DESIGN.before.md DESIGN.md
```

### Gate UI coding with DESIGN.md

Use `design-md-aesthetic-governor` for React, Next.js, Tailwind, CSS, pages, components, dashboards, landing pages, responsive layout, visual polish, redesign, or any task that changes user-facing UI.

```text
Use @project-governor design-md-aesthetic-governor.

Read DESIGN.md before UI edits.
Require Gemini/Stitch config from environment variables or project .env-design.
Run preflight to create .codex/design-md-governor/read-proof.json.
Use DESIGN.md tokens and rationale during implementation.
Verify drift after edits.
```

Required design-service keys are `GEMINI_BASE_URL`, `GEMINI_API_KEY`, `GEMINI_MODEL`, and `STITCH_MCP_API_KEY`. `GEMINI_PROTOCOL` may be `auto`, `openai`, or `gemini`; use `gemini` for native `generateContent` and `openai` for OpenAI-compatible gateways. For native Gemini through a gateway, `GEMINI_BASE_URL` must include the gateway's Gemini protocol root, for example `https://host/gemini` when the provider serves `/gemini/v1beta`. `STITCH_MCP_URL` defaults to `https://stitch.googleapis.com/mcp`. Environment variables take precedence over project-root `.env-design` for service keys. To intentionally use basic mode without Gemini/Stitch for a session, set `DESIGN_BASIC_MODE=1` in the shell environment or project-root `.env-design`; `.env-design` is useful when Codex hooks or Windows processes do not inherit later shell changes.

Full-service workflow: GPT/Codex orchestrates the repository work, Stitch MCP supports visual prototype exploration, Gemini reviews the design against `DESIGN.md`, then GPT/Codex implements the accepted direction in code and runs local verification. The hosted Stitch MCP endpoint is configured by default, so no local `stitch-mcp`, `npm`, or `gcloud` install is required unless a project opts into a local MCP server. Basic mode skips Stitch and Gemini while still requiring `DESIGN.md`, bundled lint, token discipline, and drift checks.

Dependency-free helpers:

```bash
python3 skills/design-md-aesthetic-governor/scripts/design_env_check.py --write-template
python3 skills/design-md-aesthetic-governor/scripts/design_service_smoke.py --dry-run
python3 skills/design-md-aesthetic-governor/scripts/design_service_smoke.py --task "<service smoke task>"
python3 skills/design-md-aesthetic-governor/scripts/design_service_review.py --task "<ui task>"
python3 skills/design-md-aesthetic-governor/scripts/design_md_gate.py preflight --task "<task>"
python3 skills/design-md-aesthetic-governor/scripts/select_aesthetic.py --task "<task>"
python3 skills/design-md-aesthetic-governor/scripts/verify_design_usage.py
```

### Compact memory

```text
Use @project-governor memory-compact.

Compact project memory from the last 7 days.
Read recent tasks, retros, execution logs, docs changes, PR feedback, and repeated mistakes.
Update only docs/memory/, docs/decisions/, and AGENTS.md when justified by evidence.
Do not modify application code.
```

## Scheduled memory compaction

Preferred: use Codex App Automations with a dedicated worktree. Use this prompt:

```text
Use $memory-compact.

Compact project memory from the last 7 days.
Read recent task retros, execution logs, merged PRs, docs changes, and repeated review feedback.
Update only docs/memory/, docs/decisions/, and AGENTS.md if a repeated mistake should become a rule.
Do not modify application code.
If there are uncertain items, write them to docs/memory/OPEN_QUESTIONS.md.
Produce a concise report with all changed files.
```

Alternative examples are in:

- `examples/cron/memory-compact.cron`
- `examples/launchd/com.project-governor.memory-compact.plist`
- `examples/github-actions/weekly-memory-compact.yml`

## Deterministic scripts

These scripts do not require third-party Python packages.

```bash
python3 tools/install_or_update_user_plugin.py --ref v6.2.3
python3 tools/init_project.py --mode existing --target /path/to/repo
python3 tools/init_project.py --mode existing --profile legacy-full --target /path/to/repo
python3 skills/project-hygiene-doctor/scripts/inspect_project_hygiene.py --project /path/to/project --plugin-root /path/to/codex-project-governor
python3 skills/convention-miner/scripts/detect_repo_conventions.py /path/to/repo
python3 skills/implementation-guard/scripts/check_iteration_compliance.py examples/guard-input.json
python3 skills/style-drift-check/scripts/check_style_drift.py examples/style-drift-input.json
python3 skills/upgrade-advisor/scripts/analyze_upgrade_candidates.py examples/upgrade-candidates.json
python3 skills/plugin-upgrade-migrator/scripts/compare_features.py --current-version 0.4.1 --target-version 0.4.3 --feature-matrix releases/FEATURE_MATRIX.json
python3 skills/plugin-upgrade-migrator/scripts/plan_migration.py --project . --plugin-root . --current-version 0.4.2 --target-version 0.4.3
python3 skills/version-researcher/scripts/research_versions.py --manifest examples/version-research-manifest.json --request "Need better memory and subagent governance"
python3 skills/research-radar/scripts/score_research_candidates.py --manifest examples/research-candidates.json --need memory --need subagents --need research
python3 skills/task-router/scripts/classify_task.py examples/task-router-input.json
python3 skills/task-router/scripts/classify_task.py examples/task-router-micro-input.json
python3 skills/route-guard/scripts/check_route_guard.py examples/route-guard-micro-pass.json
python3 skills/subagent-activation/scripts/select_subagents.py examples/subagent-activation-standard-feature.json
python3 skills/context-pack-builder/scripts/build_context_pack.py . --request "dashboard widget"
python3 skills/pattern-reuse-engine/scripts/find_reuse_candidates.py . --request "dashboard widget"
python3 skills/engineering-standards-governor/scripts/check_engineering_standards.py --project .
python3 skills/quality-gate/scripts/run_quality_gate.py examples/quality-gate-input.json
python3 skills/merge-readiness/scripts/check_merge_readiness.py examples/merge-readiness-input.json
python3 skills/coding-velocity-report/scripts/build_velocity_report.py examples/velocity-input.json
python3 skills/memory-compact/scripts/classify_memory_items.py examples/memory-candidates.json
python3 skills/memory-compact/scripts/record_session_learning.py --project . --input /path/to/session-learning.json
```

## Test

```bash
python3 tests/selftest.py
```

You can also run the same check through `make test`.

The tests validate:

- plugin manifest shape
- user plugin installer plans local marketplace updates and protects dirty Git checkouts
- every skill has `SKILL.md` and metadata
- templates contain the required governance files
- `.codex/rules/project.rules` uses Codex-supported rule decisions
- deterministic initialization does not overwrite existing application code
- project hygiene doctor quarantines unchanged generated `.codex` assets and protects memory and decision files
- implementation guard detects rewrite risk, dependency changes, and unjustified new files
- style drift check detects raw colors and unregistered components
- upgrade advisor classifies candidates by version distance, requirement relevance, risk, and user-selectable action
- plugin upgrade migrator compares features, plans safe migrations, detects user-modified files, and applies only safe operations
- version researcher classifies release candidates by skipped versions, evidence quality, relevance, and risk
- research radar classifies candidate capabilities by source quality, matched needs, risk, maturity, and user choices
- task router classifies micro-patches and emits route guard requirements
- route guard blocks scope creep from fast routes
- subagent activation selects project-scoped agents and model routing
- engineering standards detects source-size, function-complexity, mock-leakage, and test-assertion risks
- memory classifier separates durable facts, decisions, open questions, repeated mistakes, and sensitive items
- session learning records command failures, repeated mistakes, and stale-memory candidates into retrievable memory layers

## Governance model

The plugin intentionally separates responsibilities:

```text
AGENTS.md              project behavior constitution
docs/conventions/      style, component, architecture, and iteration contracts
docs/research/         candidate capability research policy, briefs, and registers
docs/memory/           durable project facts, risks, repeated agent mistakes
docs/decisions/        ADR/PDR records
docs/upgrades/         upgrade policy, upgrade decisions, deferrals, and pins
docs/quality/          quality gates, change budgets, and acceleration policy
tasks/                 short-lived task memory and iteration plans
skills/                reusable Codex workflows
scripts                deterministic checks
scheduled jobs         periodic memory compaction
```

If something can be checked deterministically, use a script. If it requires project understanding, use Codex/subagents. If it becomes a stable team rule, write it into `AGENTS.md` or checked-in docs.
