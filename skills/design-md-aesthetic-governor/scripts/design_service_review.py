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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a real Gemini/Stitch design-service review without printing secrets.")
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--design", default="DESIGN.md")
    parser.add_argument("--task", required=True)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--write-template", action="store_true")
    return parser.parse_args()


def load_dependencies() -> tuple[object, object, object]:
    return load_script("design_env_check.py"), load_script("design_service_smoke.py"), load_script("design_md_lint.py")


def blocked(reason: str, **extra: object) -> dict[str, object]:
    return {"ok": False, "status": "blocked", "reason": reason, **extra}


def load_design_report(root: Path, design: str, linter: object) -> tuple[Path | None, dict[str, object], dict[str, object] | None]:
    design_path = (root / design).resolve()
    if not design_path.exists():
        return None, {}, blocked("DESIGN.md missing", design=str(design_path))

    lint_report = linter.lint_design_md(design_path)
    if lint_report.get("summary", {}).get("errors", 0):
        return design_path, lint_report, blocked("DESIGN.md lint errors", lint_summary=lint_report.get("summary"))
    return design_path, lint_report, None


def initial_report(task: str, design_path: Path, lint_report: dict[str, object], config: dict[str, str], smoke: object) -> dict[str, object]:
    report: dict[str, object] = {
        "ok": False,
        "status": "running",
        "timestamp": int(time.time()),
        "task": task,
        "design": str(design_path),
        "design_sha256": sha256(design_path),
        "lint_summary": lint_report.get("summary", {}),
        "gemini": {
            "configured": True,
            "model": config["model"],
            "protocol_requested": smoke.normalize_gemini_protocol(config["requested_protocol"]),
            "protocol": config["protocol"],
            "url": config["url"],
            "request_shape": "gemini_generate_content" if config["protocol"] == "gemini" else "openai_chat_completions",
        },
        "stitch": {
            "configured": bool(config["stitch_key"]),
            "url": config["stitch_endpoint"],
            "request_shape": "mcp_initialize_and_tools_list",
        },
    }
    return report


def run_gemini_review(report: dict[str, object], smoke: object, config: dict[str, str], prompt: str, timeout: int) -> bool:
    payload = smoke.gemini_payload(config["protocol"], config["model"], prompt)
    try:
        if config["protocol"] == "gemini":
            status, data = smoke.post_gemini_native(config["url"], config["api_key"], payload, timeout)
        else:
            status, data = smoke.post_json(config["url"], config["api_key"], payload, timeout)
        response_shape_ok = smoke.valid_gemini_response(config["protocol"], data)
        gemini_ok = 200 <= status < 300 and response_shape_ok
        report["gemini"] = {
            **report["gemini"],
            "ok": gemini_ok,
            "http_status": status,
            "response_shape_ok": response_shape_ok,
            "review_preview": smoke.content_preview(data),
        }
        hint = smoke.gemini_response_hint(config["protocol"], config["base_url"], data)
        if not response_shape_ok and hint:
            report["gemini"] = {**report["gemini"], "hint": hint}
        return gemini_ok
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:500]
        report["gemini"] = {**report["gemini"], "ok": False, "http_status": exc.code, "error_preview": body}
    except Exception as exc:
        report["gemini"] = {**report["gemini"], "ok": False, "error": exc.__class__.__name__, "message": str(exc)[:300]}
    return False


def stitch_server_info(data: dict[str, object] | str) -> dict[str, object]:
    if not isinstance(data, dict):
        return {}
    result = data.get("result")
    if isinstance(result, dict) and isinstance(result.get("serverInfo"), dict):
        return {"server_info": result["serverInfo"]}
    return {}


def run_stitch_review(report: dict[str, object], smoke: object, config: dict[str, str], timeout: int) -> bool:
    try:
        init_status, init_data = smoke.post_mcp_initialize(config["stitch_endpoint"], config["stitch_key"], timeout)
        tools_status, tools_data = smoke.post_mcp_tools_list(config["stitch_endpoint"], config["stitch_key"], timeout)
        stitch_ok = 200 <= init_status < 300 and 200 <= tools_status < 300
        report["stitch"] = {
            **report["stitch"],
            "ok": stitch_ok,
            "http_status": init_status,
            "tools_status": tools_status,
            "tools": tool_names(tools_data),
        }
        report["stitch"] = {**report["stitch"], **stitch_server_info(init_data)}
        return stitch_ok
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:500]
        report["stitch"] = {**report["stitch"], "ok": False, "http_status": exc.code, "error_preview": body}
    except Exception as exc:
        report["stitch"] = {**report["stitch"], "ok": False, "error": exc.__class__.__name__, "message": str(exc)[:300]}
    return False


def finalize_report(root: Path, report: dict[str, object], gemini_ok: bool, stitch_ok: bool) -> None:
    report["ok"] = bool(gemini_ok and stitch_ok)
    report["status"] = "passed" if report["ok"] else "failed"
    try:
        json_path, md_path = write_evidence(root, report)
        report["evidence"] = {"json": str(json_path), "markdown": str(md_path)}
    except OSError as exc:
        report["evidence_error"] = {"error": exc.__class__.__name__, "message": str(exc)[:300]}


def main() -> int:
    args = parse_args()
    root = args.project.resolve()
    env_check, smoke, linter = load_dependencies()

    env_report = env_check.check_design_env(root, write_missing_template=args.write_template)
    if not env_report["ok"]:
        print(json.dumps({"ok": False, "status": "blocked", "design_env": env_report}, indent=2, ensure_ascii=False))
        return 2
    if env_report.get("mode") == "basic":
        report = {"ok": True, "status": "basic_mode", "gemini": {"skipped": True}, "stitch": {"skipped": True}}
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0

    design_path, lint_report, blocked_report = load_design_report(root, args.design, linter)
    if blocked_report:
        print(json.dumps(blocked_report, indent=2, ensure_ascii=False))
        return 2
    assert design_path is not None

    config = smoke.service_config(root, env_check, env_report)
    review_prompt = build_review_prompt(args.task, design_path, lint_report)
    report = initial_report(args.task, design_path, lint_report, config, smoke)
    gemini_ok = run_gemini_review(report, smoke, config, review_prompt, args.timeout)
    stitch_ok = run_stitch_review(report, smoke, config, args.timeout)
    finalize_report(root, report, gemini_ok, stitch_ok)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
