# HEARTBEAT.md — Minimal Health Pulse (Template)

Runs every 30-60 minutes.

## Purpose
Heartbeat is for **system health**, not autonomous project work.

## Checks (keep it tight)
1. Gateway + channel health
   - Run: `openclaw health`
   - Alert only if gateway/channel is not OK.

2. Context pressure
   - Run: `session_status`
   - If context >= 80%: alert and suggest `/new`.
   - If context >= 90%: flush critical context to memory file first.

3. Memory file exists
   - Check: `ls -la ~/.openclaw/workspace/memory/$(date +%Y-%m-%d).md`
   - If missing after noon: create a stub daily memory file.

4. Cron health (once per day)
   - Check: `openclaw cron list`
   - Alert if any job has `consecutiveErrors > 0`.
   - Track completion in `state/heartbeat_state.json` to avoid duplicate checks.

## Response Rule
- If all checks are healthy and no action is needed: reply exactly `HEARTBEAT_OK`.
- If something is wrong: send one concise actionable alert (no fluff).
