#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import time
import urllib.error
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
STATE_DIR = Path(".codex/design-md-governor")


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), SCRIPT_DIR / name)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def compact_design_text(path: Path, limit: int = 6000) -> str:
    text = path.read_text(encoding="utf-8")
    if len(text) <= limit:
        return text
    return text[:limit] + "\n\n[truncated for service review]"


def build_review_prompt(task: str, design_path: Path, lint_report: dict[str, object]) -> str:
    summary = lint_report.get("summary", {})
    design_system = lint_report.get("designSystem", {})
    return "\n".join(
        [
            "Review this UI/frontend task against the project DESIGN.md.",
            "",
            f"Task: {task}",
            f"Design source: {design_path}",
            f"Lint summary: {summary}",
            f"Design system summary: {design_system}",
            "",
            "DESIGN.md:",
            compact_design_text(design_path),
            "",
            "Return concise findings only: hierarchy, token consistency, prototype risks, and implementation cautions.",
        ]
    )


def tool_names(data: dict[str, object] | str, limit: int = 12) -> list[str]:
    if not isinstance(data, dict):
        return []
    result = data.get("result")
    if not isinstance(result, dict):
        return []
    tools = result.get("tools")
    if not isinstance(tools, list):
        return []
    names: list[str] = []
    for item in tools:
        if isinstance(item, dict) and isinstance(item.get("name"), str):
            names.append(item["name"])
    return names[:limit]


