#!/usr/bin/env python3
"""
Claude Usage Monitor — Track rate limits, alert on thresholds.

Checks Claude Pro/Max usage via CodexBar and returns JSON with:
- Current usage percentages (primary 5-hour window + secondary weekly)
- Whether new thresholds were crossed (should_alert)
- Alert at: 20%, 40%, 60%, 80%, 90%, 95%, 100%

Requires: codexbar CLI (npm install -g codexbar)

Usage:
    python3 check_usage.py          # Returns JSON
    python3 check_usage.py | jq .   # Pretty print
"""

import json
import subprocess
import sys
from pathlib import Path

STATE_FILE = Path.home() / "clawd" / "memory" / "usage-state.json"
THRESHOLDS = [20, 40, 60, 80, 90, 95, 100]


def get_usage():
    """Fetch current usage from CodexBar."""
    try:
        result = subprocess.run(
            ["codexbar", "usage", "--provider", "claude", "--format", "json"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        if not data:
            return None
        return data[0].get("usage", {})
    except Exception:
        return None


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"primary_alerted": [], "secondary_alerted": []}


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def check_thresholds(current_pct, alerted_list):
    """Check if we've crossed new thresholds."""
    alerts = []
    for t in THRESHOLDS:
        if current_pct >= t and t not in alerted_list:
            alerts.append(t)
            alerted_list.append(t)
    if current_pct < 20:
        alerted_list.clear()
    return alerts


def main():
    usage = get_usage()
    if not usage:
        print(json.dumps({"error": "Could not fetch usage"}))
        sys.exit(1)

    primary = usage.get("primary", {})
    secondary = usage.get("secondary", {})

    primary_pct = primary.get("usedPercent", 0)
    secondary_pct = secondary.get("usedPercent", 0)
    primary_reset = primary.get("resetDescription", "unknown")
    secondary_reset = secondary.get("resetDescription", "unknown")

    state = load_state()
    primary_alerts = check_thresholds(primary_pct, state["primary_alerted"])
    secondary_alerts = check_thresholds(secondary_pct, state["secondary_alerted"])
    save_state(state)

    result = {
        "primary": {
            "percent": primary_pct,
            "resets": primary_reset,
            "new_alerts": primary_alerts,
        },
        "secondary": {
            "percent": secondary_pct,
            "resets": secondary_reset,
            "new_alerts": secondary_alerts,
        },
        "should_alert": bool(primary_alerts or secondary_alerts),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
