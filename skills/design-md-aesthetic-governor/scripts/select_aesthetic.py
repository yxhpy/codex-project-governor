#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PRESETS_PATH = SCRIPT_DIR.parent / "assets" / "aesthetic-presets.json"

KEYWORDS = {
    "developer": ["developer", "dev", "api", "sdk", "code", "terminal", "infra", "deployment", "docs", "documentation", "database", "console"],
    "ai": ["ai", "agent", "llm", "model", "prompt", "copilot", "assistant"],
    "finance": ["finance", "fintech", "billing", "payment", "checkout", "invoice", "bank", "crypto", "trading", "trust"],
    "productivity": ["project", "task", "workspace", "note", "team", "settings", "dashboard", "admin", "saas"],
    "consumer": ["consumer", "mobile", "travel", "marketplace", "lifestyle", "retail", "photo", "music", "media"],
    "creative": ["design", "canvas", "creative", "website", "builder", "visual", "portfolio"],
    "enterprise": ["enterprise", "governance", "compliance", "security", "b2b", "admin", "management"],
}
BOOSTS = {
    "developer": {"vercel": 3, "supabase": 3, "voltagent": 3, "cursor": 2, "mintlify": 2, "clickhouse": 2},
    "ai": {"voltagent": 4, "cursor": 3, "nvidia": 2, "supabase": 1},
    "finance": {"stripe": 4, "revolut": 3, "coinbase": 3, "linear": 1},
    "productivity": {"linear": 4, "notion": 3, "mintlify": 2, "vercel": 1},
    "consumer": {"apple": 4, "airbnb": 3, "shopify": 2},
    "creative": {"figma": 4, "webflow": 3, "apple": 1},
    "enterprise": {"ibm": 4, "linear": 2, "coinbase": 2, "vercel": 2},
}

def load_presets():
    return json.loads(PRESETS_PATH.read_text(encoding="utf-8"))["presets"]

def score(task: str, preset: dict):
    t = task.lower()
    points, reasons = 0, []
    for group, words in KEYWORDS.items():
        hits = [w for w in words if re.search(r"\b" + re.escape(w) + r"\b", t)]
        if hits:
            bonus = BOOSTS.get(group, {}).get(preset["id"], 0)
            if bonus:
                points += bonus * max(1, min(3, len(hits)))
                reasons.append(f"{group}: {', '.join(hits[:3])}")
    hay = " ".join([preset.get("mood", ""), " ".join(preset.get("best_for", [])), preset.get("category", "")]).lower()
    for token in re.findall(r"[a-z0-9]+", t):
        if len(token) > 3 and token in hay:
            points += 1
    return points, reasons

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--format", choices=["json", "markdown"], default="json")
    args = ap.parse_args()
    ranked = []
    for p in load_presets():
        pts, reasons = score(args.task, p)
        ranked.append({**p, "score": pts, "reasons": reasons})
    ranked.sort(key=lambda x: (x["score"], x["id"]), reverse=True)
    chosen = ranked[:args.top]
    out = {"task": args.task, "recommendations": chosen, "policy": "Use as visual grammar inspiration only; convert to project-owned DESIGN.md tokens and rationale."}
    if args.format == "json":
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(f"# Aesthetic recommendations\n\nTask: {args.task}\n")
        for item in chosen:
            print(f"## {item['name']} (`{item['id']}`) — score {item['score']}")
            print(f"- Mood: {item['mood']}")
            print(f"- Best for: {', '.join(item['best_for'])}")
            if item["reasons"]:
                print(f"- Matched: {'; '.join(item['reasons'])}")
            print()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
