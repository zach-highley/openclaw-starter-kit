#!/usr/bin/env python3
"""
Intelligent Model Router for Moltbot/Moltbot
Implements logarithmic degradation based on usage thresholds.

Usage: python3 model_router.py [--task-type TYPE] [--check-only]
"""

import json
import subprocess
import sys
from pathlib import Path

# Model hierarchy (in order of preference)
MODELS = {
    "opus": "anthropic/claude-opus-4-5",
    "sonnet": "anthropic/claude-sonnet-4",
    "codex": "openai-codex/gpt-5.2",
    "gemini": "google-gemini-cli/gemini-3-pro-preview",
    "local": "ollama/qwen2.5:14b",  # Install with: ollama pull qwen2.5:14b
}

# Task type → best model mapping
TASK_MODEL_MAP = {
    # Opus territory (complex reasoning, strategy, important decisions)
    "strategy": "opus",
    "reasoning": "opus",
    "important": "opus",
    "analysis": "opus",
    "planning": "opus",
    
    # Sonnet territory (good reasoning, faster, cheaper)
    "writing": "sonnet",
    "editing": "sonnet",
    "drafting": "sonnet",
    "email": "sonnet",
    "summarize": "sonnet",
    
    # Codex territory (coding, technical)
    "coding": "codex",
    "code": "codex",
    "debug": "codex",
    "refactor": "codex",
    "script": "codex",
    
    # Gemini territory (bulk, simple, fast)
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


def get_allowed_models(usage_percent):
    """Get allowed models based on usage percentage"""
    allowed = DEGRADATION_CURVE[0][1]
    for threshold, models in DEGRADATION_CURVE:
        if usage_percent >= threshold:
            allowed = models
    return allowed


def select_model(task_type=None, usage=None):
    """
    Select the best model for a task given current usage.
    
    Returns: (model_id, reasoning)
    """
    if usage is None:
        usage = get_usage()
    
    primary_pct = usage.get("primary", {}).get("percent", 0)
    
    # Get allowed models based on usage
    allowed = get_allowed_models(primary_pct)
    
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
    
    # Otherwise, use the best available model
    best = allowed[0]
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
    args = parser.parse_args()
    
    usage = get_usage()
    primary_pct = usage.get("primary", {}).get("percent", 0)
    secondary_pct = usage.get("secondary", {}).get("percent", 0)
    allowed = get_allowed_models(primary_pct)
    
    if args.check_only:
        result = {
            "usage": {
                "primary_percent": primary_pct,
                "secondary_percent": secondary_pct,
                "primary_resets": usage.get("primary", {}).get("resets", "unknown"),
                "secondary_resets": usage.get("secondary", {}).get("resets", "unknown"),
            },
            "allowed_models": allowed,
            "degradation_level": len([t for t, _ in DEGRADATION_CURVE if primary_pct >= t]),
        }
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"📊 Usage: {primary_pct}% primary, {secondary_pct}% weekly")
            print(f"🎯 Allowed models: {', '.join(allowed)}")
            print(f"📉 Degradation level: {result['degradation_level']}/{len(DEGRADATION_CURVE)}")
        return
    
    model, reasoning = select_model(args.task_type, usage)
    
    if args.json:
        print(json.dumps({
            "model": model,
            "reasoning": reasoning,
            "usage_percent": primary_pct,
        }))
    else:
        print(f"🤖 Model: {model}")
        print(f"💭 Reasoning: {reasoning}")


if __name__ == "__main__":
    main()
