# Cron vs Heartbeat vs launchd (macOS) - a Practical Guide

This project is a **survival guide**: patterns that keep an autonomous OpenClaw system running 24/7 *without* burning rate limits.

If you only remember one thing:

- **Cron / launchd** run code on a schedule.
- **Heartbeats** are *agent sessions* (LLM calls) on a schedule.
- **Use heartbeats sparingly.** They are the most expensive kind of "schedule".

Official reference (OpenClaw docs):
- Getting started / background service: https://docs.openclaw.ai/start/getting-started
- Tooling + monitoring concepts: https://docs.openclaw.ai/

---

## Decision flow (90% of cases)

### 1) Does this require an LLM to think?

- **No** → use **cron** (Linux) or **launchd** (macOS) to run a script.
- **Yes** → continue.

### 2) Can you make it non-LLM?

Common wins:
- parsing logs
- checking process health
- scanning for "stuck" background work
- verifying files exist
- gathering metrics

If you can make it non-LLM, do it. Then run it via cron/launchd.

### 3) If it truly needs an LLM: should it be a heartbeat?

Use a **heartbeat** only when the *agent itself* needs to periodically reason, summarize, or decide what to do next.

Examples that justify a heartbeat:
- periodic "triage" where an agent reads multiple signals and decides a response
- periodic review + planning (weekly audit summaries, backlog grooming)

Examples that do **not** justify a heartbeat:
- "check usage" (script)
- "check gateway is running" (script)
- "check security basics" (script)

---

## Anti-patterns (learned the hard way)

### Anti-pattern: Many small crons that all call LLMs
A common failure mode is slowly accumulating scheduled jobs ("just one more cron"), each doing a tiny check that triggers an LLM call.

Real-world impact seen in production:
- **12+ scheduled jobs** were collectively triggering **100+ model/tool calls/day**
- after consolidating and moving non-LLM tasks to cron/launchd, it dropped to **~34/day**

The fix:
- consolidate to *one* orchestrator (or a small, MECE set)
- move *every non-LLM check* into scripts
- run scripts via launchd/cron

### Anti-pattern: Heartbeats doing sprint management
Heartbeats are great for low-frequency reasoning. They are terrible at "orchestrate a multi-step build" because:
- they often run on cheaper/faster models
- they can misinterpret "check stalled" as "re-fire the agent"
- they can create duplicate work or git conflicts

Sprint/work orchestration should be handled by a dedicated work loop (see `scripts/autonomous_work_loop.py`) and/or your main session.

---

## When to use launchd (macOS)

Use **launchd** for:
- any *non-LLM* task you want to run reliably in the background
- restarts / keep-alive
- tasks that should survive user logouts

Examples:
- run `scripts/check_usage.py` every 30-60 min
- run `scripts/subagent_watcher.py --json --mark-reported` every 5-15 min
- run `scripts/auto_doctor.py --fix --save-state` every 4 hours

Why launchd is a big deal:
- it's stable
- it's cheap (no model calls)
- it reduces "LLM scheduled noise", which reduces rate limit risk

---

## Suggested "survival" schedule

A minimal, battle-tested baseline:

- **Every 5-15 min (cron/launchd):** `scripts/subagent_watcher.py --json --mark-reported`
- **Every 30-60 min (cron/launchd):** `scripts/check_usage.py --json`
- **Every 4 hours (cron/launchd):** `scripts/auto_doctor.py --fix --save-state`
- **Daily (cron/launchd):** quick workspace audit (see `docs/WEEKLY_AUDIT_GUIDE.md`)
- **Weekly (cron/launchd + optional heartbeat summary):** full audit + summary

Keep heartbeats **max once/hour** unless you have a specific, measured reason.

---

## Pattern: Heartbeat as Work Orchestrator (Plan C)

> Learned Feb 5, 2026: Heartbeats **can** orchestrate real work, but only with the right pattern.

The key insight: heartbeats fire every 30 min. Between ticks, background processes can run real work (Codex CLI, Claude Code). The heartbeat reads state, picks tasks, launches work, and monitors progress.

### Architecture
```
Heartbeat (BRAIN) → reads state file → picks task → launches background exec
Background exec (HANDS) → runs codex exec in background → does real work
State file (MEMORY) → persists between heartbeats → tracks IDLE/BUILDING/REVIEWING
```

### Critical: `codex exec` vs `codex --full-auto`

| Command | Mode | PTY needed? | Exits? | Use for |
|---------|------|-------------|--------|---------|
| `codex --full-auto` | Interactive TUI | YES | NEVER | Manual use only |
| `codex exec --full-auto` | Non-interactive | NO | YES | **Background automation** |

**Always use `codex exec --full-auto` for background work.** The interactive mode requires a PTY, produces garbled escape codes, and never exits, which will permanently stall your state machine.

```bash
# WRONG - will hang forever
exec background=true "codex --full-auto 'build the thing'"

# RIGHT - exits cleanly with code 0
exec background=true "cd <git-repo> && codex exec --full-auto 'build the thing'"
```

Note: `codex exec` requires a git repository. Use `--skip-git-repo-check` if running outside one.

### State Machine
```
IDLE → pick task, launch codex exec, set BUILDING
BUILDING → poll process, check if done/crashed
REVIEWING → verify output, commit, update all tracking files, set IDLE
```

### Pre-flight audit (before every build)
1. Antelope check — will this make money or ship product?
2. Dedup check — is this already built?
3. Reality check — is this actually blocked?
4. Scope check — can it complete in one cycle?
5. Route decision — backend (Codex) vs frontend (Claude Code) vs direct

### Lessons learned the hard way
- **Test before trusting.** We wrote a 150-line state machine and assumed it worked. The core command (`codex --full-auto`) was wrong. Would have permanently stuck the system.
- **Dedup saves work.** Always check if a task was already completed before starting.
- **State files go stale.** Always verify reality (check actual files/deployments) before trusting state.
- **No watchers watching watchers.** The heartbeat IS the auditor. Don't add monitoring crons on top.

---

## Design principle

> If you can replace a rule with an enforcement script, do it.

- "Don't burn rate limits" → enforce with usage monitors + consolidated schedules.
- "Don't lose completed work after restart" → enforce with `subagent_watcher.py`.
- "Don't let monitoring stall" → enforce with meta-monitor + auto-doctor.
