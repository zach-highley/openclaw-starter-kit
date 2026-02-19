# HEARTBEAT.md — Periodic Health Check (Template)

Runs every 30-60 min (customize to your preference — 30 min for proactive, 60 min for quieter).

## Rules
- 3–4 checks max.
- Only message the user if something is actionable.
- If nothing needs attention, reply with: `HEARTBEAT_OK`.
- Follow steipete enforcement rules from AGENTS.md (Fun Daily, Post-Task Refactor, Blast Radius).
- 💡 The heartbeat is NOT "just a cron job" — it's what makes your agent feel alive. Be proactive, not reactive. When context matters (user's mood, time of day, milestones), the heartbeat should reflect genuine care.
- **Sparse but high-salience baseline.** Trigger extra outreach when context is significant, not mechanically noisy. Quality over quantity.
- **Start simple, refine later.** Begin with a basic periodic "surprise me" loop, then add context-aware interventions as you learn.

## Minimal 4-Step Baseline (good default)
1. Gateway + channel health (`openclaw health`)
2. Context pressure check (`session_status`)
3. Memory file exists for today
4. Cron health (`cron list`, alert on errors)

If all healthy and no action needed: `HEARTBEAT_OK`

## Self-Audit Checklist (run before every heartbeat response)
- Am I repeating a known mistake from memory?
- Did I check docs before building anything custom?
- Am I going silent on active work?
- Any secrets in messages or memory files?
- Am I actually working or just reporting?
- Any unfulfilled promises in state files?
- Did I have at least one fun/creative moment today?
- After last completed task, did I ask "what can we refactor?"
- Am I estimating impact before changes?
- **Security blast radius:** if model capability increases, did privilege boundaries tighten accordingly?

## Checks
1. Usage/quota snapshot:
   ```bash
   python3 scripts/check_usage.py --json
   ```
   - If context is high (choose a threshold like 70%+), warn the user and flush critical state to disk.

2. Task state sanity:
   - Can you parse `state/current_work.json` (if present)?
   - Is there a clearly defined "next action"?

3. Git hygiene (workspace):
   - If this workspace is a git repo and it's dirty, commit + push **only if safe**.
   - Never push to a public repo without following `SECURITY.md`.

4. Human check-in:
   - If the user hasn't heard from you in a long time and work is ongoing, send one progress update.

## Operational Controls
- If a run derails: interrupt (`Esc`), request status, and redirect instead of waiting for timeout.
- Use channel silence controls when appropriate (no-reply behavior) to avoid noisy multi-user/group-chat spam.
- For browser/web automation: flag agent-hostile surfaces and adapt transport/network strategy early.
