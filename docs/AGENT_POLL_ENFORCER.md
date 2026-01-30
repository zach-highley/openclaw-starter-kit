# Agent Poll Enforcer — External Notification Enforcement

## The Problem

When your AI spawns a background coding agent (Codex, Claude Code, etc.), it can go silent for 10+ minutes. You end up having to ping it: "hey, what's happening?"

The rules exist in AGENTS.md. The sprint notification format exists in HEARTBEAT.md. But **rules in markdown don't enforce themselves.** A model mid-conversation forgets rules. A dying session can't follow instructions. The meta monitor checks system health but not communication cadence.

## The Pattern: Architecture > Instructions

This is the single most important lesson from running an autonomous AI system:

> **If a process can't reliably execute instructions, don't write better instructions — build external enforcement that doesn't depend on the broken thing.**

We learned this three times:
1. Sprint auto-refire rules kept being violated → removed the capability entirely
2. Session reset protocol was instructions a dying session can't follow → built an external watchdog
3. Notification cadence during agent work kept failing → built the poll enforcer

## The Solution

`agent_poll_enforcer.py` is an external script that:

1. **Detects** if a background coding agent is running (via state files + process detection)
2. **Tracks** when the AI last sent a notification to the user
3. **Alerts** if silence exceeds a threshold (default: 5 minutes) by waking the AI via gateway

### Integration Points

- **Watchdog** (runs every 5 min via launchd) — calls the enforcer as CHECK 20
- **Meta Monitor** — tracks enforcer as system #10
- **AGENTS.md** — enforcement hook: call `--mark-notified` after every progress update

### How It Works

```
Background agent running
         │
         ▼
Enforcer checks every 60s:
  ├── Agent active? (state file + pgrep)
  ├── Last notification time?
  └── Silence > 5 min?
         │
    YES ──┼── NO
    │         │
    ▼         ▼
  Wake AI    OK
  via gateway
```

### Usage

```bash
# Check if enforcement needed
python3 agent_poll_enforcer.py --check

# Mark that you just sent a notification (call after every user update)
python3 agent_poll_enforcer.py --mark-notified
```

### Key Design Decisions

- **5-minute threshold** — not every minute (annoying), not 10 minutes (too long). Battle-tested and tuned.
- **External to the AI** — the watchdog runs it, not the AI itself. That's the whole point.
- **Multiple detection methods** — pgrep patterns, state files, exec session checks. Belt and suspenders.
- **Gateway wake** — sends a system event that forces the AI to respond, not a silent log entry.

## Notification Cadence Rules

| Event | Notification |
|-------|-------------|
| Sprint/plan start | Immediate |
| Sprint/plan end | Immediate |
| During active work | Every ~5 min progress update |
| Agent spawned | Announce model, task, ETA |
| Agent complete | Results, commit hash, next step |
| Silence > 5 min | Enforcer forces wake |

## Template

See `scripts/agent_poll_enforcer.py` for the full implementation.
