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
