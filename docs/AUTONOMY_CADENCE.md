# Autonomy Cadence (That Actually Fires)

This repo is designed to feel like a real 24/7 assistant, not a pile of “suggestions”.

The trick is to separate:
- **Awareness loops** (heartbeat) from
- **Scheduled actions** (cron) from
- **Event-driven reactions** (hooks)

…and ensure scheduled jobs **deliver** messages (or explicitly choose not to).

## The Simple Model

### 1) Heartbeat = periodic awareness (MECE)
Use heartbeat for batched checks:
- usage/quota
- repo hygiene
- “anything urgent?”

Heartbeat runs in the **main session** and should be quiet unless something needs attention.

### 2) Cron = exact timing and guaranteed delivery
Use cron when you need:
- exact time (7:05am, 9:05pm)
- a guaranteed message (hourly update)
- an isolated run that won’t be blocked by main-session context

**Important:** Cron jobs can run successfully but not send anything if `deliver:false`.

### 3) Hooks = run on events
Use hooks for:
- gateway startup boot
- /new, /reset session memory capture

## Recommended cadence (beginner friendly)

### ✅ Hourly “I’m alive” progress update
- **Schedule:** every hour on the hour
- **Mechanism:** cron (isolated agent turn)
- **Delivery:** YES

### ✅ Twice-daily summaries
- **Morning recap:** 7:05 AM (local)
- **Evening recap:** 9:05 PM (local)
- **Mechanism:** cron (isolated agent turn)
- **Delivery:** YES

### ✅ Daily docs upkeep
- **Schedule:** 10:45 PM (local)
- **Mechanism:** cron (isolated agent turn)
- **Delivery:** YES
- Updates:
  - WORKSTREAMS.md
  - memory/YYYY-MM-DD.md
  - any runbooks touched that day

## The "It Ran But I Saw Nothing" Checklist

If you expected a message and got none:
1) Confirm the job is enabled.
2) Confirm `deliver:true` (or that the job explicitly calls the message tool).
3) Confirm the job targets the right channel/user.
4) Confirm the agent turn isn’t immediately exiting with NO_REPLY.
5) Confirm the gateway is running.

## Keep it MECE, no bloat

- Prefer **one** heartbeat checklist over five polling jobs.
- Prefer **two** recaps + **one** hourly update over a dozen “pings”.
- If a job exists, it should have a clear owner and purpose.

Related docs:
- Cron vs Heartbeat: https://docs.openclaw.ai/automation/cron-vs-heartbeat
- Heartbeat: https://docs.openclaw.ai/gateway/heartbeat
- Cron: https://docs.openclaw.ai/cli/cron
- Hooks: https://docs.openclaw.ai/cli/hooks
