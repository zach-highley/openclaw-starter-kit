# OpenClaw Survival Guide

### Patterns for keeping an autonomous OpenClaw system running.

I've been running OpenClaw 24/7 for about a week. It breaks constantly. The gateway crashes at 3 AM, subagents die mid-task, rate limits hit when you least expect it, and scripts pile up faster than you can track them.

But it's getting better. Every failure teaches you something, and if you encode those lessons into scripts and rules, the system starts fixing itself. That's what this repo is: the stuff I learned the hard way so you don't have to.

**Fair warning:** This is not polished software. It's a collection of scripts, templates, and docs from a solo developer figuring this out in real time. Some of it is rough. Some of it will need adapting to your setup. But it works, most of the time, and when it doesn't, the monitoring layer catches it.

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

Four layers, each watching the one below:

```
watchdog  →  meta-monitor  →  auto-doctor  →  weekly audit
 (5 min)      (watches         (deep health     (catches
  keeps it     the watchers)    + state save)     entropy)
  alive)
```

- **Watchdog** — Every 5 minutes. Gateway down? Restart it. Telegram dead? Flag it. Dumb and reliable.
- **Meta-Monitor** — Watches the watchers. Your monitoring scripts will crash too. This catches that.
- **Auto-Doctor** — Every 4 hours. Deep diagnostics, state save, context check. If context is dangerously high, triggers a safe restart.
- **Weekly Audit** — Catches slow rot. Orphaned scripts, overlapping crons, stale state, secrets in git.

Scripts: `scripts/watchdog.sh`, `scripts/meta_monitor.py`, `scripts/auto_doctor.py`

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

Night shift updates (overnight autonomy + high-signal Telegram templates): `docs/NIGHT_SHIFT.md`

---

## Subagent timeouts

If you're using Codex MAX or Claude Code for subagents, the default timeout will kill them mid-task. I was running 3-minute timeouts on tasks that need 10-20 minutes. Codex would be halfway through a refactor and just die.

What actually works:
- **2-hour timeout** for subagents (global `timeoutSeconds: 7200`)
- **Completion callbacks** instead of polling (OpenClaw notifies when done)
- **Always check git after** — subagents skip the final `git push` about half the time

Guide: `docs/SUBAGENT_TIMEOUT_GUIDE.md`

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
# 1. Install OpenClaw
curl -fsSL https://openclaw.ai/install.sh | bash
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

## License

MIT.
