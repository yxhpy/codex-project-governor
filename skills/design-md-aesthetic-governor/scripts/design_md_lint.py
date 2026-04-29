#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
DIM_RE = re.compile(r"^-?(?:\d+|\d*\.\d+)(px|em|rem)$")
REF_RE = re.compile(r"\{([^{}]+)\}")
ALLOWED_COMPONENT_PROPS = {"backgroundColor", "textColor", "typography", "rounded", "padding", "size", "height", "width"}
SECTION_ORDER = [["overview", "brand & style"], ["colors"], ["typography"], ["layout", "layout & spacing"], ["elevation & depth", "elevation"], ["shapes"], ["components"], ["do's and don'ts", "dos and don'ts", "do’s and don’ts"]]

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
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    number = parse_number(value)
    if number is not None:
        return number
    return value

def parse_simple_yaml(text: str) -> Dict[str, Any]:
    root: Dict[str, Any] = {}
    stack: List[Tuple[int, Dict[str, Any]]] = [(-1, root)]
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip().strip('"\'')
        val = val.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if val == "":
            obj: Dict[str, Any] = {}
            parent[key] = obj
            stack.append((indent, obj))
        else:
            parent[key] = parse_scalar(val.split(" #", 1)[0].strip())
    return root

def split_front_matter(content: str):
    findings = []
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        findings.append({"severity": "error", "path": "frontmatter", "message": "DESIGN.md must start with a YAML front matter fence '---'."})
        return "", content, findings
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        findings.append({"severity": "error", "path": "frontmatter", "message": "DESIGN.md front matter is missing closing '---'."})
        return "\n".join(lines[1:]), "", findings
    return "\n".join(lines[1:end]), "\n".join(lines[end+1:]), findings

