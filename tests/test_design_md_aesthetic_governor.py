#!/usr/bin/env python3
"""
Smoke test hints for the DESIGN.md Aesthetic Governor.

Run from project root after copying the drop-in package:

python3 tests/test_design_md_aesthetic_governor.py

This test intentionally avoids installing dependencies.
"""
from __future__ import annotations
import hashlib, importlib.util, json, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/design-md-aesthetic-governor"

DESIGN = """---
version: alpha
name: Test System
colors:
  primary: "#111827"
  accent: "#2563EB"
  surface: "#FFFFFF"
typography:
  body-md:
    fontFamily: Inter
    fontSize: 16px
spacing:
  md: 16px
rounded:
  md: 12px
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.surface}"
    rounded: "{rounded.md}"
---

## Overview
Precise.
## Colors
Use accent for primary action.
## Typography
Inter.
"""

def load_script(name: str):
    path = SKILL / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()

def main():
    lint = load_script("design_md_lint.py")
    verify = load_script("verify_design_usage.py")
    select = load_script("select_aesthetic.py")
    env_check = load_script("design_env_check.py")
    smoke = load_script("design_service_smoke.py")
    review = load_script("design_service_review.py")
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        design = p / "DESIGN.md"
        design.write_text(DESIGN, encoding="utf-8")
        report = lint.lint_design_md(design)
        assert report["summary"]["errors"] == 0, report
        missing = env_check.check_design_env(p, environ={}, write_missing_template=True)
        assert missing["ok"] is False, missing
        assert missing["missing"] == ["GEMINI_BASE_URL", "GEMINI_API_KEY", "GEMINI_MODEL", "STITCH_MCP_API_KEY"], missing
        assert (p / ".env-design").exists(), missing
        assert "# DESIGN_BASIC_MODE=1" in (p / ".env-design").read_text(encoding="utf-8")
        (p / ".env-design").write_text(
            "\n".join(
                [
                    "GEMINI_BASE_URL=https://gemini.example/v1",
                    "GEMINI_API_KEY=test-gemini-key",
                    "GEMINI_MODEL=gemini-test",
                    "GEMINI_PROTOCOL=auto",
                    "STITCH_MCP_URL=https://stitch.googleapis.com/mcp",
                    "STITCH_MCP_API_KEY=test-stitch-key",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        configured = env_check.check_design_env(p, environ={}, write_missing_template=False)
        assert configured["ok"] is True, configured
        assert configured["gemini_protocol"] == "auto", configured
        assert configured["stitch_mcp_url"] == "https://stitch.googleapis.com/mcp", configured
        assert "test-gemini-key" not in json.dumps(configured), configured
        proc = subprocess.run(
            [
                sys.executable,
                str(SKILL / "scripts" / "design_md_gate.py"),
                "preflight",
                "--task",
                "ui prototype",
            ],
            cwd=p,
            text=True,
            capture_output=True,
            check=True,
            env={},
        )
        proof = json.loads(proc.stdout)
        assert proof["ok"] is True, proof
        assert proof["design_env"]["ok"] is True, proof
        assert proof["design_env"]["mode"] == "full_service", proof
        merged = smoke.merged_env(p, {})
        assert smoke.openai_chat_url(merged["GEMINI_BASE_URL"]) == "https://gemini.example/v1/chat/completions"
        assert smoke.gemini_generate_url("https://generativelanguage.googleapis.com/v1beta", "gemini-2.5-flash") == "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        assert smoke.resolve_gemini_protocol("auto", "https://generativelanguage.googleapis.com") == "gemini"
        assert smoke.resolve_gemini_protocol("auto", "https://co.yes.vg") == "openai"
        assert smoke.valid_gemini_response("gemini", {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}) is True
        assert smoke.valid_gemini_response("gemini", "<html></html>") is False
        assert smoke.valid_gemini_response("openai", {"choices": [{"message": {"content": "ok"}}]}) is True
        assert "/gemini/v1beta" in smoke.gemini_response_hint("gemini", "https://co.yes.vg", "<!DOCTYPE html>")
        assert smoke.first_value(merged, "GEMINI_API_KEY") == "test-gemini-key"
        assert smoke.first_value(merged, "STITCH_MCP_URL", "DESIGN_STITCH_MCP_URL") == "https://stitch.googleapis.com/mcp"
        assert env_check.DEFAULT_STITCH_MCP_URL == "https://stitch.googleapis.com/mcp"
        prompt = review.build_review_prompt("ui prototype", design, report)
        assert "Review this UI/frontend task" in prompt, prompt
        assert "test-gemini-key" not in prompt, prompt
    with tempfile.TemporaryDirectory() as td:
        env_configured = env_check.check_design_env(
            Path(td),
            environ={
                "GEMINI_BASE_URL": "https://gemini.example/v1",
                "GEMINI_API_KEY": "env-gemini-key",
                "GEMINI_MODEL": "gemini-env",
                "GEMINI_PROTOCOL": "gemini",
                "STITCH_MCP_URL": "https://stitch.example/mcp",
                "STITCH_MCP_API_KEY": "env-stitch-key",
            },
            write_missing_template=False,
        )
        assert env_configured["ok"] is True, env_configured
        assert env_configured["gemini_protocol"] == "gemini", env_configured
        assert env_configured["stitch_mcp_url"] == "https://stitch.example/mcp", env_configured
        assert "env-gemini-key" not in json.dumps(env_configured), env_configured
    with tempfile.TemporaryDirectory() as td:
        basic = env_check.check_design_env(
            Path(td),
            environ={"DESIGN_BASIC_MODE": "1"},
            write_missing_template=True,
        )
        assert basic["ok"] is True, basic
        assert basic["status"] == "basic_mode", basic
        assert basic["mode"] == "basic", basic
        assert not (Path(td) / ".env-design").exists(), basic
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        (p / "DESIGN.md").write_text(DESIGN, encoding="utf-8")
        (p / ".env-design").write_text("DESIGN_BASIC_MODE=1\n", encoding="utf-8")
        basic_file = env_check.check_design_env(p, environ={}, write_missing_template=True)
        assert basic_file["ok"] is True, basic_file
        assert basic_file["status"] == "basic_mode", basic_file
        assert basic_file["mode"] == "basic", basic_file
        assert basic_file["basic_mode_source"] == ".env-design", basic_file
        assert basic_file["basic_mode_key"] == "DESIGN_BASIC_MODE", basic_file
        assert basic_file["basic_mode_env"] == "", basic_file
        proc = subprocess.run(
            [
                sys.executable,
                str(SKILL / "scripts" / "design_md_gate.py"),
                "preflight",
                "--task",
                "ui prototype",
            ],
            cwd=p,
            text=True,
            capture_output=True,
            check=True,
            env={},
        )
        proof = json.loads(proc.stdout)
        assert proof["ok"] is True, proof
        assert proof["design_env"]["ok"] is True, proof
        assert proof["design_env"]["mode"] == "basic", proof
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        design = p / "DESIGN.md"
        design.write_text(DESIGN, encoding="utf-8")
        state = p / ".codex" / "design-md-governor"
        state.mkdir(parents=True)
        (state / "read-proof.json").write_text(json.dumps({"ok": True, "design_sha256": sha256(design)}), encoding="utf-8")
        event = {
            "hook_event_name": "PreToolUse",
            "tool_name": "apply_patch",
            "tool_input": {
                "command": "*** Begin Patch\n*** Update File: src/components/App.tsx\n@@\n+export const x = 1;\n*** End Patch\n"
            },
        }
        blocked = subprocess.run(
            [sys.executable, str(ROOT / "templates" / ".codex" / "hooks" / "design_md_codex_hook.py")],
            cwd=p,
            input=json.dumps(event),
            text=True,
            capture_output=True,
            check=True,
            env={},
        )
        assert "permissionDecision" in blocked.stdout, blocked.stdout
        (p / ".env-design").write_text("DESIGN_BASIC_MODE=1\n", encoding="utf-8")
        allowed = subprocess.run(
            [sys.executable, str(ROOT / "templates" / ".codex" / "hooks" / "design_md_codex_hook.py")],
            cwd=p,
            input=json.dumps(event),
            text=True,
            capture_output=True,
            check=True,
            env={},
        )
        assert allowed.stdout.strip() == "", allowed.stdout
    print("OK")

if __name__ == "__main__":
    main()
