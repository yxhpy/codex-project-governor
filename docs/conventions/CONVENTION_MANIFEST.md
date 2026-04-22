# Convention Manifest

## Source of truth

- Product identity: `docs/project/CHARTER.md`
- Architecture: `docs/architecture/ARCHITECTURE.md`
- API contracts: `docs/architecture/API_CONTRACTS.md`
- Code style: `docs/conventions/CODE_STYLE.md`
- UI style: `docs/conventions/UI_STYLE.md`
- Component registry: `docs/conventions/COMPONENT_REGISTRY.md`
- Pattern registry: `docs/conventions/PATTERN_REGISTRY.md`
- Iteration contract: `docs/conventions/ITERATION_CONTRACT.md`
- Upgrade policy: `docs/upgrades/UPGRADE_POLICY.md`
- Upgrade register: `docs/upgrades/UPGRADE_REGISTER.md`
- Plugin upgrade policy: `templates/docs/upgrades/PLUGIN_UPGRADE_POLICY.md`
- Release feature matrix: `releases/FEATURE_MATRIX.json`
- Release migrations: `releases/MIGRATIONS.json`
- Research brief: `docs/research/V0.3_RESEARCH_BRIEF.md`
- Acceleration policy: `docs/quality/ACCELERATION_POLICY.md`
- Testing acceleration policy: `docs/quality/TESTING_ACCELERATION_POLICY.md`
- Change budget policy: `docs/quality/CHANGE_BUDGET_POLICY.md`
- Quality gate policy: `docs/quality/QUALITY_GATE_POLICY.md`
- Project hygiene policy template: `templates/docs/quality/PROJECT_HYGIENE_POLICY.md`
- Route guard policy: `docs/quality/ROUTE_GUARD_POLICY.md`
- Subagent activation policy: `docs/quality/SUBAGENT_ACTIVATION_POLICY.md`
- Smart routing guard brief: `docs/research/V0.4.1_SMART_ROUTING_GUARD.md`
- Explicit subagent activation brief: `docs/research/V0.4.2_EXPLICIT_SUBAGENT_ACTIVATION.md`

If implementation conflicts with these files, create or update a decision record first.

## Confirmed Repository Conventions

- This is a plugin/template repository, not an application repository.
- Public plugin metadata starts in `.codex-plugin/plugin.json`.
- Skill workflows are documented in `skills/<skill>/SKILL.md`.
- Deterministic script helpers are CLI modules under `tools/` and `skills/*/scripts/`.
- Governance files copied into downstream repositories come from `templates/`.
- Example JSON inputs are stored under `examples/`.
- Tests use Python standard-library `unittest` in `tests/selftest.py`.

## Evidence

- `README.md`
- `.codex-plugin/plugin.json`
- `tests/selftest.py`
- `tools/init_project.py`
- `skills/*/SKILL.md`
