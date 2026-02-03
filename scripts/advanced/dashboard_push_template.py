#!/usr/bin/env python3
"""dashboard_push_template.py

A minimal, public-safe example of pushing data from your OpenClaw workspace
into a personal dashboard.

This intentionally avoids:
- hardcoded URLs
- hardcoded tokens
- user-specific content

Configure via env vars:
- DASHBOARD_API_URL (e.g. https://dashboard.example.com/api/openclaw)
- DASHBOARD_API_TOKEN (bearer token or similar)

Usage:
  python3 scripts/advanced/dashboard_push_template.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen


def build_payload() -> dict:
    # Keep payload MECE and small. Treat this as an integration layer.
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": {
            "mode": "autonomous",
            "note": "Example payload from OpenClaw"
        },
        "work": {
            "focus": "Example: Weekly audit",
            "running": [],
            "next": [{"id": "TASK-001", "title": "Example task"}],
        },
    }


def post_json(url: str, token: str | None, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    with urlopen(req, timeout=20) as resp:
        body = resp.read().decode("utf-8")
        return {"status": resp.status, "body": body}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    url = os.environ.get("DASHBOARD_API_URL")
    token = os.environ.get("DASHBOARD_API_TOKEN")

    payload = build_payload()

    if args.dry_run:
        print(json.dumps(payload, indent=2))
        return 0

    if not url:
        print("Missing env var DASHBOARD_API_URL", file=sys.stderr)
        return 2

    result = post_json(url, token, payload)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
