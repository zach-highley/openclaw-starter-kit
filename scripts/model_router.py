#!/usr/bin/env python3
"""
Intelligent Model Router for OpenClaw starter-kit

Principles:
- Claude Opus is the PRIMARY conversational model.
- Codex is the PRIMARY coding model.
- Always keep cross-provider fallbacks so you never get locked out.
- Do not assume Claude Sonnet exists, this starter kit intentionally avoids it.

Usage:
  python3 scripts/model_router.py --show-all
  python3 scripts/model_router.py --task-type coding
  python3 scripts/model_router.py --set-codex-status exhausted --codex-resets "2026-02-03"
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Model identifiers (OpenClaw model ids)
MODELS = {
    "opus": "anthropic/claude-opus-4-5",
    "codex": "openai-codex/gpt-5.2",
    "gemini": "google-gemini-cli/gemini-3-pro-preview",
    "kimi": "nvidia-nim/moonshotai/kimi-k2.5",
    "local": "ollama/qwen2.5:14b",
}

CODEX_STATUS_FILE = Path(__file__).parent.parent / "state" / "codex_status.json"

# Task type → preferred model
TASK_MODEL_MAP = {
    # Opus territory
    "strategy": "opus",
    "reasoning": "opus",
    "important": "opus",
    "analysis": "opus",
    "planning": "opus",

    # Writing/editorial (still Opus by default in this starter kit)
    "writing": "opus",
    "editing": "opus",
    "drafting": "opus",
    "email": "opus",
    "summarize": "gemini",

    # Coding territory
    "coding": "codex",
    "code": "codex",
    "debug": "codex",
    "refactor": "codex",
    "script": "codex",
    "bugfix": "codex",
    "review": "codex",
    "implement": "codex",
    "build": "codex",
    "test": "codex",
    "fix": "codex",

    # Bulk/simple
    "bulk": "gemini",
    "simple": "gemini",
    "translate": "gemini",
    "format": "gemini",
    "convert": "gemini",

    # Local fallback
    "local": "local",
    "private": "local",
    "offline": "local",
}

# Usage % → allowed models (removes Anthropic first, keeps system alive)
DEGRADATION_CURVE = [
    (0, ["opus", "codex", "gemini", "kimi", "local"]),
    (80, ["codex", "gemini", "kimi", "local"]),
    (95, ["gemini", "kimi", "local"]),
    (100, ["local"]),
]


def get_usage_json():
    """Get current usage from scripts/check_usage.py (JSON)."""
    try:
        result = subprocess.run(
            ["python3", str(Path(__file__).parent / "check_usage.py"), "--json"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"Warning: Could not get usage: {e}", file=sys.stderr)
    return {}


def get_codex_status():
    """Persistent Codex availability flag."""
    try:
        if CODEX_STATUS_FILE.exists():
            data = json.loads(CODEX_STATUS_FILE.read_text())
            resets = data.get("resets_at")
            if resets:
                try:
                    reset_dt = datetime.fromisoformat(resets)
                    if datetime.now() >= reset_dt:
                        set_codex_status(True)
                        return {"available": True, "resets": None, "reason": "Reset time passed"}
                except (ValueError, TypeError):
                    pass
            return {
                "available": data.get("available", True),
                "resets": data.get("resets_at"),
                "reason": data.get("reason", "unknown"),
            }
    except Exception as e:
        print(f"Warning: Could not read codex status: {e}", file=sys.stderr)
    return {"available": True, "resets": None, "reason": "No status file (assumed available)"}


def set_codex_status(available, resets_at=None, reason=None):
    CODEX_STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "available": bool(available),
        "resets_at": resets_at,
        "reason": reason or ("available" if available else "exhausted"),
        "updated_at": datetime.now().isoformat(),
    }
    CODEX_STATUS_FILE.write_text(json.dumps(data, indent=2))
    return data


def allowed_models(usage_percent):
    allowed = DEGRADATION_CURVE[0][1]
    for threshold, models in DEGRADATION_CURVE:
        if usage_percent >= threshold:
            allowed = models
    # Remove Codex if manually marked exhausted
    codex = get_codex_status()
    if not codex["available"] and "codex" in allowed:
        allowed = [m for m in allowed if m != "codex"]
    return allowed


def select_model(task_type=None):
    usage = get_usage_json()
    claude_pct = (
        usage.get("models", {})
        .get("claude", {})
        .get("context_pct", 0)
    )
    allowed = allowed_models(claude_pct)

    preferred = None
    if task_type:
        task_lower = task_type.lower()
        for key, model in TASK_MODEL_MAP.items():
            if key in task_lower:
                preferred = model
                break

    if preferred and preferred in allowed:
        return MODELS[preferred], f"Task '{task_type}' → {preferred} (claude ctx: {claude_pct}%)"

    # If coding was preferred but Codex exhausted, fall back to Gemini/Kimi/Local
    if preferred == "codex" and "codex" not in allowed:
        fallback = allowed[0] if allowed else "local"
        return MODELS[fallback], f"Codex unavailable → fallback to {fallback} (claude ctx: {claude_pct}%)"

    best = allowed[0] if allowed else "local"
    return MODELS[best], f"Default to {best} (claude ctx: {claude_pct}%)"


def show_all():
    usage = get_usage_json()
    claude = usage.get("models", {}).get("claude", {})
    codex = usage.get("models", {}).get("codex", {})
    gemini = usage.get("models", {}).get("gemini", {})
    codex_status = get_codex_status()

    claude_pct = claude.get("context_pct", 0)
    result = {
        "claude": claude,
        "codex": codex,
        "gemini": gemini,
        "codex_cli_state": codex_status,
        "allowed_models": allowed_models(claude_pct),
        "models": MODELS,
    }
    print(json.dumps(result, indent=2))


def main():
    import argparse

    p = argparse.ArgumentParser(description="Intelligent model router")
    p.add_argument("--task-type", "-t", help="Type of task (coding, writing, etc)")
    p.add_argument("--show-all", action="store_true", help="Show current model status")
    p.add_argument("--json", action="store_true", help="Output JSON")
    p.add_argument("--set-codex-status", choices=["available", "exhausted"], help="Set Codex CLI status")
    p.add_argument("--codex-resets", help="When Codex CLI resets (ISO date)")
    args = p.parse_args()

    if args.set_codex_status:
        available = args.set_codex_status == "available"
        res = set_codex_status(available, resets_at=args.codex_resets, reason=f"manual set: {args.set_codex_status}")
        print(json.dumps(res, indent=2) if args.json else f"Codex CLI: {'available' if available else 'exhausted'}")
        return

    if args.show_all:
        show_all()
        return

    model_id, reasoning = select_model(args.task_type)
    if args.json:
        print(json.dumps({"model": model_id, "reasoning": reasoning}, indent=2))
    else:
        print(model_id)
        print(reasoning)


if __name__ == "__main__":
    main()
