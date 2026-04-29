#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import urllib.error
from pathlib import Path
from typing import Mapping

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from design_service_http import content_preview, post_gemini_native, post_json, post_mcp_initialize, post_mcp_tools_list


def load_env_checker():
    spec = importlib.util.spec_from_file_location("design_env_check", SCRIPT_DIR / "design_env_check.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def merged_env(root: Path, environ: Mapping[str, str]) -> dict[str, str]:
    checker = load_env_checker()
    values = checker.parse_env_file(root / checker.ENV_FILE)
    merged = dict(values)
    for key, value in environ.items():
        if value:
            merged[key] = value
    return merged


def first_value(values: Mapping[str, str], *keys: str) -> str:
    for key in keys:
        value = str(values.get(key, "")).strip()
        if value:
            return value
    return ""


def openai_chat_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    if base.endswith("/v1"):
        return base + "/chat/completions"
    return base + "/v1/chat/completions"


def gemini_generate_url(base_url: str, model: str) -> str:
    base = base_url.rstrip("/")
    if ":generateContent" in base:
        return base
    if "/models/" in base:
        return base + ":generateContent"
    suffix = f"/models/{model}:generateContent"
    if base.endswith("/v1") or base.endswith("/v1beta"):
        return base + suffix
    return base + "/v1beta" + suffix


def normalize_gemini_protocol(protocol: str) -> str:
    value = protocol.strip().lower().replace("-", "_")
    aliases = {
        "": "auto",
        "auto": "auto",
        "openai": "openai",
        "openai_compatible": "openai",
        "chat_completions": "openai",
        "gemini": "gemini",
        "native": "gemini",
        "generate_content": "gemini",
        "generatecontent": "gemini",
    }
    if value not in aliases:
        raise ValueError(f"Unsupported GEMINI_PROTOCOL {protocol!r}; use auto, openai, or gemini.")
    return aliases[value]


def resolve_gemini_protocol(protocol: str, base_url: str) -> str:
    normalized = normalize_gemini_protocol(protocol)
    if normalized != "auto":
        return normalized
    host_hint = base_url.lower()
    if "generativelanguage.googleapis.com" in host_hint or "aiplatform.googleapis.com" in host_hint:
        return "gemini"
    return "openai"


def valid_gemini_response(protocol: str, data: dict[str, object] | str) -> bool:
    if not isinstance(data, dict):
        return False
    key = "candidates" if protocol == "gemini" else "choices"
    value = data.get(key)
    return isinstance(value, list) and bool(value)


def gemini_response_hint(protocol: str, base_url: str, data: dict[str, object] | str) -> str:
    if isinstance(data, str) and data.lstrip().lower().startswith(("<!doctype html", "<html")):
        if protocol == "gemini":
            return "Native Gemini endpoint returned HTML instead of JSON; set GEMINI_BASE_URL to the provider's Gemini protocol root, for example https://host/gemini when the gateway serves /gemini/v1beta."
        return "OpenAI-compatible endpoint returned HTML instead of JSON; verify GEMINI_BASE_URL points to the API root, not the web UI root."
    if isinstance(data, dict):
        return ""
    return "Gemini endpoint returned a non-JSON response; verify protocol and base URL."


def gemini_payload(protocol: str, model: str, task: str) -> dict[str, object]:
    if protocol == "gemini":
        return {
            "systemInstruction": {"parts": [{"text": "You are a concise design review smoke-test responder."}]},
            "contents": [{"role": "user", "parts": [{"text": task}]}],
            "generationConfig": {"temperature": 0, "maxOutputTokens": 64},
        }
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a concise design review smoke-test responder."},
            {"role": "user", "content": task},
        ],
        "temperature": 0,
        "max_tokens": 64,
    }


def gemini_request_url(protocol: str, base_url: str, model: str) -> str:
    if protocol == "gemini":
        return gemini_generate_url(base_url, model)
    return openai_chat_url(base_url)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke test DESIGN.md Aesthetic Governor external design services without printing secrets.")
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--task", default="Return one short sentence confirming the design review smoke test is reachable.")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def service_config(root: Path, checker: object, env_report: dict[str, object]) -> dict[str, str]:
    values = merged_env(root, os.environ)
    base_url = first_value(values, "GEMINI_BASE_URL", "DESIGN_GEMINI_BASE_URL")
    api_key = first_value(values, "GEMINI_API_KEY", "DESIGN_GEMINI_API_KEY")
    model = first_value(values, "GEMINI_MODEL", "DESIGN_GEMINI_MODEL")
    requested_protocol = first_value(values, "GEMINI_PROTOCOL", "DESIGN_GEMINI_PROTOCOL") or str(env_report.get("gemini_protocol") or "auto")
    stitch_key = first_value(values, "STITCH_MCP_API_KEY", "DESIGN_STITCH_MCP_API_KEY")
    stitch_endpoint = first_value(values, "STITCH_MCP_URL", "DESIGN_STITCH_MCP_URL", "STITCH_MCP_ENDPOINT", "DESIGN_STITCH_MCP_ENDPOINT") or checker.DEFAULT_STITCH_MCP_URL
    protocol = resolve_gemini_protocol(requested_protocol, base_url)
    url = gemini_request_url(protocol, base_url, model)
    return {
        "base_url": base_url,
        "api_key": api_key,
        "model": model,
        "requested_protocol": requested_protocol,
        "protocol": protocol,
        "stitch_key": stitch_key,
        "stitch_endpoint": stitch_endpoint,
        "url": url,
    }


