#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
SCRIPTS = ROOT / "skills" / "clean-reinstall-manager" / "scripts"


class CleanReinstallManagerTest(unittest.TestCase):
    def run_json(self, args: list[str]) -> dict:
        proc = subprocess.run(args, text=True, capture_output=True, check=True, timeout=15)
        return json.loads(proc.stdout)

    def make_plugin_root(self, temp: Path) -> Path:
        plugin = temp / "plugin"
        (plugin / "templates" / "docs" / "conventions").mkdir(parents=True)
        (plugin / "templates" / "docs" / "memory").mkdir(parents=True)
        (plugin / "templates" / "docs" / "upgrades").mkdir(parents=True)
        (plugin / "templates" / "tasks" / "_template").mkdir(parents=True)
        (plugin / "templates" / ".codex" / "rules").mkdir(parents=True)
        (plugin / "templates" / "AGENTS.md").write_text("# AGENTS.md\n\n## Project Governor\n\nFollow project rules.\n", encoding="utf-8")
        (plugin / "templates" / "docs" / "conventions" / "ITERATION_CONTRACT.md").write_text("# Iteration Contract\n", encoding="utf-8")
        (plugin / "templates" / "docs" / "memory" / "PROJECT_MEMORY.md").write_text("# Project Memory\n", encoding="utf-8")
        (plugin / "templates" / "docs" / "upgrades" / "CLEAN_REINSTALL_POLICY.md").write_text("# Clean Reinstall Policy\n", encoding="utf-8")
        (plugin / "templates" / "tasks" / "_template" / "ITERATION_PLAN.md").write_text("# Iteration Plan\n", encoding="utf-8")
        (plugin / "templates" / ".codex" / "rules" / "project.rules").write_text('[[commands]]\npattern="*"\ndecision="prompt"\n', encoding="utf-8")
        return plugin

    def test_reinstall_instructions_are_user_level(self) -> None:
        data = self.run_json([PYTHON, str(SCRIPTS / "generate_reinstall_instructions.py"), "--plugin-dir", "/tmp/codex-project-governor"])
        shell = data["shell"]
        self.assertIn("git clone", shell)
        self.assertIn("codex-project-governor", shell)
        self.assertIn("backup", shell.lower())
        self.assertEqual(data["status"], "instructions_only")

    def test_discover_governed_projects(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            project = root / "app"
            project.mkdir()
            (project / "AGENTS.md").write_text("# AGENTS.md\nProject Governor\n", encoding="utf-8")
            other = root / "other"
            other.mkdir()
            data = self.run_json([PYTHON, str(SCRIPTS / "discover_governed_projects.py"), "--root", str(root), "--max-depth", "2"])
            paths = {Path(item["path"]).name for item in data["projects"]}
            self.assertIn("app", paths)
            self.assertNotIn("other", paths)

    def test_refresh_quarantines_noise_and_preserves_memory(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            temp = Path(td)
            plugin = self.make_plugin_root(temp)
            project = temp / "project"
            (project / "docs" / "memory").mkdir(parents=True)
            (project / ".codex" / "agents").mkdir(parents=True)
            (project / "AGENTS.md").write_text("# AGENTS.md\n\n## Local Rule\n\nKeep this.\n", encoding="utf-8")
            (project / "docs" / "memory" / "PROJECT_MEMORY.md").write_text("# Project Memory\n\nLocal memory.\n", encoding="utf-8")
            (project / ".codex" / "agents" / "context-scout.toml").write_text('name = "context-scout"\n', encoding="utf-8")
            plan = self.run_json([PYTHON, str(SCRIPTS / "refresh_project_governance.py"), "--project", str(project), "--plugin-root", str(plugin), "--force"])
            self.assertEqual(plan["status"], "planned")
            self.assertGreaterEqual(plan["summary"]["quarantine_noise"], 1)
            applied = self.run_json([PYTHON, str(SCRIPTS / "refresh_project_governance.py"), "--project", str(project), "--plugin-root", str(plugin), "--force", "--apply"])
            self.assertEqual(applied["status"], "applied")
            self.assertFalse((project / ".codex" / "agents" / "context-scout.toml").exists())
            self.assertTrue((project / "docs" / "upgrades" / "CLEAN_REINSTALL_POLICY.md").exists())
            self.assertIn("Local memory", (project / "docs" / "memory" / "PROJECT_MEMORY.md").read_text(encoding="utf-8"))
            self.assertIn("Local Rule", (project / "AGENTS.md").read_text(encoding="utf-8"))
            self.assertIn("Project Governor", (project / "AGENTS.md").read_text(encoding="utf-8"))

    def test_refresh_stops_when_project_is_plugin_root(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            temp = Path(td)
            plugin = self.make_plugin_root(temp)
            (plugin / "AGENTS.md").write_text("Project Governor\n", encoding="utf-8")
            (plugin / "skills" / "clean-reinstall-manager").mkdir(parents=True)
            data = self.run_json([
                PYTHON,
                str(SCRIPTS / "refresh_project_governance.py"),
                "--project", str(plugin),
                "--plugin-root", str(plugin),
                "--apply",
            ])
            self.assertEqual(data["status"], "plugin_root_stop")
            self.assertTrue((plugin / "skills" / "clean-reinstall-manager").exists())

    def test_orchestrator_stops_outside_project_and_lists_projects(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            temp = Path(td)
            plugin = self.make_plugin_root(temp)
            project = temp / "governed"
            project.mkdir()
            (project / "AGENTS.md").write_text("Project Governor\n", encoding="utf-8")
            outside = temp / "outside"
            outside.mkdir()
            data = self.run_json([
                PYTHON,
                str(SCRIPTS / "clean_reinstall_orchestrator.py"),
                "--path", str(outside),
                "--plugin-root", str(plugin),
                "--discover-root", str(temp),
            ])
            self.assertEqual(data["status"], "not_project_stop")
            self.assertTrue(data["discovered_projects"])
            self.assertIn("all", data["user_choices"])

    def test_orchestrator_stops_inside_plugin_root(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            temp = Path(td)
            plugin = self.make_plugin_root(temp)
            (plugin / "AGENTS.md").write_text("Project Governor\n", encoding="utf-8")
            data = self.run_json([
                PYTHON,
                str(SCRIPTS / "clean_reinstall_orchestrator.py"),
                "--path", str(plugin),
                "--plugin-root", str(plugin),
                "--apply",
            ])
            self.assertEqual(data["status"], "plugin_root_stop")


if __name__ == "__main__":
    unittest.main(verbosity=2)
