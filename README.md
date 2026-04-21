# codex-project-governor

`codex-project-governor` is a Codex plugin for making projects self-governing across Codex sessions. It initializes governance files, mines conventions from existing repositories, forces iteration-first development, uses subagents for parallel audits, and supports scheduled memory compaction.

The core idea is simple: the project should carry durable memory and rules in version-controlled files, while Codex acts as an executor, reviewer, and compactor.

## What it provides

- Codex plugin manifest at `.codex-plugin/plugin.json`.
- 10 bundled Codex skills under `skills/`.
- Governance templates under `templates/`.
- Deterministic helper scripts for initialization, iteration checks, style drift checks, convention mining, and memory classification.
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
python3 skills/memory-compact/scripts/classify_memory_items.py examples/memory-candidates.json
```

## Test

```bash
python3 tests/selftest.py
```

The tests validate:

- plugin manifest shape
- every skill has `SKILL.md` and metadata
- templates contain the required governance files
- deterministic initialization does not overwrite existing application code
- implementation guard detects rewrite risk, dependency changes, and unjustified new files
- style drift check detects raw colors and unregistered components
- memory classifier separates durable facts, decisions, open questions, repeated mistakes, and sensitive items

## Governance model

The plugin intentionally separates responsibilities:

```text
AGENTS.md              project behavior constitution
docs/conventions/      style, component, architecture, and iteration contracts
docs/memory/           durable project facts, risks, repeated agent mistakes
docs/decisions/        ADR/PDR records
tasks/                 short-lived task memory and iteration plans
skills/                reusable Codex workflows
scripts                deterministic checks
scheduled jobs         periodic memory compaction
```

If something can be checked deterministically, use a script. If it requires project understanding, use Codex/subagents. If it becomes a stable team rule, write it into `AGENTS.md` or checked-in docs.
