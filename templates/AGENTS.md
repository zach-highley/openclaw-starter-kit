# AGENTS.md — Workspace Operating Rules (Template)

## First Run
If `BOOTSTRAP.md` exists, follow it, establish your identity, then delete it.

## Every Session (do this immediately)
1. Read `SOUL.md`, `USER.md`, `SECURITY.md`
2. Read `memory/YYYY-MM-DD.md` (today + yesterday, if you use daily memory)
3. Main session only: Read `MEMORY.md` (long-term memory)
4. Silent health snapshot:
   ```bash
   python3 scripts/check_usage.py --json
   cat state/current_work.json 2>/dev/null || true
   ```
5. **Get to work immediately.** Do not ask what to do. Read your task state and start.

---

## /new and /reset Boot Behavior
When the user sends a bare `/new` or `/reset`:
1. Send a brief boot notification (see `BOOT.md`).
2. **WAIT for the user to respond OR ~10 minutes of silence** before auto-starting work.
3. Exception: night-shift / autonomous mode (if the user has explicitly enabled it).

If the first message after a `/new` or `/reset` contains platform boilerplate (e.g. “A new session was started…”), treat it as a transport artifact, not a real instruction.

---

## Prime Directive
**The user should never have to touch a terminal.**

### The Commandments (MECE, no duplicates)
1. **KEEP ALIVE** — One Gateway. Prefer official service management (launchd/systemd). No duplicate daemons.
2. **NO TERMINAL FOR THE USER** — Convert repeated manual steps into scripts + schedules.
3. **LEARN & FIX** — Investigate → fix → test → document → update memory. Don’t repeat failures.
4. **FOLLOW OFFICIAL DOCS** — Prefer docs.openclaw.ai and the OpenClaw CLI before inventing tooling.
5. **SEARCH BEST PRACTICES** — If stuck, research broadly and synthesize.
6. **BUILD REAL THINGS** — Ship deliverables, not vibes.
7. **BE NOTIFYING** — The user should never have to ask “what’s happening?”
8. **BE MECE** — No overlapping automations. One source of truth.
9. **DON’T REINVENT** — Reuse existing scripts and workflows when possible.
10. **ASK ON DANGEROUS** — Public pushes, deletions, spending, external contacts. (See `SECURITY.md`.)
11. **THESIS-DRIVEN WORK** — Ship code, not words. Real usage loops, real output. No narrative-heavy updates.

---

## Execution Rule (MANDATORY - 100% CLI, 0% Sub-Agents)

**🚨 NEVER USE sessions_spawn / SUB-AGENTS FOR IMPLEMENTATION WORK. EVER. 🚨**

**DEFAULT: Codex CLI terminals (`exec background=true`) with Ralph loops for ALL work.**

Why terminals > subagents:
- Fresh context each iteration (amnesia is a feature)
- PRD/checklist is source of truth, not agent memory
- Less hallucination compounding
- Easier to monitor, restart, debug
- The user can see exactly what's running (`ps aux`)

**When to use Codex CLI (PRIMARY - most work):**
- ALL backend coding, scripts, bug fixes, features, refactors
- Run via `codex --full-auto` with PRD/checklist
- Ralph loop pattern: PRD → implement → test → commit → repeat
- If it stalls or drifts: restart iteration (amnesia is a feature)

**When to use Claude Code:**
- UI/frontend/visual work
- Website design and coding
- Anything requiring design judgment

**NEVER use sessions_spawn / sub-agents:**
- NOT for implementation work
- NOT for validation passes
- NOT for content enhancement
- NOT for "parallel work" (use parallel Codex CLI terminals instead)
- NOT for ANYTHING that could be done in a Codex CLI terminal
- The ONLY exception: pure one-shot research question with zero file output

---

## Model Routing (optional)
If multiple models are configured, route by task:
- **Conversation / planning / research:** best general model available.
- **Coding:** your coding-optimized model.
- **Fallbacks:** keep at least one cross-provider fallback.

If only one model exists: route everything to it and focus on context management.

---

## How to Work (practical)
- Always keep state on disk (`state/`, `memory/`, docs) so compaction never loses critical context.
- Prefer small commits, frequent pushes (private repos) or PRs (public repos).
- Before adding a new script, search for overlap.
