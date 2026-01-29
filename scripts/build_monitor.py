#!/usr/bin/env python3
"""
CI/CD Build Failure Monitor
Automatically checks Gmail for build failure emails (Xcode Cloud, GitHub Actions, etc.),
parses error details, and outputs fix tasks for your AI to handle.

Setup:
  1. Install gog CLI: brew install steipete/tap/gogcli
  2. Auth: gog auth add YOUR_EMAIL --services gmail
  3. Set env vars below or edit defaults

Usage:
  python3 build_monitor.py              # Check for new failures
  python3 build_monitor.py --status     # Show monitoring status

Environment Variables:
  BUILD_MONITOR_EMAIL    - Gmail account to check (default: first gog account)
  BUILD_MONITOR_QUERY    - Gmail search query (default: Xcode Cloud failures)
  BUILD_MONITOR_STATE    - Path to state file (default: state/build_monitor_state.json)
"""

import subprocess
import json
import sys
import os
import re
import base64
from datetime import datetime, timezone
from pathlib import Path
from html.parser import HTMLParser

# ============================================================
# CONFIGURATION — edit these or set environment variables
# ============================================================
EMAIL_ACCOUNT = os.environ.get("BUILD_MONITOR_EMAIL", "")
SEARCH_QUERY = os.environ.get(
    "BUILD_MONITOR_QUERY",
    'from:noreply@apple.com subject:"failed" newer_than:1d'
)
STATE_FILE = Path(os.environ.get(
    "BUILD_MONITOR_STATE",
    str(Path.home() / "clawd" / "state" / "build_monitor_state.json")
))
MAX_AUTO_FIX_ATTEMPTS = 2  # Don't infinite loop on the same error


class BuildEmailParser(HTMLParser):
    """Parse CI/CD email HTML to extract build errors.
    Works with Xcode Cloud emails. Extend for GitHub Actions, etc."""

    def __init__(self):
        super().__init__()
        self.errors = []
        self.current_file = None
        self.current_message = None
        self.in_message = False
        self.in_issue_path = False
        self.in_commit_message = False
        self.commit_message = None
        self.capture_text = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "x-issuepath":
            self.in_issue_path = True
            self.capture_text = ""
        elif tag == "x-commitmessage":
            self.in_commit_message = True
            self.capture_text = ""
        elif tag == "div":
            classes = attrs_dict.get("class", "")
            if "message" in classes:
                self.in_message = True
                self.capture_text = ""

    def handle_endtag(self, tag):
        if tag == "x-issuepath":
            self.in_issue_path = False
            self.current_file = self.capture_text.strip()
        elif tag == "x-commitmessage":
            self.in_commit_message = False
            self.commit_message = self.capture_text.strip()
        elif tag == "div" and self.in_message:
            self.in_message = False
            self.current_message = self.capture_text.strip()
            if self.current_file and self.current_message:
                self.errors.append({
                    "file": self.current_file,
                    "message": self.current_message
                })
                self.current_file = None
                self.current_message = None

    def handle_data(self, data):
        if self.in_issue_path or self.in_message or self.in_commit_message:
            self.capture_text += data


def load_state():
    """Load the monitor state file."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "lastChecked": None,
        "lastBuildId": None,
        "knownErrors": [],
        "fixAttempts": 0,
        "consecutiveFailures": 0,
    }


def save_state(state):
    """Save monitor state."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)


def search_failure_emails(max_results=5):
    """Search Gmail for recent build failure emails."""
    cmd = ["gog", "gmail", "search", SEARCH_QUERY,
           "--max", str(max_results), "--json"]
    if EMAIL_ACCOUNT:
        cmd += ["--account", EMAIL_ACCOUNT]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return {"error": result.stderr}
        data = json.loads(result.stdout)
        return data.get("threads", [])
    except Exception as e:
        return {"error": str(e)}


