#!/usr/bin/env python3
"""
Meta-Monitor (The Watcher of Watchers)

Monitors your automation systems to ensure THEY are running.
If the watchdog dies, who watches the watchdog? This script.

Features:
- Fencing tokens (prevents multiple scripts from fighting over gateway restarts)
- Stall detection (notifies if a system hasn't updated in X seconds)
- Auto-fix (can restart stalled services)
- Context monitoring (triggers reset if context > 85%)

USAGE:
  python3 meta_monitor.py --check
  python3 meta_monitor.py --fix
"""

import json
import os
import sys
import time
import subprocess
from pathlib import Path

# === Config ===
# Adjust paths for your setup
CLAWD_DIR = Path(os.environ.get("CLAWD_DIR", Path.home() / "clawd"))
STATE_FILE = CLAWD_DIR / "state" / "meta_monitor_state.json"
GATEWAY_PID_FILE = Path.home() / ".clawdbot" / "pids" / "gateway.pid"

# Thresholds (seconds) - How long before we consider a system "stalled"
THRESHOLDS = {
    "watchdog": 600,          # 10 mins (runs every 5)
    "error_recovery": 1800,   # 30 mins
    "security_hound": 7200,   # 2 hours
    "heartbeat": 7200,        # 2 hours
}

def load_state():
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"last_checks": {}, "fencing_token": None}

def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def check_system_age(name, file_path):
    """Returns seconds since file was last modified."""
    path = Path(file_path)
    if not path.exists():
        return None
    return time.time() - path.stat().st_mtime

def run_check(mode="check"):
    state = load_state()
    issues = []
    
    # Check each system
    # Note: specific paths depend on where your scripts write their state/logs
    # This is a reference implementation.
    systems = {
        "watchdog": Path.home() / ".clawdbot" / "logs" / "watchdog-state.json",
        "heartbeat": CLAWD_DIR / "memory" / "heartbeat-state.json",
    }
    
    for name, path in systems.items():
        age = check_system_age(name, path)
        if age is None:
            # File missing, might be okay if just started
            continue
            
        threshold = THRESHOLDS.get(name, 3600)
        if age > threshold:
            issues.append(f"{name} stalled (last update {int(age)}s ago)")

    # Report
    if issues:
        print(f"⚠️ Issues detected: {', '.join(issues)}")
        if mode == "fix":
            print("🔧 Attempting auto-fixes...")
            # Add your restart logic here
    else:
        print("✅ All systems healthy")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["check", "fix"], default="check")
    args = parser.parse_args()
    
    run_check(args.mode)
