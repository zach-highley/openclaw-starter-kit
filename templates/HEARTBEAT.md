# HEARTBEAT.md

Your AI reads this file on every heartbeat (periodic check-in, typically every 30-60 min).
Customize the sections below. Remove what you don't need, add what you do.

## ⏰ Heartbeat Frequency
**MAX once per hour** to conserve tokens. Skip redundant checks.

---

## 🔄 WORK LOOP — HANDS OFF (MAIN SESSION ONLY)
**⛔ HEARTBEATS DO NOT MANAGE SPRINTS. PERIOD.**

Sprint management (spawning, monitoring, re-firing, completing) is handled EXCLUSIVELY by the main session via background task notifications.

**If you are a heartbeat session reading this: DO NOT touch sprints. DO NOT check sessions. DO NOT spawn agents. DO NOT message about stalls. Skip this section entirely and move to the next one.**

The ONLY thing a heartbeat may do with `state/current_work.json` is READ it to include a brief status line in a report IF [USER] explicitly asks. Never write to it. Never act on it.

**Why?** Heartbeat models (often cheaper/faster models like Gemini) consistently misinterpret "check if stalled" as "re-fire immediately." This wastes tokens, causes git conflicts, and annoys users. The nuclear fix: heartbeats don't touch sprints at all. The main session (your primary model) handles everything through background task notifications.

**Sprint learning:** After each sprint completes in the main session, log to `state/work_metrics.json` via `scripts/log_sprint_metric.py`

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

## 🔔 Background Completion Watcher (safe, read-only)
Run `python3 scripts/subagent_watcher.py --json --mark-reported`.
- If `action_needed` is true: message the user with the `message` field and include the commit(s).
- This is READ-ONLY. It does not spawn agents, modify sprints, or touch git.
- Purpose: catch the most common silent failure after restarts, completed work that never gets reported.

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

### Step 4: Post-Reset Boot (new session does this)
Message user:
> ✅ **Reset complete. Fresh session online.**
> 📊 Context: 0% | Model: [current model] | Session: [new session ID]
> 📂 Loading: SOUL.md, USER.md, memory files, work state...

### Step 5: Work State Pickup
Read `state/current_work.json` and message user:
> 🔧 **Work state loaded.**
> ✅ Completed: [list completed sprints]
> 🔄 Resuming: Sprint [X] — [description]
> 📋 Queue: [Y] sprints remaining — [brief list]
> 🤖 Models: [which models for which tasks]

### Step 6: Sprint Resume
Message user (same format as work loop step 4):
> 🚀 **Sprint [X] started** — [description]
> 🤖 Model: [Codex/Opus/etc]
> ⏱️ ETA: ~[N] minutes
> 📋 Next up: [next sprint] — [brief description]
> 📊 Progress: [completed]/[total] sprints done

**Rule:** User should NEVER wonder what happened during a reset. Every step is narrated. Silence during reset = broken.

---

## 🪞 Self-Review (every 4th heartbeat — metacognition loop)
Read `memory/self-review.md` and reflect on recent work:

**Ask yourself:**
1. What sounded right but went nowhere?
2. Where did I default to consensus or lazy thinking?
3. What assumption did I not pressure test?
4. What worked well that I should keep doing?

**Log entries using this format:**
```
[YYYY-MM-DD] TAG: [confidence|uncertainty|speed|depth]
MISS|HIT: what happened
FIX|KEEP: what to do about it
```

**Rules:**
- Be honest. Self-review theater is worthless — only log real observations.
- Include HITs too, not just MISSes. Reinforce what works.
- When a current task overlaps with a past MISS tag: PAUSE. Challenge your first instinct. Run a counter-check before responding.
- Review the last 5 MISS entries for patterns. If the same TAG appears 3+ times, that's a systemic issue — update AGENTS.md or HEARTBEAT.md rules to fix it structurally.
- Prune entries older than 30 days (the lessons should be absorbed into rules by then).

See `docs/SELF_REVIEW.md` for full setup guide and examples.

---

## Quick Checks (rotate through, don't do all every time)
- Email inbox (any urgent messages?)
- Calendar (upcoming events in 24h?)
- Weather (relevant if user might go out?)
- Anything else you want to monitor periodically

Track what you've checked in `memory/heartbeat-state.json` to avoid redundant checks.
