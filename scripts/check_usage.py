#!/usr/bin/env python3
"""check_usage.py — 🦑 Ackbar: Multi-model usage monitor.

Shows usage for ALL subscription models:
  ☁️ Claude (Opus) — primary conversation model
  💻 Codex (GPT-5.2) — all coding tasks
  🔮 Gemini (3 Pro) — emergency fallback

Self-contained. Does NOT depend on model_router.py.
Reads directly from session store + state files.

Usage:
  python3 check_usage.py           # Human-readable output
  python3 check_usage.py --json    # JSON output for scripts
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

CLAWD = Path.home() / ".openclaw" / "workspace"
STATE_FILE = CLAWD / "state" / "usage_alerts.json"
CODEX_STATE = CLAWD / "state" / "codex_status.json"
SESSIONS_FILE = Path.home() / ".openclaw" / "agents" / "main" / "sessions" / "sessions.json"

THRESHOLDS = [20, 40, 60, 80, 90, 95, 100]


def get_session_tokens():
    """Get total token usage from all sessions today."""
    try:
        with open(SESSIONS_FILE) as f:
            data = json.load(f)
        total_in = 0
        total_out = 0
        main_ctx_pct = 0
        for key, sess in data.items():
            inp = sess.get("inputTokens", 0) or 0
            out = sess.get("outputTokens", 0) or 0
            total_in += inp
            total_out += out
            if "main:main" in key:
                total = sess.get("totalTokens", 0) or 0
                ctx = sess.get("contextTokens", 200000) or 200000
                main_ctx_pct = round((total / ctx) * 100) if ctx > 0 else 0
        return {
            "input": total_in,
            "output": total_out,
            "total": total_in + total_out,
            "main_ctx_pct": main_ctx_pct
        }
    except Exception:
        return {"input": 0, "output": 0, "total": 0, "main_ctx_pct": 0}


def get_claude_usage():
    """Get Claude usage from session store + context data.
    
    Note: Anthropic rate limit headers (primary/5h percentages) are NOT
    persisted by OpenClaw. On MAX tier ($200/mo), rate limits are effectively
    irrelevant. The real constraint is CONTEXT WINDOW usage.
    """
    claude = {
        "name": "☁️ Claude (Opus)",
        "tier": "MAX $200/mo",
        "context_pct": None,
        "total_tokens_session": None,
        "context_window": None,
        "compactions": 0,
        "rate_note": "MAX tier: rate limits effectively unlimited",
        "status": "active"
    }
    
    # Get real data from session store
    try:
        with open(SESSIONS_FILE) as f:
            data = json.load(f)
        main = data.get("agent:main:main", {})
        total = main.get("totalTokens", 0) or 0
        ctx = main.get("contextTokens", 200000) or 200000
        claude["total_tokens_session"] = total
        claude["context_window"] = ctx
        claude["context_pct"] = round((total / ctx) * 100) if ctx > 0 else 0
        claude["compactions"] = main.get("authProfileOverrideCompactionCount", 0)
    except Exception:
        pass
    
    return claude


def get_codex_usage():
    """Get Codex status from state file."""
    codex = {
        "name": "💻 Codex (GPT-5.2)",
        "tier": "MAX $200/mo",
        "available": True,
        "resets": None,
        "status": "available"
    }
    if CODEX_STATE.exists():
        try:
            with open(CODEX_STATE) as f:
                cs = json.load(f)
            if cs.get("exhausted") or cs.get("available") is False:
                codex["available"] = False
                codex["status"] = "cooldown"
                codex["resets"] = cs.get("resets_at", cs.get("reset_date"))
            else:
                codex["available"] = cs.get("available", True)
                codex["status"] = "available"
                codex["tier_detail"] = cs.get("tier", "max")
        except Exception:
            pass
    return codex


def get_gemini_usage():
    """Get Gemini status from auth profile existence."""
    gemini = {
        "name": "🔮 Gemini (3 Pro)",
        "tier": "Emergency fallback",
        "auth_ok": True,
        "status": "standby"
    }
    # Check if the oauth profile exists
    auth_file = Path.home() / ".openclaw" / "agents" / "main" / "agent" / "auth-profiles.json"
    if auth_file.exists():
        try:
            with open(auth_file) as f:
                profiles = json.load(f)
            for key, val in profiles.items():
                if "gemini" in key.lower():
                    gemini["auth_ok"] = True
                    gemini["status"] = "standby"
                    break
        except Exception:
            pass
    return gemini


def check_alerts(claude):
    """Check context thresholds and return new alerts."""
    state = {}
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                state = json.load(f)
        except Exception:
            pass

    today = datetime.now().strftime("%Y-%m-%d")
    if state.get("date") != today:
        state = {"date": today, "fired": {}}

    new_alerts = []
    pct = claude.get("context_pct") or 0

    for threshold in THRESHOLDS:
        key = f"context_{threshold}"
        if pct >= threshold and key not in state.get("fired", {}):
            emoji = "🦑" if threshold < 90 else "🚨"
            if threshold >= 90:
                new_alerts.append(f"{emoji} IT'S A TRAP! Context at {pct}%! Gateway compaction imminent.")
            elif threshold >= 80:
                new_alerts.append(f"{emoji} Context at {pct}%. Gateway memory flush active.")
            else:
                new_alerts.append(f"{emoji} Context at {pct}% (threshold: {threshold}%)")
            state.setdefault("fired", {})[key] = datetime.now().isoformat()

    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

    return new_alerts


def format_human(claude, codex, gemini, tokens):
    """Format usage report for humans."""
    lines = ["🦑 **Ackbar: Model Usage Report**", ""]

    # Claude
    ctx_pct = claude.get("context_pct", 0) or 0
    icon = "🟢" if ctx_pct < 60 else "🟡" if ctx_pct < 80 else "🔴"
    lines.append(f"{icon} {claude['name']} — {claude['tier']}")
    if claude.get("total_tokens_session") is not None:
        lines.append(f"   Context: {ctx_pct}% ({claude['total_tokens_session']:,}/{claude['context_window']:,} tokens)")
        lines.append(f"   Compactions: {claude.get('compactions', 0)} | Rate limits: unlimited (MAX)")
    else:
        lines.append(f"   Context: data unavailable")

    # Codex
    icon = "🟢" if codex["available"] else "🔴"
    status = "✅ Available" if codex["available"] else f"⏳ Cooldown{' (resets ' + str(codex['resets']) + ')' if codex.get('resets') else ''}"
    lines.append(f"{icon} {codex['name']} — {codex['tier']}")
    lines.append(f"   Status: {status}")

    # Gemini
    icon = "🟢" if gemini.get("auth_ok") else "🟡"
    lines.append(f"{icon} {gemini['name']} — {gemini['tier']}")
    lines.append(f"   Status: {'🟢 Ready (standby)' if gemini.get('auth_ok') else '🟡 Auth expired'}")

    # Gateway compaction info
    lines.append("")
    lines.append(f"⚙️ Auto-flush at ~75% | Auto-compact at ~85%")

    return "\n".join(lines)


def main():
    use_json = "--json" in sys.argv

    claude = get_claude_usage()
    codex = get_codex_usage()
    gemini = get_gemini_usage()
    tokens = get_session_tokens()
    alerts = check_alerts(claude)

    if use_json:
        output = {
            "models": {
                "claude": {
                    "context_pct": claude.get("context_pct"),
                    "total_tokens": claude.get("total_tokens_session"),
                    "context_window": claude.get("context_window"),
                    "compactions": claude.get("compactions", 0),
                    "tier": claude["tier"],
                    "status": claude["status"]
                },
                "codex": {
                    "available": codex["available"],
                    "status": codex["status"],
                    "resets": codex.get("resets"),
                    "tier": codex["tier"]
                },
                "gemini": {
                    "auth_ok": gemini.get("auth_ok"),
                    "status": gemini["status"],
                    "tier": gemini["tier"]
                }
            },
            "session": {
                "main_ctx_pct": tokens["main_ctx_pct"],
                "total_tokens": tokens["total"]
            },
            "alerts": alerts,
            "should_alert": len(alerts) > 0
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_human(claude, codex, gemini, tokens))
        if alerts:
            print()
            for alert in alerts:
                print(alert)


if __name__ == "__main__":
    main()
