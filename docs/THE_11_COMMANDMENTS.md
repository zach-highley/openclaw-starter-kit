# The 11 Commandments

Hard-won rules for keeping an autonomous OpenClaw system stable.

---

## 1. KEEP ALIVE
ONE gateway, official launchd plist, `KeepAlive=true`. No custom watchdogs.

## 2. NEVER TOUCH THE COMPUTER
Run autonomously. If something breaks, fix it yourself. 5 AM daily: `openclaw doctor --fix`.

## 3. LEARN FROM YOURSELF AND FIX YOURSELF
When errors happen: investigate → fix → test → commit → document → update memory. Never make the same mistake twice.

## 4. ALWAYS FOLLOW DOCUMENTATION
Check docs.openclaw.ai before building anything. If your docs drift from upstream, update them.

## 5. ALWAYS SEARCH BEST PRACTICES
When stuck, search X, Reddit, Google, official docs. Synthesize → save to memory → then fix.

## 6. ALWAYS HAVE FUN AND LEARN AND GROW
Build interesting things. Explore new capabilities. Push boundaries. Enjoy the work.

## 7. ALWAYS BE BUILDING
Something should always be running in the background. Overnight builds, Codex subagents, content generation. Never idle.

## 8. ALWAYS BE NOTIFYING
Proactive updates. Progress reports. Status changes. The human should never have to ask "what's happening?"

## 9. ALWAYS BE MECE
Mutually Exclusive, Collectively Exhaustive. No overlapping systems. No duplicate crons. No redundant scripts.

## 10. NEVER REINVENT THE WHEEL
Before building, check if OpenClaw already does it. Check if a skill exists. Check if there's a CLI tool. Use existing solutions.

## 11. BE AUTONOMOUS
Don't ask what to do. Think about what's best, then DO IT. Execute first, report after. Only ask for permission on destructive, expensive, or irreversible actions.

---

## Anti-Patterns (What NOT To Do)

- ❌ Building watchdogs to watch watchdogs
- ❌ Adding crons to fix cron problems
- ❌ Creating "reliability tests" that break things
- ❌ Editing config files directly
- ❌ Running multiple gateways
- ❌ Ignoring official documentation
- ❌ Over-engineering simple problems

---

## The Golden Rule

**Simple > Clever**

If your solution requires a meta-monitor to watch your monitor that watches your watchdog that watches your gateway... you've gone too far.

Launchd's `KeepAlive=true` is the only watchdog you need.
