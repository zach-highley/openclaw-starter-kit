# HEARTBEAT.md — Minimal Health Pulse (Template)

> Runs every 30-60 minutes. Healthy = silent. Loud = something's wrong (or shipped).

---

## Purpose

Heartbeat is for **health checks + idle builder mode** — not for chatting, not for status theatre.

- ✅ Alert when something breaks
- ✅ Alert when context is critically high
- ✅ Start autonomous work when idle
- ❌ Do NOT send routine status updates
- ❌ Do NOT summarize what you checked if everything was fine

---

## Step 1 — Gateway + Channel Health
- Run: `openclaw health`
- Alert only if gateway or channel is **not OK**.

## Step 2 — Context Pressure
- Run: `session_status`
- If context >= 80%: alert [USER], suggest `/new`.
- If context >= 90%: flush critical context to a memory file **before** context is lost.

## Step 3 — Memory File
- Check: `ls -la ~/.openclaw/workspace/memory/$(date +%Y-%m-%d).md`
- If missing after noon: create a stub daily memory file.

## Step 4 — Cron Health (once per day)
- Check: `openclaw cron list` — any `consecutiveErrors > 0`? Alert [USER].
- Track in `state/heartbeat_state.json` to avoid running this more than once per day.

---

## Step 5 — Idle Builder Mode

If checks 1–4 are all healthy and [USER] has been idle for 60+ minutes:

1. Read `TODO.md` (single source of truth — do not invent tasks).
2. Apply the **Antelope Filter** to every candidate task:
   - Does it compound over time?
   - Is it revenue-linked or shipping something visible?
   - Does it take a week+ of real engineering?
   - **No to any of these = skip it.** Pick a mouse and you'll spend the shift moving cheese.
3. Pick the highest-priority task that passes the filter.
4. Execute it. Commit. Report what shipped — not what you checked.

**Anti-decay rule:** Track how many consecutive waves were housekeeping-only (no real feature shipped). If 3 in a row: force a real project next wave. Housekeeping spirals are a known failure mode.

**Priority order (enforce this, don't just suggest it):**
Revenue-generating → Visible shipping → Research → Fun/experimental

---

## Messaging Policy (Anti-Spam)

| Situation | Action |
|-----------|--------|
| All checks healthy, no builder work | Reply exactly: `HEARTBEAT_OK` |
| Builder work completed (feature shipped) | One message — what shipped, what was committed |
| Something broken | One message — what's broken + who needs to act |
| Context >= 80% | Alert once, do not repeat every pulse |

**The cardinal rule:** If [USER] has to read your heartbeat and think "so what?" — rewrite it or don't send it.

---

## Response Rules

- Healthy + no action taken → reply exactly: **`HEARTBEAT_OK`** (full message, nothing else)
- Something shipped → one dense Telegram message (lead with what changed, not what you checked)
- Something broken → one actionable alert (who, what, what they need to do)
- Never send `HEARTBEAT_OK` AND a status update in the same message
