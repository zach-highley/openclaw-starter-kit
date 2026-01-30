#!/usr/bin/env python3
"""
Session Reset Monitor

Detects when the active session ID changes (indicating a reset happened).
Useful because a dying session can't notify you about its own death.
This script runs externally and watches the session file.
"""

import json
import os
import sys
import time
from pathlib import Path

# === Config ===
SESSION_FILE = Path.home() / ".clawdbot" / "agents" / "main" / "sessions" / "sessions.json"
STATE_FILE = Path.home() / "clawd" / "state" / "session_monitor_state.json"
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_alert(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print(f"Alert (not sent, missing credentials): {msg}")
        return
        
    import urllib.request, urllib.parse
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": CHAT_ID, "text": msg}).encode()
    try:
        urllib.request.urlopen(url, data=data, timeout=5)
    except Exception as e:
        print(f"Failed to send alert: {e}")

def get_current_session_id():
    if not SESSION_FILE.exists():
        return None
    try:
        with open(SESSION_FILE) as f:
            data = json.load(f)
            # Assuming 'main' is the active session key, adjust parsing as needed
            return data.get("sessions", {}).get("agent:main:main", {}).get("id")
    except:
        return None

def main():
    if not STATE_FILE.exists():
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        current = get_current_session_id()
        with open(STATE_FILE, "w") as f:
            json.dump({"last_session_id": current}, f)
        return

    with open(STATE_FILE) as f:
        state = json.load(f)
    
    last_id = state.get("last_session_id")
    current_id = get_current_session_id()
    
    if current_id and last_id and current_id != last_id:
        print(f"Session reset detected: {last_id} -> {current_id}")
        send_alert(f"🔄 **Session Reset Detected**\nNew Session ID: `{current_id}`")
        
        state["last_session_id"] = current_id
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)

if __name__ == "__main__":
    main()
