#!/usr/bin/env python3
"""meta_monitor.py — Watcher-of-watchers (minimal, schema-aligned).

This repo historically included a "meta monitor" concept, but the original
implementation drifted and became crash-prone.

This version is intentionally simple:
- Checks that the *other* automation scripts are updating their state files.
- Optionally attempts a safe fix by restarting the Gateway service.

It does NOT try to outsmart OpenClaw. Prefer built-ins:
- openclaw doctor
- openclaw gateway status / restart

Exit codes:
- 0: healthy
- 1: issues detected

Compatibility:
- Accepts legacy flags used by scripts/auto_doctor.py: --check --mode heartbeat
  ("mode" is ignored unless it is "check" or "fix").
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


def _workspace_root() -> Path:
    raw = os.environ.get("OPENCLAW_WORKSPACE") or os.environ.get("OPENCLAW_STARTER_WORKSPACE")
    if raw:
        return Path(raw).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


WORKSPACE = _workspace_root()


@dataclass
class SystemCheck:
    name: str
    path: Path
    threshold_seconds: int


def _age_seconds(path: Path) -> Optional[int]:
    if not path.exists():
        return None
    try:
        return int(time.time() - path.stat().st_mtime)
    except OSError:
        return None


def _run(cmd: List[str], timeout_s: int = 15) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)


def check_files(checks: List[SystemCheck]) -> List[str]:
    issues: List[str] = []
    for c in checks:
        age = _age_seconds(c.path)
        if age is None:
            # Missing state is "unknown" rather than failing hard; many users
            # won't install all scripts.
            continue
        if age > c.threshold_seconds:
            issues.append(f"{c.name} stalled (last update {age}s ago; threshold {c.threshold_seconds}s)")
    return issues


def check_gateway() -> Optional[str]:
    """Returns an issue string if gateway status fails, else None.

    We keep this intentionally weakly-coupled: if openclaw isn't installed or
    the command isn't available, we don't treat it as an issue.
    """

    try:
        p = _run(["openclaw", "gateway", "status", "--json"], timeout_s=15)
        if p.returncode != 0:
            return "gateway status probe failed"
        # Best-effort parse; schema may evolve.
        try:
            data = json.loads(p.stdout or "{}")
            # If the CLI surfaced an explicit unhealthy flag, respect it.
            if isinstance(data, dict):
                ok = data.get("ok")
                if ok is False:
                    return "gateway unhealthy"
        except Exception:
            pass
        return None
    except FileNotFoundError:
        return None
    except subprocess.TimeoutExpired:
        return "gateway status timed out"
    except Exception:
        return "gateway status error"


def try_fix(issues: List[str]) -> bool:
    """Safe-ish fix: restart gateway service."""
    if not issues:
        return True
    try:
        p = _run(["openclaw", "gateway", "restart"], timeout_s=60)
        return p.returncode == 0
    except Exception:
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Watcher-of-watchers")
    ap.add_argument("--check", action="store_true", help="run checks (default)")
    ap.add_argument("--fix", action="store_true", help="attempt safe fixes")

    # Legacy/compat flags. auto_doctor.py calls: --check --mode heartbeat
    ap.add_argument("--mode", default="check", help="legacy/compat; accepts check|fix or an ignored label")
    args = ap.parse_args()

    # Interpret legacy mode
    if args.mode == "fix":
        args.fix = True
    if not args.check and not args.fix:
        args.check = True

    checks = [
        SystemCheck(
            name="watchdog",
            path=Path.home() / ".openclaw" / "logs" / "watchdog-state.json",
            threshold_seconds=10 * 60,
        ),
        SystemCheck(
            name="auto_doctor",
            path=WORKSPACE / "state" / "doctor_report.json",
            threshold_seconds=6 * 60 * 60,
        ),
        SystemCheck(
            name="usage",
            path=WORKSPACE / "state" / "usage_state.json",
            threshold_seconds=2 * 60 * 60,
        ),
    ]

    issues = check_files(checks)

    gw_issue = check_gateway()
    if gw_issue:
        issues.append(gw_issue)

    if not issues:
        print("✅ All systems healthy")
        return 0

    print("⚠️ Issues detected:")
    for i in issues:
        # AutoDoctor counts these symbols.
        print(f"❌ {i}")

    if args.fix:
        print("🔧 Attempting safe fix: openclaw gateway restart")
        ok = try_fix(issues)
        print("✅ Fix applied" if ok else "⚠️ Fix failed")
        return 0 if ok else 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
