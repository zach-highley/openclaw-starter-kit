# NIGHT_SHIFT.md — Overnight Autonomy, High-Signal Updates

This is the "night shift" pattern: the agent keeps working while the human sleeps, and sends *one* high-signal update cadence that proves real progress without spamming.

## Goals

- **No lockouts:** the agent must not die on rate limits.
- **No spam:** 1 message per hour (or per 2 hours) plus one "goodnight" kickoff.
- **Auditability:** every claim links to a file path, diff, commit hash, or screenshot.
- **Safety:** anything involving money, deletion, posting publicly, or sending messages to third parties requires confirmation.

## Recommended Cadence

### 1) Kickoff message (when the human goes to sleep)
Send once:

- "Workshop is open, here's what's cooking"
- 3–5 bullet tasks
- Expected outputs (files, commits, reports)

### 2) Hourly update (short)
Structure:

- **This hour:** 2–4 concrete items shipped
- **Key finding:** 1 thing learned that changes the plan
- **Next:** what’s queued next

### 3) Final wrap (morning)
- total shipped (commits + files)
- what to review
- what’s next

## Copy-Paste Templates

### Kickoff
```
Goodnight. Workshop is open, here's what's cooking:

1) 🔧 [Task]
2) 📚 [Task]
3) 🧪 [Task]

Outputs you’ll wake up to:
- [file path] or [PR/commit]
- [file path] or [report]
```

### Hourly update
```
Night Shift — [HH:MM] Update

This hour:
- ✅ [shipped thing] (commit abc123)
- ✅ [shipped thing] (file /path)

Key research finding:
- [one sentence]

Next:
- [next thing]
```

## How to Automate (OpenClaw)

Use **cron** for human-facing update messages. Cron jobs are reliable and don’t consume model context unless they execute an agent turn.

Option A (simple): cron → `systemEvent` reminder text
- Reminder wakes the session and prompts the agent to send a consolidated update.

Option B (advanced): cron → isolated `agentTurn`
- A dedicated isolated night-shift agent compiles progress from git + state files and sends the update.

See also:
- `docs/WORKSTREAMS.md` (canonical chat + SSOT workstreams)
- `docs/CRON_HEARTBEAT_GUIDE.md`
- `docs/COMMUNICATION_PATTERNS.md`
