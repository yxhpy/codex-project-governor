#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

SECTION_ORDER = [
    "overview",
    "colors",
    "typography",
    "layout",
    "elevation & depth",
    "shapes",
    "components",
    "do's and don'ts",
]
SECTION_ALIASES = {
    "brand & style": "overview",
    "layout & spacing": "layout",
    "elevation": "elevation & depth",
}
VALID_COMPONENT_PROPERTIES = {
    "backgroundColor",
    "textColor",
    "typography",
    "rounded",
    "padding",
    "size",
    "height",
    "width",
}
COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$")
DIMENSION_RE = re.compile(r"^-?\d+(\.\d+)?(px|em|rem)$")
REF_RE = re.compile(r"^\{([A-Za-z0-9_.\-]+)\}$")


def finding(severity: str, path: str, message: str, rule: str) -> dict[str, str]:
    return {"severity": severity, "path": path, "message": message, "rule": rule}


def split_frontmatter(text: str) -> tuple[dict[str, Any], str, list[dict[str, str]]]:
    findings: list[dict[str, str]] = []
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        findings.append(finding("info", "frontmatter", "No YAML front matter found; DESIGN.md can exist with prose only, but tokens will be unavailable.", "missing-frontmatter"))
        return {}, text, findings
    end = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end = idx
            break
    if end is None:
        findings.append(finding("error", "frontmatter", "YAML front matter starts with --- but has no closing --- fence.", "frontmatter-fence"))
        return {}, "\n".join(lines[1:]), findings
    yaml_text = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1 :])
    tokens, parse_findings = parse_simple_yaml(yaml_text)
    findings.extend(parse_findings)
    return tokens, body, findings


def unquote(value: str) -> str | None:
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return None


def parse_number(value: str) -> Any:
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    return None


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    quoted = unquote(value)
    if quoted is not None:
        return quoted
    number = parse_number(value)
    if number is not None:
        return number
    if value in {"true", "false"}:
        return value == "true"
    return value


def yaml_line_entry(raw: str, line_no: int) -> tuple[int, str, str, dict[str, str] | None] | None:
    if not raw.strip() or raw.lstrip().startswith("#"):
        return None
    indent = len(raw) - len(raw.lstrip(" "))
    if "\t" in raw[:indent]:
        return -1, "", "", finding("error", f"frontmatter.line{line_no}", "Tabs are not supported in indentation.", "yaml-tabs")
    stripped = raw.strip()
    if ":" not in stripped:
        return -1, "", "", finding("warning", f"frontmatter.line{line_no}", "Line is not a key/value token entry.", "yaml-parse")
    key, value = stripped.split(":", 1)
    return indent, key.strip(), value, None


def parent_for_indent(stack: list[tuple[int, dict[str, Any]]], indent: int) -> dict[str, Any]:
    while stack and indent <= stack[-1][0]:
        stack.pop()
    return stack[-1][1]


def parse_simple_yaml(yaml_text: str) -> tuple[dict[str, Any], list[dict[str, str]]]:
    """A small YAML subset parser sufficient for DESIGN.md token maps.

    Supports indentation-based nested maps and scalar `key: value` lines.
    It intentionally avoids third-party dependencies. Projects that need full
    YAML should use the official @google/design.md CLI.
    """
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    findings: list[dict[str, str]] = []
    for line_no, raw in enumerate(yaml_text.splitlines(), start=2):
        entry = yaml_line_entry(raw, line_no)
        if entry is None:
            continue
        indent, key, value, line_finding = entry
        if line_finding:
            findings.append(line_finding)
            continue
        parent = parent_for_indent(stack, indent)
        if value.strip() == "":
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = parse_scalar(value)
    return root, findings


def get_path(data: dict[str, Any], path: str) -> Any:
    cur: Any = data
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def resolve_value(data: dict[str, Any], value: Any) -> Any:
    if isinstance(value, str):
        match = REF_RE.match(value)
        if match:
            return get_path(data, match.group(1))
    return value


