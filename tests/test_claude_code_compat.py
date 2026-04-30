#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
HOOK = ROOT / "claude" / "hooks" / "project_governor_claude_hook.py"


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise AssertionError(f"missing frontmatter: {path}")
    data: dict[str, str] = {}
    for line in lines[1:]:
        if line == "---":
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


class ClaudeCodeCompatTest(unittest.TestCase):
    def test_claude_manifest_matches_codex_version_and_paths(self) -> None:
        codex = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        claude = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(claude["name"], "codex-project-governor")
        self.assertEqual(claude["version"], codex["version"])
        self.assertEqual(claude["version"], "6.2.4")
        for key, rel in {
            "skills": "claude/skills/",
            "commands": "claude/commands/",
            "hooks": "claude/hooks/hooks.json",
            "mcpServers": ".mcp.json",
        }.items():
            self.assertEqual(claude[key], f"./{rel}")
            self.assertTrue((ROOT / rel.rstrip("/")).exists(), rel)
        for rel in claude["agents"]:
            self.assertTrue(rel.startswith("./claude/agents/"), rel)
            self.assertTrue((ROOT / rel.removeprefix("./")).exists(), rel)

        hooks = json.loads((ROOT / "claude" / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        self.assertIn("UserPromptSubmit", hooks["hooks"])
        self.assertIn("PreToolUse", hooks["hooks"])
        self.assertIn("Stop", hooks["hooks"])

    def test_claude_commands_reference_plugin_root_scripts(self) -> None:
        command_files = sorted((ROOT / "claude" / "commands").glob("pg-*.md"))
        self.assertGreaterEqual(len(command_files), 8)
        for path in command_files:
            meta = frontmatter(path)
            self.assertTrue(meta["name"].startswith("pg-"), path)
            text = path.read_text(encoding="utf-8")
            self.assertIn("${CLAUDE_PLUGIN_ROOT}", text, path)
            self.assertIn("description", meta, path)

        skill = ROOT / "claude" / "skills" / "project-governor" / "SKILL.md"
        self.assertIn("${CLAUDE_PLUGIN_ROOT}", skill.read_text(encoding="utf-8"))

    def test_claude_agents_align_with_codex_agents(self) -> None:
        codex_agents = {}
        for path in sorted((ROOT / ".codex" / "agents").glob("*.toml")):
            data = tomllib.loads(path.read_text(encoding="utf-8"))
            codex_agents[data["name"]] = data["description"]

        claude_agents = {}
        for path in sorted((ROOT / "claude" / "agents").glob("*.md")):
            meta = frontmatter(path)
            claude_agents[meta["name"]] = meta

        self.assertEqual(set(claude_agents), set(codex_agents))
        writers = {"implementation-writer", "repair-agent", "test-writer"}
        for name, description in codex_agents.items():
            meta = claude_agents[name]
            self.assertEqual(meta["description"], description)
            tools = meta.get("tools", "")
            if name in writers:
                self.assertIn("Edit", tools)
                self.assertIn("Write", tools)
            else:
                self.assertNotIn("Edit", tools)
                self.assertNotIn("Write", tools)

    def run_hook(self, cwd: Path, payload: dict) -> str:
        proc = subprocess.run(
            [PY, str(HOOK)],
            cwd=cwd,
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=True,
            timeout=10,
        )
        return proc.stdout.strip()

    def test_claude_hook_blocks_ui_write_until_design_proof(self) -> None:
        event = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "src/components/App.tsx", "content": "export function App() { return null }\n"},
        }
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            denied = json.loads(self.run_hook(project, event))
            output = denied["hookSpecificOutput"]
            self.assertEqual(output["permissionDecision"], "deny")
            self.assertIn("Design service config missing", output["permissionDecisionReason"])

            design = project / "DESIGN.md"
            design.write_text("# Design\n\n## Tokens\n\n- color.primary: #ffffff\n", encoding="utf-8")
            (project / ".env-design").write_text("DESIGN_BASIC_MODE=1\n", encoding="utf-8")
            proof_dir = project / ".codex" / "design-md-governor"
            proof_dir.mkdir(parents=True)
            proof_dir.joinpath("read-proof.json").write_text(
                json.dumps({"ok": True, "design_sha256": hashlib.sha256(design.read_bytes()).hexdigest()}),
                encoding="utf-8",
            )
            self.assertEqual(self.run_hook(project, event), "")

    def test_init_project_copies_claude_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            proc = subprocess.run(
                [PY, str(ROOT / "tools" / "init_project.py"), "--mode", "existing", "--target", str(project), "--json"],
                text=True,
                capture_output=True,
                check=True,
                timeout=20,
            )
            result = json.loads(proc.stdout)
            self.assertIn("CLAUDE.md", result["created"])
            self.assertTrue((project / "CLAUDE.md").exists())
            self.assertIn("@AGENTS.md", (project / "CLAUDE.md").read_text(encoding="utf-8"))

    def test_claude_marketplaces_are_versioned(self) -> None:
        marketplace = json.loads((ROOT / "examples/claude-marketplace/.claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(marketplace["name"], "project-governor-claude-marketplace")
        self.assertEqual(marketplace["owner"], {"name": "yxhpy"})
        entry = marketplace["plugins"][0]
        self.assertEqual(entry["name"], "codex-project-governor")
        self.assertEqual(entry["version"], "6.2.4")
        self.assertEqual(entry["source"]["ref"], "v6.2.4")


if __name__ == "__main__":
    unittest.main(verbosity=2)
