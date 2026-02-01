# AGENTS.md (template) — Your Workspace Rules

This repo is a **survival guide** for running OpenClaw as a self-healing system.
Your goal is simple:

> Keep the assistant alive 24/7 without requiring a human to touch the terminal.

Read first:
- Cron vs Heartbeat vs launchd: `docs/CRON_HEARTBEAT_GUIDE.md`
- Subagent timeouts: `docs/SUBAGENT_TIMEOUT_GUIDE.md`
- Weekly audits: `docs/WEEKLY_AUDIT_GUIDE.md`
- Security hardening: `docs/SECURITY_HARDENING.md`

---

## Workspace assumptions

- This file lives in your **workspace root**.
- Scripts live in `scripts/`
- State lives in `state/`
- Memory logs (optional) live in `memory/`

---

## Every session boot (do this first)

1) Read: `SOUL.md`, `USER.md`, `SECURITY.md`.
2) Read recent memory: `memory/YYYY-MM-DD.md` (today + yesterday) if you use memory files.
3) If you keep long-term memory: read `MEMORY.md`.
4) **Check system status (silent):**
   ```bash
   openclaw status
   python3 scripts/check_usage.py --json
   python3 scripts/meta_monitor.py --check --mode heartbeat
   ```
5) **Catch finished background work (MANDATORY):**
   ```bash
   python3 scripts/subagent_watcher.py --json --mark-reported
   ```
   If `action_needed=true`, message the user with the completion summary.

---

## The self-healing loop (architecture)

A resilient setup uses a layered loop:

1) **watchdog** (restart gateway if it dies)
2) **meta-monitor** (watches the watchers)
3) **auto-doctor** (periodic deep checks + save state)
4) **weekly audit** (prevents entropy: bloat, duplicates, stale schedules, security drift)

---

## Non-negotiable rules

### 1) Never require terminal interaction
If a human needs to run commands repeatedly, the system is incomplete.
Convert it into:
- scripts
- schedules (cron/launchd)
- safe auto-recovery

### 2) MECE enforcement (anti-bloat)
Before creating any file/script:
- search for overlap
- extend existing tooling
- keep one clear purpose per file

### 3) Trust the models (timeouts)
If you delegate real code work to a coder model, give it enough time.
See: `docs/SUBAGENT_TIMEOUT_GUIDE.md`.

### 4) Security: never hardcode secrets
If a secret appears in git, assume compromise and rotate.
See: `docs/SECURITY_HARDENING.md`.

---

## Recommended schedules

Prefer **cron/launchd** scripts over heartbeats.
A battle-tested baseline:

- every 5–15 min: `scripts/subagent_watcher.py --json --mark-reported`
- every 30–60 min: `scripts/check_usage.py --json`
- every 4 hours: `scripts/auto_doctor.py --fix --save-state`
- weekly: audit (see `docs/WEEKLY_AUDIT_GUIDE.md`)

---

## Status line (optional, but extremely useful)

Include a short status line in normal replies:

`[model | ctx X% | workers N/M]`

Where:
- `ctx` comes from `python3 scripts/check_usage.py --json`
- `workers` comes from `python3 scripts/meta_monitor.py --check`
