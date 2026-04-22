#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

class SmartRoutingGuardTest(unittest.TestCase):
    def run_json(self, args: list[str], expect_success: bool = True) -> dict:
        proc = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, timeout=20)
        if expect_success:
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        return json.loads(proc.stdout)

    def test_micro_patch_route(self) -> None:
        data = self.run_json([PY, "skills/task-router/scripts/classify_task.py", "examples/task-router-micro-input.json"])
        self.assertEqual(data["route"], "micro_patch")
        self.assertGreaterEqual(data["confidence"], 0.85)
        self.assertIn("do_not_change_api", data["negative_constraints"])
        self.assertIn("do_not_change_schema", data["negative_constraints"])
        self.assertEqual(data["route_guard_requirements"]["max_modified_files"], 1)
        self.assertEqual(data["route_guard_requirements"]["max_added_files"], 0)
        self.assertIn("subagent-audit", data["skipped_workflow"])

    def test_shared_component_escalates(self) -> None:
        data = self.run_json([PY, "skills/task-router/scripts/classify_task.py", "examples/task-router-shared-component-input.json"])
        self.assertNotEqual(data["route"], "micro_patch")
        self.assertEqual(data["route"], "ui_change")
        self.assertEqual(data["lane"], "standard_lane")
        self.assertLess(data["confidence"], 0.85)

    def test_route_guard_passes_micro_patch(self) -> None:
        data = self.run_json([PY, "skills/route-guard/scripts/check_route_guard.py", "examples/route-guard-micro-pass.json"])
        self.assertEqual(data["status"], "pass")
        self.assertEqual(data["required_action"], "continue")

    def test_route_guard_blocks_scope_creep(self) -> None:
        data = self.run_json([PY, "skills/route-guard/scripts/check_route_guard.py", "examples/route-guard-micro-fail.json"], expect_success=False)
        self.assertEqual(data["status"], "fail")
        self.assertEqual(data["required_action"], "stop_and_reroute")
        types = {item["type"] for item in data["violations"]}
        self.assertIn("modified_file_budget_exceeded", types)
        self.assertIn("added_file_budget_exceeded", types)
        self.assertIn("global_style_change_not_allowed", types)
        self.assertIn("shared_component_change_not_allowed", types)
        self.assertIn("new_component_not_allowed", types)

    def test_quality_gate_integrates_route_guard(self) -> None:
        data = self.run_json([PY, "skills/quality-gate/scripts/run_quality_gate.py", "examples/quality-gate-with-route-guard.json"])
        self.assertEqual(data["status"], "pass")
        self.assertEqual(data["route_guard"]["status"], "pass")

if __name__ == "__main__":
    unittest.main(verbosity=2)
