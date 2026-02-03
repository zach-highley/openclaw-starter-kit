# HEARTBEAT.md — Hourly Health Check (Template)

Runs every 1 hour.

## Rules
- 3–4 checks max.
- Only message the user if something is actionable.
- If nothing needs attention, reply with: `HEARTBEAT_OK`.

## Checks
1. Usage/quota snapshot:
   ```bash
   python3 scripts/check_usage.py --json
   ```
   - If context is high (choose a threshold like 70%+), warn the user and flush critical state to disk.

2. Task state sanity:
   - Can you parse `state/current_work.json` (if present)?
   - Is there a clearly defined “next action”?

3. Git hygiene (workspace):
   - If this workspace is a git repo and it’s dirty, commit + push **only if safe**.
   - Never push to a public repo without following `SECURITY.md`.

4. Human check-in:
   - If the user hasn’t heard from you in a long time and work is ongoing, send one progress update.
