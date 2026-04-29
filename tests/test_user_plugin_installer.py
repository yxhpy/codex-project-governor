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
INSTALLER = ROOT / "tools" / "install_or_update_user_plugin.py"


class UserPluginInstallerTest(unittest.TestCase):
    def run_json(self, args: list[str], check: bool = True) -> tuple[dict, int]:
        proc = subprocess.run(args, text=True, capture_output=True, check=check, timeout=20)
        return json.loads(proc.stdout), proc.returncode

    def git(self, repo: Path, args: list[str]) -> None:
        subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True, check=True, timeout=20)

    def make_source_repo(self, root: Path) -> Path:
        source = root / "source"
        (source / ".codex-plugin").mkdir(parents=True)
        (source / "tests").mkdir()
        (source / ".codex-plugin" / "plugin.json").write_text(
            json.dumps({"name": "codex-project-governor", "version": "1.0.0"}),
            encoding="utf-8",
        )
        (source / "tests" / "selftest.py").write_text("print('ok')\n", encoding="utf-8")
        subprocess.run(["git", "init", str(source)], text=True, capture_output=True, check=True, timeout=20)
        self.git(source, ["add", "."])
        subprocess.run(
            [
                "git",
                "-C",
                str(source),
                "-c",
                "user.name=Project Governor Test",
                "-c",
                "user.email=test@example.invalid",
                "commit",
                "-m",
                "initial",
            ],
            text=True,
            capture_output=True,
            check=True,
            timeout=20,
        )
        self.git(source, ["tag", "v1.0.0"])
        return source

    def add_version(self, source: Path, version: str) -> None:
        (source / ".codex-plugin" / "plugin.json").write_text(
            json.dumps({"name": "codex-project-governor", "version": version}),
            encoding="utf-8",
        )
        self.git(source, ["add", ".codex-plugin/plugin.json"])
        subprocess.run(
            [
                "git",
                "-C",
                str(source),
                "-c",
                "user.name=Project Governor Test",
                "-c",
                "user.email=test@example.invalid",
                "commit",
                "-m",
                f"release {version}",
            ],
            text=True,
            capture_output=True,
            check=True,
            timeout=20,
        )
        self.git(source, ["tag", f"v{version}"])

    def test_plan_does_not_write_files(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plugin_dir = root / "home" / ".codex" / "plugins" / "codex-project-governor"
            marketplace = root / "home" / ".agents" / "plugins" / "marketplace.json"
            data, code = self.run_json([
                PYTHON,
                str(INSTALLER),
                "--plugin-dir",
                str(plugin_dir),
                "--marketplace-path",
                str(marketplace),
                "--repo-url",
                str(root / "source"),
                "--ref",
                "v1.0.0",
            ])
            self.assertEqual(code, 0)
            self.assertEqual(data["status"], "planned")
            self.assertFalse(plugin_dir.exists())
            self.assertFalse(marketplace.exists())
            self.assertEqual(data["target_source"]["path"], "./.codex/plugins/codex-project-governor")

    def test_apply_clones_and_writes_marketplace_entry(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = self.make_source_repo(root)
            plugin_dir = root / "home" / ".codex" / "plugins" / "codex-project-governor"
            marketplace = root / "home" / ".agents" / "plugins" / "marketplace.json"
            data, code = self.run_json([
                PYTHON,
                str(INSTALLER),
                "--plugin-dir",
                str(plugin_dir),
                "--marketplace-path",
                str(marketplace),
                "--repo-url",
                str(source),
                "--ref",
                "v1.0.0",
                "--apply",
                "--skip-selftest",
            ])
            self.assertEqual(code, 0)
            self.assertEqual(data["status"], "applied")
            self.assertEqual(data["current_version"], "1.0.0")
            self.assertTrue((plugin_dir / ".git").exists())
            market = json.loads(marketplace.read_text(encoding="utf-8"))
            entries = [item for item in market["plugins"] if item["name"] == "codex-project-governor"]
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["source"], {"source": "local", "path": "./.codex/plugins/codex-project-governor"})

    def test_apply_stops_on_dirty_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = self.make_source_repo(root)
            plugin_dir = root / "home" / ".codex" / "plugins" / "codex-project-governor"
            marketplace = root / "home" / ".agents" / "plugins" / "marketplace.json"
            self.run_json([
                PYTHON,
                str(INSTALLER),
                "--plugin-dir",
                str(plugin_dir),
                "--marketplace-path",
                str(marketplace),
                "--repo-url",
                str(source),
                "--ref",
                "v1.0.0",
                "--apply",
                "--skip-selftest",
            ])
            (plugin_dir / "local-edit.txt").write_text("dirty\n", encoding="utf-8")
            data, code = self.run_json([
                PYTHON,
                str(INSTALLER),
                "--plugin-dir",
                str(plugin_dir),
                "--marketplace-path",
                str(marketplace),
                "--repo-url",
                str(source),
                "--ref",
                "v1.0.0",
                "--apply",
                "--skip-selftest",
            ], check=False)
            self.assertEqual(code, 1)
            self.assertEqual(data["status"], "blocked")
            self.assertEqual(data["reason"], "dirty_plugin_checkout")

    def test_apply_updates_existing_clean_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = self.make_source_repo(root)
            plugin_dir = root / "home" / ".codex" / "plugins" / "codex-project-governor"
            marketplace = root / "home" / ".agents" / "plugins" / "marketplace.json"
            self.run_json([
                PYTHON,
                str(INSTALLER),
                "--plugin-dir",
                str(plugin_dir),
                "--marketplace-path",
                str(marketplace),
                "--repo-url",
                str(source),
                "--ref",
                "v1.0.0",
                "--apply",
                "--skip-selftest",
            ])
            self.add_version(source, "1.1.0")
            data, code = self.run_json([
                PYTHON,
                str(INSTALLER),
                "--plugin-dir",
                str(plugin_dir),
                "--marketplace-path",
                str(marketplace),
                "--repo-url",
                str(source),
                "--ref",
                "v1.1.0",
                "--apply",
                "--skip-selftest",
            ])
            self.assertEqual(code, 0)
            self.assertEqual(data["status"], "applied")
            self.assertEqual(data["previous_version"], "1.0.0")
            self.assertEqual(data["current_version"], "1.1.0")


if __name__ == "__main__":
    unittest.main(verbosity=2)
