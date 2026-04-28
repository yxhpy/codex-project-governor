#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os, re, subprocess, sys
from pathlib import Path

UI_PROMPT_RE = re.compile(r"\b(ui|frontend|front-end|react|next\.js|nextjs|tailwind|css|component|page|layout|dashboard|landing|modal|dialog|form|table|card|responsive|mobile|visual|design|theme|style|redesign|polish)\b", re.I)
UI_FILE_RE = re.compile(r"(^|/)(app|pages|src/app|src/pages|components|src/components|styles|ui|design-system)/|\.(tsx|jsx|css|scss|sass|less)$|tailwind\.config\.|theme\.(ts|js|tsx|jsx)$")
STATE_DIR = Path(".codex/design-md-governor")
ENV_FILE = ".env-design"
SKIP_ENV_KEYS = ("DESIGN_BASIC_MODE", "DESIGN_ENV_SKIP", "DESIGN_SERVICE_CONFIG_SKIP")
REQUIRED_ENV = (
    ("GEMINI_BASE_URL", ("GEMINI_BASE_URL", "DESIGN_GEMINI_BASE_URL")),
    ("GEMINI_API_KEY", ("GEMINI_API_KEY", "DESIGN_GEMINI_API_KEY")),
    ("GEMINI_MODEL", ("GEMINI_MODEL", "DESIGN_GEMINI_MODEL")),
    ("STITCH_MCP_API_KEY", ("STITCH_MCP_API_KEY", "DESIGN_STITCH_MCP_API_KEY")),
)

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

def parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values

def design_env_ok(root: Path):
    if any(os.environ.get(key, "").strip() in {"1", "true", "TRUE", "yes", "YES"} for key in SKIP_ENV_KEYS):
        return True, "ok"
    file_values = parse_env_file(root / ENV_FILE)
    missing = []
    for canonical, aliases in REQUIRED_ENV:
        if any(os.environ.get(key, "").strip() for key in aliases):
            continue
        if any(file_values.get(key, "").strip() for key in aliases):
            continue
        missing.append(canonical)
    if missing:
        return False, "Design service config missing: " + ", ".join(missing) + ". Set shell environment variables or fill project .env-design before UI edits."
    return True, "ok"

def proof_ok(root: Path):
    env_ok, env_reason = design_env_ok(root)
    if not env_ok:
        return False, env_reason
    design = root / "DESIGN.md"
    proof = root / STATE_DIR / "read-proof.json"
    if not design.exists():
        return False, "DESIGN.md is missing. Create/adopt DESIGN.md before UI edits."
    if not proof.exists():
        return False, "DESIGN.md read proof is missing. Run design_md_gate.py preflight before UI edits."
    try:
        data = json.loads(proof.read_text(encoding="utf-8"))
    except Exception:
        return False, "DESIGN.md read proof is invalid JSON. Run preflight again."
    if data.get("design_sha256") != sha256(design):
        return False, "DESIGN.md read proof is stale because DESIGN.md changed. Run preflight again."
    if not data.get("ok", False):
        return False, "DESIGN.md preflight did not pass. Fix lint errors before UI edits."
    return True, "ok"

def extract_paths_from_patch(command: str) -> list[str]:
    paths = []
    patterns = [r"^\*\*\* (?:Update|Add|Delete) File:\s+(.+)$", r"^\+\+\+ b/(.+)$", r"^--- a/(.+)$"]
    for line in command.splitlines():
        for pat in patterns:
            m = re.match(pat, line.strip())
            if m:
                paths.append(m.group(1).strip())
    return paths

def bash_mentions_ui_write(command: str) -> bool:
    writey = re.search(r"\b(sed\s+-i|perl\s+-pi|tee\b|cat\s+>|printf\s+.*>|git\s+apply|python3?\s+-c|node\s+-e|mv\b|cp\b|touch\b)\b", command)
    return bool(writey and UI_FILE_RE.search(command))

def block(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":reason}}, ensure_ascii=False))

def main() -> int:
    try:
        event = json.load(sys.stdin)
    except Exception:
        return 0
    root = root_dir()
    os.chdir(root)
    name = event.get("hook_event_name")
    if name == "UserPromptSubmit":
        prompt = event.get("prompt", "")
        if UI_PROMPT_RE.search(prompt):
            (root / STATE_DIR).mkdir(parents=True, exist_ok=True)
            (root / STATE_DIR / "last-ui-prompt.json").write_text(json.dumps({"prompt": prompt}, indent=2, ensure_ascii=False), encoding="utf-8")
            msg = "This appears to be UI/frontend work. Use $design-md-aesthetic-governor, configure Gemini/Stitch via environment variables or project .env-design, or set DESIGN_BASIC_MODE=1 for basic mode. Then read DESIGN.md, run preflight, and edit UI files."
            print(json.dumps({"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":msg}}, ensure_ascii=False))
        return 0
    if name == "PreToolUse":
        tool = event.get("tool_name", "")
        tool_input = event.get("tool_input") or {}
        command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""
        should_gate = False
        if tool == "apply_patch":
            paths = extract_paths_from_patch(command)
            should_gate = any(UI_FILE_RE.search(p) for p in paths)
        elif tool == "Bash":
            should_gate = bash_mentions_ui_write(command)
        else:
            should_gate = UI_FILE_RE.search(json.dumps(tool_input, ensure_ascii=False)) is not None
        if should_gate:
            ok, reason = proof_ok(root)
            if not ok:
                block(reason)
                return 0
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