def initial_report(config: dict[str, str], dry_run: bool) -> dict[str, object]:
    report: dict[str, object] = {
        "ok": False,
        "status": "dry_run" if dry_run else "running",
        "gemini": {
            "configured": True,
            "model": config["model"],
            "protocol_requested": normalize_gemini_protocol(config["requested_protocol"]),
            "protocol": config["protocol"],
            "url": config["url"],
            "request_shape": "gemini_generate_content" if config["protocol"] == "gemini" else "openai_chat_completions",
        },
        "stitch": {
            "configured": bool(config["stitch_key"]),
            "endpoint_configured": bool(config["stitch_endpoint"]),
            "url": config["stitch_endpoint"],
            "request_shape": "mcp_initialize_streamable_http",
            "status": "endpoint_present",
        },
    }
    return report


def run_gemini_smoke(report: dict[str, object], config: dict[str, str], task: str, timeout: int) -> bool:
    payload = gemini_payload(config["protocol"], config["model"], task)
    try:
        if config["protocol"] == "gemini":
            status, data = post_gemini_native(config["url"], config["api_key"], payload, timeout)
        else:
            status, data = post_json(config["url"], config["api_key"], payload, timeout)
        response_shape_ok = valid_gemini_response(config["protocol"], data)
        gemini_ok = 200 <= status < 300 and response_shape_ok
        report["gemini"] = {
            **report["gemini"],
            "ok": gemini_ok,
            "http_status": status,
            "response_shape_ok": response_shape_ok,
            "content_preview": content_preview(data),
        }
        hint = gemini_response_hint(config["protocol"], config["base_url"], data)
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
    if not isinstance(result, dict):
        return {}
    server_info = result.get("serverInfo")
    if not isinstance(server_info, dict):
        return {}
    return {
        "server_name": server_info.get("name"),
        "server_version": server_info.get("version"),
    }


def run_stitch_smoke(report: dict[str, object], config: dict[str, str], timeout: int) -> bool:
    if not config["stitch_key"]:
        return False
    try:
        stitch_status, stitch_data = post_mcp_initialize(config["stitch_endpoint"], config["stitch_key"], timeout)
        stitch_ok = 200 <= stitch_status < 300
        report["stitch"] = {**report["stitch"], "ok": stitch_ok, "http_status": stitch_status, **stitch_server_info(stitch_data)}
        return stitch_ok
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:500]
        report["stitch"] = {**report["stitch"], "ok": False, "http_status": exc.code, "error_preview": body}
    except Exception as exc:
        report["stitch"] = {**report["stitch"], "ok": False, "error": exc.__class__.__name__, "message": str(exc)[:300]}
    return False


def main() -> int:
    args = parse_args()
    root = args.project.resolve()
    checker = load_env_checker()
    env_report = checker.check_design_env(root, write_missing_template=False)
    if not env_report["ok"]:
        print(json.dumps({"ok": False, "status": "blocked", "design_env": env_report}, indent=2, ensure_ascii=False))
        return 2
    if env_report.get("mode") == "basic":
        print(json.dumps({"ok": True, "status": "basic_mode", "gemini": {"skipped": True}, "stitch": {"skipped": True}}, indent=2, ensure_ascii=False))
        return 0

    try:
        config = service_config(root, checker, env_report)
    except ValueError as exc:
        print(json.dumps({"ok": False, "status": "blocked", "error": str(exc)}, indent=2, ensure_ascii=False))
        return 2

    report = initial_report(config, args.dry_run)
    if args.dry_run:
        report["ok"] = True
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0

    gemini_ok = run_gemini_smoke(report, config, args.task, args.timeout)
    stitch_ok = run_stitch_smoke(report, config, args.timeout)
    report["ok"] = bool(gemini_ok and stitch_ok)
    report["status"] = "passed" if report["ok"] else "failed"
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
