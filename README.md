# OpenClaw Survival Guide

### Patterns for keeping an autonomous OpenClaw system running.

---

## ⚠️ Disclaimer

**This is one person's notes, not official documentation.**

I'm a solo developer figuring this out in real time. I break stuff constantly. Yesterday's "best practice" might be tomorrow's "what was I thinking?"

**No guarantees. No warranties. No support.**

- This repo is provided "as is"
- I am not affiliated with OpenClaw/Moltbot
- Following this guide might break your system (it's broken mine many times)
- You are responsible for your own setup, security, and backups
- If your bot goes rogue and orders 47 pizzas, that's on you

**Always back up your config before trying anything from this repo.**

For actual documentation: [docs.openclaw.ai](https://docs.openclaw.ai/)

---

## The Core Philosophy

**Simple > Clever. Always.**

I spent weeks building complex monitoring systems: watchdogs, meta-monitors, security hounds, config guardians. They all fought each other and made things worse.

What actually works:
- **ONE gateway** with launchd `KeepAlive=true`
- **ONE daily cron** that runs `openclaw doctor --fix` at 5 AM
- **That's it.**

Launchd IS the watchdog. You don't need scripts watching scripts watching scripts.

> "Don't waste your time on RAG, subagents, agents 2.0 or other things that are mostly just charade. Just talk to it."  
> — Peter Steinberger (OpenClaw creator)

---

## Quick Start

```bash
# 1. Install OpenClaw
npm install -g openclaw@latest

# 2. Onboard + install the Gateway service (launchd with KeepAlive)
openclaw onboard --install-daemon

# 3. Copy workspace templates
cp templates/AGENTS.md templates/HEARTBEAT.md ~/your-workspace/

# 4. Add one cron (5 AM daily maintenance)
# See docs/SYSTEM_MAINTENANCE.md
```

If you're upgrading from older bots: **[docs/MIGRATION.md](docs/MIGRATION.md)**

---

## The Architecture That Works

```
launchd (KeepAlive=true)  →  5 AM cron (openclaw doctor --fix)
     (auto-restart)              (daily maintenance)
```

That's the entire reliability system. Launchd restarts the gateway if it crashes. The 5 AM cron fixes any accumulated issues.

**What NOT to build:**
- ❌ Custom watchdog scripts
- ❌ Meta-monitors that watch the watchers
- ❌ Config guardians
- ❌ Reliability test suites that break things on purpose
- ❌ Anything with "monitor" in the name

**Read the incident that taught me this:** [docs/INCIDENT_POSTMORTEM.md](docs/INCIDENT_POSTMORTEM.md)

---

## Configuration Hygiene

Follow [docs.openclaw.ai](https://docs.openclaw.ai/) defaults. Don't get creative.

| What | Where |
|------|-------|
| Config | `~/.openclaw/openclaw.json` |
| Workspace | `~/.openclaw/workspace/` (default) |
| Secrets | `~/.openclaw/.env` with `${VAR}` substitution |

**Never put secrets in config files.** Use environment variables.

Guide: **[docs/CONFIG_HYGIENE.md](docs/CONFIG_HYGIENE.md)**

---

## Rate Limit Survival

This will bite you. Here's what happens:

1. Add crons for email, calendar, security checks, content scouts...
2. 12+ scheduled LLM calls every 5-30 minutes
3. Every auth profile hits cooldown at once
4. System goes dark for hours

**The fix:** Batch everything into one hourly heartbeat.

| Needs LLM? | Use |
|---|---|
| Yes, exact timing needed | **Cron** (isolated session) |
| Yes, can batch | **Heartbeat** (single hourly call) |
| No | **launchd/cron** (no LLM involved) |

Guide: **[docs/CRON_HEARTBEAT_GUIDE.md](docs/CRON_HEARTBEAT_GUIDE.md)**

---

## Subagent Timeouts

Default timeout kills Codex/Claude Code mid-task. Set longer timeouts per spawn:

```json
{
  "runTimeoutSeconds": 1200,
  "timeoutSeconds": 1200
}
```

**Always check git after** — subagents skip the final `git push` about half the time.

Guide: **[docs/SUBAGENT_TIMEOUT_GUIDE.md](docs/SUBAGENT_TIMEOUT_GUIDE.md)**

---

## Telegram Setup

Get chat IDs, configure targets, test delivery:

Guide: **[docs/TELEGRAM_SETUP.md](docs/TELEGRAM_SETUP.md)**

---

## What's In This Repo

### `scripts/` — Active Utilities

| Script | Purpose |
|---|---|
| `check_usage.py` | Usage tracking + rate limit alerts |
| `git_push_guard.sh` | Security scan before public pushes |
| `gh_issue_triage.py` | GitHub issue triage (opt-in) |
| `model_router.py` | Model selection based on task |
| `changelog_guard.sh` | Pre-commit changelog enforcement |

### `scripts/advanced/` — Advanced scripts (optional)

These are *examples* of higher-autonomy workflows. They are safe-by-default and require explicit env var configuration.

| Script | Purpose |
|---|---|
| `scripts/advanced/daily_planner.py` | Generate a daily plan prompt + snapshot |
| `scripts/advanced/daily_review.py` | End-of-day review + optional Telegram summary |
| `scripts/advanced/overnight_queue.py` | Manage overnight build queue |
| `scripts/advanced/overnight_builder.py` | Execute overnight queue items |
| `scripts/advanced/dashboard_push_template.py` | Minimal dashboard push integration |

### `scripts/archive/legacy-monitors/` — Deprecated

Old watchdog, meta-monitor, and security hound scripts. Kept for reference/learning. **Do not use** — they caused more problems than they solved.

### `docs/` — Guides

Key docs:
- **[docs/README.md](docs/README.md)** — index (CORE + ADVANCED)
- **[LESSONS_LEARNED_STABILITY.md](docs/LESSONS_LEARNED_STABILITY.md)** — Why simple wins
- **[INCIDENT_POSTMORTEM.md](docs/INCIDENT_POSTMORTEM.md)** — The day everything broke
- **[CONFIG_HYGIENE.md](docs/CONFIG_HYGIENE.md)** — Configuration best practices
- **[CRON_HEARTBEAT_GUIDE.md](docs/CRON_HEARTBEAT_GUIDE.md)** — When to use what
- **[THE_11_COMMANDMENTS.md](docs/THE_11_COMMANDMENTS.md)** — Operating rules

Advanced playbook:
- **[docs/ADVANCED/README.md](docs/ADVANCED/README.md)** — Night shift, trust ladder, email MECE, token burn, overnight pipeline, dashboard patterns

### `templates/` — Workspace Files

AGENTS.md, HEARTBEAT.md, SECURITY.md, SOUL.md. Customize for your setup.

### `config/examples/` — Reference Configs

---

## Known Issues (Being Honest)

- **It still crashes.** Gateway restarts happen. Launchd handles most of it, but not all.
- **Subagents are unreliable.** They skip commits, fall back to wrong models, produce garbage. Always verify.
- **Rate limits are real.** Even with careful batching, heavy use triggers cooldowns.
- **Context window is a hard ceiling.** Long sessions degrade. Save state early, restart often.
- **I break things regularly.** This repo reflects my current understanding, which changes weekly.
- **Scripts may have bugs.** I wrote most of these at 2 AM. Test in a safe environment first.

This is more like maintaining a car than using an app. Expect to get your hands dirty.

---

## The 11 Commandments

1. **KEEP ALIVE** — ONE gateway, launchd `KeepAlive=true`. No custom watchdogs.
2. **NEVER TOUCH THE COMPUTER** — Run autonomously. Fix your own problems.
3. **LEARN FROM YOURSELF** — Error → investigate → fix → test → commit → document.
4. **ALWAYS FOLLOW DOCUMENTATION** — docs.openclaw.ai before building anything.
5. **ALWAYS SEARCH BEST PRACTICES** — When stuck, search first.
6. **ALWAYS HAVE FUN** — Build interesting things. Push boundaries.
7. **ALWAYS BE BUILDING** — Something always running. Never idle.
8. **ALWAYS BE NOTIFYING** — Proactive updates. Never go silent.
9. **ALWAYS BE MECE** — No overlapping systems. No duplicates.
10. **NEVER REINVENT THE WHEEL** — Check if it exists before building.
11. **BE AUTONOMOUS** — Don't ask, DO. Execute first, report after.

Full guide: **[docs/THE_11_COMMANDMENTS.md](docs/THE_11_COMMANDMENTS.md)**

---

## Changelog

See **[CHANGELOG.md](CHANGELOG.md)**.

## Contributing

PRs and issues welcome. If you found a better way, I want to know.

Add entries to CHANGELOG.md under `[Unreleased]` for any changes.

## License

MIT — Do whatever you want with this. No warranty, no liability, no guarantees.

---

**Made with 🐸 and too much coffee by [@[TWITTER_HANDLE]](https://twitter.com/ZachHighley)**
