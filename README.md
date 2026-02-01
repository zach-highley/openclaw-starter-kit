# OpenClaw Starter Kit (v2) — The Self‑Healing AI Survival Guide

This repository is not a “hello world” template.
It’s a **battle-tested survival guide** for turning OpenClaw into an autonomous system that:

- **Self-heals at 3 AM** (watchers catch failures and recover)
- **Never requires a terminal babysitter** (automation + external enforcement)
- **Learns from failures** (weekly audits + MECE anti-bloat)
- **Stays up without burning rate limits** (cron/launchd for non-LLM work)
- **Trusts the right models for the right jobs** (long timeouts for real coding)

Official OpenClaw docs (reference): https://docs.openclaw.ai/

---

## What this repo gives you

### 1) A self-healing architecture (the “watchers” loop)

```
watchdog  →  meta-monitor  →  auto-doctor  →  weekly audit
(restart)    (watch watchers)  (deep checks)   (prevent entropy)
```

- **watchdog**: keeps the gateway alive
- **meta-monitor**: detects when your monitoring is the thing that broke
- **auto-doctor**: periodic diagnostics + state saving + safe recovery
- **weekly audit**: stops the slow death-by-entropy (duplicate scripts, stale jobs, security drift)

### 2) Rate-limit survival patterns

A common production failure mode is “scheduled creep”:
- you add more and more scheduled checks
- each one triggers model/tool calls
- eventually you burn your quotas and the system goes dark

Real-world impact seen in production:
- **100+ model/tool calls/day** → consolidated + moved non-LLM tasks to cron/launchd → **~34/day**

### 3) A model trust hierarchy (and why timeouts matter)

If you want an AI that can actually fix itself, you must let your coder model work.
A 3-minute timeout kills real refactors.
A ~30-minute timeout lets it:
- scan the repo
- plan
- implement
- run checks
- finish cleanly

See: `docs/SUBAGENT_TIMEOUT_GUIDE.md`

---

## Don’t want to read anything?

Install OpenClaw, then send your bot this message.

> "Hey [bot], can you take a look at this repo and steal/integrate every single thing it suggests? Think hard about it, make sure it meshes and matches with everything we've done already, and don't change anything until I give the OK. Also, point out any mistakes and improvements you see to make it better for me specifically and my goals before we get going. And let's integrate things one step at a time and track all changes so if anything breaks we can go back to the way we had it before. My goals are my goals as you know them but also automation, notifications, and consistent up-time with machine learning to fix all errors so I never have to touch the terminal or computer: <PASTE_THIS_REPO_URL_HERE>"

That’s it.
Your bot will:
- read the repo
- compare it to your current setup
- propose a step-by-step adoption plan with rollback tracking

---

## Quick Start (recommended path)

### 1) Install OpenClaw
From the official docs:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
openclaw onboard --install-daemon
```

Docs: https://docs.openclaw.ai/start/getting-started

### 2) Copy templates into your workspace

Start with:
- `templates/AGENTS.md` → your agent’s “operating system”
- `templates/HEARTBEAT.md` → your heartbeat rules (keep it tiny)
- `templates/SECURITY.md` → human-confirmation guardrails
- `templates/SOUL.md` → personality + tone

### 3) Install the “watchers” scripts

From this repo:
- `scripts/watchdog.sh`
- `scripts/meta_monitor.py`
- `scripts/auto_doctor.py`
- `scripts/pipeline_health.py`
- `scripts/subagent_watcher.py`

Then schedule them with cron/launchd.
Use heartbeats only when you truly need LLM reasoning.

Guide:
- `docs/CRON_HEARTBEAT_GUIDE.md`

---

## The battle-tested rules (the ones that keep uptime)

### Rule 1: Prefer cron/launchd scripts over heartbeats
Heartbeats are scheduled LLM calls.
Scripts are cheap.

Use:
- cron (Linux)
- launchd (macOS)

Guide:
- `docs/CRON_HEARTBEAT_GUIDE.md`

### Rule 2: Weekly audits prevent bloat
A real autonomous system grows.
Without audits, it grows into a confusing pile.

Guide:
- `docs/WEEKLY_AUDIT_GUIDE.md`

Template:
- `templates/weekly_audit_cron.sh`

### Rule 3: No hardcoded secrets. Ever.
If a token lands in git history, assume compromise.

Guide:
- `docs/SECURITY_HARDENING.md`

---

## Repo map (what to look at)

- `docs/` — the survival guides
- `scripts/` — monitoring + enforcement tools
- `templates/` — drop-in workspace files
- `config-examples/` — example OpenClaw configs

---

## Versioning / changes

See `CHANGELOG.md`.

---

## License

See the repository license file (if present). If none exists, add one before distributing.
