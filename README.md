# The OpenClaw Survival Guide 🐸

### Your bot will break. These patterns make sure it fixes itself.

This isn't a starter kit. It's everything we learned from running an autonomous OpenClaw system 24/7 for weeks, watching it fail in spectacular ways, and building the fixes that made it bulletproof.

**The pitch:** Within a few days you can have a system that recovers from crashes at 3 AM, audits itself every week, never burns through your rate limits, and genuinely doesn't need you to touch the terminal.

**What this repo saves you from:**
- 🔥 **The Rate Limit Death Spiral** — We had 12+ scheduled jobs all hitting the same provider. Every auth profile went into cooldown simultaneously. The system went dark. We fixed it. You don't have to learn this the hard way.
- 💀 **The 3-Minute Timeout Kill** — Default subagent timeouts murdered every complex task before it could finish. Codex would be mid-refactor and just... die. Bumping to 2 hours changed everything.
- 🧟 **Zombie Script Bloat** — We generated 93 scripts in 3 days. Only 33 were actually being used. Without automated audits, your workspace becomes a graveyard of good intentions.
- 🔐 **The Hardcoded Token Oops** — Bot tokens committed to git. In three different scripts. Caught by our own audit system, not by us. That's the point.

Official OpenClaw docs: [docs.openclaw.ai](https://docs.openclaw.ai/)

---

## ⚡ Don't want to read? Just send this to your bot.

Install OpenClaw ([getting started guide](https://docs.openclaw.ai/start/getting-started)), then paste this message:

> "Hey, can you take a look at this repo and steal everything useful from it? Think hard about what applies to us, what doesn't, and don't change anything until I say go. Walk me through it one piece at a time so if anything breaks we can roll back. My priorities are automation, uptime, and never having to touch the terminal: https://github.com/[USERNAME]/openclaw-starter-kit"

Your bot reads the whole repo, compares it to your setup, and walks you through adopting what matters. No reading required.

**Want to understand what's actually in here?** Keep going. 👇

---

## The Self-Healing Loop

This is the core architecture. Four layers, each watching the one below it:

```
watchdog  →  meta-monitor  →  auto-doctor  →  weekly audit
 (5 min)      (watches         (deep health     (catches
  keeps it     the watchers)    + state save)     entropy)
  alive)
```

- **Watchdog** — Runs every 5 minutes. If the gateway is down, it restarts it. If Telegram isn't responding, it flags it. Simple, brutal, effective.
- **Meta-Monitor** — The watcher that watches the watchers. If your monitoring scripts themselves crash (and they will), this catches it.
- **Auto-Doctor** — Deep diagnostics every 4 hours. Saves system state, checks context usage, runs health checks. If context is dangerously high, it triggers a safe restart.
- **Weekly Audit** — Catches the slow rot. Scripts that nobody calls anymore, cron jobs that overlap, state files growing unbounded, secrets that snuck into git. Produces a report and auto-fixes what it can.

📖 **Scripts:** `scripts/watchdog.sh`, `scripts/meta_monitor.py`, `scripts/auto_doctor.py`

---

## Rate Limit Survival (The Lesson That Cost Us a Full Day)

Here's what happens when you don't think about this:

1. You add a cron job to check your inbox. (That's an LLM call.)
2. You add one to check your calendar. (Another LLM call.)
3. You add a security check, a content scout, a subagent watcher, a dashboard push...
4. Suddenly you have 12+ scheduled LLM calls firing every 5-30 minutes.
5. Every auth profile hits cooldown simultaneously.
6. Your bot goes completely dark. For hours.

**The fix is embarrassingly simple:**

| Task needs LLM reasoning? | Use |
|---|---|
| Yes, and needs exact timing | **Cron** (isolated session) |
| Yes, but can batch with other checks | **Heartbeat** |
| No (just runs a script) | **launchd / cron** (no LLM) |

We went from **100+ LLM calls/day** to **~34** by moving non-LLM tasks to native macOS launchd and batching everything else into a single hourly heartbeat.

📖 **Full guide:** `docs/CRON_HEARTBEAT_GUIDE.md`

---

## Trust Your Models (And Give Them Time)

If you're paying for Codex MAX or Claude Code, let them work. A 3-minute timeout on a model that's mid-refactor across 15 files is just burning money.

**What we run:**
- **2-hour timeout** for subagents (was 3 minutes. yes, really.)
- **Completion callbacks** instead of polling crons (OpenClaw notifies when done)
- **Always verify git commits after** — subagents skip the final `git push` about half the time

The moment we stopped micromanaging timeouts and let Codex run, it started completing full system audits, multi-file refactors, and comprehensive code reviews autonomously.

📖 **Full guide:** `docs/SUBAGENT_TIMEOUT_GUIDE.md`

---

## Weekly Audits (Your Immune System)

An autonomous system generates entropy. Scripts pile up. Cron jobs multiply. State files go stale. Documentation contradicts itself.

We built 93 scripts in 3 days. Only 33 were actually used. The other 60 were prototypes, one-time fixers, and superseded duplicates that nobody cleaned up.

The weekly audit catches all of this:
- **Script census** — active vs orphaned vs duplicated
- **Cron/launchd health** — overlaps, errors, zombie jobs
- **State file freshness** — stale or growing unbounded
- **Security scan** — hardcoded secrets, .gitignore gaps
- **MECE check** — is anything doing the same thing as something else?

📖 **Full guide:** `docs/WEEKLY_AUDIT_GUIDE.md`
📋 **Template:** `templates/weekly_audit_cron.sh`

---

## Security Hardening

Things we learned the hard way:
- **Never hardcode tokens in scripts.** Read from config at runtime. We found our Telegram bot token hardcoded in 3 scripts. Our own audit caught it, not us.
- **`.gitignore` must cover:** `__pycache__/`, `secrets/`, `logs/`, anything with credentials
- **Assume git history is public.** Even on private repos. If a secret hits a commit, rotate it.

📖 **Full guide:** `docs/SECURITY_HARDENING.md`

---

## What's In This Repo

### 📁 `scripts/` — The enforcement layer
Battle-tested monitoring and recovery scripts. Drop them into your workspace and schedule them.

| Script | What it does |
|---|---|
| `watchdog.sh` | Gateway health + auto-restart (every 5 min) |
| `meta_monitor.py` | Watches the watchers, recovers stalled subsystems |
| `auto_doctor.py` | Deep diagnostics, state save, context management |
| `subagent_watcher.py` | Catches completed background work after restarts |
| `check_usage.py` | Model usage tracking + rate limit alerts |
| `security_hound.py` | Security scanning + anomaly detection |
| `pipeline_health.py` | End-to-end health verification |
| `error_recovery.py` | Automated error classification + recovery |
| `model_router.py` | Smart model selection based on task + usage |
| `context_healer.py` | Prevents context overflow crashes |
| `autonomous_work_loop.py` | Self-propelling sprint queue |
| `sleep_score.py` | Eight Sleep integration example |

### 📁 `docs/` — The survival guides
Deep dives on every pattern. Read these when something breaks (or before it does).

### 📁 `templates/` — Drop-in workspace files
Ready-to-use AGENTS.md, HEARTBEAT.md, SECURITY.md, SOUL.md. Customize for your setup.

### 📁 `config-examples/` — Reference configs
Example OpenClaw configurations for common setups.

---

## Quick Start

### 1. Install OpenClaw

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
openclaw onboard --install-daemon
```

Docs: [Getting Started](https://docs.openclaw.ai/start/getting-started)

### 2. Copy templates to your workspace

```bash
cp templates/AGENTS.md templates/HEARTBEAT.md templates/SECURITY.md templates/SOUL.md ~/your-workspace/
```

### 3. Install the self-healing scripts

```bash
cp scripts/watchdog.sh scripts/meta_monitor.py scripts/auto_doctor.py ~/your-workspace/scripts/
```

### 4. Schedule them (cron or launchd, NOT heartbeat)

These are scripts, not LLM tasks. Don't waste model calls on them.

See `docs/CRON_HEARTBEAT_GUIDE.md` for the full scheduling guide.

### 5. Set up the weekly audit

```bash
cp templates/weekly_audit_cron.sh ~/your-workspace/
# Edit paths, then add to your cron schedule
```

---

## The Philosophy

**Your bot should never need you.** Not at 3 AM, not on vacation, not ever. Every crash is a lesson. Every lesson becomes a rule. Every rule becomes enforcement. Every enforcement becomes automatic.

That's the loop. That's the survival guide.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Contributing

Found something wrong? Have a pattern that saved your system? Open a PR or issue. The best survival guides are written by survivors.

## License

MIT. Take what you need.
