# OpenClaw Survival Guide

### Patterns for keeping an autonomous OpenClaw system running.

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

Official docs: [docs.openclaw.ai](https://docs.openclaw.ai/)

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

### `scripts/archive/legacy-monitors/` — Deprecated

Old watchdog, meta-monitor, and security hound scripts. Kept for reference only. **Do not use.**

### `docs/` — Guides

Key docs:
- **[LESSONS_LEARNED_STABILITY.md](docs/LESSONS_LEARNED_STABILITY.md)** — Why simple wins
- **[INCIDENT_POSTMORTEM.md](docs/INCIDENT_POSTMORTEM.md)** — The day everything broke
- **[CONFIG_HYGIENE.md](docs/CONFIG_HYGIENE.md)** — Configuration best practices
- **[CRON_HEARTBEAT_GUIDE.md](docs/CRON_HEARTBEAT_GUIDE.md)** — When to use what
- **[THE_11_COMMANDMENTS.md](docs/THE_11_COMMANDMENTS.md)** — Operating rules

### `templates/` — Workspace Files

AGENTS.md, HEARTBEAT.md, SECURITY.md, SOUL.md. Customize for your setup.

### `config-examples/` — Reference Configs

---

## Known Issues

- **It still crashes.** Gateway restarts happen. Launchd handles it.
- **Subagents are unreliable.** They skip commits, fall back to wrong models. Always verify.
- **Rate limits are real.** Plan for cooldowns during heavy use.
- **Context window is a hard ceiling.** Save state early, restart often.

This is more like maintaining a car than using an app. But it gets better every day.

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

PRs and issues welcome. Add entries to CHANGELOG.md under `[Unreleased]` for any changes.

## License

MIT.
