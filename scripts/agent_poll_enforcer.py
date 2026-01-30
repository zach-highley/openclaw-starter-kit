#!/usr/bin/env python3
"""
Agent Poll Enforcer — Catches AI silence during background agent work.

Problem: Your AI keeps going silent while coding agents run. Rules exist
but aren't followed. This script enforces the notification cadence externally.

Setup:
  1. Add to your watchdog.sh as a check
  2. Call --mark-notified after every progress message to the user
  3. If silence > MAX_SILENCE_SEC, script wakes the AI via gateway

Usage:
  python3 agent_poll_enforcer.py              # Check for silence violations
  python3 agent_poll_enforcer.py --mark-notified  # Record notification sent
"""

import json
import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# === CONFIGURE THESE ===
CLAWD = Path.home() / "clawd"  # Your workspace root
STATE_FILE = CLAWD / "state" / "poll_enforcer_state.json"
WORK_STATE = CLAWD / "state" / "current_work.json"
MAX_SILENCE_SEC = 300  # 5 minutes — adjust to taste

def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def is_agent_running():
    """Check if a background coding agent is currently active."""
    work = load_json(WORK_STATE)

    # Check for active sprints in work state
    current = work.get("current_sprint")
    if current and isinstance(current, dict):
        status = current.get("status", "")
        if status in ("running", "in_progress", "active"):
            return True, current.get("name", "unknown sprint")

    # Check for coding agent processes
    for pattern in ["codex", "claude-code", "npx codex", "codex-cli"]:
        try:
            result = subprocess.run(
                ["pgrep", "-f", pattern],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return True, f"process: {pattern}"
        except Exception:
            pass

    return False, None

def check():
    """Main check — run from watchdog or cron."""
    running, agent_desc = is_agent_running()

    if not running:
        state = load_json(STATE_FILE)
        state["last_check_ts"] = time.time()
        state["agent_active"] = False
        state["should_alert"] = False
        save_json(STATE_FILE, state)
        print(json.dumps({"agent_active": False, "should_alert": False}))
        return

    # Agent running — check silence
    state = load_json(STATE_FILE)
    last_notif = state.get("last_notification_ts", 0)
    now = time.time()
    silence_sec = now - last_notif if last_notif > 0 else 9999

    should_alert = silence_sec > MAX_SILENCE_SEC

    state.update({
        "last_check_ts": now,
        "agent_active": True,
        "agent_desc": agent_desc,
        "silence_seconds": int(silence_sec),
        "should_alert": should_alert
    })
    save_json(STATE_FILE, state)

    result = {
        "agent_active": True,
        "agent_desc": agent_desc,
        "silence_seconds": int(silence_sec),
        "should_alert": should_alert
    }

    if should_alert:
        msg = (f"⚠️ SILENCE ALERT: Background agent ({agent_desc}) running "
               f"for {int(silence_sec)}s with no update. CHECK NOW.")
        try:
            subprocess.run(
                ["openclaw", "gateway", "wake", "--text", msg, "--mode", "now"],
                timeout=10, capture_output=True
            )
            result["alert_sent"] = True
            state["last_notification_ts"] = time.time()
            save_json(STATE_FILE, state)
        except Exception:
            result["alert_sent"] = False

    print(json.dumps(result, indent=2))

def mark_notified():
    """Record that a notification was just sent."""
    state = load_json(STATE_FILE)
    state["last_notification_ts"] = time.time()
    state["last_notification_iso"] = datetime.now(timezone.utc).isoformat()
    save_json(STATE_FILE, state)
    print("Notification timestamp recorded.")

if __name__ == "__main__":
    if "--mark-notified" in sys.argv:
        mark_notified()
    else:
        check()
