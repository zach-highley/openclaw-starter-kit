#!/usr/bin/env python3
"""Optional weekly cleanup helper (safe defaults).

This starter-kit version is *workspace-scoped* on purpose:
- No sudo.
- No deletion outside the current repo/workspace.
- Defaults to dry-run unless --apply is passed.

What it can do:
- Run `brew cleanup` (optional; only if brew is installed)
- Delete old *.log files under the current directory (opt-in, time-gated)

Examples:
  python3 scripts/auto_cleanup.py                 # dry-run
  python3 scripts/auto_cleanup.py --apply         # apply cleanup
  python3 scripts/auto_cleanup.py --apply --json
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import time
from pathlib import Path


def run(cmd: list[str]) -> tuple[int, str]:
    cp = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return cp.returncode, cp.stdout


def list_old_logs(root: Path, *, older_than_days: int) -> list[Path]:
    cutoff = time.time() - older_than_days * 86400
    out: list[Path] = []
    for p in root.rglob("*.log"):
        try:
            st = p.stat()
        except FileNotFoundError:
            continue
        if st.st_mtime < cutoff:
            out.append(p)
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="Weekly cleanup helper (workspace-scoped, safe)")
    ap.add_argument("--apply", action="store_true", help="Actually delete files / run cleanup (default: dry-run)")
    ap.add_argument("--json", action="store_true", help="Emit JSON summary")
    ap.add_argument("--older-than-days", type=int, default=14, help="Only delete *.log older than N days")
    ap.add_argument(
        "--no-brew",
        action="store_true",
        help="Skip `brew cleanup` even if brew is installed",
    )
    args = ap.parse_args()

    root = Path.cwd()
    result: dict = {
        "ok": True,
        "applied": bool(args.apply),
        "cwd": str(root),
        "timestamp": int(time.time()),
        "removed": [],
        "steps": [],
    }

    # Optional: Homebrew cleanup
    brew = None if args.no_brew else shutil.which("brew")
    if brew:
        cmd = [brew, "cleanup"]
        if not args.apply:
            result["steps"].append({"cmd": " ".join(cmd), "dry_run": True})
        else:
            code, out = run(cmd)
            result["steps"].append({"cmd": " ".join(cmd), "exitCode": code, "outputTail": out[-4000:]})
            if code != 0:
                result["ok"] = False

    # Workspace logs cleanup
    old_logs = list_old_logs(root, older_than_days=args.older_than_days)
    if not args.apply:
        result["steps"].append(
            {
                "action": "delete_old_logs",
                "dry_run": True,
                "older_than_days": args.older_than_days,
                "count": len(old_logs),
            }
        )
    else:
        for p in old_logs:
            try:
                p.unlink()
                result["removed"].append(str(p))
            except Exception as e:
                result["ok"] = False
                result["steps"].append({"action": "unlink", "path": str(p), "error": str(e)})

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        if not args.apply:
            print("[dry-run] auto_cleanup summary")
        else:
            print("auto_cleanup complete")
        for s in result["steps"]:
            if s.get("cmd"):
                print("-", s["cmd"], "(dry-run)" if s.get("dry_run") else f"(exit {s.get('exitCode')})")
            elif s.get("action") == "delete_old_logs":
                print(f"- Would delete {s['count']} *.log files older than {s['older_than_days']} days")
        if args.apply and result["removed"]:
            print(f"Removed {len(result['removed'])} log file(s).")

    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
