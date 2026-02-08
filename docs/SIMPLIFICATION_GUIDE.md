# Simplification Guide — Less Tools, More Product

*"Don't waste your time on RAG, CLI terminals, agents 2.0 or other things that are mostly just charade. Just talk to it."* — Peter Steinberger (OpenClaw creator)

## The Problem

It's incredibly easy to fall into the "agentic trap": building tools to manage tools instead of building product. After a few days of enthusiastic setup, you might find yourself with:

- 75+ scripts (most monitoring other scripts)
- 18+ cron jobs (many erroring silently)
- 40+ state files (most never read)
- 20+ enforcement hooks (that the model ignores anyway)
- Named "council members" watching each other in circles

This happened to us. Codex audited our system and scored **bloat 6.0/10** — the lowest category.

## The Fix

### Scripts: Keep ~25, Archive the Rest

**Keep:**
- Usage monitoring (`check_usage.py`) — one script for the status line
- Morning report — real daily value
- Email scanner — real notification value
- Dashboard data push — actual product
- Personal automation (lights, cameras, alarms) — Steipete-approved
- Git security guard — simple, essential
- App health monitoring (Sentry, Xcode Cloud) — real product value

**Archive (don't delete):**
- Meta-monitors (watchers watching watchers)
- Model routing scripts (the rules fit in AGENTS.md)
- Self-healing protocols (OpenClaw has `openclaw doctor`)
- Session monitors (OpenClaw handles this natively)
- Config pre-flight scripts (just be careful)
- Auto-recovery scripts (OpenClaw handles restarts)

### Crons: Keep ~10, Kill the Rest

**Keep:**
- Morning briefing (daily, exact time needed)
- Overnight build (daily, exact time needed)
- Daily maintenance + update (daily)
- Weekly summary/audit (weekly)
- Subscription reminders (one-shot)

**Kill:**
- Hourly check-ins (heartbeat handles this)
- Security checks (built into weekly audit)
- Content scouts (do this yourself in the main session)
- Auto-doctor (use `openclaw doctor` instead)
- Email triage (fold into heartbeat)

### Heartbeat: 3 Checks Max

```markdown
# HEARTBEAT.md

1. Check usage — alert if limits approaching
2. Git status — commit any uncommitted work
3. Human check — send update if silent for 30+ min
```

That's it. No Council. No scripts watching scripts.

### AGENTS.md: 4KB, Not 15KB

Keep:
- Prime directive
- Model routing (2 rules: Codex for code, Opus for everything else)
- Communication rules (be verbose, never go silent)
- Status line format
- Task persistence

Cut:
- Named "council members"
- 20+ mid-session enforcement hooks
- Elaborate self-healing protocols
- MECE enforcement rules (just be sensible)

## OpenClaw's Built-In Tools Replace Custom Scripts

| Custom Script | OpenClaw Replacement |
|--------------|---------------------|
| `meta_monitor.py` | `openclaw status --deep` |
| `auto_doctor.py` | `openclaw doctor --non-interactive` |
| (removed) | launchd KeepAlive handles restarts |
| `session_monitor.py` | `openclaw sessions --json` |
| `config_preflight.py` | `openclaw doctor --fix` |
| `context_healer.py` | OpenClaw auto-compaction + memory flush |

## The Philosophy

1. **Just talk to it.** No orchestrators, no meta-monitoring.
2. **CLIs > MCPs.** Agents learn CLIs naturally.
3. **Stay in the loop.** Human-in-the-loop produces better product.
4. **Codex for code, Opus for everything else.** That's the whole routing strategy.
5. **Don't build tools to manage tools.** Build product instead.

## How to Simplify

1. `mkdir scripts/archive` — archive, don't delete
2. Move anything that monitors another script
3. Move anything OpenClaw handles natively
4. Rewrite HEARTBEAT.md to 3 checks
5. Trim AGENTS.md to essentials only
6. Kill erroring crons (they're burning tokens for nothing)
7. Use `openclaw doctor` and `openclaw status --deep` instead of custom health checks
8. Commit, push, and get back to building product
