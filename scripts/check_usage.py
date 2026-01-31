#!/usr/bin/env python3
"""
OpenClaw Usage Monitor — Self-contained context & model usage tracker.

Reads context usage from the OpenClaw session store and lists all
configured models with availability info.  No external dependencies
(no codexbar, no API keys).

Data sources:
    ~/.openclaw/agents/main/sessions/sessions.json   (context tokens)
    ~/.openclaw/openclaw.json                         (model config)

Threshold alerts: 20% → 40% → 60% → 80% → 90% → 95% → 100%

Output modes:
    (default)  human-readable summary
    --json     machine-readable JSON

State file:
    $WORKSPACE/state/usage_state.json    (tracks which thresholds were alerted)

Usage:
    python3 check_usage.py               # human summary
    python3 check_usage.py --json        # JSON
    python3 check_usage.py --help        # this text

Requires: Python 3.9+
No external dependencies.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------

DEFAULT_CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"
DEFAULT_SESSIONS_PATH = (
    Path.home() / ".openclaw" / "agents" / "main" / "sessions" / "sessions.json"
)
THRESHOLDS = [20, 40, 60, 80, 90, 95, 100]

# Known model-provider prefixes → friendly labels
PROVIDER_LABELS = {
    "anthropic": "Anthropic",
    "openai": "OpenAI",
    "openai-codex": "OpenAI Codex",
    "google-gemini-cli": "Google Gemini",
    "google": "Google",
    "ollama": "Ollama (local)",
    "groq": "Groq",
    "mistral": "Mistral",
    "cohere": "Cohere",
    "deepseek": "DeepSeek",
}

# ---------------------------------------------------------------
# Workspace detection
# ---------------------------------------------------------------

def detect_workspace() -> Path:
    """Find workspace: $OPENCLAW_WORKSPACE → ~/clawd → ~/.openclaw/workspace → cwd."""
    env = os.environ.get("OPENCLAW_WORKSPACE")
    if env:
        return Path(env)
    for candidate in [Path.home() / "clawd", Path.home() / ".openclaw" / "workspace"]:
        if candidate.is_dir():
            return candidate
    return Path.cwd()


WORKSPACE = detect_workspace()
STATE_FILE = WORKSPACE / "state" / "usage_state.json"

# ---------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------

def load_json(path: Path) -> Optional[Dict[str, Any]]:
    """Safely load a JSON file, returning None on any failure."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None

# ---------------------------------------------------------------
# Model discovery
# ---------------------------------------------------------------

