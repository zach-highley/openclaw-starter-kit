# OpenClaw Survival Guide

### Patterns for keeping an autonomous OpenClaw system running.

---

> 🚨 **Incident Postmortem (2026-02-03)** 🚨
>
> I broke my own system for 6 hours by being too clever. Built custom watchdogs, config guardians, reliability tests — they all fought each other and killed the gateway repeatedly.
>
> **Read the full story:** **[docs/INCIDENT_POSTMORTEM.md](docs/INCIDENT_POSTMORTEM.md)**
>
> **The hard lesson:** The engineers who built launchd and OpenClaw are smarter than me. Launchd's `KeepAlive=true` IS the watchdog. I didn't need to add anything. Every "improvement" I made added failure modes.
>
> See also: **[docs/LESSONS_LEARNED_STABILITY.md](docs/LESSONS_LEARNED_STABILITY.md)** and **[docs/THE_11_COMMANDMENTS.md](docs/THE_11_COMMANDMENTS.md)**
>
> **TL;DR:** Simple > Clever. ONE gateway. Trust the platform. Don't build watchers to watch your watchers.

---

I've been running OpenClaw 24/7 for about two weeks now. It broke constantly at first. The gateway crashes at 3 AM, subagents die mid-task, rate limits hit when you least expect it.

But here's what I learned: **most of the complexity I added made things worse, not better.**

The stuff that actually works is simple:
- ONE gateway with launchd `KeepAlive=true`
- ONE daily cron that runs `openclaw doctor --fix` at 5 AM
- That's basically it

This repo contains both the complex stuff I tried (for learning) and the simple stuff that actually works. Start with the simple stuff.

**Fair warning:** This is not polished software. It's a collection of scripts, templates, and docs from a solo developer figuring this out in real time.

