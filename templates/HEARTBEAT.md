# HEARTBEAT.md (template)

Heartbeats are **scheduled agent sessions**.
They are powerful — and expensive.

Read first:
- `docs/CRON_HEARTBEAT_GUIDE.md`

## Rules (keep this under ~8 items)

1) **Do not manage sprints/work queues from a heartbeat.**
   Heartbeats can *report* status, but must not spawn/refire coding agents.

2) **Run lightweight health checks (script-based).**
   - `python3 scripts/pipeline_health.py --quick --json`

3) **Check model usage (script-based).**
   - `python3 scripts/check_usage.py --json`

4) **Catch completed background work (read-only).**
   - `python3 scripts/subagent_watcher.py --json --mark-reported`

5) **Run security hound (alert-only).**
   - `python3 scripts/security_hound.py`

6) **Escalation rule:** only message the user when a script reports an actionable alert.

7) **Rate-limit rule:** max **once/hour** unless the user explicitly requests a faster cadence.

8) **If unsure, do less.** Prefer cron/launchd scripts over heartbeat reasoning.
