#!/usr/bin/env python3
"""
OpenClaw Context Healer — Monitor session context usage.

Reads the gateway session store and reports context utilisation for
the main agent session.  Notification-only: this script does NOT
trigger resets or compaction (the gateway handles that).

Thresholds (awareness levels):
    60%  — context getting warm
    70%  — consider wrapping up current task
    80%  — compaction likely imminent

Output modes:
    (default)  human-readable summary
    --json     machine-readable JSON

Usage:
    python3 context_healer.py               # human summary
    python3 context_healer.py --json        # JSON output
    python3 context_healer.py --help        # this text

Requires: Python 3.9+
No external dependencies.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------
# Defaults & constants
# ---------------------------------------------------------------

# Where OpenClaw stores session data
DEFAULT_SESSIONS_PATH = Path.home() / ".openclaw" / "agents" / "main" / "sessions" / "sessions.json"

# Awareness thresholds (not action thresholds — gateway handles compaction)
THRESHOLDS = [60, 70, 80]

# ---------------------------------------------------------------
# Workspace detection
# ---------------------------------------------------------------

def detect_workspace() -> Path:
    """Find the workspace directory using the standard cascade."""
    env = os.environ.get("OPENCLAW_WORKSPACE")
    if env:
        return Path(env).expanduser().resolve()
    candidates = [
        Path.home() / ".openclaw" / "workspace",
    ]
    for c in candidates:
        if c.is_dir():
            return c
    return Path.cwd()

# ---------------------------------------------------------------
# Session parsing
# ---------------------------------------------------------------

def load_sessions(path: Path) -> Optional[Dict[str, Any]]:
    """Load sessions.json, returning the parsed dict or None on failure."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Warning: could not read {path}: {exc}", file=sys.stderr)
        return None


def extract_main_session(sessions: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract the main agent session from the sessions store.

    The store format can vary between OpenClaw versions.  We try several
    common shapes:
        1. Top-level dict with a "main" key
        2. A list of session objects with .agent == "main"
        3. A single session object (if the file only contains one)
    """
    # Shape 1: dict keyed by agent name
    if isinstance(sessions, dict):
        if "main" in sessions:
            return sessions["main"]
        # Maybe it's a wrapper with a "sessions" key
        inner = sessions.get("sessions")
        if isinstance(inner, dict) and "main" in inner:
            return inner["main"]
        if isinstance(inner, list):
            for s in inner:
                if isinstance(s, dict) and s.get("agent") == "main":
                    return s
        # If there's only one key, use it
        if len(sessions) == 1:
            val = next(iter(sessions.values()))
            if isinstance(val, dict):
                return val
        # Return the whole dict as a last resort (might be the session itself)
        if "contextTokens" in sessions or "tokens" in sessions or "usage" in sessions:
            return sessions

    # Shape 2: list of sessions
    if isinstance(sessions, list):
        for s in sessions:
            if isinstance(s, dict) and s.get("agent") == "main":
                return s
        if len(sessions) == 1 and isinstance(sessions[0], dict):
            return sessions[0]

    return None


def get_context_percent(session: Dict[str, Any]) -> Optional[float]:
    """
    Derive context utilisation percentage from a session object.

    Tries several field names that OpenClaw may use:
        contextTokens / maxContextTokens
        tokens.used / tokens.max
        usage.contextPercent (direct percentage)
    """
    # Direct percentage field
    for key in ("contextPercent", "context_percent"):
        val = session.get(key)
        if val is not None:
            return float(val)

    # usage sub-object
    usage = session.get("usage", {})
    if isinstance(usage, dict):
        for key in ("contextPercent", "context_percent"):
            val = usage.get(key)
            if val is not None:
                return float(val)

    # Token counts
    used = (
        session.get("contextTokens")
        or session.get("tokens", {}).get("used")
        or session.get("tokenCount")
        or usage.get("contextTokens")
    )
    maximum = (
        session.get("maxContextTokens")
        or session.get("tokens", {}).get("max")
        or session.get("maxTokens")
        or usage.get("maxContextTokens")
    )

    if used is not None and maximum is not None:
        maximum = float(maximum)
        if maximum > 0:
            return round(float(used) / maximum * 100, 1)

    return None

# ---------------------------------------------------------------
# Threshold evaluation
# ---------------------------------------------------------------

def evaluate_thresholds(pct: float) -> List[int]:
    """Return the list of thresholds that have been breached."""
    return [t for t in THRESHOLDS if pct >= t]


def severity_label(pct: float) -> str:
    if pct >= 80:
        return "HIGH"
    if pct >= 70:
        return "ELEVATED"
    if pct >= 60:
        return "WARM"
    return "OK"

# ---------------------------------------------------------------
# Output
# ---------------------------------------------------------------

def output_json(pct: Optional[float], sessions_path: Path) -> None:
    breached = evaluate_thresholds(pct) if pct is not None else []
    result = {
        "context_percent": pct,
        "severity": severity_label(pct) if pct is not None else "UNKNOWN",
        "thresholds_breached": breached,
        "sessions_path": str(sessions_path),
    }
    print(json.dumps(result, indent=2))


def output_human(pct: Optional[float], sessions_path: Path) -> None:
    if pct is None:
        print("Context usage: UNKNOWN (could not read session data)")
        print(f"  Sessions path: {sessions_path}")
        print("  Tip: is the OpenClaw gateway running?")
        return

    severity = severity_label(pct)
    bar_len = 30
    filled = int(pct / 100 * bar_len)
    bar = "█" * filled + "░" * (bar_len - filled)

    emoji = {"OK": "🟢", "WARM": "🟡", "ELEVATED": "🟠", "HIGH": "🔴"}.get(severity, "⚪")

    print(f"Context: {emoji} {pct:.1f}% [{bar}] ({severity})")

    breached = evaluate_thresholds(pct)
    if breached:
        print(f"  Thresholds breached: {', '.join(f'{t}%' for t in breached)}")
    else:
        print("  All clear — no thresholds breached.")

    if pct >= 80:
        print("  ⚠️  Compaction is likely imminent. The gateway will handle it automatically.")
    elif pct >= 70:
        print("  📝 Consider finishing current task soon.")
    elif pct >= 60:
        print("  💡 Context is getting warm. Nothing to do yet.")

# ---------------------------------------------------------------
# CLI
# ---------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Monitor OpenClaw main session context usage.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  python3 context_healer.py              # human-readable
  python3 context_healer.py --json       # JSON output
  python3 context_healer.py --sessions-path /custom/path/sessions.json
""",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output machine-readable JSON instead of human-readable text.",
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

    sessions = load_sessions(args.sessions_path)
    pct: Optional[float] = None

    if sessions is not None:
        main_session = extract_main_session(sessions)
        if main_session is not None:
            pct = get_context_percent(main_session)

    if args.json_output:
        output_json(pct, args.sessions_path)
    else:
        output_human(pct, args.sessions_path)

    # Exit code: 0 = OK, 1 = threshold breached, 2 = unknown
    if pct is None:
        sys.exit(2)
    if pct >= THRESHOLDS[0]:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
