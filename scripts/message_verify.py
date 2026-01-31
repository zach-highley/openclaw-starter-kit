#!/usr/bin/env python3
"""
OpenClaw Message Delivery Verifier — check Telegram connectivity.

Reads the Telegram bot token from the OpenClaw config and verifies that
messages can be sent.  Tracks message_id sequences to detect delivery
gaps (missed messages).

Data source:
    ~/.openclaw/openclaw.json  →  channels.telegram.botToken
                                   channels.telegram.allowFrom[0]  (chat_id)

State file:
    $WORKSPACE/state/message_verify_state.json

Output modes:
    (default)  human-readable summary
    --json     machine-readable JSON

Usage:
    python3 message_verify.py                # human summary
    python3 message_verify.py --json         # JSON output
    python3 message_verify.py --dry-run      # check config without sending
    python3 message_verify.py --help         # this text

Environment:
    MESSAGE_VERIFY_CHAT_ID    Override chat_id from config

Requires: Python 3.9+
No external dependencies (uses stdlib urllib).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------

DEFAULT_CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"
TELEGRAM_API = "https://api.telegram.org"

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
STATE_FILE = WORKSPACE / "state" / "message_verify_state.json"

# ---------------------------------------------------------------
# JSON / config helpers
# ---------------------------------------------------------------

def load_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def get_bot_token(config: Optional[Dict[str, Any]]) -> Optional[str]:
    """Extract channels.telegram.botToken from config."""
    if config is None:
        return None
    try:
        return config["channels"]["telegram"]["botToken"]
    except (KeyError, TypeError):
        return None


def get_chat_id(config: Optional[Dict[str, Any]]) -> Optional[str]:
    """Get chat_id from env override or config's allowFrom list."""
    env_id = os.environ.get("MESSAGE_VERIFY_CHAT_ID")
    if env_id:
        return env_id
    if config is None:
        return None
    try:
        allow_from = config["channels"]["telegram"]["allowFrom"]
        if isinstance(allow_from, list) and len(allow_from) > 0:
            return str(allow_from[0])
    except (KeyError, TypeError):
        pass
    return None

# ---------------------------------------------------------------
# Telegram API (stdlib only — no requests dependency)
# ---------------------------------------------------------------

