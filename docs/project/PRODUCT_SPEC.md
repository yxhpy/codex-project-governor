# Product Spec

## Product

Project Governor is a Codex governance plugin.

## Capabilities

- Initialize empty or existing repositories with governance docs, memory docs, Codex prompts, rules, and task templates.
- Mine conventions from existing repositories.
- Plan changes as iterations instead of rewrites.
- Run implementation, style, architecture, and PR governance checks.
- Compact recent activity into durable project memory.
- Research candidate capabilities and release versions before implementation or upgrade planning.
- Advise on dependency/tool upgrades before version changes are applied.

## User Workflows

1. Install the plugin through a personal or repo-scoped marketplace.
2. Run `init-empty-project` or `init-existing-project` to seed governance.
3. Use `iteration-planner` before non-trivial changes.
4. Use deterministic helper scripts for convention mining, guard checks, style checks, research scoring, release research, upgrade analysis, and memory classification.
5. Run `python3 tests/selftest.py` before publishing plugin changes.

## Constraints

- Scripts should remain Python standard-library CLIs unless a decision record approves new dependencies.
- Templates are copied into downstream repositories; template path changes are public behavior changes.
- Helper script JSON output shapes are public contracts and need tests when changed.

## Evidence

- README sections: What it provides, Skills, Use, Deterministic scripts, Test.
- `.codex-plugin/plugin.json` default prompts and plugin metadata.
- `tests/selftest.py` coverage of manifest, templates, scripts, and fixtures.
