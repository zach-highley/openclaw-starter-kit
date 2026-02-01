# Meta-Monitor Documentation

*The "Watcher of Watchers"*

## The Problem
You have a watchdog that restarts the gateway if it crashes.
But what if the watchdog crashes?
Or what if the heartbeat cron job stops firing?
Who watches the watchers?

## The Solution
The **Meta-Monitor** (`scripts/meta_monitor.py`) is a high-level Python script that sits above your other automation systems. It doesn't check *health*; it checks *liveness*.

It answers the question: **"Are the automation scripts actually running?"**

## What It Monitors
| System | How It Checks | Threshold (Stall Time) |
|--------|---------------|------------------------|
| **Watchdog** | Checks timestamp of `watchdog-state.json` | 10 minutes |
| **Error Recovery** | Checks timestamp of recovery logs | 30 minutes |
| **Security Hound** | Checks timestamp of `security-hound.json` | 2 hours |
| **Heartbeat** | Checks timestamp of `heartbeat-state.json` | 2 hours |

## Fencing Tokens
One dangerous race condition in autonomous systems is **Restart Contention**.
- Script A sees the gateway is slow → Issues Restart
- Script B sees the gateway is down (because A killed it) → Issues Restart
- Script C sees memory is low → Issues Restart

Result: The gateway gets stuck in a restart loop and never boots.

**The Fix:** The Meta-Monitor manages a "fencing token" (a lock file).
- Before any script can restart the gateway, it must check the token.
- If a restart happened < 60 seconds ago, it must WAIT.

## Setup
1. Copy `scripts/meta_monitor.py` to your scripts folder.
2. Add it to your `HEARTBEAT.md` task list (so it runs hourly).
3. OR run it via cron independent of the main bot.
