#!/usr/bin/env python3
"""subagent_watcher.py — Detect completed background work after agent restarts.

Why this exists
--------------
In agentic systems, the most common "silent failure" is not a crash.
It's *missing a completion* because the orchestrator session restarted or
compacted and forgot what was running.

This script is an external enforcement layer. It does NOT rely on the agent's
memory. Instead, it uses an immutable audit trail (git commits) to detect new
work and deduplicate notifications.

What it does
------------
- Detects the workspace directory (OPENCLAW_WORKSPACE → ~/clawd → ~/.openclaw/workspace → cwd)
- Checks one or more git repos for commits in the last N minutes
- Deduplicates commits already reported via a state file
- Emits:
  - human-readable output (default)
  - JSON output (--json) suitable for heartbeat/cron automation

This is safe to run in a heartbeat because it is READ-ONLY.

Usage
-----
  python3 scripts/subagent_watcher.py
  python3 scripts/subagent_watcher.py --json
  python3 scripts/subagent_watcher.py --json --mark-reported

Optional env
------------
- OPENCLAW_WATCH_REPOS: comma-separated list of additional repo paths to scan
  Example:
    export OPENCLAW_WATCH_REPOS="$HOME/my-app,$HOME/another-repo"

State
-----
Writes to: <workspace>/state/subagent_watcher_state.json

Requires: Python 3.9+, git
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def detect_workspace() -> Path:
    env = os.environ.get("OPENCLAW_WORKSPACE")
    if env:
        return Path(env)
    for candidate in [Path.home() / "clawd", Path.home() / ".openclaw" / "workspace"]:
        if candidate.is_dir():
            return candidate
    return Path.cwd()


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def save_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def is_git_repo(p: Path) -> bool:
    return (p / ".git").exists()


def parse_repos(workspace: Path) -> List[Path]:
    repos: List[Path] = []
    if is_git_repo(workspace):
        repos.append(workspace)

    extra = os.environ.get("OPENCLAW_WATCH_REPOS", "").strip()
    if extra:
        for raw in extra.split(","):
            rp = Path(raw.strip()).expanduser()
            if rp.exists() and is_git_repo(rp):
                repos.append(rp)

    # Dedup
    seen = set()
    out: List[Path] = []
    for r in repos:
        key = str(r.resolve())
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def recent_commits(repo: Path, minutes: int) -> List[Dict[str, str]]:
    try:
        res = subprocess.run(
            [
                "git",
                "log",
                f"--since={minutes} minutes ago",
                "--format=%H|%s|%ai|%an",
            ],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if res.returncode != 0:
            return []
        commits: List[Dict[str, str]] = []
        for line in res.stdout.strip().split("\n"):
            if not line:
                continue
            h, subj, dt, author = (line.split("|", 3) + ["", "", "", ""])[:4]
            commits.append({
                "hash": h[:8],
                "subject": subj,
                "date": dt,
                "author": author,
            })
        return commits
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def main() -> None:
    ap = argparse.ArgumentParser(description="Detect new work via git commits, dedupe via state file.")
    ap.add_argument("--json", action="store_true", dest="json_output")
    ap.add_argument("--mark-reported", action="store_true")
    ap.add_argument("--lookback", type=int, default=60, help="Look back N minutes for commits (default: 60)")
    args = ap.parse_args()

    workspace = detect_workspace()
    state_path = workspace / "state" / "subagent_watcher_state.json"
    state = load_json(state_path) or {"reported": [], "last_check": None}
    reported: List[str] = state.get("reported", []) if isinstance(state.get("reported"), list) else []

    repos = parse_repos(workspace)
    found: List[Dict[str, Any]] = []

    for repo in repos:
        repo_name = repo.name
        for c in recent_commits(repo, args.lookback):
            cid = f"{repo_name}:{c['hash']}"
            if cid in reported:
                continue
            found.append({
                "repo": repo_name,
                "path": str(repo),
                "commit": c["hash"],
                "subject": c["subject"],
                "date": c["date"],
                "author": c["author"],
                "id": cid,
            })

    action_needed = bool(found)

    if args.mark_reported and found:
        for f in found:
            reported.append(f["id"])
        state["reported"] = reported[-500:]
        state["last_check"] = datetime.now(timezone.utc).isoformat()
        save_json(state_path, state)

    if args.json_output:
        msg = (
            f"{len(found)} new commit(s) detected" if found else "No new completions"
        )
        print(json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "workspace": str(workspace),
            "repos": [str(r) for r in repos],
            "action_needed": action_needed,
            "completions": found,
            "message": msg,
        }, indent=2))
        sys.exit(1 if action_needed else 0)

    if not found:
        print("✅ No new background completions detected.")
        sys.exit(0)

    print("🔔 Background completions detected:")
    for f in found:
        print(f"- [{f['repo']}] {f['commit']} {f['subject']}")
    sys.exit(1)


if __name__ == "__main__":
    main()
