#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path

UI_PROMPT_RE = re.compile(
    r"\b(ui|frontend|front-end|react|next\.js|nextjs|tailwind|css|component|page|layout|dashboard|landing|modal|dialog|form|table|card|responsive|mobile|visual|design|theme|style|redesign|polish)\b"
    r"|界面|前端|样式|页面|布局|组件|响应式|移动端|视觉|设计|主题|美化|弹窗|表单|表格|卡片|仪表盘",
    re.I,
)
PROJECT_WORK_PROMPT_RE = re.compile(
    r"\b(code|coding|implement|implementation|feature|fix|bug|refactor|test|tests|review|pr|docs|documentation|readme|release|publish|deploy|upgrade|dependency|init|initialize|governance|quality|memory|route|context|compat|adapter|plugin|check|inspect|audit|verify|validate|compliance|comply|scenario|scenarios)\b"
    r"|改|修|实现|添加|新增|删除|更新|升级|测试|评审|审查|检查|验证|审计|文档|发布|初始化|治理|质量|记忆|路由|上下文|兼容|适配|插件|遵循|合规|达标|通过|场景",
    re.I,
)
UI_FILE_RE = re.compile(
    r"(^|/)(app|pages|src/app|src/pages|components|src/components|styles|ui|design-system)/|\.(tsx|jsx|css|scss|sass|less)$|tailwind\.config\.|theme\.(ts|js|tsx|jsx)$"
)
ENV_FILE = ".env-design"
SKIP_ENV_KEYS = ("DESIGN_BASIC_MODE", "DESIGN_ENV_SKIP", "DESIGN_SERVICE_CONFIG_SKIP")
TRUTHY_VALUES = {"1", "true", "yes", "on"}
REQUIRED_ENV = (
    ("GEMINI_BASE_URL", ("GEMINI_BASE_URL", "DESIGN_GEMINI_BASE_URL")),
    ("GEMINI_API_KEY", ("GEMINI_API_KEY", "DESIGN_GEMINI_API_KEY")),
    ("GEMINI_MODEL", ("GEMINI_MODEL", "DESIGN_GEMINI_MODEL")),
    ("STITCH_MCP_API_KEY", ("STITCH_MCP_API_KEY", "DESIGN_STITCH_MCP_API_KEY")),
)
PROOF_DIRS = (
    Path(".codex/design-md-governor"),
    Path(".project-governor/design-md-governor"),
)
GOVERNANCE_AUTO_CONTEXT = (
    "Project Governor is active for this project task. Do not wait for the user to invoke `/pg-*` commands. "
    "For non-trivial work, read `CLAUDE.md` or `AGENTS.md` when present, classify the request with "
    "`${CLAUDE_PLUGIN_ROOT}/skills/task-router/scripts/classify_task.py`, query compact context with "
    "`${CLAUDE_PLUGIN_ROOT}/skills/context-indexer/scripts/query_context_index.py`, then choose the fastest safe governed workflow. "
    "Prefer local project files and Project Governor deterministic scripts; do not call unrelated web, browser, or MCP tools unless the user asks or local context is insufficient. "
    "Use `/pg-*` commands only as manual shortcuts or diagnostics."
)
UI_AUTO_CONTEXT = (
    "This appears to be UI/frontend work. Use Project Governor DESIGN.md preflight before editing UI files. "
    "Configure Gemini/Stitch with environment variables or project .env-design, or set DESIGN_BASIC_MODE=1 in .env-design for basic mode."
)


def root_dir() -> Path:
    try:
        out = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], stderr=subprocess.DEVNULL, text=True).strip()
        if out:
            return Path(out)
    except Exception:
        pass
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    return Path(project_dir) if project_dir else Path.cwd()


def parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def is_truthy(value: object) -> bool:
    return str(value).strip().lower() in TRUTHY_VALUES


def has_truthy_key(values: Mapping[str, str], keys: tuple[str, ...]) -> bool:
    return any(is_truthy(values.get(key, "")) for key in keys)


def has_config_value(file_values: dict[str, str], aliases: tuple[str, ...]) -> bool:
    return any(os.environ.get(key, "").strip() or file_values.get(key, "").strip() for key in aliases)