def flatten_tokens(obj: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    out = {}
    for k, v in obj.items():
        path = f"{prefix}.{k}" if prefix else k
        out[path] = v
        if isinstance(v, dict):
            out.update(flatten_tokens(v, path))
    return out

def hex_to_rgb(hex_color: str):
    h = hex_color.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def lin(c: float) -> float:
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

def contrast_ratio(a: str, b: str) -> float:
    r1, g1, b1 = hex_to_rgb(a)
    r2, g2, b2 = hex_to_rgb(b)
    l1 = 0.2126 * lin(r1) + 0.7152 * lin(g1) + 0.0722 * lin(b1)
    l2 = 0.2126 * lin(r2) + 0.7152 * lin(g2) + 0.0722 * lin(b2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)

def canonical_section(name: str) -> int:
    n = name.strip().lower()
    for idx, aliases in enumerate(SECTION_ORDER):
        if n in aliases:
            return idx
    return 999


def finding(severity: str, path: str, message: str) -> dict[str, str]:
    return {"severity": severity, "path": path, "message": message}


def token_group(data: Dict[str, Any], name: str) -> Dict[str, Any]:
    value = data.get(name)
    return value if isinstance(value, dict) else {}


def lint_metadata(data: Dict[str, Any], colors: Dict[str, Any], typography: Dict[str, Any]) -> List[dict[str, str]]:
    findings: List[dict[str, str]] = []
    if not data.get("name"):
        findings.append(finding("warning", "name", "Missing design system name."))
    if colors and "primary" not in colors:
        findings.append(finding("warning", "colors.primary", "Colors exist but no primary color token is defined."))
    if colors and not typography:
        findings.append(finding("warning", "typography", "Colors exist but no typography tokens are defined."))
    return findings


def lint_color_tokens(colors: Dict[str, Any]) -> List[dict[str, str]]:
    findings: List[dict[str, str]] = []
    for name, val in colors.items():
        if not isinstance(val, str) or not HEX_RE.match(val):
            findings.append(finding("error", f"colors.{name}", f"Color token must be #RGB or #RRGGBB, got {val!r}."))
    return findings


def lint_dimension_tokens(group_name: str, group: Dict[str, Any]) -> List[dict[str, str]]:
    findings: List[dict[str, str]] = []
    for name, val in group.items():
        if isinstance(val, (int, float)):
            continue
        if not isinstance(val, str) or not (DIM_RE.match(val) or REF_RE.fullmatch(val)):
            findings.append(finding("warning", f"{group_name}.{name}", f"Expected dimension like 8px/1rem or token reference, got {val!r}."))
    return findings


def lint_typography_tokens(typography: Dict[str, Any]) -> List[dict[str, str]]:
    findings: List[dict[str, str]] = []
    for tname, tval in typography.items():
        if not isinstance(tval, dict):
            findings.append(finding("error", f"typography.{tname}", "Typography token must be an object."))
            continue
        for required in ("fontFamily", "fontSize"):
            if required not in tval:
                findings.append(finding("warning", f"typography.{tname}.{required}", f"Typography token should define {required}."))
    return findings


def component_reference_findings(flat: Dict[str, Any], cname: str, prop: str, val: Any) -> tuple[List[dict[str, str]], set[str]]:
    findings: List[dict[str, str]] = []
    referenced_color_paths: set[str] = set()
    if not isinstance(val, str):
        return findings, referenced_color_paths
    for ref in REF_RE.findall(val):
        if ref not in flat:
            findings.append(finding("error", f"components.{cname}.{prop}", f"Broken token reference {{{ref}}}."))
        if ref.startswith("colors."):
            referenced_color_paths.add(ref)
    return findings, referenced_color_paths


def component_contrast_finding(flat: Dict[str, Any], cname: str, cval: Dict[str, Any]) -> dict[str, str] | None:
    bg = cval.get("backgroundColor")
    fg = cval.get("textColor")
    if not (isinstance(bg, str) and isinstance(fg, str)):
        return None
    bgv = flat.get(bg.strip("{}")) if REF_RE.fullmatch(bg) else bg
    fgv = flat.get(fg.strip("{}")) if REF_RE.fullmatch(fg) else fg
    if not (isinstance(bgv, str) and isinstance(fgv, str) and HEX_RE.match(bgv) and HEX_RE.match(fgv)):
        return None
    cr = contrast_ratio(bgv, fgv)
    severity = "warning" if cr < 4.5 else "info"
    return finding(severity, f"components.{cname}", f"textColor {fgv} on backgroundColor {bgv} contrast ratio {cr:.2f}:1.")


def lint_component_tokens(components: Dict[str, Any], flat: Dict[str, Any]) -> tuple[List[dict[str, str]], set[str]]:
    findings: List[dict[str, str]] = []
    referenced_color_paths: set[str] = set()
    for cname, cval in components.items():
        if not isinstance(cval, dict):
            findings.append(finding("error", f"components.{cname}", "Component token must be an object."))
            continue
        for prop, val in cval.items():
            if prop not in ALLOWED_COMPONENT_PROPS:
                findings.append(finding("warning", f"components.{cname}.{prop}", f"Unknown component property {prop!r}; preserve but review."))
            ref_findings, ref_colors = component_reference_findings(flat, cname, prop, val)
            findings.extend(ref_findings)
            referenced_color_paths.update(ref_colors)
        contrast_finding = component_contrast_finding(flat, cname, cval)
        if contrast_finding:
            findings.append(contrast_finding)
    return findings, referenced_color_paths


def lint_unused_colors(colors: Dict[str, Any], components: Dict[str, Any], referenced_color_paths: set[str]) -> List[dict[str, str]]:
    findings: List[dict[str, str]] = []
    base_colors = {"primary", "secondary", "neutral", "surface", "background", "text"}
    if not (colors and components):
        return findings
    for cname in colors.keys():
        if f"colors.{cname}" not in referenced_color_paths and cname not in base_colors:
            findings.append(finding("info", f"colors.{cname}", "Color token is not referenced by component tokens."))
    return findings


def lint_sections(body: str) -> tuple[List[dict[str, str]], list[str]]:
    findings: List[dict[str, str]] = []
    sections = re.findall(r"^##\s+(.+?)\s*$", body, flags=re.M)
    seen, order = set(), []
    for section in sections:
        key = section.strip().lower()
        if key in seen:
            findings.append(finding("error", f"section.{section}", "Duplicate section heading; reject the file."))
        seen.add(key)
        order.append(canonical_section(section))
    filtered = [x for x in order if x != 999]
    if filtered != sorted(filtered):
        findings.append(finding("warning", "sections", "Known sections appear outside canonical DESIGN.md order."))
    return findings, sections


def summary_for(findings: List[dict[str, str]]) -> Dict[str, int]:
    summary = {"errors": 0, "warnings": 0, "info": 0}
    for item in findings:
        if item["severity"] == "error":
            summary["errors"] += 1
        elif item["severity"] == "warning":
            summary["warnings"] += 1
        else:
            summary["info"] += 1
    return summary


def design_system(data: Dict[str, Any], colors: Dict[str, Any], typography: Dict[str, Any], spacing: Dict[str, Any], rounded: Dict[str, Any], components: Dict[str, Any], sections: list[str]) -> Dict[str, Any]:
    return {
        "name": data.get("name"),
        "version": data.get("version"),
        "tokenCounts": {
            "colors": len(colors),
            "typography": len(typography),
            "spacing": len(spacing),
            "rounded": len(rounded),
            "components": len(components),
        },
        "sections": sections,
    }


def lint_design_md(path: Path) -> Dict[str, Any]:
    content = path.read_text(encoding="utf-8")
    fm, body, findings = split_front_matter(content)
    data = parse_simple_yaml(fm) if fm else {}
    flat = flatten_tokens(data)
    colors = token_group(data, "colors")
    typography = token_group(data, "typography")
    spacing = token_group(data, "spacing")
    rounded = token_group(data, "rounded")
    components = token_group(data, "components")

    findings.extend(lint_metadata(data, colors, typography))
    findings.extend(lint_color_tokens(colors))
    for group_name, group in (("spacing", spacing), ("rounded", rounded)):
        findings.extend(lint_dimension_tokens(group_name, group))
    findings.extend(lint_typography_tokens(typography))
    component_findings, referenced_color_paths = lint_component_tokens(components, flat)
    findings.extend(component_findings)
    findings.extend(lint_unused_colors(colors, components, referenced_color_paths))
    section_findings, sections = lint_sections(body)
    findings.extend(section_findings)

    findings.append(finding("info", "token-summary", f"colors={len(colors)}, typography={len(typography)}, spacing={len(spacing)}, rounded={len(rounded)}, components={len(components)}"))
    return {
        "file": str(path),
        "summary": summary_for(findings),
        "findings": findings,
        "designSystem": design_system(data, colors, typography, spacing, rounded, components, sections),
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?", default="DESIGN.md")
    ap.add_argument("--format", choices=["json", "text"], default="json")
    args = ap.parse_args()
    path = Path(args.file)
    if not path.exists():
        print(json.dumps({"summary": {"errors": 1, "warnings": 0, "info": 0}, "findings": [{"severity": "error", "path": str(path), "message": "File not found."}]}, indent=2))
        return 1
    report = lint_design_md(path)
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"{path}: {report['summary']}")
        for f in report["findings"]:
            print(f"[{f['severity']}] {f['path']}: {f['message']}")
    return 1 if report["summary"]["errors"] else 0

if __name__ == "__main__":
    raise SystemExit(main())