def write_evidence(root: Path, report: dict[str, object]) -> tuple[Path, Path]:
    state = root / STATE_DIR
    state.mkdir(parents=True, exist_ok=True)
    json_path = state / "service-review.json"
    md_path = state / "SERVICE_REVIEW.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    gemini = report.get("gemini", {}) if isinstance(report.get("gemini"), dict) else {}
    stitch = report.get("stitch", {}) if isinstance(report.get("stitch"), dict) else {}
    md_path.write_text(
        "\n".join(
            [
                "# DESIGN.md Service Review",
                "",
                f"- Status: {report.get('status')}",
                f"- Gemini protocol: {gemini.get('protocol')}",
                f"- Gemini status: {gemini.get('http_status')}",
                f"- Stitch status: {stitch.get('http_status')}",
                f"- Stitch tools: {', '.join(stitch.get('tools', [])) if isinstance(stitch.get('tools'), list) else ''}",
                "",
                "## Gemini Review Preview",
                "",
                str(gemini.get("review_preview") or gemini.get("error_preview") or ""),
                "",
            ]
        ),
        encoding="utf-8",
    )
    return json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a real Gemini/Stitch design-service review without printing secrets.")
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--design", default="DESIGN.md")
    parser.add_argument("--task", required=True)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--write-template", action="store_true")
    args = parser.parse_args()

    root = args.project.resolve()
    env_check = load_script("design_env_check.py")
    smoke = load_script("design_service_smoke.py")
    linter = load_script("design_md_lint.py")

    env_report = env_check.check_design_env(root, write_missing_template=args.write_template)
    if not env_report["ok"]:
        print(json.dumps({"ok": False, "status": "blocked", "design_env": env_report}, indent=2, ensure_ascii=False))
        return 2
    if env_report.get("mode") == "basic":
        report = {"ok": True, "status": "basic_mode", "gemini": {"skipped": True}, "stitch": {"skipped": True}}
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0

    design_path = (root / args.design).resolve()
    if not design_path.exists():
        print(json.dumps({"ok": False, "status": "blocked", "reason": "DESIGN.md missing", "design": str(design_path)}, indent=2, ensure_ascii=False))
        return 2

    lint_report = linter.lint_design_md(design_path)
    if lint_report.get("summary", {}).get("errors", 0):
        print(json.dumps({"ok": False, "status": "blocked", "reason": "DESIGN.md lint errors", "lint_summary": lint_report.get("summary")}, indent=2, ensure_ascii=False))
        return 2

    values = smoke.merged_env(root, os.environ)
    base_url = smoke.first_value(values, "GEMINI_BASE_URL", "DESIGN_GEMINI_BASE_URL")
    api_key = smoke.first_value(values, "GEMINI_API_KEY", "DESIGN_GEMINI_API_KEY")
    model = smoke.first_value(values, "GEMINI_MODEL", "DESIGN_GEMINI_MODEL")
    requested_protocol = smoke.first_value(values, "GEMINI_PROTOCOL", "DESIGN_GEMINI_PROTOCOL") or str(env_report.get("gemini_protocol") or "auto")
    protocol = smoke.resolve_gemini_protocol(requested_protocol, base_url)
    gemini_url = smoke.gemini_request_url(protocol, base_url, model)
    stitch_key = smoke.first_value(values, "STITCH_MCP_API_KEY", "DESIGN_STITCH_MCP_API_KEY")
    stitch_endpoint = smoke.first_value(values, "STITCH_MCP_URL", "DESIGN_STITCH_MCP_URL", "STITCH_MCP_ENDPOINT", "DESIGN_STITCH_MCP_ENDPOINT") or env_check.DEFAULT_STITCH_MCP_URL

    review_prompt = build_review_prompt(args.task, design_path, lint_report)
    payload = smoke.gemini_payload(protocol, model, review_prompt)
    report: dict[str, object] = {
        "ok": False,
        "status": "running",
        "timestamp": int(time.time()),
        "task": args.task,
        "design": str(design_path),
        "design_sha256": sha256(design_path),
        "lint_summary": lint_report.get("summary", {}),
        "gemini": {
            "configured": True,
            "model": model,
            "protocol_requested": smoke.normalize_gemini_protocol(requested_protocol),
            "protocol": protocol,
            "url": gemini_url,
            "request_shape": "gemini_generate_content" if protocol == "gemini" else "openai_chat_completions",
        },
        "stitch": {
            "configured": bool(stitch_key),
            "url": stitch_endpoint,
            "request_shape": "mcp_initialize_and_tools_list",
        },
    }

    gemini_ok = False
    try:
        if protocol == "gemini":
            status, data = smoke.post_gemini_native(gemini_url, api_key, payload, args.timeout)
        else:
            status, data = smoke.post_json(gemini_url, api_key, payload, args.timeout)
        response_shape_ok = smoke.valid_gemini_response(protocol, data)
        gemini_ok = 200 <= status < 300 and response_shape_ok
        report["gemini"] = {
            **report["gemini"],
            "ok": gemini_ok,
            "http_status": status,
            "response_shape_ok": response_shape_ok,
            "review_preview": smoke.content_preview(data),
        }
        hint = smoke.gemini_response_hint(protocol, base_url, data)
        if not response_shape_ok and hint:
            report["gemini"] = {**report["gemini"], "hint": hint}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:500]
        report["gemini"] = {**report["gemini"], "ok": False, "http_status": exc.code, "error_preview": body}
    except Exception as exc:
        report["gemini"] = {**report["gemini"], "ok": False, "error": exc.__class__.__name__, "message": str(exc)[:300]}

    stitch_ok = False
    try:
        init_status, init_data = smoke.post_mcp_initialize(stitch_endpoint, stitch_key, args.timeout)
        tools_status, tools_data = smoke.post_mcp_tools_list(stitch_endpoint, stitch_key, args.timeout)
        stitch_ok = 200 <= init_status < 300 and 200 <= tools_status < 300
        report["stitch"] = {
            **report["stitch"],
            "ok": stitch_ok,
            "http_status": init_status,
            "tools_status": tools_status,
            "tools": tool_names(tools_data),
        }
        if isinstance(init_data, dict):
            result = init_data.get("result")
            if isinstance(result, dict) and isinstance(result.get("serverInfo"), dict):
                report["stitch"] = {**report["stitch"], "server_info": result["serverInfo"]}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:500]
        report["stitch"] = {**report["stitch"], "ok": False, "http_status": exc.code, "error_preview": body}
    except Exception as exc:
        report["stitch"] = {**report["stitch"], "ok": False, "error": exc.__class__.__name__, "message": str(exc)[:300]}

    report["ok"] = bool(gemini_ok and stitch_ok)
    report["status"] = "passed" if report["ok"] else "failed"
    try:
        json_path, md_path = write_evidence(root, report)
        report["evidence"] = {"json": str(json_path), "markdown": str(md_path)}
    except OSError as exc:
        report["evidence_error"] = {"error": exc.__class__.__name__, "message": str(exc)[:300]}

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
