#!/usr/bin/env python3
"""auto_doctor.py — Autonomous health checks + (optional) safe fixes.

This script is designed to be run by cron/launchd/heartbeat.
It validates that your OpenClaw gateway + your "watchers" are healthy, and writes a
machine-readable report to state/doctor_report.json.

Key goal: if something breaks at 3 AM, your system can diagnose and recover
without you touching the terminal.

Usage:
  python3 scripts/auto_doctor.py
  python3 scripts/auto_doctor.py --json
  python3 scripts/auto_doctor.py --fix
  python3 scripts/auto_doctor.py --save-state

Workspace:
  By default, the workspace root is the parent directory of this script's folder.
  Override with OPENCLAW_WORKSPACE=/path/to/workspace.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _workspace_root() -> Path:
    import os

    for k in ("OPENCLAW_WORKSPACE", "OPENCLAW_STARTER_WORKSPACE"):
        raw = os.environ.get(k)
        if raw:
            return Path(raw).expanduser().resolve()

    # If this file is at <workspace>/scripts/auto_doctor.py, parents[1] is <workspace>/.
    return Path(__file__).resolve().parents[1]


WORKSPACE = _workspace_root()
SCRIPTS_DIR = WORKSPACE / "scripts"
STATE_DIR = WORKSPACE / "state"
MEMORY_DIR = WORKSPACE / "memory"


def run_cmd(cmd: List[str], timeout_s: int = 20) -> Dict[str, Any]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)
        return {
            "ok": p.returncode == 0,
            "returncode": p.returncode,
            "stdout": (p.stdout or "").strip(),
            "stderr": (p.stderr or "").strip(),
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "returncode": -1, "stdout": "", "stderr": "TIMEOUT"}
    except Exception as e:
        return {"ok": False, "returncode": -1, "stdout": "", "stderr": str(e)}


def run_py(script: str, args: Optional[List[str]] = None, timeout_s: int = 30) -> Dict[str, Any]:
    cmd = [sys.executable, str(SCRIPTS_DIR / script)]
    if args:
        cmd.extend(args)
    return run_cmd(cmd, timeout_s=timeout_s)


@dataclass
class CheckResult:
    name: str
    healthy: bool
    details: Dict[str, Any]


def check_openclaw_status() -> CheckResult:
    r = run_cmd(["openclaw", "status"], timeout_s=20)
    return CheckResult(
        name="openclaw",
        healthy=bool(r["ok"]),
        details={
            "returncode": r["returncode"],
            "stdout": r["stdout"][:800],
            "stderr": r["stderr"][:800],
        },
    )


def check_usage() -> CheckResult:
    r = run_py("check_usage.py", args=["--json"], timeout_s=35)
    if not r["ok"]:
        return CheckResult("usage", False, {"error": r["stderr"][:800]})
    try:
        data = json.loads(r["stdout"])
    except Exception:
        return CheckResult("usage", False, {"error": "non-json output", "raw": r["stdout"][:800]})

    ctx = (
        data.get("models", {})
        .get("claude", {})
        .get("context_pct")
    )
    return CheckResult(
        name="usage",
        healthy=True,
        details={
            "context_pct": ctx,
            "alerts": data.get("alerts", []),
        },
    )


def check_meta_monitor() -> CheckResult:
    if not (SCRIPTS_DIR / "meta_monitor.py").exists():
        return CheckResult("meta_monitor", True, {"note": "meta_monitor.py not installed"})
    r = run_py("meta_monitor.py", args=["--check", "--mode", "heartbeat"], timeout_s=45)
    out = r["stdout"] or ""
    broken = out.count("❌")
    stalled = out.count("⚠️")
    healthy = r["ok"] and broken == 0
    return CheckResult(
        name="meta_monitor",
        healthy=healthy,
        details={
            "broken": broken,
            "stalled": stalled,
            "stdout": out[:800],
            "stderr": r["stderr"][:400],
        },
    )


def check_security_hound() -> CheckResult:
    if not (SCRIPTS_DIR / "security_hound.py").exists():
        return CheckResult("security", True, {"note": "security_hound.py not installed"})
    r = run_py("security_hound.py", timeout_s=35)
    text = (r["stdout"] or "").lower()
    should_alert = "should_alert" in text and "true" in text
    return CheckResult(
        name="security",
        healthy=(r["ok"] and not should_alert),
        details={
            "should_alert": should_alert,
            "stdout": (r["stdout"] or "")[:600],
            "stderr": (r["stderr"] or "")[:300],
        },
    )


def check_git_clean() -> CheckResult:
    if not (WORKSPACE / ".git").exists():
        return CheckResult("git", True, {"note": "workspace is not a git repo"})
    r = run_cmd(["git", "-C", str(WORKSPACE), "status", "--porcelain"], timeout_s=15)
    lines = [l for l in (r["stdout"] or "").splitlines() if l.strip()]
    return CheckResult(
        name="git",
        healthy=True,
        details={
            "uncommitted_changes": len(lines),
            "sample": lines[:20],
        },
    )


def apply_safe_fixes(checks: List[CheckResult]) -> List[Dict[str, Any]]:
    fixes: List[Dict[str, Any]] = []

    mm = next((c for c in checks if c.name == "meta_monitor"), None)
    if mm and not mm.healthy and (SCRIPTS_DIR / "meta_monitor.py").exists():
        r = run_py("meta_monitor.py", args=["--check", "--mode", "fix"], timeout_s=90)
        fixes.append({"name": "meta_monitor_fix", "ok": r["ok"], "stdout": r["stdout"][:800], "stderr": r["stderr"][:300]})

    return fixes


def save_report(checks: List[CheckResult], fixes: List[Dict[str, Any]]) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    report = {
        "timestamp": now.isoformat(),
        "workspace": str(WORKSPACE),
        "overall_healthy": all(c.healthy for c in checks),
        "issues": [c.name for c in checks if not c.healthy],
        "checks": [
            {"name": c.name, "healthy": c.healthy, "details": c.details}
            for c in checks
        ],
        "fixes": fixes,
    }

    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        (STATE_DIR / "doctor_report.json").write_text(json.dumps(report, indent=2) + "\n")
    except Exception:
        pass

    # Optional lightweight memory append (if the user maintains memory/)
    try:
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        day = now.astimezone().strftime("%Y-%m-%d")
        mem = MEMORY_DIR / f"{day}.md"
        lines = ["", f"## Auto-Doctor Report ({now.astimezone().strftime('%H:%M %Z')})"]
        for c in checks:
            lines.append(f"- {'✅' if c.healthy else '❌'} **{c.name}**")
        if fixes:
            lines.append("- Fixes:")
            for f in fixes:
                lines.append(f"  - {'✅' if f.get('ok') else '❌'} {f.get('name')}")
        mem.write_text(mem.read_text() + "\n".join(lines) + "\n" if mem.exists() else "\n".join(lines) + "\n")
    except Exception:
        pass

    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="print JSON output")
    ap.add_argument("--fix", action="store_true", help="apply safe fixes (best-effort)")
    ap.add_argument("--save-state", action="store_true", help="write report to state/doctor_report.json")
    args = ap.parse_args()

    checks = [
        check_openclaw_status(),
        check_usage(),
        check_meta_monitor(),
        check_security_hound(),
        check_git_clean(),
    ]

    fixes: List[Dict[str, Any]] = []
    if args.fix:
        fixes = apply_safe_fixes(checks)

    report = save_report(checks, fixes) if args.save_state or args.fix else {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "overall_healthy": all(c.healthy for c in checks),
        "issues": [c.name for c in checks if not c.healthy],
        "checks": [{"name": c.name, "healthy": c.healthy, "details": c.details} for c in checks],
        "fixes": fixes,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Auto-Doctor: {'HEALTHY' if report['overall_healthy'] else 'ISSUES'}")
        if report["issues"]:
            print("Issues:", ", ".join(report["issues"]))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
