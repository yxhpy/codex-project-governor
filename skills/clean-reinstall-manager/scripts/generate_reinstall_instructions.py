#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

DEFAULT_REPO = "https://github.com/yxhpy/codex-project-governor.git"


def default_plugin_dir() -> Path:
    return Path(os.environ.get("CODEX_PROJECT_GOVERNOR_PLUGIN_DIR", Path.home() / ".codex" / "plugins" / "codex-project-governor")).expanduser()


def build(plugin_dir: Path, repo_url: str, ref: str, package_manager: str = "git") -> dict:
    plugin_dir = plugin_dir.expanduser()
    backup_dir = f"{plugin_dir}.backup.$(date +%Y%m%d-%H%M%S)"
    commands = [
        "set -euo pipefail",
        f'PLUGIN_DIR="{plugin_dir}"',
        f'BACKUP_DIR="{backup_dir}"',
        'if [ -d "$PLUGIN_DIR" ]; then mv "$PLUGIN_DIR" "$BACKUP_DIR"; fi',
        'mkdir -p "$(dirname "$PLUGIN_DIR")"',
        f'git clone --depth 1 --branch "{ref}" "{repo_url}" "$PLUGIN_DIR"' if ref not in {"", "main", "HEAD"} else f'git clone --depth 1 "{repo_url}" "$PLUGIN_DIR"',
        'python3 "$PLUGIN_DIR/tests/selftest.py" || true',
        'echo "Project Governor reinstalled at: $PLUGIN_DIR"',
        'echo "Previous install backup: ${BACKUP_DIR:-none}"',
    ]
    return {
        "status": "instructions_only",
        "plugin_dir": str(plugin_dir),
        "repo_url": repo_url,
        "ref": ref,
        "destructive_actions": ["moves existing plugin directory to backup", "creates a fresh clone"],
        "commands": commands,
        "shell": "\n".join(commands),
        "notes": [
            "Run these commands outside the plugin directory.",
            "This reinstalls the user-level plugin only; it does not overwrite initialized project governance files.",
            "After reinstall, run clean-reinstall-manager or project-hygiene-doctor inside each governed project if project refresh is needed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plugin-dir", type=Path, default=default_plugin_dir())
    parser.add_argument("--repo-url", default=DEFAULT_REPO)
    parser.add_argument("--ref", default="main")
    parser.add_argument("--format", choices=["json", "shell"], default="json")
    args = parser.parse_args()
    result = build(args.plugin_dir, args.repo_url, args.ref)
    if args.format == "shell":
        print(result["shell"])
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
