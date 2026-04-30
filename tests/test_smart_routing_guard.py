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
        self.assertEqual(data["artifact_policy"]["mode"], "none")
        self.assertFalse(data["artifact_policy"]["task_plan_required"])
        self.assertIn("subagent-audit", data["skipped_workflow"])

    def test_shared_component_escalates(self) -> None:
        data = self.run_json([PY, "skills/task-router/scripts/classify_task.py", "examples/task-router-shared-component-input.json"])
        self.assertNotEqual(data["route"], "micro_patch")
        self.assertEqual(data["route"], "ui_change")
        self.assertEqual(data["lane"], "standard_lane")
        self.assertLess(data["confidence"], 0.85)

    def test_readme_typo_routes_to_docs_only(self) -> None:
        data = self.run_json([PY, "skills/task-router/scripts/classify_task.py", "--request", "fix a typo in README"])
        self.assertEqual(data["route"], "docs_only")
        self.assertEqual(data["quality_level"], "light")
        self.assertEqual(data["subagent_mode"], "none")
        self.assertFalse(data["evidence_required"])
        self.assertIn("quality-gate", data["required_workflow"])
        self.assertNotIn("context-pack-builder", data["required_workflow"])

    def test_ui_copy_routes_to_micro_patch_without_task_artifacts(self) -> None:
        data = self.run_json([PY, "skills/task-router/scripts/classify_task.py", "--request", "fix a typo on the dashboard button copy"])
        self.assertEqual(data["route"], "micro_patch")
        self.assertEqual(data["quality_level"], "light")
        self.assertFalse(data["evidence_required"])
        self.assertEqual(data["artifact_policy"]["mode"], "none")
        self.assertNotIn("context-pack-builder", data["required_workflow"])

    def test_tiny_patch_uses_inline_artifacts_and_diff_scoped_standards(self) -> None:
        data = self.run_json([PY, "skills/task-router/scripts/classify_task.py", "--request", "fix broken dashboard widget rendering in dashboard page"])
        self.assertEqual(data["route"], "tiny_patch")
        self.assertEqual(data["quality_level"], "light")
        self.assertEqual(data["subagent_mode"], "none")
        self.assertEqual(data["artifact_policy"]["mode"], "inline")
        self.assertFalse(data["artifact_policy"]["task_plan_required"])
        self.assertIn("engineering-standards-governor", data["required_workflow"])
        self.assertNotIn("context-pack-builder", data["required_workflow"])

    def test_new_widget_does_not_route_to_tiny_patch(self) -> None:
        data = self.run_json([PY, "skills/task-router/scripts/classify_task.py", "examples/task-router-input.json"])
        self.assertEqual(data["route"], "ui_change")
        self.assertEqual(data["artifact_policy"]["mode"], "files")

    def test_feature_with_tests_does_not_route_as_test_only(self) -> None:
        data = self.run_json([PY, "skills/task-router/scripts/classify_task.py", "--request", "Add an export helper that reuses the existing parser utilities and updates tests."])
        self.assertEqual(data["route"], "standard_feature")
        self.assertIn("test_signal", data["risk_signals"])
        self.assertIn("parallel-feature-builder", data["required_workflow"])

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
