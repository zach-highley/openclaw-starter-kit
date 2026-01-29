# HEARTBEAT.md

Your AI reads this file on every heartbeat (periodic check-in, typically every 30-60 min).
Customize the sections below. Remove what you don't need, add what you do.

## ⏰ Heartbeat Frequency
**MAX once per hour** to conserve tokens. Skip redundant checks.

---

## 🔄 WORK LOOP (HIGHEST PRIORITY — check every heartbeat)
Read `state/current_work.json`. If `queue` has items:

1. **Read the work state** — what task, what queue, what's in progress, what's done
2. **Pick next item** from `queue` (first item), set it as `inProgress`
3. **Execute it** — spawn the appropriate agent (Codex for coding, Gemini for docs, etc.)
4. **Sprint-start notification** — IMMEDIATELY message the user:
   > 🚀 **Sprint [X] started** — [description from spec]
   > 🤖 Model: [Codex/Opus/etc]
   > ⏱️ ETA: ~[N] minutes (based on `work_metrics.json` avg for that agent)
   > 📋 Next up: [next sprint in queue] — [brief description]
   > 📊 Progress: [completed count]/[total count] sprints done
5. **On success:** move from `inProgress` to `completed`, remove from `queue`, update `lastUpdated`
6. **On rate limit:** log it, set `rateLimitedUntil` timestamp, wait and retry next heartbeat
7. **On failure:** log error, retry up to `maxRetries`, then skip and move to next
8. **Sprint-complete notification** — message the user:
   > ✅ **Sprint [X] COMPLETE** — [what was done, commit hash]
   > ⏱️ Duration: [actual time] (est was [N] min)
   > [then the sprint-start notification for the NEXT sprint, same format as step 4]
9. **After `autoNewAfterSprints` completions (default 3):** save state, reset session for fresh context
10. **When queue is empty:** set `active: false`, send a full completion report

**Smart work detection:** Queue has items = work mode ON. Queue empty = work mode OFF.

**Stall Detection (3-strikes):**
- A sprint "stalls" when the agent produces no output for 5+ minutes
- **Strike 1-2:** Kill the stalled agent, re-spawn with updated instructions
- **Strike 3:** Deep dive — read the spec, find the root cause, fix it or do it yourself
- Always notify the user when a stall is detected and resolved

**Learning:** After each sprint, log to `state/work_metrics.json` via `scripts/log_sprint_metric.py`

---

## 🔨 Build Monitor (every heartbeat — fast)
Run `python3 scripts/build_monitor.py` and check the result:
- If `has_failures` is true AND `should_auto_fix` is true:
  1. Message user about the failure
  2. Spawn coding agent with the `fix_task` from the output
  3. Next heartbeat: check if the new build passed
- If `has_failures` and NOT `should_auto_fix` (repeat after fix attempt):
  1. Message user: needs manual review
- If no failures: skip silently

---

## ⚡ Usage Monitoring (every heartbeat)
Run `python3 scripts/check_usage.py` and check the result:
- If `should_alert` is true, message the user with the threshold crossed
- Thresholds: 20%, 40%, 60%, 80%, 90%, 95%, 100%
- At 80%+: warn "Running low"
- At 95%+: warn "Almost out"

---

## 🐕 Security (every heartbeat — fast)
Run `python3 scripts/security_hound.py`:
- Only alert if `should_alert` is true (real threats, not noise)
- Learns your devices/locations over time

---

## 🔄 Session Reset Protocol

When context hits ~85%:

### Step 1: Pre-Reset
Message user: "Context at ~X% — saving state and resetting."

### Step 2: Save
1. Write session highlights to daily memory file
2. Save work state (already persistent)
3. Commit and push

### Step 3: Reset
Run session reset command

### Step 4: Post-Reset Boot
Message user: "Reset complete. Loading work state..."

### Step 5: Resume
Read work state, report what's completed/queued, start next sprint with full notification format.

**Rule:** User should NEVER wonder what happened during a reset. Every step is narrated.

---

## Quick Checks (rotate through, don't do all every time)
- Email inbox (any urgent messages?)
- Calendar (upcoming events in 24h?)
- Weather (relevant if user might go out?)
- Anything else you want to monitor periodically

Track what you've checked in `memory/heartbeat-state.json` to avoid redundant checks.
