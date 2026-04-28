#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Mapping

ENV_FILE = ".env-design"
DEFAULT_STITCH_MCP_URL = "https://stitch.googleapis.com/mcp"
SKIP_ENV_KEYS = ("DESIGN_BASIC_MODE", "DESIGN_ENV_SKIP", "DESIGN_SERVICE_CONFIG_SKIP")
GEMINI_PROTOCOL_ALIASES = ("GEMINI_PROTOCOL", "DESIGN_GEMINI_PROTOCOL")
STITCH_URL_ALIASES = ("STITCH_MCP_URL", "DESIGN_STITCH_MCP_URL", "STITCH_MCP_ENDPOINT", "DESIGN_STITCH_MCP_ENDPOINT")
REQUIRED_KEYS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("GEMINI_BASE_URL", ("GEMINI_BASE_URL", "DESIGN_GEMINI_BASE_URL")),
    ("GEMINI_API_KEY", ("GEMINI_API_KEY", "DESIGN_GEMINI_API_KEY")),
    ("GEMINI_MODEL", ("GEMINI_MODEL", "DESIGN_GEMINI_MODEL")),
    ("STITCH_MCP_API_KEY", ("STITCH_MCP_API_KEY", "DESIGN_STITCH_MCP_API_KEY")),
)


def root_dir(project: Path | None = None) -> Path:
    if project is not None:
        return project.resolve()
    try:
        out = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], stderr=subprocess.DEVNULL, text=True).strip()
        if out:
            return Path(out)
    except Exception:
        pass
    return Path.cwd()


def parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def write_template(path: Path) -> bool:
    if path.exists():
        return False
    path.write_text(
        "\n".join(
            [
                "# Project-local design tooling configuration. Do not commit this file.",
                "# Shell environment variables with the same names take precedence.",
                "GEMINI_BASE_URL=",
                "GEMINI_API_KEY=",
                "GEMINI_MODEL=",
                "GEMINI_PROTOCOL=auto",
                f"STITCH_MCP_URL={DEFAULT_STITCH_MCP_URL}",
                "STITCH_MCP_API_KEY=",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return True


def resolve_stitch_mcp_url(env: Mapping[str, str], file_values: Mapping[str, str] | None = None) -> str:
    values = file_values or {}
    for key in STITCH_URL_ALIASES:
        value = str(env.get(key, "")).strip()
        if value:
            return value
    for key in STITCH_URL_ALIASES:
        value = str(values.get(key, "")).strip()
        if value:
            return value
    return DEFAULT_STITCH_MCP_URL


def resolve_gemini_protocol(env: Mapping[str, str], file_values: Mapping[str, str] | None = None) -> str:
    values = file_values or {}
    for key in GEMINI_PROTOCOL_ALIASES:
        value = str(env.get(key, "")).strip()
        if value:
            return value
    for key in GEMINI_PROTOCOL_ALIASES:
        value = str(values.get(key, "")).strip()
        if value:
            return value
    return "auto"


def ensure_git_exclude(root: Path) -> bool:
    try:
        rel = subprocess.check_output(["git", "rev-parse", "--git-path", "info/exclude"], cwd=root, stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return False
    if not rel:
        return False
    exclude = (root / rel).resolve() if not Path(rel).is_absolute() else Path(rel)
    exclude.parent.mkdir(parents=True, exist_ok=True)
    existing = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
    if ENV_FILE in {line.strip() for line in existing.splitlines()}:
        return False
    prefix = "" if existing.endswith("\n") or not existing else "\n"
    try:
        exclude.write_text(existing + prefix + "# Project Governor design tooling secrets\n" + ENV_FILE + "\n", encoding="utf-8")
    except OSError:
        return False
    return True


def check_design_env(
    root: Path | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    write_missing_template: bool = False,
) -> dict[str, object]:
    project = root_dir(root)
    env = environ if environ is not None else os.environ
    skip_key = next((key for key in SKIP_ENV_KEYS if str(env.get(key, "")).strip() in {"1", "true", "TRUE", "yes", "YES"}), "")
    if skip_key:
        return {
            "ok": True,
            "status": "basic_mode",
            "mode": "basic",
            "env_file": ENV_FILE,
            "gemini_protocol": resolve_gemini_protocol(env),
            "stitch_mcp_url": resolve_stitch_mcp_url(env),
            "basic_mode_env": skip_key,
            "required": [canonical for canonical, _aliases in REQUIRED_KEYS],
            "provided": {},
            "missing": [],
            "template_created": False,
            "git_exclude_updated": False,
            "instructions": [
                "Design-service configuration was intentionally bypassed by shell environment variable; use basic mode.",
                "Basic mode allows frontend work with DESIGN.md, local lint, token discipline, and drift checks, but without Gemini/Stitch review or prototyping assistance.",
                "Do not place basic-mode flags in .env-design; use a shell environment variable for intentional bypass only.",
            ],
        }
    env_file = project / ENV_FILE
    file_values = parse_env_file(env_file)
    gemini_protocol = resolve_gemini_protocol(env, file_values)
    stitch_mcp_url = resolve_stitch_mcp_url(env, file_values)
    provided: dict[str, str] = {}
    missing: list[str] = []

    for canonical, aliases in REQUIRED_KEYS:
        source = ""
        for key in aliases:
            if str(env.get(key, "")).strip():
                source = f"environment:{key}"
                break
        if not source:
            for key in aliases:
                if file_values.get(key, "").strip():
                    source = f"{ENV_FILE}:{key}"
                    break
        if source:
            provided[canonical] = source
        else:
            missing.append(canonical)

    template_created = False
    git_exclude_updated = False
    if missing and write_missing_template:
        template_created = write_template(env_file)
        git_exclude_updated = ensure_git_exclude(project)

    return {
        "ok": not missing,
        "status": "configured" if not missing else "missing",
        "mode": "full_service" if not missing else "blocked",
        "env_file": ENV_FILE,
        "gemini_protocol": gemini_protocol,
        "stitch_mcp_url": stitch_mcp_url,
        "required": [canonical for canonical, _aliases in REQUIRED_KEYS],
        "provided": provided,
        "missing": missing,
        "template_created": template_created,
        "git_exclude_updated": git_exclude_updated,
        "instructions": [
            "Set the required keys as shell environment variables, or fill them in the project-root .env-design file.",
            "Do not commit .env-design because it may contain API keys.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check DESIGN.md Aesthetic Governor service configuration.")
    parser.add_argument("--project", type=Path, default=None)
    parser.add_argument("--write-template", action="store_true", help="Create a blank .env-design file when required keys are missing.")
    args = parser.parse_args()
    report = check_design_env(args.project, write_missing_template=args.write_template)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
