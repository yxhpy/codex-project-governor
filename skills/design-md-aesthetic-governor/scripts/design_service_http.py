#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import ssl
import urllib.request
from pathlib import Path

CA_FILE_CANDIDATES = (
    "/etc/ssl/cert.pem",
    "/opt/homebrew/etc/openssl@3/cert.pem",
    "/opt/homebrew/etc/ca-certificates/cert.pem",
    "/usr/local/etc/openssl@3/cert.pem",
    "/usr/local/etc/ca-certificates/cert.pem",
)
ROOT = Path(__file__).resolve().parents[3]


def plugin_version() -> str:
    try:
        data = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "unknown"
    version = data.get("version")
    return str(version) if isinstance(version, str) and version else "unknown"


PLUGIN_VERSION = plugin_version()
USER_AGENT = f"project-governor-design-smoke/{PLUGIN_VERSION}"


def default_ssl_context() -> ssl.SSLContext:
    env_cafile = os.environ.get("SSL_CERT_FILE", "").strip()
    candidates = (env_cafile, *CA_FILE_CANDIDATES) if env_cafile else CA_FILE_CANDIDATES
    for candidate in candidates:
        path = Path(candidate)
        if path.is_file():
            return ssl.create_default_context(cafile=str(path))
    return ssl.create_default_context()


def decode_json_response(response) -> dict[str, object] | str:
    text = response.read().decode("utf-8", errors="replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text[:500]


def post_json(url: str, api_key: str, payload: dict[str, object], timeout: int) -> tuple[int, dict[str, object] | str]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout, context=default_ssl_context()) as response:
        return response.status, decode_json_response(response)


def post_gemini_native(url: str, api_key: str, payload: dict[str, object], timeout: int) -> tuple[int, dict[str, object] | str]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "X-Goog-Api-Key": api_key,
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout, context=default_ssl_context()) as response:
        return response.status, decode_json_response(response)


def post_mcp(url: str, api_key: str, payload: dict[str, object], timeout: int) -> tuple[int, dict[str, object] | str]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "X-Goog-Api-Key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout, context=default_ssl_context()) as response:
        return response.status, decode_json_response(response)


def post_mcp_initialize(url: str, api_key: str, timeout: int) -> tuple[int, dict[str, object] | str]:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "project-governor-design-smoke", "version": PLUGIN_VERSION},
        },
    }
    return post_mcp(url, api_key, payload, timeout)


def post_mcp_tools_list(url: str, api_key: str, timeout: int) -> tuple[int, dict[str, object] | str]:
    return post_mcp(url, api_key, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}, timeout)


def openai_content_preview(data: dict[str, object]) -> str:
    choices = data.get("choices")
    if not (isinstance(choices, list) and choices):
        return ""
    first = choices[0]
    if not isinstance(first, dict):
        return ""
    message = first.get("message")
    if isinstance(message, dict) and isinstance(message.get("content"), str):
        return str(message["content"])[:300]
    text = first.get("text")
    return text[:300] if isinstance(text, str) else ""


def gemini_parts_preview(parts: object) -> str:
    if not isinstance(parts, list):
        return ""
    text_parts = [
        part.get("text", "")
        for part in parts
        if isinstance(part, dict) and isinstance(part.get("text"), str)
    ]
    return "\n".join(text_parts)[:300] if text_parts else ""


def gemini_content_preview(data: dict[str, object]) -> str:
    candidates = data.get("candidates")
    if not (isinstance(candidates, list) and candidates):
        return ""
    first = candidates[0]
    if not isinstance(first, dict):
        return ""
    content = first.get("content")
    return gemini_parts_preview(content.get("parts")) if isinstance(content, dict) else ""


def content_preview(data: dict[str, object] | str) -> str:
    if isinstance(data, str):
        return data[:300]
    return openai_content_preview(data) or gemini_content_preview(data)
