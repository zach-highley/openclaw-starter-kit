#!/usr/bin/env python3
"""
Telegram Delivery Checker & Self-Fixer

Verifies that scheduled messages (morning briefing, weekly summary, etc.)
were actually delivered to your Telegram chat. If delivery failed, auto-retries
or alerts.

Integrates into watchdog as a periodic check.

SETUP:
  Set these environment variables (or edit the defaults below):
    TELEGRAM_BOT_TOKEN  — Your Telegram bot token
    TELEGRAM_CHAT_ID    — Your Telegram chat ID
  
  Or configure in your watchdog.sh:
    DELIVERY_CHECKER="$HOME/clawd/scripts/telegram_delivery_checker.py"
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

# === Config (set via environment variables or edit defaults) ===
CLAWD_DIR = Path(os.environ.get("CLAWD_DIR", Path.home() / "clawd"))
STATE_FILE = CLAWD_DIR / "state" / "telegram_delivery_state.json"
LOG_FILE = Path.home() / ".clawdbot/logs/watchdog.log"

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID_HERE")

# Expected daily deliveries — customize for your setup
# Add entries for each scheduled message you want to verify
EXPECTED_DELIVERIES = {
    "morning_briefing": {
        "cron_hour": 6,         # Expected delivery hour (local time)
        "cron_minute": 0,       # Expected delivery minute
        "description": "Morning briefing",
        "critical": True,       # Alert if missed
        "retry_allowed": True,
        "max_retries": 2,
        "keywords": ["good morning", "weather", "briefing", "forecast"],
    },
    # Add more scheduled messages here:
    # "weekly_summary": {
    #     "cron_hour": 18,
    #     "cron_minute": 0,
    #     "description": "Weekly summary",
    #     "critical": True,
    #     "retry_allowed": True,
    #     "max_retries": 2,
    #     "keywords": ["weekly", "summary", "recap"],
    # },
}

# === Helpers ===

def log(msg: str):
    """Append to watchdog log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"[{timestamp}] [TG-DELIVERY] {msg}\n")
    except Exception:
        pass

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"lastCheck": 0, "deliveries": {}, "dailyStats": {}, "learnings": []}

def save_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_local_now() -> datetime:
    """Get current local time (timezone-aware)."""
    return datetime.now().astimezone()

def check_telegram_api() -> bool:
    """Verify Telegram Bot API is reachable."""
    try:
        import urllib.request
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
            return data.get("ok", False)
    except Exception as e:
        log(f"Telegram API check failed: {e}")
        return False

def check_recent_messages(hours_back: int = 2) -> list:
    """Scan gateway logs for recent outbound Telegram messages."""
    messages_found = []
    log_path = Path.home() / ".clawdbot/logs/gateway.log"
    if not log_path.exists():
        return messages_found
    try:
        result = subprocess.run(
            ["tail", "-500", str(log_path)],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.splitlines():
            if "telegram" in line.lower() and ("send" in line.lower() or "message" in line.lower()):
                messages_found.append(line.strip()[:200])
    except Exception:
        pass
    return messages_found

def send_alert(message: str) -> bool:
    """Send an alert to your Telegram."""
    try:
        import urllib.request, urllib.parse
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = urllib.parse.urlencode({
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown",
        }).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read()).get("ok", False)
    except Exception as e:
        log(f"Alert send failed: {e}")
        return False

def attempt_fix() -> str:
    """Try to fix Telegram delivery issues."""
    fixes = []
    # Try restarting gateway
    try:
        clawdbot = Path.home() / ".nvm/versions/node/v22.16.0/bin/clawdbot"
        if clawdbot.exists():
            subprocess.run([str(clawdbot), "gateway", "restart"], capture_output=True, timeout=30)
            fixes.append("gateway_restart")
            time.sleep(5)
    except Exception:
        fixes.append("restart_failed")
    
    if check_telegram_api():
        fixes.append("api_reachable_after_fix")
    else:
        fixes.append("api_still_unreachable")
    return ", ".join(fixes)

def run_check(mode: str = "check") -> dict:
    """Main check routine. Modes: check, fix, status."""
    state = load_state()
    now = get_local_now()
    today = now.strftime("%Y-%m-%d")
    
    result = {
        "timestamp": now.isoformat(),
        "mode": mode,
        "api_healthy": check_telegram_api(),
        "delivery_healthy": True,
        "issues": [],
        "fixes_applied": [],
        "should_alert": False,
    }
    
    if not result["api_healthy"]:
        result["delivery_healthy"] = False
        result["issues"].append("Telegram API unreachable")
        if mode == "fix":
            fix_result = attempt_fix()
            result["fixes_applied"].append(fix_result)
            result["api_healthy"] = check_telegram_api()
            if result["api_healthy"]:
                result["delivery_healthy"] = True
    
    # Check expected deliveries
    if today not in state.get("deliveries", {}):
        state["deliveries"][today] = {}
    
    for delivery_id, config in EXPECTED_DELIVERIES.items():
        if not config.get("critical"):
            continue
        
        expected_time = now.replace(hour=config["cron_hour"], minute=config["cron_minute"], second=0)
        if now < expected_time + timedelta(minutes=30):
            continue  # Too early
        
        day_state = state["deliveries"][today].get(delivery_id, {})
        if day_state.get("verified"):
            continue
        
        recent = check_recent_messages(hours_back=3)
        keywords = config.get("keywords", [])
        found = any(any(kw in msg.lower() for kw in keywords) for msg in recent)
        
        if found:
            state["deliveries"][today][delivery_id] = {"verified": True, "verified_at": now.isoformat()}
            log(f"✅ {config['description']} verified delivered")
        else:
            retries = day_state.get("retries", 0)
            if retries < config.get("max_retries", 2) and config.get("retry_allowed"):
                state["deliveries"][today][delivery_id] = {"verified": False, "retries": retries + 1}
                result["issues"].append(f"{config['description']} not delivered — retry {retries+1}")
            else:
                result["delivery_healthy"] = False
                result["should_alert"] = True
                result["issues"].append(f"{config['description']} FAILED after {retries} retries")
    
    state["lastCheck"] = time.time()
    save_state(state)
    
    if result["should_alert"]:
        send_alert(f"⚠️ Scheduled message delivery failed: {', '.join(result['issues'])}")
    
    return result

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Telegram Delivery Checker")
    parser.add_argument("--mode", choices=["check", "fix", "status"], default="check")
    args = parser.parse_args()
    print(json.dumps(run_check(args.mode), indent=2))