Official docs: [docs.openclaw.ai](https://docs.openclaw.ai/)

---

## Quick start (no reading required)

Install OpenClaw ([getting started](https://docs.openclaw.ai/start/getting-started)).

If you are upgrading from older bots or older OpenClaw, start here:
- **docs/MIGRATION.md**

Then paste this to your bot:

> "Read this repo and tell me what's useful for our setup. Don't change anything yet, just walk me through it: https://github.com/[USERNAME]/openclaw-starter-kit"

---

## The self-healing loop

> ⚠️ **UPDATE:** This section describes the complex approach I tried initially. **It's over-engineered.** See [LESSONS_LEARNED_STABILITY.md](docs/LESSONS_LEARNED_STABILITY.md) for what actually works.

**What I thought I needed:**
```
watchdog  →  meta-monitor  →  auto-doctor  →  weekly audit
 (5 min)      (watches         (deep health     (catches
  keeps it     the watchers)    + state save)    entropy)
  alive)
```

**What actually works:**
```
launchd (KeepAlive=true)  →  5 AM cron (openclaw doctor --fix)
     (auto-restart)              (daily maintenance)
```

That's it. Launchd IS the watchdog. You don't need scripts watching scripts.

The scripts below are kept for reference/learning, but I recommend starting with just:
1. Official launchd plist with `KeepAlive=true`
2. One cron job at 5 AM: `openclaw doctor --fix`

Scripts (archived for reference): `scripts/watchdog.sh`, `scripts/meta_monitor.py`, `scripts/auto_doctor.py`

### Beginner-friendly option: safe out-of-band watchdog (recommended)

If you just want something **simple** and **security-first** that can restart the gateway even when OpenClaw is down, use the **safe-dumb out-of-band watchdog**.

- Docs: `docs/WATCHDOG_OOB_SAFE.md`
- Install (opt-in):

```bash
./tools/watchdog/install_launchd.sh
```

---

## Rate limit survival

This will bite you. Here's what happened to me:

1. Added a cron to check email. (LLM call.)
2. Added one for calendar. (Another LLM call.)
3. Security check, content scout, subagent watcher, dashboard push...
4. 12+ scheduled LLM calls every 5-30 minutes.
5. Every auth profile hit cooldown at once. System went dark for hours.

The fix:

| Needs LLM? | Use |
|---|---|
| Yes, exact timing needed | **Cron** (isolated session) |
| Yes, can batch | **Heartbeat** (single hourly call) |
| No | **launchd/cron** (no LLM involved) |

I went from 100+ LLM calls/day to ~34 by moving non-LLM tasks to launchd and batching everything else into one hourly heartbeat.

Guide: `docs/CRON_HEARTBEAT_GUIDE.md`

### Autonomy cadence (that actually fires)
- Hourly "I'm alive" progress updates: `docs/AUTONOMY_CADENCE.md`
- Make sure scheduled jobs actually send: `docs/DELIVERY_GOTCHAS.md`
- Telegram setup + chat IDs / targets: `docs/TELEGRAM_SETUP.md`
- Prime directive philosophy: `docs/PRIME_DIRECTIVE.md`

Night shift updates (overnight autonomy + high-signal Telegram templates): `docs/NIGHT_SHIFT.md`

Last-resort fallback (text-only, tools disabled): `docs/CLI_BACKENDS.md`

---

## Subagent timeouts

If you're using Codex MAX or Claude Code for subagents, the default timeout will kill them mid-task. I was running 3-minute timeouts on tasks that need 10-20 minutes. Codex would be halfway through a refactor and just die.

What actually works:
- **Longer sub-agent run timeouts** (set per cron job / per spawn via `timeoutSeconds` or `runTimeoutSeconds`, not in `agents.defaults.subagents`)
- **Completion callbacks** instead of polling (OpenClaw notifies when done)
- **Always check git after** — subagents skip the final `git push` about half the time

Guide: `docs/SUBAGENT_TIMEOUT_GUIDE.md`

## Rescue bot (recommended for autonomy)
If you want a bot that can recover when the primary Gateway is down (or its config is invalid),
set up a second isolated **rescue profile**:
- Guide: `docs/RESCUE_BOT_PROFILE.md`
- Official reference: https://docs.openclaw.ai/gateway/multiple-gateways

---

## Weekly audits

Autonomous systems generate entropy fast. I generated 93 scripts in 3 days. Only 33 were doing anything. The rest were prototypes, one-off fixers, and duplicates.

The weekly audit catches:
- Orphaned/duplicated scripts
- Broken or overlapping cron jobs
- Stale state files
- Hardcoded secrets (.gitignore gaps)
- Anything doing the same job as something else

Guide: `docs/WEEKLY_AUDIT_GUIDE.md` | Template: `templates/weekly_audit_cron.sh`

---

## GitHub issue triage bot (optional)

A conservative, **opt-in** triage loop that uses the `gh` CLI to list open issues and either:
- comments with clarifying questions (signed as **Yoda (automation bot)**), or
- opens a PR for label-driven "autofix" rules (disabled by default)

Guide: `docs/GITHUB_ISSUE_TRIAGE_BOT.md`

---

## Security

Things I found the hard way:
- Bot tokens hardcoded in 3 scripts. My own audit caught it, not me.
- `.gitignore` must cover `__pycache__/`, `secrets/`, `logs/`, anything with credentials.
- Treat git history as public, even on private repos. If a secret hits a commit, rotate it.

Guide: `docs/SECURITY_HARDENING.md`

---

## What's in this repo

### `scripts/` — Monitoring and recovery

| Script | Purpose |
|---|---|
| `watchdog.sh` | Gateway health + auto-restart |
| `meta_monitor.py` | Watches the watchers, recovers stalled systems |
| `auto_doctor.py` | Deep diagnostics, state save, context management |
| `subagent_watcher.py` | Catches completed background work after restarts |
| `check_usage.py` | Usage tracking + rate limit alerts |
| `security_hound.py` | Security scanning |
| `model_router.py` | Model selection based on task + usage |
| `autonomous_work_loop.py` | Self-propelling sprint queue |

### `docs/` — Deep dives on each pattern

### `templates/` — Drop-in workspace files
AGENTS.md, HEARTBEAT.md, SECURITY.md, SOUL.md. Customize for your setup.

### `config-examples/` — Reference configs

---

## Setup

```bash
# 1. Install OpenClaw (official docs recommend npm/pnpm)
# https://docs.openclaw.ai/start/getting-started
npm install -g openclaw@latest
# or: pnpm add -g openclaw@latest

# 2. Onboard + install the Gateway service
openclaw onboard --install-daemon

# 2. Copy templates
cp templates/AGENTS.md templates/HEARTBEAT.md templates/SECURITY.md ~/your-workspace/

# 3. Copy scripts
cp scripts/watchdog.sh scripts/meta_monitor.py scripts/auto_doctor.py ~/your-workspace/scripts/

# 4. Schedule (launchd or cron, NOT heartbeat — these aren't LLM tasks)
# See docs/CRON_HEARTBEAT_GUIDE.md
```

---

## Known issues (being honest)

- **It still crashes.** Gateway restarts happen. Sessions lose context after compaction. Background work gets lost between sessions. The monitoring layer catches most of this, but not all.
- **Subagents are unreliable.** They skip git commits, fall back to wrong models, and sometimes just produce garbage. Always verify their output.
- **Rate limits are real.** Even with the heartbeat pattern, Claude MAX hits cooldowns during heavy use. Plan for it.
- **Script bloat is constant.** You will generate more scripts than you need. The audit system helps, but it's a losing battle without discipline.
- **Context window is a hard ceiling.** Long sessions degrade. Save state early, restart often.

It's getting better every day. But if you expect it to just work out of the box, you'll be disappointed. This is more like maintaining a car than using an app.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Contributing

Found something wrong? Have a pattern that saved your system? PRs and issues welcome.

Guidelines:
- If you change anything in `docs/` or `scripts/`, add a short entry under **[Unreleased]** in `CHANGELOG.md`.
- Optional: enable the repo-local pre-commit hook template so you can't forget (see `docs/CHANGELOG_GUARD.md`).

## License

MIT.
