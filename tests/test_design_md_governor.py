#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable


class DesignMdGovernorTest(unittest.TestCase):
    def run_json(self, args: list[str], *, check: bool = True) -> dict:
        proc = subprocess.run(args, text=True, capture_output=True)
        if check:
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        return json.loads(proc.stdout)

    def test_lints_valid_design_md(self) -> None:
        data = self.run_json([PY, str(ROOT / "skills" / "design-md-governor" / "scripts" / "lint_design_md.py"), str(ROOT / "examples" / "design-md-example.md")])
        self.assertEqual(data["status"], "pass")
        self.assertEqual(data["summary"]["errors"], 0)
        self.assertIn("colors", data["designSystem"])
        self.assertIn("button-primary", data["designSystem"]["components"])

    def test_summarizes_design_tokens(self) -> None:
        data = self.run_json([PY, str(ROOT / "skills" / "design-md-governor" / "scripts" / "summarize_design_md.py"), str(ROOT / "examples" / "design-md-example.md")])
        self.assertEqual(data["name"], "Heritage")
        self.assertGreaterEqual(data["token_counts"]["colors"], 4)
        self.assertIn("button-primary", data["component_tokens"])
        self.assertIn("colors", data["sections"])

    def test_detects_contrast_regression(self) -> None:
        proc = subprocess.run(
            [
                PY,
                str(ROOT / "skills" / "design-md-governor" / "scripts" / "diff_design_md.py"),
                str(ROOT / "examples" / "design-md-before.md"),
                str(ROOT / "examples" / "design-md-after-regression.md"),
            ],
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        data = json.loads(proc.stdout)
        self.assertTrue(data["regression"])
        self.assertIn("on-primary", data["tokens"]["colors"]["modified"])

    def test_rejects_broken_reference(self) -> None:
        broken = ROOT / "examples" / "design-md-broken-ref.tmp.md"
        broken.write_text(
            "---\nname: Broken\ncolors:\n  primary: \"#000000\"\ncomponents:\n  button-primary:\n    backgroundColor: \"{colors.missing}\"\n---\n\n## Overview\n\nBroken.\n",
            encoding="utf-8",
        )
        try:
            proc = subprocess.run([PY, str(ROOT / "skills" / "design-md-governor" / "scripts" / "lint_design_md.py"), str(broken)], text=True, capture_output=True)
            self.assertNotEqual(proc.returncode, 0)
            data = json.loads(proc.stdout)
            rules = {item["rule"] for item in data["findings"]}
            self.assertIn("broken-ref", rules)
        finally:
            broken.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
