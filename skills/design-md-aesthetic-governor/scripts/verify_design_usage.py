#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, subprocess
from pathlib import Path

HEX_RE = re.compile(r"#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?\b")
TAILWIND_PALETTE_RE = re.compile(r"\b(?:bg|text|border|from|to|via|ring|shadow|fill|stroke)-(?:slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-(?:50|100|200|300|400|500|600|700|800|900|950)\b")
UI_SUFFIXES = {".tsx", ".jsx", ".css", ".scss", ".sass", ".less"}
UI_PARTS = {"app", "pages", "components", "styles", "theme", "themes", "ui", "design-system"}

def git_changed_files() -> list[Path]:
    try:
        out = subprocess.check_output(["git", "diff", "--name-only"], text=True, stderr=subprocess.DEVNULL)
        files = [Path(x) for x in out.splitlines() if x.strip()]
        out2 = subprocess.check_output(["git", "diff", "--name-only", "--cached"], text=True, stderr=subprocess.DEVNULL)
        files += [Path(x) for x in out2.splitlines() if x.strip()]
        return sorted(set(files))
    except Exception:
        return []

def parse_design_colors(design: Path) -> set[str]:
    if not design.exists():
        return set()
    return {m.group(0).lower() for m in HEX_RE.finditer(design.read_text(encoding="utf-8"))}

def is_ui_file(path: Path) -> bool:
    s = str(path).replace("\\", "/")
    if path.suffix in UI_SUFFIXES:
        return True
    if path.name.startswith("tailwind.config") or path.name in {"theme.ts", "theme.js", "tokens.ts", "tokens.js"}:
        return True
    return any(part in s.split("/") for part in UI_PARTS)


def findings_for_file(path: Path, allowed_colors: set[str]) -> list[dict[str, str]]:
    try:
        txt = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    findings: list[dict[str, str]] = []
    for m in HEX_RE.finditer(txt):
        val = m.group(0).lower()
        if val not in allowed_colors:
            findings.append({"severity":"error", "file":str(path), "kind":"raw-hex-not-in-design-md", "value":m.group(0), "message":"Raw hex color is not declared in DESIGN.md."})
    for m in TAILWIND_PALETTE_RE.finditer(txt):
        findings.append({"severity":"warning", "file":str(path), "kind":"tailwind-palette-class", "value":m.group(0), "message":"Tailwind palette class may bypass DESIGN.md token roles. Prefer mapped theme tokens."})
    return findings


def scan_files(files: list[Path], allowed_colors: set[str]) -> tuple[list[dict[str, str]], list[str]]:
    findings: list[dict[str, str]] = []
    scanned: list[str] = []
    for f in files:
        if not f.exists() or not is_ui_file(f):
            continue
        scanned.append(str(f))
        findings.extend(findings_for_file(f, allowed_colors))
    return findings, scanned


def summary_for(findings: list[dict[str, str]], scanned: list[str]) -> dict[str, int]:
    return {"errors": sum(1 for x in findings if x["severity"]=="error"), "warnings": sum(1 for x in findings if x["severity"]=="warning"), "scanned_files": len(scanned)}


def write_report(report: dict[str, object]) -> None:
    out_dir = Path(".codex/design-md-governor")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "design-usage-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def print_report(report: dict[str, object], fmt: str) -> None:
    if fmt == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return
    print(report["summary"])
    for f in report["findings"]:
        print(f"[{f['severity']}] {f['file']}: {f['value']} — {f['message']}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--design", default="DESIGN.md")
    ap.add_argument("--changed-files", nargs="*", default=None)
    ap.add_argument("--format", choices=["json", "text"], default="json")
    args = ap.parse_args()
    files = [Path(x) for x in args.changed_files] if args.changed_files else git_changed_files()
    allowed_colors = parse_design_colors(Path(args.design))
    findings, scanned = scan_files(files, allowed_colors)
    summary = summary_for(findings, scanned)
    report = {"summary": summary, "scanned_files": scanned, "findings": findings}
    write_report(report)
    print_report(report, args.format)
    return 1 if summary["errors"] else 0

if __name__ == "__main__":
    raise SystemExit(main())
