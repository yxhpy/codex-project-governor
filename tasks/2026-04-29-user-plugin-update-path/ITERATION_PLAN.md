# Iteration Plan: User Plugin Update Path

## User request

Make Project Governor easier to upgrade for users whose Codex marketplace entry points at a local plugin checkout. The built-in marketplace upgrade path does not update this local marketplace source.

## Existing behavior

The README documents a local marketplace entry pointing at `~/.codex/plugins/codex-project-governor` or `./plugins/codex-project-governor`. That directory is expected to be a Git clone, but Codex sees the marketplace source as `local`, so the plugin checkout must be updated outside the built-in marketplace upgrade flow.

`clean-reinstall-manager` can generate reinstall commands, but there is no single deterministic helper that installs or updates the user-level plugin checkout and ensures the marketplace entry exists.

## Existing patterns to reuse

| Pattern | Source file | How it will be reused |
|---|---|---|
| Dependency-free Python CLI helpers | `tools/init_project.py`, `skills/*/scripts/*.py` | Add a standard-library-only installer/updater. |
| Instructions-only safety default | `skills/clean-reinstall-manager/scripts/generate_reinstall_instructions.py` | Make the new updater dry-run by default and require `--apply` for writes. |
| Local marketplace entry shape | `examples/personal-marketplace/marketplace.json` | Preserve `source: local` and write only the local pointer entry. |
| Standard unittest coverage | `tests/test_clean_reinstall_manager.py` | Add temp Git fixture tests without network access. |

## Files expected to change

- `tools/install_or_update_user_plugin.py`
- `tests/test_user_plugin_installer.py`
- `Makefile`
- `README.md`
- `README.zh-CN.md`
- `docs/architecture/API_CONTRACTS.md`
- `skills/clean-reinstall-manager/SKILL.md`
- `.codex-plugin/plugin.json`
- `CHANGELOG.md`
- `releases/FEATURE_MATRIX.json`
- `releases/6.0.4.md`
- `docs/project/CHARTER.md`
- `docs/conventions/CONVENTION_MANIFEST.md`
- `docs/memory/PROJECT_MEMORY.md`

## Files not to change

- Existing marketplace JSON schema examples
- Template paths under `templates/`
- Existing migration JSON output schemas
- Dependency manifests or lockfiles

## New files

| File | Why existing files cannot cover it |
|---|---|
| `tools/install_or_update_user_plugin.py` | Users need a runnable helper before Project Governor is installed or when the local marketplace entry is stale. |
| `tests/test_user_plugin_installer.py` | The new helper mutates Git checkouts and marketplace files, so it needs isolated regression coverage. |
| `releases/6.0.4.md` | Versioned release notes are required for the user-facing upgrade path change. |
| `tasks/2026-04-29-user-plugin-update-path/ITERATION_PLAN.md` | Required for a non-trivial helper, docs, version, and test change. |

## Dependencies

No new dependencies. The helper uses Python standard library plus the user's installed `git` command.

## Tests

- `python3 tests/test_user_plugin_installer.py`
- `python3 tests/test_clean_reinstall_manager.py`
- `python3 tests/selftest.py`
- `python3 -m compileall tools skills tests`

## Risks

- Updating a dirty local plugin checkout could discard local edits. The helper must stop when the checkout has uncommitted changes.
- A local marketplace entry still cannot be updated by the built-in Git marketplace upgrade command. Documentation must say that clearly and point to the Git checkout updater.
- Repo-scoped team installs may still need project-specific Git or submodule policy. Keep this patch focused on the common user-level path.

## Rollback

Remove the new helper, tests, release notes, and documentation references. Existing manual clone and clean reinstall commands will continue to work.
