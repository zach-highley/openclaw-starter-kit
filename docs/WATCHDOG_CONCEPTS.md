# Watchdog Concepts: Self-Healing & Self-Learning

**"A system that crashes is annoying. A system that fixes itself is magic. A system that learns *why* it crashed is alive."**

The Moltbot Watchdog is not just a cron job that restarts a process. It is a resilient, learning organism that ensures the agent is always available, even when things go wrong.

## Core Philosophy

1.  **Redundancy:** If the main brain fails, the lizard brain (Watchdog) takes over.
2.  **Escalation:** Don't just restart. Try a soft fix. Then a hard fix. Then the nuclear option.
3.  **Learning:** Every failure is data. If we fix it, record *why* it broke and *how* we fixed it.
4.  **Adaptation:** If the same error happens 3 times in a row, stop trying the same fix. Change the system.

## The Loop

The Watchdog runs every 5 minutes (via cron or launchd).

1.  **Check:**
    *   Is the Gateway process running?
    *   Is memory usage safe (<2GB)?
    *   Is the process too old (>48h)?
    *   Is the HTTP health endpoint responding?
    *   Is disk space adequate?

2.  **Detect Failure:**
    *   "Gateway not running"
    *   "Health check timeout"
    *   "Memory leak (2.5GB)"

3.  **Intervene (The Fix):**
    *   *Level 1:* Start process / Soft restart.
    *   *Level 2:* Force kill (SIGKILL) + Restart (for memory leaks).
    *   *Level 3:* Nuclear Session Reset (archive corrupt session, start fresh).

4.  **Learn (The Analysis):**
    *   Calls `watchdog_learn.sh`.
    *   Analyzes logs to find the *Root Cause* (e.g., "Auth token expired", "OOM Kill").
    *   Updates `WATCHDOG.md` with an incident report.
    *   Updates `metrics.json` (Did this fix work? Yes/No).

5.  **Adapt (The Evolution):**
    *   If `metrics.json` shows "Auth token expired" caused 3 crashes today -> Send an alert suggesting API Key switch.
    *   If "Context limit exceeded" caused crashes -> Trigger session compaction earlier.

## Architecture

### 1. `watchdog.sh` (The Enforcer)
The dumb muscle. It runs checks and executes commands. It doesn't think deeply; it acts quickly. It maintains a state file (`watchdog-state.json`) to track consecutive failures.

### 2. `watchdog_learn.sh` (The Analyst)
The smarts. Called *after* an intervention. It:
*   Parses recent logs for error keywords.
*   Determines the likely root cause.
*   Updates the `WATCHDOG.md` log.
*   Updates the `watchdog_metrics.json` database.
*   Decides if this is a "fluke" or a "pattern".

### 3. `watchdog_metrics.json` (The Memory)
A database of what went wrong and what worked.
```json
{
  "fixes": {
    "gateway-restart": {
      "attempted": 12,
      "succeeded": 10,
      "successRate": 0.83,
      "worksFor": ["memory-leak", "process-death"]
    }
  }
}
```

## Escalation Ladder

| Level | Failure Count | Action | Description |
|-------|---------------|--------|-------------|
| 0 | 0 | None | System healthy. |
| 1 | 1 | Restart | Process died? Just start it back up. |
| 2 | 2-3 | Force Restart | Still failing? Kill -9 and restart. |
| 3 | 4+ | **NUCLEAR** | Session is likely corrupt. Move it to `archive/` and start fresh. |

## Quickstart

1.  Ensure scripts are in `~/clawd/scripts/`.
2.  Add `watchdog.sh` to your crontab (every 5 mins).
    ```bash
    */5 * * * * /bin/bash ~/clawd/scripts/watchdog.sh
    ```
3.  Relax. If it breaks, it fixes itself.