def get_email_body(thread_id):
    """Fetch full email body and parse errors."""
    cmd = ["gog", "gmail", "read", "get", thread_id, "--full", "--json"]
    if EMAIL_ACCOUNT:
        cmd += ["--account", EMAIL_ACCOUNT]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        thread = data.get("thread", {})
        messages = thread.get("messages", [])
        if not messages:
            return None

        msg = messages[0]
        snippet = msg.get("snippet", "")

        # Parse HTML body for detailed errors
        payload = msg.get("payload", {})
        parts = payload.get("parts", [])
        html_body = None
        for part in parts:
            if part.get("mimeType") == "text/html":
                body_data = part.get("body", {}).get("data", "")
                if body_data:
                    html_body = base64.urlsafe_b64decode(body_data + "==").decode("utf-8", errors="replace")
                break

        errors = []
        commit_msg = None
        if html_body:
            parser = BuildEmailParser()
            parser.feed(html_body)
            errors = parser.errors
            commit_msg = parser.commit_message

        return {
            "snippet": snippet,
            "errors": errors,
            "commit_message": commit_msg,
        }
    except Exception as e:
        return {"error": str(e)}


def extract_relative_path(full_path):
    """Convert CI absolute path to project-relative path."""
    # Xcode Cloud format
    prefix = "file:///Volumes/workspace/repository/"
    if full_path.startswith(prefix):
        return full_path[len(prefix):]
    # GitHub Actions format
    prefix2 = "/home/runner/work/"
    if full_path.startswith(prefix2):
        parts = full_path[len(prefix2):].split("/", 2)
        return parts[-1] if len(parts) > 2 else full_path
    return full_path


def format_fix_task(errors, project_root="YOUR_PROJECT_PATH"):
    """Format errors into a fix task for the AI agent."""
    if not errors:
        return None
    lines = ["Fix the following CI/CD build errors:\n"]
    for i, err in enumerate(errors, 1):
        rel_path = extract_relative_path(err["file"])
        line_match = re.search(r'\((\d+)\)$', err["message"])
        line_num = f" (line {line_match.group(1)})" if line_match else ""
        lines.append(f"{i}. **{rel_path}**{line_num}")
        lines.append(f"   Error: {err['message']}")
        lines.append("")
    lines.append(f"\nProject root: {project_root}")
    lines.append("After fixing: git add -A && git commit -m 'fix: resolve CI build errors' && git push")
    return "\n".join(lines)


def check_for_failures():
    """Main check: look for new build failures and return structured result."""
    state = load_state()
    threads = search_failure_emails()

    if isinstance(threads, dict) and "error" in threads:
        return {"status": "error", "message": threads["error"], "has_failures": False}

    if not threads:
        return {"status": "ok", "has_failures": False}

    latest = threads[0]
    latest_id = latest.get("id", "")
    latest_subject = latest.get("subject", "")

    # Already processed this exact build?
    if latest_id == state.get("lastBuildId"):
        return {"status": "ok", "has_failures": False, "already_handled": True}

    # Parse errors
    email_data = get_email_body(latest_id)
    if not email_data or "error" in email_data:
        return {"status": "error", "message": f"Failed to read email: {email_data}", "has_failures": False}

    errors = email_data.get("errors", [])
    error_sigs = [f"{e['file']}:{e['message']}" for e in errors]
    known_sigs = state.get("knownErrors", [])
    is_repeat = set(error_sigs) == set(known_sigs) if known_sigs else False

    # Update state
    state["lastChecked"] = datetime.now(timezone.utc).isoformat()
    state["lastBuildId"] = latest_id
    state["knownErrors"] = error_sigs
    if is_repeat:
        state["fixAttempts"] = state.get("fixAttempts", 0) + 1
    else:
        state["fixAttempts"] = 0
    state["consecutiveFailures"] = state.get("consecutiveFailures", 0) + 1
    save_state(state)

    return {
        "status": "failure_detected",
        "has_failures": True,
        "is_repeat": is_repeat,
        "fix_attempts": state["fixAttempts"],
        "should_auto_fix": not is_repeat or state["fixAttempts"] < MAX_AUTO_FIX_ATTEMPTS,
        "build_subject": latest_subject,
        "error_count": len(errors),
        "errors": errors,
        "fix_task": format_fix_task(errors),
    }


if __name__ == "__main__":
    if "--status" in sys.argv:
        state = load_state()
        print("=== Build Monitor Status ===")
        print(f"Last checked: {state.get('lastChecked', 'never')}")
        print(f"Consecutive failures: {state.get('consecutiveFailures', 0)}")
        print(f"Fix attempts on current error: {state.get('fixAttempts', 0)}")
        print(f"Known errors: {len(state.get('knownErrors', []))}")
    else:
        result = check_for_failures()
        print(json.dumps(result, indent=2, default=str))
