#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class PluginUpgradeMigratorTest(unittest.TestCase):
    def run_json(self, args: list[str]) -> dict:
        process = subprocess.run(args, text=True, capture_output=True, check=True, timeout=20)
        return json.loads(process.stdout)

    def test_compare_features(self) -> None:
        data = self.run_json(
            [
                PY,
                str(ROOT / "skills" / "plugin-upgrade-migrator" / "scripts" / "compare_features.py"),
                "--current-version",
                "0.4.1",
                "--target-version",
                "0.4.3",
                "--feature-matrix",
                str(ROOT / "releases" / "FEATURE_MATRIX.json"),
            ]
        )
        self.assertEqual(data["versions_behind"], 2)
        ids = {feature["id"] for feature in data["features"]}
        self.assertIn("explicit_subagent_activation", ids)
        self.assertIn("safe_migration_plan", ids)
        self.assertTrue(data["migration_required"])

    def test_inspect_installation_detects_user_modified(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            (project / ".project-governor").mkdir()
            original = "# AGENTS\n"
            modified = "# AGENTS\n\nTeam rule.\n"
            (project / "AGENTS.md").write_text(modified, encoding="utf-8")
            manifest = {
                "plugin": {"installed_version": "0.4.1"},
                "generated_files": [{"path": "AGENTS.md", "installed_sha256": sha(original), "upgrade_policy": "three_way_merge"}],
            }
            (project / ".project-governor" / "INSTALL_MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
            data = self.run_json(
                [
                    PY,
                    str(ROOT / "skills" / "plugin-upgrade-migrator" / "scripts" / "inspect_installation.py"),
                    "--project",
                    str(project),
                ]
            )
            self.assertEqual(data["summary"]["user_modified_count"], 1)
            self.assertEqual(data["tracked_files"][0]["status"], "user_modified")

    def test_plan_migration_classifies_safe_and_manual(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            (project / ".project-governor").mkdir()
            (project / "AGENTS.md").write_text("# AGENTS\n\nLocal customization.\n", encoding="utf-8")
            manifest = {
                "plugin": {"installed_version": "0.4.2"},
                "generated_files": [{"path": "AGENTS.md", "installed_sha256": sha("# AGENTS\n"), "upgrade_policy": "three_way_merge"}],
            }
            (project / ".project-governor" / "INSTALL_MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
            data = self.run_json(
                [
                    PY,
                    str(ROOT / "skills" / "plugin-upgrade-migrator" / "scripts" / "plan_migration.py"),
                    "--project",
                    str(project),
                    "--plugin-root",
                    str(ROOT),
                    "--current-version",
                    "0.4.2",
                    "--target-version",
                    "0.4.3",
                ]
            )
            actions = {operation["path"]: operation["action"] for operation in data["operations"]}
            self.assertEqual(actions["AGENTS.md"], "manual_review_or_three_way_merge")
            self.assertEqual(actions[".project-governor/INSTALL_MANIFEST.json"], "manual_review")
            self.assertEqual(actions["docs/upgrades/PLUGIN_UPGRADE_POLICY.md"], "add_if_missing")
            self.assertGreaterEqual(data["summary"]["safe_operation_count"], 1)
            self.assertGreaterEqual(data["summary"]["manual_review_count"], 1)

    def test_plan_migration_treats_hygiene_check_as_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            data = self.run_json(
                [
                    PY,
                    str(ROOT / "skills" / "plugin-upgrade-migrator" / "scripts" / "plan_migration.py"),
                    "--project",
                    str(project),
                    "--plugin-root",
                    str(ROOT),
                    "--current-version",
                    "0.4.3",
                    "--target-version",
                    "0.4.4",
                ]
            )
            operations = {operation["op"]: operation for operation in data["operations"]}
            self.assertEqual(operations["run_hygiene_check"]["status"], "diagnostic_only")
            self.assertEqual(operations["run_hygiene_check"]["action"], "manual_review")
            self.assertEqual(data["summary"]["manual_review_count"], 1)

    def test_plan_migration_updates_design_hook_for_env_design_basic_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            hook_path = project / ".codex" / "hooks" / "design_md_codex_hook.py"
            policy_path = project / "docs" / "quality" / "DESIGN_MD_AESTHETIC_GATE_POLICY.md"
            hook_path.parent.mkdir(parents=True)
            policy_path.parent.mkdir(parents=True)
            old_hook = "# old hook\n"
            old_policy = "# old policy\n"
            hook_path.write_text(old_hook, encoding="utf-8")
            policy_path.write_text(old_policy, encoding="utf-8")
            (project / ".project-governor").mkdir()
            manifest = {
                "plugin": {"installed_version": "6.0.5"},
                "generated_files": [
                    {
                        "path": ".codex/hooks/design_md_codex_hook.py",
                        "template": "templates/.codex/hooks/design_md_codex_hook.py",
                        "installed_sha256": sha(old_hook),
                        "upgrade_policy": "three_way_merge",
                    },
                    {
                        "path": "docs/quality/DESIGN_MD_AESTHETIC_GATE_POLICY.md",
                        "template": "templates/docs/quality/DESIGN_MD_AESTHETIC_GATE_POLICY.md",
                        "installed_sha256": sha(old_policy),
                        "upgrade_policy": "three_way_merge",
                    },
                ],
            }
            (project / ".project-governor" / "INSTALL_MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
            data = self.run_json(
                [
                    PY,
                    str(ROOT / "skills" / "plugin-upgrade-migrator" / "scripts" / "plan_migration.py"),
                    "--project",
                    str(project),
                    "--plugin-root",
                    str(ROOT),
                    "--current-version",
                    "6.0.5",
                    "--target-version",
                    "6.0.6",
                ]
            )
            operations = {operation["path"]: operation for operation in data["operations"]}
            self.assertEqual(operations[".codex/hooks/design_md_codex_hook.py"]["action"], "replace_from_template")
            self.assertEqual(operations[".codex/hooks/design_md_codex_hook.py"]["status"], "safe_update_unchanged_from_install")
            self.assertEqual(operations["docs/quality/DESIGN_MD_AESTHETIC_GATE_POLICY.md"]["action"], "replace_from_template")
            self.assertEqual(operations["docs/quality/DESIGN_MD_AESTHETIC_GATE_POLICY.md"]["status"], "safe_update_unchanged_from_install")

    def test_plan_migration_adds_engineering_standards_templates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            data = self.run_json(
                [
                    PY,
                    str(ROOT / "skills" / "plugin-upgrade-migrator" / "scripts" / "plan_migration.py"),
                    "--project",
                    str(project),
                    "--plugin-root",
                    str(ROOT),
                    "--current-version",
                    "6.0.6",
                    "--target-version",
                    "6.1.0",
                ]
            )
            operations = {operation["path"]: operation for operation in data["operations"]}
            self.assertEqual(operations["docs/quality/ENGINEERING_STANDARDS_POLICY.md"]["action"], "add_if_missing")
            self.assertEqual(operations["tasks/_template/ENGINEERING_STANDARDS_REPORT.md"]["action"], "add_if_missing")
            self.assertEqual(operations[".codex/prompts/engineering-standards-governor.md"]["action"], "add_if_missing")
            self.assertIn("AGENTS.md", operations)
            self.assertGreaterEqual(data["summary"]["safe_operation_count"], 3)

    def test_plan_migration_adds_claude_md_template(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            data = self.run_json(
                [
                    PY,
                    str(ROOT / "skills" / "plugin-upgrade-migrator" / "scripts" / "plan_migration.py"),
                    "--project",
                    str(project),
                    "--plugin-root",
                    str(ROOT),
                    "--current-version",
                    "6.1.0",
                    "--target-version",
                    "6.2.0",
                ]
            )
            operations = {operation["path"]: operation for operation in data["operations"]}
            self.assertEqual(operations["CLAUDE.md"]["action"], "add_if_missing")
            self.assertEqual(operations["CLAUDE.md"]["status"], "safe_add")
            self.assertEqual(operations["CLAUDE.md"]["source"], "templates/CLAUDE.md")
            self.assertEqual(operations["AGENTS.md"]["action"], "add_if_missing")

    def test_plan_migration_surfaces_agents_template_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            (project / ".project-governor").mkdir()
            installed = "# AGENTS.md\n\n## Project Governor\n\nOld mandatory rule.\n"
            (project / "AGENTS.md").write_text(installed, encoding="utf-8")
            manifest = {
                "plugin": {"installed_version": "6.0.2"},
                "generated_files": [
                    {
                        "path": "AGENTS.md",
                        "template": "templates/AGENTS.md",
                        "template_sha256": sha(installed),
                        "installed_sha256": sha(installed),
                        "upgrade_policy": "three_way_merge",
                    }
                ],
            }
            (project / ".project-governor" / "INSTALL_MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
            data = self.run_json(
                [
                    PY,
                    str(ROOT / "skills" / "plugin-upgrade-migrator" / "scripts" / "plan_migration.py"),
                    "--project",
                    str(project),
                    "--plugin-root",
                    str(ROOT),
                    "--current-version",
                    "6.0.2",
                    "--target-version",
                    "6.0.2",
                ]
            )
            operation = data["operations"][0]
            self.assertEqual(operation["op"], "review_rule_template_drift")
            self.assertEqual(operation["path"], "AGENTS.md")
            self.assertEqual(operation["action"], "replace_from_template")
            self.assertEqual(operation["status"], "safe_update_unchanged_from_install")
            self.assertEqual(operation["migration_id"], "rule_template_drift")

    def test_plan_migration_adds_missing_execution_policy_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            (project / ".project-governor").mkdir()
            manifest = {
                "plugin": {"installed_version": "6.2.4"},
                "generated_files": [
                    {
                        "path": "docs/quality/QUALITY_GATE_POLICY.md",
                        "template": "templates/docs/quality/QUALITY_GATE_POLICY.md",
                        "installed_sha256": sha("# Quality Gate Policy\n"),
                        "upgrade_policy": "three_way_merge",
                    }
                ],
            }
            (project / ".project-governor" / "INSTALL_MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
            data = self.run_json(
                [
                    PY,
                    str(ROOT / "skills" / "plugin-upgrade-migrator" / "scripts" / "plan_migration.py"),
                    "--project",
                    str(project),
                    "--plugin-root",
                    str(ROOT),
                    "--current-version",
                    "6.2.4",
                    "--target-version",
                    "6.2.4",
                ]
            )
            operations = {operation["path"]: operation for operation in data["operations"]}
            operation = operations[".project-governor/runtime/EXECUTION_POLICY.json"]
            self.assertEqual(operation["op"], "add_required_project_runtime_template")
            self.assertEqual(operation["action"], "add_if_missing")
            self.assertEqual(operation["status"], "safe_add")
            self.assertEqual(operation["migration_id"], "required_project_runtime_templates")

    def test_plan_migration_keeps_modified_agents_template_drift_manual(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            (project / ".project-governor").mkdir()
            installed = "# AGENTS.md\n\n## Project Governor\n\nOld mandatory rule.\n"
            modified = installed + "\n## Local Rule\n\nKeep this.\n"
            (project / "AGENTS.md").write_text(modified, encoding="utf-8")
            manifest = {
                "plugin": {"installed_version": "6.0.2"},
                "generated_files": [
                    {
                        "path": "AGENTS.md",
                        "template": "templates/AGENTS.md",
                        "template_sha256": sha(installed),
                        "installed_sha256": sha(installed),
                        "upgrade_policy": "three_way_merge",
                    }
                ],
            }
            (project / ".project-governor" / "INSTALL_MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
            data = self.run_json(
                [
                    PY,
                    str(ROOT / "skills" / "plugin-upgrade-migrator" / "scripts" / "plan_migration.py"),
                    "--project",
                    str(project),
                    "--plugin-root",
                    str(ROOT),
                    "--current-version",
                    "6.0.2",
                    "--target-version",
                    "6.0.2",
                ]
            )
            operation = data["operations"][0]
            self.assertEqual(operation["op"], "review_rule_template_drift")
            self.assertEqual(operation["path"], "AGENTS.md")
            self.assertEqual(operation["action"], "manual_review_or_three_way_merge")
            self.assertEqual(operation["status"], "user_modified")
            self.assertEqual(data["summary"]["manual_review_count"], 1)

    def test_apply_safe_migration_adds_only_safe_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            project.mkdir()
            output = project / ".project-governor" / "upgrade" / "0.4.2-to-0.4.3" / "UPGRADE_PLAN.json"
            self.run_json(
                [
                    PY,
                    str(ROOT / "skills" / "plugin-upgrade-migrator" / "scripts" / "plan_migration.py"),
                    "--project",
                    str(project),
                    "--plugin-root",
                    str(ROOT),
                    "--current-version",
                    "0.4.2",
                    "--target-version",
                    "0.4.3",
                    "--output",
                    str(output),
                ]
            )
            data = self.run_json(
                [
                    PY,
                    str(ROOT / "skills" / "plugin-upgrade-migrator" / "scripts" / "apply_safe_migration.py"),
                    "--plan",
                    str(output),
                    "--apply",
                ]
            )
            self.assertGreaterEqual(data["summary"]["applied_count"], 1)
            self.assertTrue((project / ".project-governor" / "INSTALL_MANIFEST.json").exists())
            self.assertTrue((project / "docs" / "upgrades" / "PLUGIN_UPGRADE_POLICY.md").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
