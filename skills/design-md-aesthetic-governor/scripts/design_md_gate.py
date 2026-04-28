#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, re, subprocess, sys, time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
STATE_DIR = Path(".codex/design-md-governor")
UI_TERMS = re.compile(r"\b(ui|frontend|front-end|react|next\.js|nextjs|tailwind|css|component|page|layout|dashboard|landing|modal|dialog|form|table|card|responsive|mobile|visual|design|theme|style|redesign|polish)\b", re.I)

def load_linter():
    spec = importlib.util.spec_from_file_location("design_md_lint", SCRIPT_DIR / "design_md_lint.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod

def load_env_checker():
    spec = importlib.util.spec_from_file_location("design_env_check", SCRIPT_DIR / "design_env_check.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod

def root_dir() -> Path:
    try:
        out = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], stderr=subprocess.DEVNULL, text=True).strip()
        if out:
            return Path(out)
    except Exception:
        pass
    return Path.cwd()

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()

def run_lint(design: Path):
    mod = load_linter()
    report = mod.lint_design_md(design)
    return (1 if report["summary"]["errors"] else 0), report

def summarize_design(design: Path, lint_report: dict) -> str:
    ds = lint_report.get("designSystem", {})
    counts = ds.get("tokenCounts", {})
    name = ds.get("name") or design.name
    sections = ds.get("sections") or []
    return "\n".join([
        "# DESIGN.md read report", "",
        f"- Source: `{design}`",
        f"- Name: {name}",
        f"- Hash: `{sha256(design)}`",
        f"- Token counts: {counts}",
        f"- Sections: {', '.join(sections) if sections else 'none detected'}",
        f"- Lint summary: {lint_report.get('summary')}",
        "",
        "Codex must implement UI from the tokens and rationale above, not from arbitrary default styling.",
    ])

def adoption_plan(task: str, root: Path) -> Path:
    out = root / "docs/design/DESIGN_MD_ADOPTION_PLAN.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    safe_task = task.replace('"', "'")
    out.write_text(f"""# DESIGN.md Adoption Plan

Task: {task}

No repository-level `DESIGN.md` was found, so UI coding is blocked by the DESIGN.md Aesthetic Governor.

## Required decision

Choose one of these paths before implementation:

1. Create a project-specific `DESIGN.md` from current brand/product requirements.
2. Select one primary aesthetic reference from the awesome-design-md catalog and convert it into project-owned tokens.
3. Provide an existing design system source and convert it to DESIGN.md.

## Recommended next command

```bash
python3 "${PROJECT_GOVERNOR_ROOT:-.}/skills/design-md-aesthetic-governor/scripts/select_aesthetic.py" --task "{safe_task}" --format markdown
```

## Blocker

Do not edit production UI files until a `DESIGN.md` exists and `design_md_gate.py preflight` passes.
""", encoding="utf-8")
    return out

def cmd_preflight(args) -> int:
    root = root_dir()
    os.chdir(root)
    design = Path(args.design)
    state = root / STATE_DIR
    state.mkdir(parents=True, exist_ok=True)
    env_report = load_env_checker().check_design_env(root, write_missing_template=True)
    (state / "design-env-report.json").write_text(json.dumps(env_report, indent=2, ensure_ascii=False), encoding="utf-8")
    if not env_report["ok"]:
        print(json.dumps({"ok": False, "blocked": True, "reason": "design service environment missing", "design_env": env_report}, indent=2, ensure_ascii=False))
        return 2
    if not design.exists():
        plan = adoption_plan(args.task, root)
        print(json.dumps({"ok": False, "blocked": True, "reason": "DESIGN.md missing", "adoption_plan": str(plan)}, indent=2))
        return 2
    code, report = run_lint(design)
    proof = {
        "ok": code == 0,
        "timestamp": int(time.time()),
        "task": args.task,
        "task_is_ui": bool(UI_TERMS.search(args.task)),
        "design_path": str(design),
        "design_sha256": sha256(design),
        "lint_summary": report.get("summary", {}),
        "design_env": {"ok": env_report["ok"], "mode": env_report.get("mode"), "provided": env_report["provided"]},
        "required_final_section": "DESIGN.md compliance",
        "aesthetic_reference": args.inspiration or None,
    }
    (state / "read-proof.json").write_text(json.dumps(proof, indent=2, ensure_ascii=False), encoding="utf-8")
    (state / "lint-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (state / "DESIGN_MD_READ_REPORT.md").write_text(summarize_design(design, report), encoding="utf-8")
    print(json.dumps(proof, indent=2, ensure_ascii=False))
    return 0 if code == 0 else 1

def cmd_check(args) -> int:
    root = root_dir()
    os.chdir(root)
    design = Path(args.design)
    proof_path = root / STATE_DIR / "read-proof.json"
    env_report = load_env_checker().check_design_env(root, write_missing_template=False)
    if not env_report["ok"]:
        print("design service environment missing; set environment variables or fill .env-design", file=sys.stderr); return 2
    if not design.exists():
        print("DESIGN.md missing", file=sys.stderr); return 2
    if not proof_path.exists():
        print("read-proof.json missing; run preflight first", file=sys.stderr); return 2
    proof = json.loads(proof_path.read_text(encoding="utf-8"))
    current = sha256(design)
    if proof.get("design_sha256") != current:
        print("read-proof.json is stale; DESIGN.md changed", file=sys.stderr); return 2
    print(json.dumps({"ok": True, "design_sha256": current, "proof": str(proof_path)}, indent=2))
    return 0

def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("preflight")
    p.add_argument("--task", required=True)
    p.add_argument("--design", default="DESIGN.md")
    p.add_argument("--inspiration", default="")
    p.set_defaults(func=cmd_preflight)
    c = sub.add_parser("check")
    c.add_argument("--design", default="DESIGN.md")
    c.set_defaults(func=cmd_check)
    args = ap.parse_args()
    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())
