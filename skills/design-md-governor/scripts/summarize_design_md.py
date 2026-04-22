#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from lint_design_md import split_frontmatter, section_headings


def summarize(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    tokens, body, findings = split_frontmatter(text)
    return {
        "file": str(path),
        "name": tokens.get("name"),
        "version": tokens.get("version"),
        "description": tokens.get("description"),
        "token_counts": {
            "colors": len(tokens.get("colors", {})) if isinstance(tokens.get("colors"), dict) else 0,
            "typography": len(tokens.get("typography", {})) if isinstance(tokens.get("typography"), dict) else 0,
            "rounded": len(tokens.get("rounded", {})) if isinstance(tokens.get("rounded"), dict) else 0,
            "spacing": len(tokens.get("spacing", {})) if isinstance(tokens.get("spacing"), dict) else 0,
            "components": len(tokens.get("components", {})) if isinstance(tokens.get("components"), dict) else 0,
        },
        "colors": tokens.get("colors", {}),
        "typography_tokens": sorted(tokens.get("typography", {}).keys()) if isinstance(tokens.get("typography"), dict) else [],
        "component_tokens": sorted(tokens.get("components", {}).keys()) if isinstance(tokens.get("components"), dict) else [],
        "sections": section_headings(body),
        "parse_findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize DESIGN.md tokens and sections.")
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(args.file), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
