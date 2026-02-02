# Beginner Start Here

This repo is a survival guide for running OpenClaw continuously.

If you are a beginner, start with these three docs in order:

1) **docs/MIGRATION.md**
   - Upgrading from clawdbot/moltbot/older OpenClaw

2) **docs/CRON_HEARTBEAT_GUIDE.md**
   - The simplest way to keep the system alive without rate limiting

3) **docs/BOT-HEALTH-CHECKS.md**
   - What to check when something feels off

## Minimal, professional operating rules

- Prefer **one heartbeat** for recurring LLM tasks.
- Keep HEARTBEAT.md tiny.
- Use `openclaw doctor --non-interactive` whenever the gateway behaves strangely.
- Use `openclaw health` and `openclaw logs --tail 200` before debugging blind.

## Recommended docs (next)

- **docs/CONFIG_SAFETY.md**
- **docs/MODEL_FAILOVER_GUIDE.md**
- **docs/SECURITY_HARDENING.md**
- **docs/WEEKLY_AUDIT_GUIDE.md**