def design_env_ok(root: Path) -> tuple[bool, str]:
    file_values = parse_env_file(root / ENV_FILE)
    if has_truthy_key(os.environ, SKIP_ENV_KEYS) or has_truthy_key(file_values, SKIP_ENV_KEYS):
        return True, "ok"

    missing = [canonical for canonical, aliases in REQUIRED_ENV if not has_config_value(file_values, aliases)]
    if missing:
        return (
            False,
            "Design service config missing: "
            + ", ".join(missing)
            + ". Set shell environment variables, fill project .env-design, or set DESIGN_BASIC_MODE=1 in .env-design before UI edits.",
        )
    return True, "ok"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def find_read_proof(root: Path) -> Path | None:
    for proof_dir in PROOF_DIRS:
        candidate = root / proof_dir / "read-proof.json"
        if candidate.exists():
            return candidate
    return None


def proof_ok(root: Path) -> tuple[bool, str]:
    env_ok, env_reason = design_env_ok(root)
    if not env_ok:
        return False, env_reason

    design = root / "DESIGN.md"
    if not design.exists():
        return False, "DESIGN.md is missing. Create or adopt DESIGN.md before UI edits."

    proof = find_read_proof(root)
    if proof is None:
        return False, "DESIGN.md read proof is missing. Run Project Governor DESIGN.md preflight before UI edits."
    try:
        data = json.loads(proof.read_text(encoding="utf-8"))
    except Exception:
        return False, "DESIGN.md read proof is invalid JSON. Run preflight again."
    if data.get("design_sha256") != sha256(design):
        return False, "DESIGN.md read proof is stale because DESIGN.md changed. Run preflight again."
    if not data.get("ok", False):
        return False, "DESIGN.md preflight did not pass. Fix lint errors before UI edits."
    return True, "ok"


def bash_mentions_ui_write(command: str) -> bool:
    writey = re.search(r"\b(sed\s+-i|perl\s+-pi|tee\b|cat\s+>|printf\s+.*>|git\s+apply|python3?\s+-c|node\s+-e|mv\b|cp\b|touch\b)\b", command)
    return bool(writey and UI_FILE_RE.search(command))


def deny(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            },
            ensure_ascii=False,
        )
    )


def additional_context(event_name: str, message: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event_name, "additionalContext": message}}, ensure_ascii=False))


def run_git(root: Path, args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=root, text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return ""


def stop_warnings(root: Path) -> list[str]:
    changed = run_git(root, ["diff", "--name-only", "--cached"]).splitlines()
    if not changed:
        return []
    warnings: list[str] = []
    package_files = {"package.json", "pnpm-lock.yaml", "package-lock.json", "yarn.lock", "uv.lock", "poetry.lock"}
    if any(Path(path).name in package_files for path in changed):
        warnings.append("Dependency or package metadata changed; ensure an upgrade or dependency decision exists.")
    if len([path for path in changed if path.startswith(("src/", "app/", "packages/", "services/"))]) > 12:
        warnings.append("Large application change detected; verify this remains an iteration and not a rewrite.")
    return warnings


def should_gate_pre_tool(tool: str, tool_input: object) -> bool:
    payload = json.dumps(tool_input, ensure_ascii=False)
    if tool == "Bash":
        command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""
        return bash_mentions_ui_write(command)
    if tool in {"Edit", "Write", "MultiEdit", "NotebookEdit"}:
        return UI_FILE_RE.search(payload) is not None
    return False


def handle_user_prompt(event: dict[str, object]) -> None:
    prompt = str(event.get("prompt", ""))
    contexts: list[str] = []
    if PROJECT_WORK_PROMPT_RE.search(prompt):
        contexts.append(GOVERNANCE_AUTO_CONTEXT)
    if UI_PROMPT_RE.search(prompt):
        contexts.append(UI_AUTO_CONTEXT)
    if contexts:
        additional_context("UserPromptSubmit", "\n\n".join(contexts))


def handle_pre_tool(root: Path, event: dict[str, object]) -> None:
    tool = str(event.get("tool_name", ""))
    tool_input = event.get("tool_input") or {}
    if should_gate_pre_tool(tool, tool_input):
        ok, reason = proof_ok(root)
        if not ok:
            deny(reason)


def handle_stop(root: Path) -> None:
    warnings = stop_warnings(root)
    if warnings:
        additional_context("Stop", "Project Governor governance hints:\n- " + "\n- ".join(warnings))


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except Exception:
        return 0

    root = root_dir()
    try:
        os.chdir(root)
    except Exception:
        pass

    event_name = event.get("hook_event_name", "")
    if event_name == "UserPromptSubmit":
        handle_user_prompt(event)
        return 0

    if event_name == "PreToolUse":
        handle_pre_tool(root, event)
        return 0

    if event_name == "Stop":
        handle_stop(root)
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
