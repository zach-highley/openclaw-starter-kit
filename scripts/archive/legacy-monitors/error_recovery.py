#!/usr/bin/env python3
"""error_recovery.py — lightweight, pattern-based self-healing.

This script scans ~/.openclaw/logs/gateway.err.log for common failure patterns and
suggests (or applies) safe recovery actions.

Important:
- It must NEVER hardcode tokens.
- It should only auto-apply fixes that are safe and reversible.

Usage:
  python3 scripts/error_recovery.py
  python3 scripts/error_recovery.py --json
  python3 scripts/error_recovery.py --auto   # apply safe fixes

Workspace:
  Defaults to parent directory of this script's folder.
  Override with OPENCLAW_WORKSPACE=/path/to/workspace.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def workspace_root() -> Path:
    raw = os.environ.get("OPENCLAW_WORKSPACE")
    if raw:
        return Path(raw).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


WORKSPACE = workspace_root()
STATE_DIR = WORKSPACE / "state"
LOG_DIR = Path.home() / ".openclaw" / "logs"
ERR_LOG = LOG_DIR / "gateway.err.log"
STATE_FILE = STATE_DIR / "recovery_state.json"


Error = Dict[str, Any]


ERROR_PATTERNS: List[Dict[str, Any]] = [
    {
        "name": "llm_timeout",
        "regex": r"embedded run timeout.*timeoutMs=(\d+)",
        "severity": "warning",
        "auto_fixable": True,
        "fix": "ensure_ollama_running",
        "description": "An LLM call exceeded the configured timeout.",
    },
    {
        "name": "rate_limit_429",
        "regex": r"\b429\b",
        "severity": "warning",
        "auto_fixable": False,
        "fix": None,
        "description": "Rate limiting detected (HTTP 429). Consider reducing frequency or adding backoff.",
    },
    {
        "name": "unknown_model",
        "regex": r"Unknown model: ([^\s]+)",
        "severity": "critical",
        "auto_fixable": False,
        "fix": None,
        "description": "A configured model name is not available. Fix your OpenClaw config.",
    },
    {
        "name": "file_not_found",
        "regex": r"ENOENT: no such file or directory",
        "severity": "error",
        "auto_fixable": False,
        "fix": None,
        "description": "A file path was referenced but does not exist.",
    },
]


def load_state() -> Dict[str, Any]:
    try:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text())
    except Exception:
        pass
    return {
        "created": datetime.now(timezone.utc).isoformat(),
        "last_scan": None,
        "patterns_seen": {},
        "fixes_applied": [],
    }


def save_state(state: Dict[str, Any]) -> None:
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        state["last_updated"] = datetime.now(timezone.utc).isoformat()
        STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")
    except Exception:
        pass


def scan_errors(minutes: int = 60, max_lines: int = 800) -> List[Error]:
    if not ERR_LOG.exists():
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)

    try:
        lines = ERR_LOG.read_text(errors="ignore").splitlines()[-max_lines:]
    except Exception:
        return []

    out: List[Error] = []

    for line in lines:
        if not line.strip():
            continue

        # Parse ISO timestamp prefix
        ts_match = re.match(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})", line)
        if not ts_match:
            continue
        try:
            ts = datetime.fromisoformat(ts_match.group(1) + "+00:00")
        except Exception:
            continue
        if ts < cutoff:
            continue

        for p in ERROR_PATTERNS:
            m = re.search(p["regex"], line)
            if m:
                out.append(
                    {
                        "timestamp": ts.isoformat(),
                        "pattern": p["name"],
                        "severity": p["severity"],
                        "auto_fixable": bool(p.get("auto_fixable")),
                        "fix": p.get("fix"),
                        "description": p.get("description"),
                        "match": m.group(0)[:160],
                        "groups": list(m.groups()),
                    }
                )
                break

    return out


def aggregate(errors: List[Error]) -> Dict[str, Any]:
    agg: Dict[str, Any] = {}
    for e in errors:
        k = e["pattern"]
        agg.setdefault(
            k,
            {
                "count": 0,
                "severity": e["severity"],
                "auto_fixable": e["auto_fixable"],
                "fix": e.get("fix"),
                "description": e.get("description"),
                "samples": [],
                "first_seen": e["timestamp"],
                "last_seen": e["timestamp"],
            },
        )
        agg[k]["count"] += 1
        agg[k]["last_seen"] = e["timestamp"]
        if len(agg[k]["samples"]) < 3:
            agg[k]["samples"].append(e["match"])
    return agg


def ensure_ollama_running() -> Tuple[bool, str]:
    """Safe fix: make sure a local fallback exists if you use Ollama."""
    try:
        p = subprocess.run(["pgrep", "-x", "ollama"], capture_output=True)
        if p.returncode == 0:
            return True, "Ollama already running"
        # Best-effort start; if ollama isn't installed, this will fail cleanly.
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, "Started ollama serve"
    except FileNotFoundError:
        return False, "ollama not installed"
    except Exception as e:
        return False, str(e)


FIX_FUNCTIONS = {
    "ensure_ollama_running": ensure_ollama_running,
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--auto", action="store_true", help="apply safe fixes")
    ap.add_argument("--minutes", type=int, default=60)
    args = ap.parse_args()

    state = load_state()
    errs = scan_errors(minutes=max(1, args.minutes))
    agg = aggregate(errs)

    fixes_applied: List[Dict[str, Any]] = []
    if args.auto:
        for name, info in agg.items():
            if not info.get("auto_fixable"):
                continue
            fix_name = info.get("fix")
            fn = FIX_FUNCTIONS.get(fix_name)
            if not fn:
                continue
            ok, msg = fn()
            fixes_applied.append({"pattern": name, "fix": fix_name, "ok": ok, "message": msg})

    # Update state
    state["last_scan"] = datetime.now(timezone.utc).isoformat()
    seen = state.get("patterns_seen", {})
    for k, v in agg.items():
        seen[k] = {"count": int(v.get("count", 0)), "last_seen": v.get("last_seen")}
    state["patterns_seen"] = seen
    if fixes_applied:
        state.setdefault("fixes_applied", []).extend(fixes_applied)
    save_state(state)

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "errors_found": len(errs),
        "aggregated": agg,
        "fixes_applied": fixes_applied,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        if not agg:
            print("Error recovery: no recent errors detected")
        else:
            print("Error recovery: recent patterns:")
            for k, v in agg.items():
                print(f"- {k}: {v['count']} ({v['severity']})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
