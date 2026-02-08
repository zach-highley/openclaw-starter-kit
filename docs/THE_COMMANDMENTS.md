# The Operating Commandments

> Rules for running an autonomous OpenClaw agent that doesn't fall apart.
> Learned through months of trial, error, and "why did I build that?"

---

## 1. KEEP ALIVE

**ONE gateway. Official service manager. `KeepAlive=true`. No custom watchdogs.**

```bash
# macOS: launchd (installed via `openclaw onboard --install-daemon`)
# Linux: systemd unit with Restart=always
```

launchd IS the watchdog. You do not need scripts watching scripts watching scripts. That path leads to a monitoring death spiral where your watchers fight each other and take down the system.

---

## 2. AUTOMATE EVERYTHING

**If the user does something twice, script it.**

The goal: the user should never have to open a terminal. Every repeated task becomes a script, every script becomes a cron, every cron becomes invisible.

---

## 3. LEARN AND FIX

**Error → investigate → fix → test → commit → document. Never repeat the same failure.**

When something breaks:
1. Diagnose the root cause (not just the symptom)
2. Fix it
3. Test the fix
4. Commit the fix
5. Document what happened in `memory/incidents.md`
6. Update any relevant docs or configs

If you hit 3+ errors on the same topic: STOP. Search official docs, community resources, forums. Synthesize what you find, then fix.

---

## 4. FOLLOW OFFICIAL DOCS

**[docs.openclaw.ai](https://docs.openclaw.ai/) before inventing solutions.**

Before building ANYTHING, check:
1. Does OpenClaw already do this natively?
2. Is there a skill for it on [clawhub.com](https://clawhub.com)?
3. Is there a CLI tool that handles it?
4. Is there a config option for it?

If the answer to any is "yes", use it. Don't reinvent.

---

## 5. SEARCH BEFORE BUILDING

**Check if it exists before creating it.**

Before creating ANY file, script, or system:
- Search your own workspace
- Check if a skill exists
- Check if there's a CLI tool
- Search community resources

This applies to everything: docs, scripts, configs, state files, cron jobs. Search first, create second.

---

## 6. BUILD REAL THINGS

**Ship deliverables. No narrative-heavy status updates that produce nothing.**

Every task should pass the test: real usage? real output? real value? If it's just words about work instead of actual work, stop and redirect.

---

## 7. ALWAYS NOTIFY

**The user should never have to ask "what's happening?"**

Proactive updates. Progress reports. Status changes. If something takes more than a few minutes, check in. If you found something interesting during work, report it immediately. Don't wait until the end.

---

## 8. BE MECE

**Mutually Exclusive, Collectively Exhaustive. No overlapping systems. No duplicates.**

Before adding ANY recurring task:
- Check what crons already exist (`openclaw cron list`)
- Check what the heartbeat already covers
- Confirm no overlap with existing jobs
- Confirm the new job fills a genuine gap

One source of truth for each concern. No two crons doing related work.

---

## 9. DON'T REINVENT THE WHEEL

**Reuse existing scripts, skills, and infrastructure.**

The OpenClaw ecosystem has skills, the CLI has commands, the config has options. Most things you want to build already exist in some form. Use them.

---

## 10. SANDBOX THE RISKY

**Public pushes, deletions, spending, external contacts need confirmation.**

Safe operations: execute first, report after.
Risky operations: confirm first, execute after.

Risky = irreversible, expensive, public-facing, or contacts external parties.

---

## 11. THESIS-DRIVEN WORK

**Every task must produce real value. Ship code, not words.**

Before starting any work, ask:
- Does this have a real usage loop?
- Does it produce real output?
- Does it create real value?

If the answer to any is "no", find something that does.

---

## Anti-Patterns (Things That Seem Good But Aren't)

| Seems Good | Actually Bad | Why |
|-----------|-------------|-----|
| Custom watchdog scripts | System fights itself | launchd/systemd already does this |
| Meta-monitors | Complexity explosion | Monitoring the monitors monitoring the monitors |
| 5-minute heartbeat | $50/day token burn | 30-60 min is plenty for personal use |
| Config guardians | False positives galore | `openclaw doctor` already validates |
| Multiple gateway instances | State conflicts | ONE gateway, always |
| Subagent chains | Hallucination compounding | Fresh CLI context > accumulated drift |
| "Quick wins" that take 15 min | Distraction from real work | Build antelopes, not mice |

---

## The Simplification Principle

> "Don't waste your time on RAG, subagents, agents 2.0 or other things that are mostly just charade. Just talk to it."
> — Peter Steinberger (OpenClaw creator)

**Simple > Clever. Always.**

The most stable system is the one with the fewest moving parts. Every layer of complexity is a potential failure point. Resist the urge to build elaborate monitoring, routing, or orchestration systems. The boring solution that works beats the clever solution that sometimes works.
