#!/usr/bin/env python3
"""Minimal, safe "autofix" helper for the GitHub issue triage bot.

This is intentionally simple:
- Replaces a known typo in a single file.
- Defaults to dry-run unless --apply is passed.

Why this exists:
- The issue triage bot supports label-driven autofix rules.
- Examples in docs and config-examples should reference real files in this repo.

Usage:
  python3 scripts/fix_readme_typo.py --path README.md --old 'teh' --new 'the' --apply

Notes:
- If no changes are needed, exits 0 and prints a message.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description="Replace a known typo in a file (safe helper)")
    ap.add_argument("--path", type=Path, default=Path("README.md"), help="File to edit (default: README.md)")
    ap.add_argument("--old", required=True, help="Literal text (or regex when --regex) to replace")
    ap.add_argument("--new", required=True, help="Replacement text")
    ap.add_argument("--regex", action="store_true", help="Treat --old as a regular expression")
    ap.add_argument("--apply", action="store_true", help="Actually write changes (default: dry-run)")

    args = ap.parse_args()

    path: Path = args.path
    if not path.exists():
        raise SystemExit(f"File not found: {path}")

    before = path.read_text(encoding="utf-8")

    if args.regex:
        after, n = re.subn(args.old, args.new, before)
    else:
        n = before.count(args.old)
        after = before.replace(args.old, args.new)

    if n == 0:
        print(f"No matches for {args.old!r} in {path}. Nothing to do.")
        return 0

    if not args.apply:
        print(f"[dry-run] Would replace {n} occurrence(s) in {path}: {args.old!r} -> {args.new!r}")
        return 0

    path.write_text(after, encoding="utf-8")
    print(f"Updated {path}: replaced {n} occurrence(s) ({args.old!r} -> {args.new!r}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
