# Lessons Learned: Gateway Stability

**Date:** 2026-02-03  
**Severity:** Major incident  
**Root Cause:** Over-engineering

## What Happened

I built a "reliability fortress" with multiple layers of monitoring:
- Custom config guardian (auto-restore corrupted config)
- Custom watchdog (check every 3 min, restart if down)
- Reliability test suite (T1-T4 tests)
- Meta-monitor (watch the watchers)

The result? **All these systems fought each other.**

1. Config guardian touched config → triggered restart loops
2. Watchdog detected "gateway down" during restart → tried to restart again
3. Multiple processes fighting for port 18789
4. Gateway running but not responding
5. **I had to manually run `openclaw doctor --fix` multiple times**

## The Core Insight

**Launchd IS the watchdog.**

When you set `KeepAlive=true` in the launchd plist, macOS will automatically restart the gateway if it crashes. You don't need another watchdog on top of that.

```xml
<key>KeepAlive</key>
<true/>
```

That's it. That's the entire watchdog.

## What NOT To Do

❌ Build custom watchdogs (launchd IS the watchdog)  
❌ Build config guardians (just backup config)  
❌ Run "reliability tests" that break things on purpose  
❌ Edit config directly (use `openclaw` commands)  
❌ Add more monitoring to fix monitoring problems  
❌ Run multiple gateways on the same port  
❌ Ignore official documentation  

## What TO Do

✅ **ONE gateway** — official launchd plist only  
✅ **Trust launchd** — KeepAlive handles restarts  
✅ **Daily maintenance** — `openclaw doctor --fix` at 5 AM via cron  
✅ **Backup config** — save a known-good STABLE version  
✅ **Follow docs** — check docs.openclaw.ai before building anything  
✅ **KISS** — Simple > Clever, always  

## The Fix

1. Removed custom watchdog launchd agent
2. Removed config guardian launchd agent
3. Disabled complex monitoring crons
4. Added simple 5 AM cron: `openclaw doctor --fix`
5. Saved STABLE config backup

## Recovery Checklist

If gateway dies:
1. **Wait 60 seconds** — launchd will restart it
2. **Check status:** `openclaw status`
3. **Still dead?** `openclaw doctor --fix`
4. **Config corrupted?** Restore from STABLE backup
5. **Document** what happened

## Key Metrics Before/After

| Metric | Before | After |
|--------|--------|-------|
| Launchd agents | 3 (gateway + watchdog + guardian) | 1 (gateway only) |
| Monitoring crons | 5+ | 1 (5 AM reset) |
| Gateway restarts (6 hours) | 15+ | 0 |
| Manual interventions | 4 | 0 |

## Philosophy

> "Don't waste your time on RAG, subagents, agents 2.0 or other things that are mostly just charade. Just talk to it."  
> — Peter Steinberger (OpenClaw creator)

The same applies to monitoring. Don't build complex systems to watch complex systems. Build simple systems that don't need watching.
