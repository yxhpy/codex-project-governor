# codex-project-governor

[中文文档](README.zh-CN.md) | English

`codex-project-governor` is a Codex plugin for making projects self-governing across Codex sessions. It initializes governance files, mines conventions from existing repositories, forces iteration-first development, researches candidate capabilities and release evidence, uses subagents for parallel audits, advises on upgrades, and supports scheduled memory compaction.

The core idea is simple: the project should carry durable memory and rules in version-controlled files, while Codex acts as an executor, reviewer, and compactor.

## What it provides

- Codex plugin manifest at `.codex-plugin/plugin.json`.
- 22 bundled Codex skills under `skills/`.
- Governance templates under `templates/`.
- Deterministic helper scripts for initialization, iteration checks, style drift checks, convention mining, upgrade advisory analysis, release research, research scoring, task routing, context pack construction, pattern reuse discovery, quality gates, merge readiness checks, velocity reporting, and memory classification.
- Local marketplace examples for repo-scoped and personal plugin installation.
- Cron, launchd, and GitHub Actions examples for scheduled memory compaction.
- Self-tests that validate plugin structure and core deterministic scripts.

## Skills

| Skill | Purpose |
|---|---|
| `init-empty-project` | Initialize a new repository with governance docs before application code exists. |
| `init-existing-project` | Initialize an existing repository by mining current conventions without modifying application code. |
| `convention-miner` | Read-only convention mining for stack, structure, style, APIs, tests, and components. |
| `iteration-planner` | Plan a feature/fix/refactor as an iteration rather than a rewrite. |
| `implementation-guard` | Detect rewrite risk, unapproved dependencies, unexplained new files, and public contract drift. |
| `style-drift-check` | Detect component, design-token, naming, and visual style drift. |
| `architecture-drift-check` | Detect module boundary, import direction, and contract drift. |
| `pr-governance-review` | Run subagent-based PR governance review. |
| `memory-compact` | Compact recent activity into durable project memory. |
| `release-retro` | Convert release learning into retrospectives, memory, and decision records. |
| `upgrade-advisor` | Show version distance, requirement relevance, risk, and user-selectable upgrade choices before changing versions. |
| `version-researcher` | Research candidate release versions, skipped versions, evidence quality, relevance, and risk before upgrade advice. |
| `research-radar` | Research candidate capabilities, evidence quality, risk, and project fit before implementation. |
| `task-router` | Classify a user request into the fastest safe Project Governor workflow, lane, quality level, change budget, and required downstream skills. |
| `context-pack-builder` | Build a minimal task-specific context pack so Codex and subagents can implement faster without repeatedly rediscovering the repository. |
| `pattern-reuse-engine` | Find existing components, services, hooks, schemas, tests, and style patterns that must be reused before creating new implementation patterns. |
| `parallel-feature-builder` | Implement a feature through a quality-gated subagent pipeline that uses parallel read-only analysis, one bounded implementation writer, test writing, review, and repair. |
| `test-first-synthesizer` | Produce a targeted test plan or test skeletons before implementation, using existing project test style and covering behavior, regression risk, boundaries, and errors. |
| `quality-gate` | Run tiered quality checks for speed-safe development, including iteration compliance, style drift, architecture drift, change budget, tests, docs, and memory update requirements. |
| `repair-loop` | Repair failed quality checks through a bounded loop without deleting tests, weakening assertions, skipping gates, or expanding implementation scope. |
| `merge-readiness` | Decide whether a task or branch is PR-ready by checking blockers, quality gate status, docs, memory, tests, change budget, and unresolved approvals. |
| `coding-velocity-report` | Produce a velocity report for a task, measuring context time, first patch time, repair rounds, quality gate pass rate, patch size, reuse ratio, drift findings, and manual approvals. |

## Install locally for yourself

Clone the plugin into your personal Codex plugin folder:

```bash
mkdir -p ~/.codex/plugins
git clone https://github.com/yxhpy/codex-project-governor.git ~/.codex/plugins/codex-project-governor
```

Create or update `~/.agents/plugins/marketplace.json`:

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

## Install repo-scoped for a project team

From the target repository:

```bash
mkdir -p plugins .agents/plugins
git clone https://github.com/yxhpy/codex-project-governor.git plugins/codex-project-governor
cp plugins/codex-project-governor/examples/repo-marketplace/marketplace.json .agents/plugins/marketplace.json
```

Restart Codex, open `/plugins`, choose the repository marketplace, and install **Project Governor**.

## Use

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
Create an ITERATION_PLAN.md.
Do not implement until the plan is complete.
```


### Accelerate a feature with quality gates

```text
Use @project-governor task-router.

Request:
<your feature, bug fix, or refactor>

Choose the fastest safe workflow. Do not implement yet.
Return the route, lane, quality level, change budget, and required downstream skills.
```

Then build context and reuse constraints with `context-pack-builder` and `pattern-reuse-engine`, implement with `parallel-feature-builder`, run `quality-gate`, use `repair-loop` only if the gate fails, and finish with `merge-readiness`.

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
python3 tools/init_project.py --mode existing --target /path/to/repo
python3 skills/convention-miner/scripts/detect_repo_conventions.py /path/to/repo
python3 skills/implementation-guard/scripts/check_iteration_compliance.py examples/guard-input.json
python3 skills/style-drift-check/scripts/check_style_drift.py examples/style-drift-input.json
python3 skills/upgrade-advisor/scripts/analyze_upgrade_candidates.py examples/upgrade-candidates.json
python3 skills/version-researcher/scripts/research_versions.py --manifest examples/version-research-manifest.json --request "Need better memory and subagent governance"
python3 skills/research-radar/scripts/score_research_candidates.py --manifest examples/research-candidates.json --need memory --need subagents --need research
python3 skills/task-router/scripts/classify_task.py examples/task-router-input.json
python3 skills/context-pack-builder/scripts/build_context_pack.py . --request "dashboard widget"
python3 skills/pattern-reuse-engine/scripts/find_reuse_candidates.py . --request "dashboard widget"
python3 skills/quality-gate/scripts/run_quality_gate.py examples/quality-gate-input.json
python3 skills/merge-readiness/scripts/check_merge_readiness.py examples/merge-readiness-input.json
python3 skills/coding-velocity-report/scripts/build_velocity_report.py examples/velocity-input.json
python3 skills/memory-compact/scripts/classify_memory_items.py examples/memory-candidates.json
```

## Test

```bash
python3 tests/selftest.py
```

You can also run the same check through `make test`.

The tests validate:

- plugin manifest shape
- every skill has `SKILL.md` and metadata
- templates contain the required governance files
- `.codex/rules/project.rules` uses Codex-supported rule decisions
- deterministic initialization does not overwrite existing application code
- implementation guard detects rewrite risk, dependency changes, and unjustified new files
- style drift check detects raw colors and unregistered components
- upgrade advisor classifies candidates by version distance, requirement relevance, risk, and user-selectable action
- version researcher classifies release candidates by skipped versions, evidence quality, relevance, and risk
- research radar classifies candidate capabilities by source quality, matched needs, risk, maturity, and user choices
- memory classifier separates durable facts, decisions, open questions, repeated mistakes, and sensitive items

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