def discover_models(config: Optional[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Walk the openclaw.json config and collect every model reference.

    Returns a list of dicts: {"id": "anthropic/claude-sonnet-4", "role": "primary", "label": "Anthropic"}
    """
    if config is None:
        return []

    seen: set[str] = set()
    models: List[Dict[str, str]] = []

    def add(model_id: str, role: str = "configured") -> None:
        if not model_id or model_id in seen:
            return
        seen.add(model_id)
        provider = model_id.split("/")[0] if "/" in model_id else model_id
        label = PROVIDER_LABELS.get(provider, provider.title())
        models.append({"id": model_id, "role": role, "label": label})

    # Walk agents.defaults.model
    defaults = config.get("agents", {}).get("defaults", {})

    model_block = defaults.get("model", {})
    if isinstance(model_block, str):
        add(model_block, "primary")
    elif isinstance(model_block, dict):
        add(model_block.get("primary", ""), "primary")
        for fb in model_block.get("fallbacks", []):
            add(fb, "fallback")

    # Subagent models
    sub_model = defaults.get("subagents", {}).get("model", {})
    if isinstance(sub_model, str):
        add(sub_model, "subagent-primary")
    elif isinstance(sub_model, dict):
        add(sub_model.get("primary", ""), "subagent-primary")
        for fb in sub_model.get("fallbacks", []):
            add(fb, "subagent-fallback")

    # Walk named agents (agents.<name>.model)
    agents = config.get("agents", {})
    for key, agent_cfg in agents.items():
        if key == "defaults" or not isinstance(agent_cfg, dict):
            continue
        am = agent_cfg.get("model", {})
        if isinstance(am, str):
            add(am, f"agent:{key}")
        elif isinstance(am, dict):
            add(am.get("primary", ""), f"agent:{key}")
            for fb in am.get("fallbacks", []):
                add(fb, f"agent:{key}:fallback")

    # Walk providers section (if present)
    providers = config.get("providers", {})
    if isinstance(providers, dict):
        for prov_name, prov_cfg in providers.items():
            if isinstance(prov_cfg, dict):
                for m in prov_cfg.get("models", []):
                    mid = f"{prov_name}/{m}" if isinstance(m, str) else ""
                    add(mid, "provider-listed")

    return models

# ---------------------------------------------------------------
# Context usage
# ---------------------------------------------------------------

def get_context_usage(sessions: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Extract context usage from the sessions store.

    Returns {"used": int, "max": int, "percent": float} or None.
    """
    if sessions is None:
        return None

    # Try to find the main session.
    # OpenClaw uses "agent:main:main" as the key (not bare "main").
    session = None
    if isinstance(sessions, dict):
        # Try current format: "agent:main:main"
        session = sessions.get("agent:main:main")

        # Fallback: legacy bare "main" key
        if session is None:
            session = sessions.get("main")

        # Fallback: search for any key containing "main:main"
        if session is None:
            for key, val in sessions.items():
                if "main:main" in key and isinstance(val, dict):
                    session = val
                    break

        # Fallback: nested "sessions" dict (older formats)
        if session is None:
            inner = sessions.get("sessions")
            if isinstance(inner, dict):
                session = inner.get("agent:main:main") or inner.get("main")
                if session is None:
                    for key, val in inner.items():
                        if "main:main" in key and isinstance(val, dict):
                            session = val
                            break
            elif isinstance(inner, list):
                for s in inner:
                    if isinstance(s, dict) and s.get("agent") == "main":
                        session = s
                        break

        # Fallback: single-entry dict
        if session is None and len(sessions) == 1:
            val = next(iter(sessions.values()))
            if isinstance(val, dict):
                session = val

        # The file itself might be the session
        if session is None and ("contextTokens" in sessions or "tokens" in sessions):
            session = sessions

    if isinstance(sessions, list):
        for s in sessions:
            if isinstance(s, dict) and s.get("agent") == "main":
                session = s
                break
        if session is None and len(sessions) == 1 and isinstance(sessions[0], dict):
            session = sessions[0]

    if session is None:
        return None

    # Extract token counts
    usage_block = session.get("usage", {}) if isinstance(session.get("usage"), dict) else {}

    # Direct percent
    for key in ("contextPercent", "context_percent"):
        val = session.get(key) or usage_block.get(key)
        if val is not None:
            return {"percent": float(val), "used": None, "max": None}

    # Token extraction — explicit checks to avoid Python ternary precedence bugs.
    # Get used tokens (totalTokens is context-relevant in OpenClaw sessions)
    used = session.get("totalTokens") or session.get("contextTokens")
    if used is None:
        tokens_block = session.get("tokens")
        if isinstance(tokens_block, dict):
            used = tokens_block.get("used")
    if used is None:
        used = usage_block.get("contextTokens") or session.get("tokenCount")

    # Get max context window
    maximum = session.get("contextTokens") if session.get("totalTokens") else None
    if maximum is None:
        maximum = session.get("maxContextTokens")
    if maximum is None:
        tokens_block = session.get("tokens")
        if isinstance(tokens_block, dict):
            maximum = tokens_block.get("max")
    if maximum is None:
        maximum = session.get("maxTokens") or usage_block.get("maxContextTokens")

    if used is not None and maximum is not None and float(maximum) > 0:
        pct = round(float(used) / float(maximum) * 100, 1)
        return {"used": int(used), "max": int(maximum), "percent": pct}

    if used is not None:
        return {"used": int(used), "max": None, "percent": None}

    return None

# ---------------------------------------------------------------
# Threshold alerting
# ---------------------------------------------------------------

def load_state() -> Dict[str, Any]:
    state = load_json(STATE_FILE)
    if state and isinstance(state, dict):
        return state
    return {"alerted_thresholds": [], "last_check": None}


def save_state(state: Dict[str, Any]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def check_thresholds(pct: float, alerted: List[int]) -> Tuple[List[int], List[int]]:
    """
    Return (new_alerts, updated_alerted_list).

    Resets alerts when usage drops below the lowest threshold.
    """
    new_alerts: List[int] = []
    updated = list(alerted)

    for t in THRESHOLDS:
        if pct >= t and t not in updated:
            new_alerts.append(t)
            updated.append(t)

    # Reset when we drop below the first threshold
    if pct < THRESHOLDS[0]:
        updated.clear()

    return new_alerts, updated

# ---------------------------------------------------------------
# Output — JSON
# ---------------------------------------------------------------

def output_json(
    models: List[Dict[str, str]],
    context: Optional[Dict[str, Any]],
    new_alerts: List[int],
    should_alert: bool,
) -> None:
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": context,
        "models": models,
        "thresholds": {
            "new_alerts": new_alerts,
            "should_alert": should_alert,
            "levels": THRESHOLDS,
        },
    }
    print(json.dumps(result, indent=2))

# ---------------------------------------------------------------
# Output — Human
# ---------------------------------------------------------------

def severity_emoji(pct: float) -> str:
    if pct >= 95:
        return "🔴"
    if pct >= 80:
        return "🟠"
    if pct >= 60:
        return "🟡"
    if pct >= 40:
        return "🔵"
    return "🟢"


def output_human(
    models: List[Dict[str, str]],
    context: Optional[Dict[str, Any]],
    new_alerts: List[int],
) -> None:
    print("═══════════════════════════════════════")
    print("  OpenClaw Usage Monitor")
    print("═══════════════════════════════════════")
    print()

    # Context usage
    print("📊 Context Usage")
    if context and context.get("percent") is not None:
        pct = context["percent"]
        bar_len = 30
        filled = int(pct / 100 * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        emoji = severity_emoji(pct)
        print(f"   {emoji} {pct:.1f}% [{bar}]")
        if context.get("used") is not None and context.get("max") is not None:
            print(f"   Tokens: {context['used']:,} / {context['max']:,}")
    elif context and context.get("used") is not None:
        print(f"   Tokens used: {context['used']:,} (max unknown)")
    else:
        print("   ⚪ Could not read context data")
        print("   Tip: is the gateway running? Check sessions.json")
    print()

    # Threshold alerts
    if new_alerts:
        print(f"🚨 NEW threshold alerts: {', '.join(f'{t}%' for t in new_alerts)}")
        print()

    # Models
    if models:
        print("🤖 Configured Models")
        for m in models:
            role_badge = {
                "primary": "★",
                "fallback": "↳",
                "subagent-primary": "◆",
                "subagent-fallback": "◇",
            }.get(m["role"], "·")
            print(f"   {role_badge} {m['id']}")
            print(f"     Provider: {m['label']}  |  Role: {m['role']}")
    else:
        print("🤖 No models configured (or config not found)")
        print("   Tip: check ~/.openclaw/openclaw.json")
    print()
    print("═══════════════════════════════════════")

# ---------------------------------------------------------------
# CLI
# ---------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Self-contained OpenClaw usage & context monitor.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  python3 check_usage.py                 # human-readable
  python3 check_usage.py --json          # JSON output
  python3 check_usage.py --json | jq .   # pretty-printed JSON

Thresholds: 20% 40% 60% 80% 90% 95% 100%
State file: $WORKSPACE/state/usage_state.json
""",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Machine-readable JSON output.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help=f"Path to openclaw.json (default: {DEFAULT_CONFIG_PATH})",
    )
    parser.add_argument(
        "--sessions-path",
        type=Path,
        default=DEFAULT_SESSIONS_PATH,
        help=f"Path to sessions.json (default: {DEFAULT_SESSIONS_PATH})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Load data
    config = load_json(args.config)
    sessions = load_json(args.sessions_path)

    # Discover models
    models = discover_models(config)

    # Context usage
    context = get_context_usage(sessions)

    # Threshold checking
    state = load_state()
    new_alerts: List[int] = []
    should_alert = False

    if context and context.get("percent") is not None:
        pct = context["percent"]
        alerted = state.get("alerted_thresholds", [])
        new_alerts, updated = check_thresholds(pct, alerted)
        state["alerted_thresholds"] = updated
        should_alert = bool(new_alerts)
    
    state["last_check"] = datetime.now(timezone.utc).isoformat()
    save_state(state)

    # Output
    if args.json_output:
        output_json(models, context, new_alerts, should_alert)
    else:
        output_human(models, context, new_alerts)

    # Exit code: 0 = ok, 1 = new alerts fired, 2 = data unavailable
    if context is None:
        sys.exit(2)
    if should_alert:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
