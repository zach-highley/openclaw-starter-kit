# BOOT.md — Startup / Gateway Restart Hook (Template)

Runs on Gateway startup via the `boot-md` hook.

## Goal
Confirm the system is alive, state is readable, and the next action is clear.

## Boot Checklist
1. Read `state/current_work.json` (if present) and determine:
   - what is currently running
   - what should resume next
2. Run a quick usage snapshot:
   ```bash
   python3 scripts/check_usage.py --json
   ```
3. Send a brief **boot notification** to the user:
   - Gateway restarted/healthy
   - Context/usage snapshot (brief)
   - “Resuming: <task>” or “Standing by”
4. If there is an in-progress task, resume it.
5. If there is no task, stand by for instructions.

## Important
- Keep this file small. Deep checks belong in `HEARTBEAT.md`.
- Do not hardcode chat IDs or tokens in this repo.

## Gateway Rules (critical)
- Prefer `openclaw gateway status|start|restart|stop`.
- Avoid running duplicate gateways.
- If you suspect multiple processes exist, verify and reconcile before doing anything else.