def hex_to_rgb(hex_color: str) -> tuple[float, float, float] | None:
    if not isinstance(hex_color, str) or not COLOR_RE.match(hex_color):
        return None
    hex_color = hex_color.lstrip("#")[:6]
    return tuple(int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def channel(c: float) -> float:
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb: tuple[float, float, float]) -> float:
    r, g, b = rgb
    return 0.2126 * channel(r) + 0.6722 * channel(g) + 0.0722 * channel(b)


def contrast(a: str, b: str) -> float | None:
    rgb_a = hex_to_rgb(a)
    rgb_b = hex_to_rgb(b)
    if not rgb_a or not rgb_b:
        return None
    la, lb = luminance(rgb_a), luminance(rgb_b)
    lighter, darker = max(la, lb), min(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


def section_headings(body: str) -> list[str]:
    headings: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            title = line[3:].strip()
            normalized = SECTION_ALIASES.get(title.lower(), title.lower())
            headings.append(normalized)
    return headings


def lint_colors(colors: Any, typography: Any) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if colors and isinstance(colors, dict):
        if "primary" not in colors:
            findings.append(finding("warning", "colors.primary", "Colors are defined but no primary color token exists.", "missing-primary"))
        for name, value in colors.items():
            if not isinstance(value, str) or not COLOR_RE.match(value):
                findings.append(finding("error", f"colors.{name}", f"Color token {name!r} must be a hex sRGB value like #1A1C1E.", "invalid-color"))
    if colors and not typography:
        findings.append(finding("warning", "typography", "Colors are defined but no typography tokens exist.", "missing-typography"))
    return findings


def lint_dimension_group(tokens: dict[str, Any], group_name: str) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    group = tokens.get(group_name, {})
    if not isinstance(group, dict):
        return findings
    for name, value in group.items():
        if isinstance(value, (int, float)):
            continue
        if not isinstance(value, str) or (not DIMENSION_RE.match(value) and not REF_RE.match(value)):
            findings.append(finding("warning", f"{group_name}.{name}", "Spacing/rounded tokens should be dimensions, numbers, or token references.", "dimension-format"))
    return findings


def lint_typography_required(name: str, spec: dict[str, Any]) -> list[dict[str, str]]:
    if "fontFamily" not in spec or "fontSize" not in spec:
        return [finding("warning", f"typography.{name}", "Typography token should include fontFamily and fontSize.", "typography-required")]
    return []


def lint_typography_font_size(name: str, spec: dict[str, Any]) -> list[dict[str, str]]:
    font_size = spec.get("fontSize")
    if font_size and not (isinstance(font_size, str) and (DIMENSION_RE.match(font_size) or REF_RE.match(font_size))):
        return [finding("warning", f"typography.{name}.fontSize", "fontSize should be a dimension or token reference.", "font-size-format")]
    return []


def lint_typography_item(name: str, spec: Any) -> list[dict[str, str]]:
    if not isinstance(spec, dict):
        return [finding("warning", f"typography.{name}", "Typography token should be an object.", "typography-object")]
    return [*lint_typography_required(name, spec), *lint_typography_font_size(name, spec)]


def lint_typography(typography: Any) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for name, spec in (typography.items() if isinstance(typography, dict) else []):
        findings.extend(lint_typography_item(name, spec))
    return findings


def lint_component_property(tokens: dict[str, Any], component: str, prop: str, value: Any) -> tuple[list[dict[str, str]], set[str]]:
    findings: list[dict[str, str]] = []
    referenced_colors: set[str] = set()
    if prop not in VALID_COMPONENT_PROPERTIES:
        findings.append(finding("warning", f"components.{component}.{prop}", "Unknown component property; preserve but review for DESIGN.md compatibility.", "unknown-component-property"))
    if isinstance(value, str):
        ref = REF_RE.match(value)
        if ref:
            target = ref.group(1)
            resolved = get_path(tokens, target)
            if resolved is None:
                findings.append(finding("error", f"components.{component}.{prop}", f"Broken token reference {{{target}}}.", "broken-ref"))
            if target.startswith("colors."):
                referenced_colors.add(target.split(".", 1)[1])
    return findings, referenced_colors


def lint_component(tokens: dict[str, Any], component: str, spec: Any) -> tuple[list[dict[str, str]], set[str]]:
    findings: list[dict[str, str]] = []
    referenced_colors: set[str] = set()
    if not isinstance(spec, dict):
        findings.append(finding("warning", f"components.{component}", "Component token should be an object.", "component-object"))
        return findings, referenced_colors
    for prop, value in spec.items():
        prop_findings, prop_colors = lint_component_property(tokens, component, prop, value)
        findings.extend(prop_findings)
        referenced_colors.update(prop_colors)
    bg = resolve_value(tokens, spec.get("backgroundColor"))
    fg = resolve_value(tokens, spec.get("textColor"))
    if isinstance(bg, str) and isinstance(fg, str) and COLOR_RE.match(bg) and COLOR_RE.match(fg):
        ratio = contrast(bg, fg)
        if ratio is not None and ratio < 4.5:
            findings.append(finding("warning", f"components.{component}", f"backgroundColor/textColor contrast ratio {ratio:.2f}:1 is below WCAG AA 4.5:1.", "contrast-ratio"))
    return findings, referenced_colors


def lint_components(tokens: dict[str, Any], components: Any) -> tuple[list[dict[str, str]], set[str]]:
    findings: list[dict[str, str]] = []
    referenced_colors: set[str] = set()
    if not isinstance(components, dict):
        return findings, referenced_colors
    for component, spec in components.items():
        component_findings, component_colors = lint_component(tokens, component, spec)
        findings.extend(component_findings)
        referenced_colors.update(component_colors)
    return findings, referenced_colors


def lint_orphaned_colors(colors: Any, components: Any, referenced_colors: set[str]) -> list[dict[str, str]]:
    if not isinstance(colors, dict):
        return []
    orphaned = sorted(set(colors) - referenced_colors)
    if orphaned and components:
        return [finding("info", "colors", "Color tokens not referenced by components: " + ", ".join(orphaned), "orphaned-tokens")]
    return []


def token_summary(colors: Any, typography: Any, components: Any) -> dict[str, str]:
    color_count = len(colors) if isinstance(colors, dict) else 0
    typography_count = len(typography) if isinstance(typography, dict) else 0
    component_count = len(components) if isinstance(components, dict) else 0
    return finding("info", "tokens", f"Token summary: colors={color_count}, typography={typography_count}, components={component_count}.", "token-summary")


def lint_tokens(tokens: dict[str, Any]) -> list[dict[str, str]]:
    colors = tokens.get("colors", {})
    typography = tokens.get("typography", {})
    components = tokens.get("components", {})
    findings: list[dict[str, str]] = []
    findings.extend(lint_colors(colors, typography))
    for group_name in ("spacing", "rounded"):
        findings.extend(lint_dimension_group(tokens, group_name))
    findings.extend(lint_typography(typography))
    component_findings, referenced_colors = lint_components(tokens, components)
    findings.extend(component_findings)
    findings.extend(lint_orphaned_colors(colors, components, referenced_colors))
    findings.append(token_summary(colors, typography, components))
    return findings


def lint_sections(body: str) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    headings = section_headings(body)
    seen: set[str] = set()
    for heading in headings:
        if heading in seen:
            findings.append(finding("error", f"section.{heading}", "Duplicate DESIGN.md section heading.", "duplicate-section"))
        seen.add(heading)
    positions = [SECTION_ORDER.index(h) for h in headings if h in SECTION_ORDER]
    if positions != sorted(positions):
        findings.append(finding("warning", "sections", "Sections are not in canonical DESIGN.md order.", "section-order"))
    if headings and not any(h in headings for h in ("overview", "colors", "typography")):
        findings.append(finding("info", "sections", "Core sections Overview, Colors, and Typography are absent.", "missing-sections"))
    return findings


def lint_design_md(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    tokens, body, findings = split_frontmatter(text)
    findings.extend(lint_tokens(tokens))
    findings.extend(lint_sections(body))
    summary = {
        "errors": sum(1 for item in findings if item["severity"] == "error"),
        "warnings": sum(1 for item in findings if item["severity"] == "warning"),
        "info": sum(1 for item in findings if item["severity"] == "info"),
    }
    return {"status": "fail" if summary["errors"] else "pass", "file": str(path), "summary": summary, "findings": findings, "designSystem": tokens}


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint a DESIGN.md file using bundled Project Governor checks.")
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    result = lint_design_md(args.file)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
