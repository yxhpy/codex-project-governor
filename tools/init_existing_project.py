#!/usr/bin/env python3
"""Compatibility wrapper for older self-test commands."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from init_project import copy_templates  # noqa: E402


def main(plugin_root: str, repo: str) -> int:
    result = copy_templates(Path(repo), mode="existing", overwrite=False)
    print(f"initialized governance templates in {repo}; created={len(result.created)} preserved={len(result.preserved)}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 3:
        raise SystemExit(main(sys.argv[1], sys.argv[2]))
    raise SystemExit("usage: init_existing_project.py <plugin_root> <repo>")
