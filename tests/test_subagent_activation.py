#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable


class SubagentActivationTest(unittest.TestCase):
    def run_json(self, input_file: str) -> dict:
        proc = subprocess.run(
            [PY, "skills/subagent-activation/scripts/select_subagents.py", input_file],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=20,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        return json.loads(proc.stdout)

    def test_micro_patch_uses_no_subagents(self) -> None:
        data = self.run_json("examples/subagent-activation-micro.json")
        self.assertEqual(data["subagent_mode"], "none")
        self.assertEqual(data["selected_agents"], [])
        self.assertIn("Do not spawn subagents", data["spawn_instructions"])

    def test_standard_feature_selects_fast_read_only_and_writers(self) -> None:
        data = self.run_json("examples/subagent-activation-standard-feature.json")
        self.assertEqual(data["subagent_mode"], "required")
        names = {agent["name"] for agent in data["selected_agents"]}
        self.assertIn("context-scout", names)
        self.assertIn("pattern-reuse-scout", names)
        self.assertIn("test-planner", names)
        self.assertIn("implementation-writer", names)
        models = {agent["name"]: agent["model"] for agent in data["selected_agents"]}
        self.assertEqual(models["context-scout"], "gpt-5.4-mini")
        self.assertEqual(models["implementation-writer"], "gpt-5.4")

    def test_risk_feature_uses_high_reasoning_reviewers(self) -> None:
        data = self.run_json("examples/subagent-activation-risk.json")
        names = {agent["name"] for agent in data["selected_agents"]}
        self.assertIn("risk-scout", names)
        self.assertIn("quality-reviewer", names)
        by_name = {agent["name"]: agent for agent in data["selected_agents"]}
        self.assertEqual(by_name["risk-scout"]["model"], "gpt-5.4")
        self.assertEqual(by_name["risk-scout"]["reasoning"], "high")
        self.assertEqual(by_name["quality-reviewer"]["reasoning"], "high")

    def test_project_scoped_agent_templates_exist(self) -> None:
        required = [
            "context-scout",
            "pattern-reuse-scout",
            "risk-scout",
            "test-planner",
            "quality-reviewer",
            "implementation-writer",
            "test-writer",
            "repair-agent",
        ]
        for name in required:
            path = ROOT / "templates" / ".codex" / "agents" / f"{name}.toml"
            text = path.read_text(encoding="utf-8")
            self.assertIn(f'name = "{name}"', text)
            self.assertIn("developer_instructions", text)
            self.assertIn("model =", text)
        config = (ROOT / "templates" / ".codex" / "config.toml").read_text(encoding="utf-8")
        self.assertIn("max_depth = 1", config)
        self.assertIn("max_threads = 6", config)


if __name__ == "__main__":
    unittest.main(verbosity=2)
