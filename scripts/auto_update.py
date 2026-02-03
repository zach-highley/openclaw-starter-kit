#!/usr/bin/env python3
"""Optional weekly package update helper (safe defaults).

This script is intentionally conservative:
- Defaults to dry-run unless --apply is passed.
- Only manages Homebrew updates (no sudo / no OS updates).

Examples:
  python3 scripts/auto_update.py            # dry-run
  python3 scripts/auto_update.py --apply    # run brew update/upgrade
  python3 scripts/auto_update.py --apply --json
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time


def run(cmd: list[str]) -> tuple[int, str]:
    cp = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return cp.returncode, cp.stdout


def main() -> int:
    ap = argparse.ArgumentParser(description="Weekly Homebrew update helper (safe)")
    ap.add_argument("--apply", action="store_true", help="Actually run commands (default: dry-run)")
    ap.add_argument("--json", action="store_true", help="Emit JSON summary")
    args = ap.parse_args()

    brew = shutil.which("brew")
    result: dict = {
        "ok": True,
        "applied": bool(args.apply),
        "timestamp": int(time.time()),
        "steps": [],
    }

    if not brew:
        result.update({"ok": True, "skipped": True, "reason": "brew not found"})
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print("brew not found; skipping auto_update.")
        return 0

    commands = [[brew, "update"], [brew, "upgrade"]]

    if not args.apply:
        result["steps"] = [{"cmd": " ".join(c), "dry_run": True} for c in commands]
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print("[dry-run] Would run:")
            for c in commands:
                print("-", " ".join(c))
        return 0

    for c in commands:
        code, out = run(c)
        step = {"cmd": " ".join(c), "exitCode": code}
        # Keep output bounded; these logs can be huge.
        step["outputTail"] = out[-4000:]
        result["steps"].append(step)
        if code != 0:
            result["ok"] = False

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("auto_update complete.")
        for s in result["steps"]:
            print(f"- {s['cmd']} (exit {s['exitCode']})")
            print(s.get("outputTail", "").rstrip())
            print()

    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