def telegram_request(
    bot_token: str,
    method: str,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """Make a Telegram Bot API request using urllib."""
    url = f"{TELEGRAM_API}/bot{bot_token}/{method}"
    data = urllib.parse.urlencode(params or {}).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def check_bot_reachable(bot_token: str) -> Dict[str, Any]:
    """Call getMe to verify the token is valid and the bot is reachable."""
    try:
        result = telegram_request(bot_token, "getMe")
        return {
            "reachable": result.get("ok", False),
            "bot_username": result.get("result", {}).get("username", "unknown"),
            "error": None,
        }
    except Exception as exc:
        return {"reachable": False, "bot_username": None, "error": str(exc)}


def check_chat_reachable(bot_token: str, chat_id: str) -> Dict[str, Any]:
    """Call getChat to verify the chat_id is accessible."""
    try:
        result = telegram_request(bot_token, "getChat", {"chat_id": chat_id})
        chat = result.get("result", {})
        return {
            "reachable": result.get("ok", False),
            "chat_type": chat.get("type", "unknown"),
            "chat_title": chat.get("title") or chat.get("first_name") or "unknown",
            "error": None,
        }
    except Exception as exc:
        return {"reachable": False, "chat_type": None, "chat_title": None, "error": str(exc)}


def send_verify_ping(bot_token: str, chat_id: str) -> Dict[str, Any]:
    """Send a verification ping and return the message_id."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    text = f"🔍 OpenClaw message verify ping — {ts}"
    try:
        result = telegram_request(
            bot_token,
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": text,
                "disable_notification": "true",
            },
        )
        msg = result.get("result", {})
        return {
            "sent": result.get("ok", False),
            "message_id": msg.get("message_id"),
            "error": None,
        }
    except Exception as exc:
        return {"sent": False, "message_id": None, "error": str(exc)}

# ---------------------------------------------------------------
# State tracking (message_id gap detection)
# ---------------------------------------------------------------

def load_state() -> Dict[str, Any]:
    state = load_json(STATE_FILE)
    if state and isinstance(state, dict):
        return state
    return {"message_ids": [], "gaps": [], "last_check": None, "total_pings": 0}


def save_state(state: Dict[str, Any]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def record_message_id(state: Dict[str, Any], msg_id: Optional[int]) -> List[Dict[str, Any]]:
    """
    Record a message_id and detect gaps.

    Returns a list of new gaps found (each gap is a dict with from/to/size).
    Note: Telegram message_ids are per-chat and increment.  Gaps may indicate
    messages from other sources, not necessarily lost messages.
    """
    if msg_id is None:
        return []

    ids: List[int] = state.get("message_ids", [])
    new_gaps: List[Dict[str, Any]] = []

    if ids:
        last = ids[-1]
        diff = msg_id - last
        if diff > 1:
            gap = {
                "after_id": last,
                "before_id": msg_id,
                "size": diff - 1,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            new_gaps.append(gap)
            state.setdefault("gaps", []).append(gap)

    # Keep only last 50 IDs to bound state size
    ids.append(msg_id)
    state["message_ids"] = ids[-50:]
    state["total_pings"] = state.get("total_pings", 0) + 1

    return new_gaps

# ---------------------------------------------------------------
# Output — JSON
# ---------------------------------------------------------------

def output_json(report: Dict[str, Any]) -> None:
    print(json.dumps(report, indent=2))

# ---------------------------------------------------------------
# Output — Human
# ---------------------------------------------------------------

def output_human(report: Dict[str, Any]) -> None:
    print("═══════════════════════════════════════")
    print("  OpenClaw Message Delivery Verifier")
    print("═══════════════════════════════════════")
    print()

    # Bot status
    bot = report.get("bot", {})
    if bot.get("reachable"):
        print(f"  🤖 Bot: @{bot.get('bot_username', '?')} — reachable ✅")
    else:
        print(f"  🤖 Bot: NOT reachable ❌")
        if bot.get("error"):
            print(f"     Error: {bot['error']}")

    # Chat status
    chat = report.get("chat", {})
    if chat.get("reachable"):
        label = chat.get("chat_title", "?")
        ctype = chat.get("chat_type", "?")
        print(f"  💬 Chat: {label} ({ctype}) — reachable ✅")
    elif chat.get("error"):
        print(f"  💬 Chat: NOT reachable ❌ — {chat['error']}")
    elif report.get("chat_id_missing"):
        print(f"  💬 Chat: no chat_id configured (set MESSAGE_VERIFY_CHAT_ID or allowFrom)")

    # Ping result
    ping = report.get("ping", {})
    if ping.get("sent"):
        print(f"  📨 Ping: sent (message_id={ping.get('message_id')})")
    elif ping.get("dry_run"):
        print(f"  📨 Ping: dry run (no message sent)")
    elif ping.get("error"):
        print(f"  📨 Ping: FAILED — {ping['error']}")

    # Gap detection
    gaps = report.get("new_gaps", [])
    total_gaps = report.get("total_gaps", 0)
    if gaps:
        print()
        print(f"  ⚠️  {len(gaps)} new message gap(s) detected:")
        for g in gaps:
            print(f"     IDs {g['after_id']}→{g['before_id']} ({g['size']} missing)")
    elif total_gaps > 0:
        print(f"  📊 Historical gaps: {total_gaps} (none new)")
    else:
        print(f"  📊 No message gaps detected")

    print()
    print("═══════════════════════════════════════")

# ---------------------------------------------------------------
# CLI
# ---------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify OpenClaw Telegram message delivery and detect gaps.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  python3 message_verify.py                  # human-readable
  python3 message_verify.py --json           # JSON output
  python3 message_verify.py --dry-run        # check connectivity only, don't send ping
  MESSAGE_VERIFY_CHAT_ID=12345 python3 message_verify.py

State: $WORKSPACE/state/message_verify_state.json
""",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Machine-readable JSON output.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check bot/chat reachability without sending a ping message.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help=f"Path to openclaw.json (default: {DEFAULT_CONFIG_PATH})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    config = load_json(args.config)
    bot_token = get_bot_token(config)
    chat_id = get_chat_id(config)

    report: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "config_path": str(args.config),
        "bot": {},
        "chat": {},
        "ping": {},
        "new_gaps": [],
        "total_gaps": 0,
        "chat_id_missing": False,
    }

    # Check 1: Is the bot token configured & valid?
    if not bot_token:
        report["bot"] = {"reachable": False, "error": "No botToken found in config"}
        if args.json_output:
            output_json(report)
        else:
            output_human(report)
        sys.exit(2)

    report["bot"] = check_bot_reachable(bot_token)

    # Check 2: Is the chat reachable?
    if not chat_id:
        report["chat_id_missing"] = True
    else:
        report["chat"] = check_chat_reachable(bot_token, chat_id)

    # Check 3: Send a verification ping (unless --dry-run)
    state = load_state()

    if args.dry_run:
        report["ping"] = {"dry_run": True, "sent": False}
    elif chat_id and report["bot"].get("reachable"):
        ping_result = send_verify_ping(bot_token, chat_id)
        report["ping"] = ping_result

        if ping_result.get("sent"):
            new_gaps = record_message_id(state, ping_result.get("message_id"))
            report["new_gaps"] = new_gaps
    else:
        report["ping"] = {"sent": False, "error": "Bot or chat not reachable"}

    report["total_gaps"] = len(state.get("gaps", []))

    state["last_check"] = datetime.now(timezone.utc).isoformat()
    save_state(state)

    # Output
    if args.json_output:
        output_json(report)
    else:
        output_human(report)

    # Exit code: 0 = all good, 1 = gaps detected, 2 = config/connectivity issue
    if not report["bot"].get("reachable"):
        sys.exit(2)
    if report["new_gaps"]:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
