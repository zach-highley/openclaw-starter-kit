#!/usr/bin/env python3
"""pipeline_health.py — quick health checks for the *whole* OpenClaw pipeline.

This is intentionally lightweight and safe to run frequently.

Checks (best-effort):
- Workspace context files exist + are non-empty (AGENTS.md, SOUL.md, ...)
- Recent gateway errors (from ~/.openclaw/logs/gateway.err.log)
- Telegram API reachability (HEAD https://api.telegram.org)
- Optional: Ollama process running (as a local fallback)

Usage:
  python3 scripts/pipeline_health.py
  python3 scripts/pipeline_health.py --json
  python3 scripts/pipeline_health.py --quick

Workspace:
  Defaults to parent directory of this script's folder.
  Override with OPENCLAW_WORKSPACE=/path/to/workspace.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List


def workspace_root() -> Path:
    raw = os.environ.get("OPENCLAW_WORKSPACE")
    if raw:
        return Path(raw).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


WORKSPACE = workspace_root()
LOG_DIR = Path.home() / ".openclaw" / "logs"
GATEWAY_ERR = LOG_DIR / "gateway.err.log"


CONTEXT_FILES = [
    "AGENTS.md",
    "SOUL.md",
    "USER.md",
    "SECURITY.md",
    "HEARTBEAT.md",
]


def check_context_files() -> Dict[str, Any]:
    res: Dict[str, Any] = {
        "status": "healthy",
        "files_ok": [],
        "files_missing": [],
        "files_empty": [],
        "files_too_large": [],
    }

    for name in CONTEXT_FILES:
        p = WORKSPACE / name
        if not p.exists():
            res["files_missing"].append(name)
            res["status"] = "warning"
            continue
        try:
            size = p.stat().st_size
            if size == 0:
                res["files_empty"].append(name)
                res["status"] = "warning"
            elif size > 150_000:
                res["files_too_large"].append({"file": name, "kb": int(size / 1024)})
                res["status"] = "warning"
            else:
                res["files_ok"].append(name)
        except Exception:
            res["status"] = "warning"

    if "AGENTS.md" in res["files_missing"] or "SOUL.md" in res["files_missing"]:
        res["status"] = "critical"

    return res


def _tail(path: Path, n: int) -> str:
    try:
        out = subprocess.run(["tail", f"-{n}", str(path)], capture_output=True, text=True)
        return (out.stdout or "").strip()
    except Exception:
        return ""


def check_recent_gateway_errors(minutes: int = 30) -> Dict[str, Any]:
    res: Dict[str, Any] = {
        "status": "healthy",
        "period_minutes": minutes,
        "counts": {"timeouts": 0, "telegram": 0, "model": 0, "tool": 0, "other": 0},
        "samples": [],
    }

    if not GATEWAY_ERR.exists():
        res["note"] = "no gateway.err.log found"
        return res

    cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    lines = _tail(GATEWAY_ERR, 600).splitlines()

    for line in lines:
        if not line.strip():
            continue
        # Expect ISO timestamps like 2026-01-28T13:05:58.256Z ...
        ts_str = line[:30]
        if "T" not in ts_str or "Z" not in ts_str:
            continue
        try:
            ts = datetime.fromisoformat(ts_str[:24].replace("Z", "+00:00"))
        except Exception:
            continue
        if ts < cutoff:
            continue

        low = line.lower()
        bucket = "other"
        if "timeout" in low:
            bucket = "timeouts"
        elif "telegram" in low and ("error" in low or "fail" in low):
            bucket = "telegram"
        elif "model" in low and "error" in low:
            bucket = "model"
        elif "tool" in low and ("error" in low or "fail" in low):
            bucket = "tool"

        res["counts"][bucket] += 1
        if len(res["samples"]) < 3 and bucket in ("telegram", "model"):
            res["samples"].append(line[:160])

    real = res["counts"]["telegram"] + res["counts"]["model"]
    total = sum(res["counts"].values())

    if real > 10 or total > 80:
        res["status"] = "critical"
    elif real > 3 or total > 30:
        res["status"] = "warning"

    return res


def check_telegram_api() -> Dict[str, Any]:
    import time
    import urllib.request

    res: Dict[str, Any] = {"status": "healthy", "reachable": False, "latency_ms": None}

    try:
        start = time.time()
        req = urllib.request.Request("https://api.telegram.org", method="HEAD")
        urllib.request.urlopen(req, timeout=10)
        ms = (time.time() - start) * 1000
        res["reachable"] = True
        res["latency_ms"] = round(ms, 2)
        if ms > 2000:
            res["status"] = "warning"
    except Exception as e:
        res["status"] = "critical"
        res["error"] = str(e)

    return res


def check_ollama() -> Dict[str, Any]:
    res: Dict[str, Any] = {"status": "unknown", "running": False}
    try:
        p = subprocess.run(["pgrep", "-x", "ollama"], capture_output=True)
        res["running"] = p.returncode == 0
        res["status"] = "healthy" if res["running"] else "offline"
    except Exception as e:
        res["status"] = "error"
        res["error"] = str(e)
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quick", action="store_true", help="skip log scanning")
    args = ap.parse_args()

    checks: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "context": check_context_files(),
        "telegram": check_telegram_api(),
        "ollama": check_ollama(),
    }

    if not args.quick:
        checks["gateway_errors"] = check_recent_gateway_errors(minutes=30)

    # Overall status
    statuses = []
    for k, v in checks.items():
        if isinstance(v, dict) and "status" in v:
            statuses.append(v["status"])
    if "critical" in statuses:
        checks["status"] = "critical"
    elif "warning" in statuses:
        checks["status"] = "warning"
    else:
        checks["status"] = "healthy"

    if args.json:
        print(json.dumps(checks, indent=2))
    else:
        print(f"Pipeline health: {checks['status']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
