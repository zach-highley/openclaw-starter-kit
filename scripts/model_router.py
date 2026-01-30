#!/usr/bin/env python3
"""
Intelligent Model Router for Clawdbot/OpenClaw
Implements logarithmic degradation based on usage thresholds.

Tracks ALL model availability including:
- Claude (Opus/Sonnet): 5h rolling + weekly limits
- Codex CLI: ChatGPT Plus weekly messages (SEPARATE from Codex Code Review)
- Codex Code Review: GitHub App, separate quota, review-only
- Gemini: API-based, generally available
- Local: always available (Ollama)

Usage: python3 model_router.py [--task-type TYPE] [--check-only]
       python3 model_router.py --set-codex-status exhausted --codex-resets "Feb 3"
       python3 model_router.py --show-all
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Model hierarchy (in order of preference)
MODELS = {
    "opus": "anthropic/claude-opus-4-5",
    "sonnet": "anthropic/claude-sonnet-4",
    "codex": "openai-codex/gpt-5.2",
    "gemini": "google-gemini-cli/gemini-3-pro-preview",
    "local": "ollama/qwen2.5:14b",  # Install with: ollama pull qwen2.5:14b
}

# Codex has TWO separate products — NEVER confuse them
# codex CLI/API = writes code = shares ChatGPT Plus weekly quota
# codex Code Review = reviews PRs on GitHub = separate quota entirely
CODEX_STATUS_FILE = Path(__file__).parent.parent / "state" / "codex_status.json"

# ═══════════════════════════════════════════════════════════════════
# HYBRID WORKFLOW STRATEGY (2026-01-30)
# ═══════════════════════════════════════════════════════════════════
# Community consensus from 200+ devs:
#   - Codex 5.2 (High/xHigh) is the CODING MASTER — slow, methodical,
#     catches bugs Claude misses. Non-existent limits on MAX tier.
#   - Claude (Opus/Sonnet) is the CREATIVE WORKHORSE — fast, great for
#     planning, architecture, initial code generation.
#   - Gemini is NOT for coding. Period.
#
# PRO-GAMER HYBRID WORKFLOW:
#   1. Claude plans architecture & generates initial code (fast, creative)
#   2. Codex 5.2 executes coding tasks & reviews for bugs (thorough, methodical)
#   3. Claude orchestrates and makes strategic decisions
#
# For ALL coding tasks: Codex is PRIMARY. Not fallback. PRIMARY.
# Claude Code is the fallback if Codex is somehow unavailable.
# ═══════════════════════════════════════════════════════════════════

# Task type → best model mapping
TASK_MODEL_MAP = {
    # Opus territory (complex reasoning, strategy, architecture, planning)
    "strategy": "opus",
    "reasoning": "opus",
    "important": "opus",
    "analysis": "opus",
    "planning": "opus",
    "architecture": "opus",
    
    # Sonnet territory (good reasoning, faster, cheaper)
    "writing": "sonnet",
    "editing": "sonnet",
    "drafting": "sonnet",
    "email": "sonnet",
    "summarize": "sonnet",
    
    # Codex territory — THE CODING MASTER (all code tasks go here)
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
    
    # Codex sub-tasks (mapped to effort levels below)
    "audit": "codex",         # Full codebase audit → xhigh effort
    "architecture": "codex",  # Architecture changes → high effort  
    "hotfix": "codex",        # Quick single-file fix → medium effort
    "lint": "codex",          # Lint/format → medium effort, mini model
    
    # Gemini territory (bulk processing, simple tasks — NEVER coding)
    "bulk": "gemini",
    "simple": "gemini",
    "translate": "gemini",
    "format": "gemini",
    "convert": "gemini",
    
    # Local territory (fallback, privacy, unlimited)
    "local": "local",
    "private": "local",
    "offline": "local",
}

# Degradation thresholds (usage % → allowed models)
DEGRADATION_CURVE = [
    (0, ["opus", "sonnet", "codex", "gemini", "local"]),   # 0-70%: all models available
    (70, ["opus", "sonnet", "codex", "gemini", "local"]),  # 70%: start watching
    (80, ["sonnet", "codex", "gemini", "local"]),          # 80%: prefer sonnet
    (90, ["sonnet", "codex", "gemini", "local"]),          # 90%: sonnet primary
    (95, ["codex", "gemini", "local"]),                    # 95%: no more anthropic
    (100, ["gemini", "local"]),                            # 100%: gemini + local only
]


# ═══════════════════════════════════════════════════════════════════
# CODEX SUB-SELECTION: Model + Effort Level
# Source: https://developers.openai.com/codex/models/
#         https://cookbook.openai.com/examples/gpt-5/codex_prompting_guide
#
# Models:
#   gpt-5.2-codex     — Most advanced, our MAX tier default
#   gpt-5.1-codex-mini — Faster, cheaper, for simpler tasks
#   gpt-5.1-codex-max  — Long-horizon agentic tasks
#
# Effort Levels:
#   medium  — Fast + smart. Most interactive coding. DEFAULT.
#   high    — Multi-file changes, complex refactors, hard bugs
#   xhigh   — Full codebase audits, architecture overhauls, hardest tasks
#
# RULES:
#   - Don't refire a working session. Only refire on ACTUAL CRASHES.
#   - If a task crashes, break into smaller sub-tasks and retry.
#   - "Taking a long time" ≠ crashed. Be patient.
# ═══════════════════════════════════════════════════════════════════

CODEX_TASK_CONFIG = {
    # task_type → (codex_model, effort_level, description)
    "audit":        ("gpt-5.2-codex", "xhigh", "Full codebase audit — maximum thoroughness"),
    "architecture": ("gpt-5.2-codex", "high",  "Architecture changes — needs deep reasoning"),
    "refactor":     ("gpt-5.2-codex", "high",  "Multi-file refactor — complex coordination"),
    "implement":    ("gpt-5.2-codex", "high",  "Feature implementation — substantial new code"),
    "review":       ("gpt-5.2-codex", "high",  "Code review — thorough analysis"),
    "debug":        ("gpt-5.2-codex", "high",  "Complex debugging — needs careful analysis"),
    "coding":       ("gpt-5.2-codex", "medium","General coding — balanced speed/intelligence"),
    "code":         ("gpt-5.2-codex", "medium","General code task"),
    "bugfix":       ("gpt-5.2-codex", "medium","Bug fix — targeted, usually single-file"),
    "fix":          ("gpt-5.2-codex", "medium","Quick fix"),
    "test":         ("gpt-5.2-codex", "medium","Write/fix tests"),
    "build":        ("gpt-5.2-codex", "medium","Build configuration"),
    "script":       ("gpt-5.1-codex-mini", "medium","Simple script — mini model is sufficient"),
    "hotfix":       ("gpt-5.1-codex-mini", "medium","Quick hotfix — speed over depth"),
    "lint":         ("gpt-5.1-codex-mini", "medium","Lint/format — mechanical, mini is fine"),
}

def get_codex_config(task_type):
    """Get the right Codex model + effort level for a task type."""
    config = CODEX_TASK_CONFIG.get(task_type, ("gpt-5.2-codex", "medium", "Default coding task"))
    return {
        "codex_model": config[0],
        "effort": config[1],
        "description": config[2],
    }


def get_usage():
    """Get current usage from check_usage.py"""
    try:
        result = subprocess.run(
            ["python3", str(Path(__file__).parent / "check_usage.py")],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"Warning: Could not get usage: {e}", file=sys.stderr)
    return {"primary": {"percent": 0}, "secondary": {"percent": 0}}


def get_codex_status():
    """
    Get Codex CLI availability from persistent state file.
    Codex CLI shares quota with ChatGPT Plus weekly messages.
    This is DIFFERENT from Codex Code Review (GitHub App, separate quota).
    
    Returns: {"available": bool, "resets": str or None, "reason": str}
    """
    try:
        if CODEX_STATUS_FILE.exists():
            data = json.loads(CODEX_STATUS_FILE.read_text())
            # Check if reset date has passed
            resets = data.get("resets_at")
            if resets:
                try:
                    reset_dt = datetime.fromisoformat(resets)
                    if datetime.now() >= reset_dt:
                        # Reset has passed — mark as available
                        set_codex_status(True)
                        return {"available": True, "resets": None, "reason": "Reset time passed, assumed available"}
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
    """
    Persist Codex CLI availability status.
    Call this when you discover Codex is exhausted or has reset.
    """
    CODEX_STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "available": available,
        "resets_at": resets_at,
        "reason": reason or ("available" if available else "exhausted"),
        "updated_at": datetime.now().isoformat(),
    }
    CODEX_STATUS_FILE.write_text(json.dumps(data, indent=2))
    return data


def get_allowed_models(usage_percent):
    """Get allowed models based on usage percentage"""
    allowed = DEGRADATION_CURVE[0][1]
    for threshold, models in DEGRADATION_CURVE:
        if usage_percent >= threshold:
            allowed = models
    return allowed


def get_effective_allowed_models(usage_percent):
    """
    Get allowed models considering BOTH Claude usage AND Codex availability.
    This is the smart router — it removes exhausted models from the list.
    """
    allowed = get_allowed_models(usage_percent)
    
    # Check Codex CLI status
    codex = get_codex_status()
    if not codex["available"] and "codex" in allowed:
        allowed = [m for m in allowed if m != "codex"]
    
    return allowed


def select_model(task_type=None, usage=None):
    """
    Select the best model for a task given current usage AND model availability.
    Now checks Codex CLI exhaustion status.
    For coding tasks: Codex → Claude Code (sonnet) → Opus (last resort)
    
    Returns: (model_id, reasoning)
    """
    if usage is None:
        usage = get_usage()
    
    primary_pct = usage.get("primary", {}).get("percent", 0)
    
    # Get allowed models (includes Codex availability check)
    allowed = get_effective_allowed_models(primary_pct)
    
    # If task type specified, try to use the best model for it
    preferred = None
    if task_type:
        task_lower = task_type.lower()
        for key, model in TASK_MODEL_MAP.items():
            if key in task_lower:
                preferred = model
                break
    
    # If preferred model is allowed, use it
    if preferred and preferred in allowed:
        return (
            MODELS[preferred],
            f"Task '{task_type}' → {preferred} (usage: {primary_pct}%)"
        )
    
    # Codex was preferred but exhausted — silent fallback for coding tasks
    # RULE: Never ask permission. Just use the next available model.
    codex_status = get_codex_status()
    if preferred == "codex" and not codex_status["available"]:
        # Coding fallback chain: Claude Code (sonnet) → Opus → Gemini (last resort, not ideal)
        fallback = "sonnet" if "sonnet" in allowed else ("opus" if "opus" in allowed else allowed[0] if allowed else "local")
        resets_msg = f", resets {codex_status['resets']}" if codex_status.get("resets") else ""
        return (
            MODELS[fallback],
            f"Codex unavailable{resets_msg} → auto-fallback to {fallback} (Claude Code). Usage: {primary_pct}%"
        )
    
    # Otherwise, use the best available model
    best = allowed[0] if allowed else "local"
    return (
        MODELS[best],
        f"Fallback to {best} (usage: {primary_pct}%, preferred '{preferred}' not available)"
        if preferred else f"Default to {best} (usage: {primary_pct}%)"
    )


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Intelligent model router")
    parser.add_argument("--task-type", "-t", help="Type of task (coding, writing, etc)")
    parser.add_argument("--check-only", "-c", action="store_true", help="Only show current state")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    parser.add_argument("--show-all", action="store_true", help="Show all model statuses")
    parser.add_argument("--set-codex-status", choices=["available", "exhausted"], help="Set Codex CLI status")
    parser.add_argument("--codex-resets", help="When Codex CLI resets (ISO date or human-readable)")
    args = parser.parse_args()
    
    # Handle Codex status setting
    if args.set_codex_status:
        available = args.set_codex_status == "available"
        result = set_codex_status(
            available=available,
            resets_at=args.codex_resets,
            reason=f"manually set to {args.set_codex_status}"
        )
        print(json.dumps(result, indent=2) if args.json else f"Codex CLI: {'✅ available' if available else '❌ exhausted'} (resets: {args.codex_resets or 'unknown'})")
        return
    
    usage = get_usage()
    primary_pct = usage.get("primary", {}).get("percent", 0)
    secondary_pct = usage.get("secondary", {}).get("percent", 0)
    codex = get_codex_status()
    allowed = get_effective_allowed_models(primary_pct)
    
    if args.show_all or args.check_only:
        result = {
            "usage": {
                "primary_percent": primary_pct,
                "secondary_percent": secondary_pct,
                "primary_resets": usage.get("primary", {}).get("resets", "unknown"),
                "secondary_resets": usage.get("secondary", {}).get("resets", "unknown"),
            },
            "codex_cli": {
                "available": codex["available"],
                "resets": codex.get("resets"),
                "reason": codex.get("reason"),
                "note": "Codex CLI ≠ Codex Code Review. Code Review is a separate GitHub App with its own quota."
            },
            "allowed_models": allowed,
            "degradation_level": len([t for t, _ in DEGRADATION_CURVE if primary_pct >= t]),
        }
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"📊 Claude: {primary_pct}% primary, {secondary_pct}% weekly")
            print(f"💻 Codex CLI: {'✅ available' if codex['available'] else '❌ exhausted'} (resets: {codex.get('resets', 'unknown')})")
            print(f"📝 Codex Code Review: separate quota (GitHub App)")
            print(f"🎯 Allowed models: {', '.join(allowed)}")
            print(f"📉 Degradation level: {result['degradation_level']}/{len(DEGRADATION_CURVE)}")
        return
    
    model, reasoning = select_model(args.task_type, usage)
    
    if args.json:
        print(json.dumps({
            "model": model,
            "reasoning": reasoning,
            "usage_percent": primary_pct,
            "codex_available": codex["available"],
        }))
    else:
        print(f"🤖 Model: {model}")
        print(f"💭 Reasoning: {reasoning}")


if __name__ == "__main__":
    main()
