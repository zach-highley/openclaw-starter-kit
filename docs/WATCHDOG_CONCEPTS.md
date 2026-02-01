# Watchdog Concepts: Self-Healing & Self-Learning

**"A system that crashes is annoying. A system that fixes itself is magic. A system that learns *why* it crashed is alive."**

The OpenClaw Watchdog is not just a cron job that restarts a process. It is a resilient, learning organism that ensures the agent is always available, even when things go wrong.

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

## v8 Additions: Lessons From Real Failures

These checks were added after real-world production incidents. They solve problems you WILL hit.

### CHECK 14: Session Size Monitor
**Problem:** Long conversations grow the session file to 2-3MB. When it exceeds the model's context window, you get "Context overflow: prompt too large" and the bot goes unresponsive. This is the #1 scariest failure because it looks like your bot died.

**Fix:** Watchdog monitors session file size every 5 minutes. Warns at 1.5MB, auto-resets at 2.5MB. The reset saves context to memory so the bot picks up where it left off.

### CHECK 15: Telegram Delivery Health
**Problem:** After rapid session resets or re-onboarding, Telegram delivery can break one-way. Your messages reach the bot fine, but its replies only go to the terminal — not back to Telegram. The bot looks dead even though it's responding.

**Fix:** Watchdog compares inbound vs outbound Telegram message counts. If there are inbound messages but zero outbound, it auto-restarts the gateway to fix the pipe.

### "Don't Panic" Messaging
**Problem:** When things break, users panic and start running terminal commands that make things worse (re-onboarding, cancelling wizards, creating junk auth profiles).

**Fix:** Two new functions:
- `reassure()` — Sends "I'm fixing this automatically, don't touch anything, back in X minutes"
- `all_clear()` — Sends "All fixed! Here's what happened. You didn't have to do anything."

The watchdog also has a direct Telegram API fallback — if OpenClaw itself is too broken to send messages, the watchdog calls the Telegram Bot API directly. Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` environment variables to enable this.

### Common Gotcha: Ollama "Model Not Allowed"
If you configure Ollama as a fallback but get "model not allowed" errors, you need to add it to `agents.defaults.models` in your config. This key acts as an **allowlist** — models not listed there can't be used for overrides or explicit selection:

```json5
{
  agents: {
    defaults: {
      models: {
        "ollama/qwen2.5:14b": { alias: "Ollama Local" },
        // ... add all your models here
      }
    }
  }
}
```

### Auth Cooldown Cascade
When you use multiple auth profiles for the same provider and hit rate limits, ALL profiles can enter cooldown simultaneously. The bot retries each profile, and each retry can extend the cooldown. 

**Prevention:**
- Don't retry during cooldowns (makes it worse)
- Have Ollama as a local fallback that never rate-limits
- The watchdog's model health check (CHECK 10) detects this pattern

## Quickstart

1.  Ensure scripts are in your workspace `scripts/` directory (e.g. `$OPENCLAW_WORKSPACE/scripts/`).
2.  Add `watchdog.sh` to your crontab or launchd (every 5 mins).
    ```bash
    */5 * * * * /bin/bash "$OPENCLAW_WORKSPACE/scripts/watchdog.sh"
    ```
3.  (Optional) Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` for direct Telegram fallback.
4.  Relax. If it breaks, it fixes itself. And it'll tell you about it.
