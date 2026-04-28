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

def parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if re.fullmatch(r"-?\d+", value):
        try: return int(value)
        except Exception: return value
    if re.fullmatch(r"-?\d+\.\d+", value):
        try: return float(value)
        except Exception: return value
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

def lint_design_md(path: Path) -> Dict[str, Any]:
    content = path.read_text(encoding="utf-8")
    fm, body, findings = split_front_matter(content)
    data = parse_simple_yaml(fm) if fm else {}
    flat = flatten_tokens(data)

    def finding(sev, path_, msg):
        findings.append({"severity": sev, "path": path_, "message": msg})

    colors = data.get("colors") if isinstance(data.get("colors"), dict) else {}
    typography = data.get("typography") if isinstance(data.get("typography"), dict) else {}
    spacing = data.get("spacing") if isinstance(data.get("spacing"), dict) else {}
    rounded = data.get("rounded") if isinstance(data.get("rounded"), dict) else {}
    components = data.get("components") if isinstance(data.get("components"), dict) else {}

    if not data.get("name"):
        finding("warning", "name", "Missing design system name.")
    if colors and "primary" not in colors:
        finding("warning", "colors.primary", "Colors exist but no primary color token is defined.")
    if colors and not typography:
        finding("warning", "typography", "Colors exist but no typography tokens are defined.")

    for name, val in colors.items():
        if not isinstance(val, str) or not HEX_RE.match(val):
            finding("error", f"colors.{name}", f"Color token must be #RGB or #RRGGBB, got {val!r}.")

    for group_name, group in (("spacing", spacing), ("rounded", rounded)):
        for name, val in group.items():
            if isinstance(val, (int, float)):
                continue
            if not isinstance(val, str) or not (DIM_RE.match(val) or REF_RE.fullmatch(val)):
                finding("warning", f"{group_name}.{name}", f"Expected dimension like 8px/1rem or token reference, got {val!r}.")

    for tname, tval in typography.items():
        if not isinstance(tval, dict):
            finding("error", f"typography.{tname}", "Typography token must be an object.")
            continue
        for required in ("fontFamily", "fontSize"):
            if required not in tval:
                finding("warning", f"typography.{tname}.{required}", f"Typography token should define {required}.")

    referenced_color_paths = set()
    for cname, cval in components.items():
        if not isinstance(cval, dict):
            finding("error", f"components.{cname}", "Component token must be an object.")
            continue
        for prop, val in cval.items():
            if prop not in ALLOWED_COMPONENT_PROPS:
                finding("warning", f"components.{cname}.{prop}", f"Unknown component property {prop!r}; preserve but review.")
            if isinstance(val, str):
                for ref in REF_RE.findall(val):
                    if ref not in flat:
                        finding("error", f"components.{cname}.{prop}", f"Broken token reference {{{ref}}}.")
                    if ref.startswith("colors."):
                        referenced_color_paths.add(ref)
        bg = cval.get("backgroundColor")
        fg = cval.get("textColor")
        if isinstance(bg, str) and isinstance(fg, str):
            bgv = flat.get(bg.strip("{}")) if REF_RE.fullmatch(bg) else bg
            fgv = flat.get(fg.strip("{}")) if REF_RE.fullmatch(fg) else fg
            if isinstance(bgv, str) and isinstance(fgv, str) and HEX_RE.match(bgv) and HEX_RE.match(fgv):
                cr = contrast_ratio(bgv, fgv)
                finding("warning" if cr < 4.5 else "info", f"components.{cname}", f"textColor {fgv} on backgroundColor {bgv} contrast ratio {cr:.2f}:1.")

    if colors and components:
        for cname in colors.keys():
            if f"colors.{cname}" not in referenced_color_paths and cname not in {"primary", "secondary", "neutral", "surface", "background", "text"}:
                finding("info", f"colors.{cname}", "Color token is not referenced by component tokens.")

    sections = re.findall(r"^##\s+(.+?)\s*$", body, flags=re.M)
    seen, order = set(), []
    for s in sections:
        key = s.strip().lower()
        if key in seen:
            finding("error", f"section.{s}", "Duplicate section heading; reject the file.")
        seen.add(key)
        order.append(canonical_section(s))
    filtered = [x for x in order if x != 999]
    if filtered != sorted(filtered):
        finding("warning", "sections", "Known sections appear outside canonical DESIGN.md order.")

    finding("info", "token-summary", f"colors={len(colors)}, typography={len(typography)}, spacing={len(spacing)}, rounded={len(rounded)}, components={len(components)}")
    summary = {"errors": 0, "warnings": 0, "info": 0}
    for f in findings:
        if f["severity"] == "error": summary["errors"] += 1
        elif f["severity"] == "warning": summary["warnings"] += 1
        else: summary["info"] += 1
    return {"file": str(path), "summary": summary, "findings": findings, "designSystem": {"name": data.get("name"), "version": data.get("version"), "tokenCounts": {"colors": len(colors), "typography": len(typography), "spacing": len(spacing), "rounded": len(rounded), "components": len(components)}, "sections": sections}}

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
