# Meta-Monitor — The Operations Manager

The meta-monitor watches everything else. It's the monitor that monitors the monitors.

## What It Does

Every heartbeat, it checks:
- **Work loop health** — is the sprint system running? Stalled? Queue stuck?
- **Script health** — are monitoring scripts erroring out?
- **Gateway health** — is the bot process stable? Restarting too often?
- **Context usage** — is the session getting full? Time to reset?
- **Memory freshness** — are daily files being written? Is learning happening?

## Usage

```bash
# Quick health check (read-only)
python3 scripts/meta_monitor.py --check

# JSON output for parsing
python3 scripts/meta_monitor.py --check --json

# Lightweight heartbeat mode (skip heavy checks)
python3 scripts/meta_monitor.py --check --mode heartbeat

# Attempt auto-recovery on issues found
python3 scripts/meta_monitor.py --fix
```

## When to Escalate

The meta-monitor reports a severity level:
- **OK** — everything's fine
- **WARN** — something's degraded but not broken
- **ESCALATE** — 3+ systems stalled/broken, message the user immediately

## Adding to Your Heartbeat

```markdown
## 🔍 Meta-Monitor (every heartbeat — fast)
Run `python3 scripts/meta_monitor.py --check --mode heartbeat`
If it reports ESCALATE, message [USER] with the summary.
```

## Why It Matters

Without a meta-monitor, individual monitors can silently break. The security hound stops running. The usage checker crashes. You don't notice until you're over budget or exposed. The meta-monitor catches that drift.
