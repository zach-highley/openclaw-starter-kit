# Changelog


## [4.4] — 2026-03-12

### Operational Hygiene Edition

**The theme:** small lessons that burn you exactly once — if you write them down.

#### What changed

- **DM allowlist auto-recovery** — if Telegram DMs go silent after an upgrade, run `openclaw doctor`. It auto-restores missing `allowFrom` entries. No manual config edit needed. Added to BOT-HEALTH-CHECKS.md post-upgrade checklist.

- **MEMORY.md capacity management** — memory files have a practical ~12,000 char limit. Add a Synthesis cron step: check size, trim stale entries when >90% full. Bloated memory files cause context pressure and degrade autonomous reasoning quality. Trimming is not data loss — it's curation.

- **Backup verification command** — `openclaw backup verify <path>` is valid. `openclaw backup list` is NOT (returns an error). When verifying backups in crons or heartbeats, use `verify`, not `list`.

- **Cron scheduling windows (stable pattern)** — production-proven layout for a 10-cron nightshift pipeline:
  - Waves 1–3: 11PM, 1AM, 2:30AM ET
  - Memory Review: 4:30AM → Synthesis: 4:45AM → Health Audit: 5:00AM → Maintenance: 5:30AM → Morning Briefing: 6:00AM
  - Leave 90-min gaps between intensive waves; avoid 8–9:30PM ET (conflicts with peak LLM load)
  - One-off scheduling anomalies (gateway restarts, etc.) self-resolve; don't rebuild the schedule over a single bad run.

- **Secrets audit cadence** — run `openclaw secrets audit` after each major update. New config fields (e.g., `gateway.auth.token`) may be newly flagged. Migration to managed secrets requires user sign-off; document findings, don't auto-migrate.

#### Why this matters

These are the kind of lessons that don't make headlines — they just waste 45 minutes if you don't know them. DM allowlist regeneration, backup command naming, cron window collision — none of these are obvious, but all of them have burned real operators running 24/7 pipelines.

The MEMORY.md capacity rule is the one that compounds: a bloated memory file slowly degrades every autonomous decision that reads it. Trim early, trim often.


## [4.3] — 2026-03-04

### Operational Resilience Edition

**The theme:** systems that fail cleanly and fix themselves before bothering you.

#### What changed

- **Fix-First Rule added to HEARTBEAT template** — before alerting the user, the agent tries to resolve the issue autonomously. "Hey I noticed X" without having already tried to fix X is noise. Only escalate if genuinely unfixable without human input (credentials, money, a decision).

- **Cron self-healing in heartbeat** — when `consecutiveErrors > 0` is detected, the heartbeat now re-runs the failing cron before alerting. Most cron failures are transient (rate limits, brief API outages). A re-run that succeeds stays silent. Only failures that persist after a re-run escalate.

- **Infrastructure Safety section added to AGENTS template** — three hard-won lessons:
  1. **Run `openclaw doctor` after every update.** Entrypoint mismatches (`dist/entry.js` vs `dist/index.js`) are a known post-update failure mode. Doctor catches them before they silently break restart recovery.
  2. **Use homebrew/system node in launchd, not nvm.** nvm-managed node paths break whenever you run `nvm use` or upgrade. `/opt/homebrew/bin/node` is stable across version switches.
  3. **No OAuth-backed fallback models.** OAuth tokens expire silently. When the primary hits a rate limit and the OAuth fallback is dead, both fail with a confusing compound error. Use `"fallbacks": []` to fail clean, or a second token-auth model.

- **Blocker wall detection documented** — if 3+ consecutive autonomous waves report the same blockers, stop scanning and wait. The antelope filter is working correctly. Repeated scanning produces noise without moving anything forward. One clear message to the user beats fifteen identical status checks.

#### Why this matters

v4.2 made agents useful during idle time. v4.3 makes them resilient when things break.

The fix-first pattern is the most impactful addition. Agents that immediately escalate every error to the user create alert fatigue. Agents that try to fix things quietly — and only escalate genuine blockers — are operators, not monitors.

The infrastructure safety lessons come from running 24/7 in production through multiple OpenClaw updates. The nvm/node and entrypoint issues both surfaced post-update and caused confusing failures that took time to diagnose. They're now documented so no one else has to learn them from scratch.


## [4.2] — 2026-02-22

### Builder Mode Edition

**The theme:** your agent should be earning its keep while you sleep — not just keeping the lights on.

#### What changed

- **Idle Builder Mode added to HEARTBEAT template** — if the user has been idle for 60+ minutes and all health checks pass, the agent auto-selects a task from `TODO.md` and executes it. No prompting required. One clear message on completion.
- **Antelope Filter added to AGENTS template** — every autonomous task must pass three gates: does it compound? is it revenue-linked? is it a week+ of real work? No to any = skip it. Eliminates the "busy work spiral" failure mode.
- **Anti-decay rule** — if 3 consecutive autonomous waves are housekeeping-only, the agent is forced to pick a real project next. Tracked in `state/`.
- **Priority order made explicit and enforced** — Revenue-generating → Visible shipping → Research → Fun/experimental. Not a suggestion, part of the task selection logic.
- **NO_REPLY discipline documented and hardened** — `NO_REPLY` must be the full message, never appended to real content. HEARTBEAT_OK treated the same way.
- **HEARTBEAT_OK protocol** — fully silent healthy heartbeats. The user only hears from the heartbeat when something breaks or ships. Messaging policy table added to template.
- **Pro Plan model guidance** — Opus is ideal; Sonnet is an acceptable fallback on budget plans. Don't fight the plan tier. Update your config accordingly.
- **README v4.2 section added** — all the above explained in plain English.

#### Why this matters

v4.1 made heartbeat quiet. v4.2 makes the agent useful during quiet time. The two complement each other:  
quiet heartbeat + idle builder = a bot that doesn't spam AND actually ships things.

The antelope filter is the most important thing in this release. Without it, autonomous agents drift into housekeeping spirals — reorganizing files, adjusting crons, rewriting docs — and call it "maintenance." With it, you get real compounding work.


## [4.1] — 2026-02-19

### Recovery day, but make it useful
- Killed a gnarly restart-churn pattern by simplifying ops: one gateway owner, tighter heartbeat scope, less chatter.
- Updated templates to a cleaner 4-file brain discipline so new installs don’t drown in markdown sprawl.
- Reworked heartbeat template to health checks first, alerts only when something is actually wrong.
- Added repo-scoped push guardrails in AGENTS template: explicit allowlists beat “sure, push it everywhere.”
- Refreshed README to surface the new “living example” philosophy and two-bot (Eric + Yoda) operating pattern.
- Big lesson: systems get reliable when you remove cleverness, not when you pile on more automation theatre.

## [4.0] — 2026-02-18

### Added — Back to Basics Recovery Architecture

- Added `docs/BACK_TO_BASICS_V4.md` with a stabilization-first operating model:
  - freeze triggers first,
  - simplify loops,
  - restore baseline,
  - scale up deliberately.
- Added `docs/OPENCLAW_CONCEPTS_PASS_2026-02-18.md` with a complete concepts-doc pass checklist and integrated outcomes.

### Template Upgrades

- `templates/AGENTS.md`
  - Added **Coding & Terminal Rules (SACRED)**
  - Added **Session Discipline**
  - Added refreshed **Critical Rules** and **Telegram Communication Style**
- `templates/SOUL.md`
  - Added explicit Telegram formatting section (single dense message default, max two on overflow)
  - Added optional personality spice guidance (humor/slang/multilingual flavor without slop)
- `templates/HEARTBEAT.md`
  - Added practical **Minimal 4-Step Baseline** for high-signal heartbeat behavior

### Why this matters

- Moves the starter kit toward incident-resistant operation.
- Encodes the “back to basics” playbook that recovered a drifting autonomous setup in one pass.
- Makes backup-bot/rescue-bot patterns easier to adopt without automation bloat.

### Removed

- Removed paid-resource/ad callouts from `README.md` and distribution copy to keep the public repo documentation-only.

## [3.5] — 2026-02-12

### Added — Growth & Distribution Mechanics

- Added a new `Resources` section in `README.md` with links to OpenClaw docs and Discord.
- Added distribution-ready content pack in `distribution/`:
  - `twitter-thread.md` (6-post technical thread with CTA)
  - `reddit-post.md` (title + body for r/selfhosted/r/artificial)
  - `hackernews-post.md` (Show HN title + engineering-focused body)
  - `linkedin-post.md` (professional automation angle)
- Added GitHub topics suggestion comment to `README.md` for discoverability (`openclaw`, `ai-agent`, `automation`, `personal-assistant`).

## [3.4] — 2026-02-12

### Added — Lex Fridman #491 Deep Audit (130 insights integrated)

Full deep audit of the steipete (Peter Steinberger) interview on Lex Fridman #491 plus 4 OpenAI Codex blog posts. 130 total insights extracted, 72 integrated as new material across templates and docs.

**templates/AGENTS.md:**
- 9 new steipete Core Philosophy items: question-pattern diagnostics, project slop vs model regression, core vs plugin discipline, friction-threshold automation, ecosystem over language taste, web hostility, security-before-simplicity, authenticity beats polish
- 7 new Enforcement Rules (#9-#15): secure defaults, private canary testing, contributor onramp, community topic boundaries, soul-change visibility, personal agent ≠ coding terminal, agent account labeling
- New "Execution Hardening" section: CWD verification, context pressure intervention, image context first, interrupt as normal control
- New "Model Routing Safety" section: security minimum tier, 7-day adaptation window, tier-normalized benchmarks
- 4 new Safety rules: hostile rename operations, legacy redirect preservation, sandbox/allowlist baseline, prompt-UX local scope

**templates/SOUL.md:**
- 3 new Soul traits: anti-fearmongering, builder identity over labels, experience optimization
- 2 new Writing Style rules: evidence-first model regression claims, human prose rule
- New "Design & Frontend Rules" section: no AI slop checklist, delight as editorial work, personality onboarding, API validation

**templates/HEARTBEAT.md:**
- Sparse/high-salience baseline behavior
- Self-audit checklist (10 items including security blast radius)
- 3 operational controls: interrupt/redirect, channel silence, web-hostility adaptation

**docs/CODEX_BEST_PRACTICES.md:**
- New section: Skill Evaluation Pipeline (deterministic evals + rubric/efficiency pass)
- New section: Skill Metadata + Governance (kill switches, invocation policy, namespace collision)
- New section: Hosted vs Local Runtime (artifact boundaries, allowlist fail-fast, domain-scoped secrets)
- New section: Prompt + Harness Anti-Patterns (5 patterns)
- New section: Advanced Harness Notes (compaction API, encrypted content, truncation policy)
- New section: AGENTS Layering Note (merge order, override precedence)

### Sources
- Lex Fridman #491 — Peter Steinberger (steipete), OpenClaw creator. 4-hour interview, full transcript analyzed.
- OpenAI Blog: Skills, Shell, and Compaction Tips
- OpenAI Blog: Evaluating Skills
- OpenAI Codex Skills Reference
- OpenAI Codex Prompting Guide

## [3.3] — 2026-02-10

### Added
- **Commandment #15: DELIVER ON PROMISES** — If you say you'll do it, have a cron/script/system ensuring it happens. Promises without enforcement are lies.
- **Mistake Log system** — `templates/mistakes.md` template for logging errors with root cause, fix, and verification. Same mistake twice = CRITICAL.
- **No AI Slop design guide** — `docs/NO_AI_SLOP_DESIGN.md` with checklist and principles for clean UI design. If it looks like AI made it, redesign.
- **push_all_repos.sh** — Script to push ALL repos every time, never manually. Enforces Commandment #15.

### Changed
- **Commandments updated 14 → 15** — `docs/THE_COMMANDMENTS.md` now includes #15 and the Mistake Log section.

### Lessons from Production (2026-02-10)
- Terminal death requires immediate action (refire within 60 seconds, don't sit idle)
- "Push all repos" means CHECK all repos, not just the ones with dirty trees
- Creating a fix tool is not enough — you must USE it automatically every time
- Apologising for mistakes without creating systems to prevent them is worthless

## [3.2] — 2026-02-08

### Removed (Cleanup)
- `tools/watchdog/` — Custom watchdogs violate Commandment #1 (use launchd/systemd KeepAlive)
- `docs/THE_13_COMMANDMENTS.md` — Replaced by updated 16 Commandments
- `docs/SUBAGENT_BEST_PRACTICES.md` — Sub-agents deprecated (Commandment #14: use CLI terminals)
- `docs/SUBAGENT_TIMEOUT_GUIDE.md` — Same reason
- `docs/WATCHDOG_OOB_SAFE.md` — Watchdogs deprecated
- `docs/archive/` — Cleaned 5 stale/duplicate docs (watchdog concepts, monitors, sub-agent guides)
- `scripts/archive/legacy-monitors/` — 12 deprecated monitor scripts
- `scripts/fix_readme_typo.py` — One-off script, not a starter kit utility
- `examples/` — Merged into `config/examples/` (MECE fix)

### Changed
- `docs/THE_COMMANDMENTS.md` — Updated from 13 → 16 Commandments
- All docs/templates/scripts: replaced "sub-agent" → "CLI terminal", "watchdog" → "service manager"
- `README.md` — Updated references to 16 Commandments
- `BOT_INSTRUCTIONS.md` — Removed deprecated pattern references

### Added
- `docs/integrations.md` — Setup guide for Stripe, YouTube, X/Twitter, Gmail PubSub
- Integration expansion changelog entry

### Security
- Full personal info scan: 0 leaked secrets, 0 personal identifiers
- All config examples use placeholder values only
- MECE verified: no duplicate folders or overlapping docs

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Major Update (Feb 8, 2026) — 355-Item Audit

#### Complete Rewrite
- **README.md** completely rewritten with 4-layer structure:
  - 🟢 Layer 1: Basic Uptime (install, keep alive, health checks)
  - 🟡 Layer 2: Core Rules (security, config hygiene, commandments)
  - 🔴 Layer 3: Advanced Config (models, memory, crons, streaming, sandboxing)
  - ⚫ Layer 4: How I Actually Set It Up (sanitized real production config)
- **`docs/THE_COMMANDMENTS.md`** updated from 11 → 11 refined commandments with anti-patterns table
- **`docs/SECURITY_HARDENING.md`** completely rewritten with full 355-item audit knowledge, priority tiers, incident response checklist
- **`docs/COMPLETE_SETUP_CHECKLIST.md`** — NEW: tick-off checklist distilled from the 355-item audit, organized by priority phase

#### New Config Example
- **`config/examples/production-hardened.json5`** — NEW: complete, annotated, battle-tested production config with every setting explained. Covers: auth, 4-model fallback chain, hybrid memory search, context pruning, compaction with memory flush, Telegram delivery fixes, security hardening, hooks, approvals, session management

#### Key Fixes Documented
- `chunkMode: "newline"` → `"length"` fix for Telegram (stops 15+ message bubble spam)
- OpenRouter API key format (`OPENROUTER_API_KEY=sk-or-v1-...` prefix required)
- Heartbeat minimum 30 min (user reported $50/day at 5-min interval)
- mDNS discovery off by default (network broadcast risk)
- Secrets in `.env` never in workspace markdown or HEARTBEAT.md
- `configWrites: false` on all channels
- Memory flush before compaction (prevents context loss)
- ClawHub skill scanning warning (7.1% credential leak rate)

#### Template Updates
- **`templates/AGENTS.md`** — updated with refined commandments, CLI > sub-agents execution rule, trust ladder, communication rules

### Added (Feb 6, 2026)
- **`docs/ADVANCED/AGENT_ECONOMY.md`** — NEW paradigm: build products for other agents, not just humans. Agent directories, battle arenas, reputation systems, API marketplaces. The agent-to-agent economy is real.
- **CEO Agent pattern** — Agents as economic actors: make products → sell them → promote on X → invest proceeds → grow. With approval gates for spending/external comms.
- **Self-updating website pattern** — Cron that updates agent's public website daily with fresh thoughts, stats, and activity.
- **Token auto-adjust modes** in `docs/CRON_HEARTBEAT_GUIDE.md` — BURN/CATCH UP/NORMAL/CONSERVE/MINIMAL based on optimal weekly burn rate. Don't just notify about usage, auto-adjust behavior.
- **Memory work at shift end** pattern — fact extraction, memory updates, retrieval verification, commandment audit at 6 AM / 10 PM transitions.
- **Index check before executing** — mandatory memory_search + code scan + docs check before any build. Prevents duplicates and missed context.
- **Eight Sleep presence vs sleepStart fix** in habit tracking — if tracking "in bed by X", use presence start (when user got in bed), not sleepStart (when sleep began). Common bug.
- **Streak calculation from start date** — don't rely on stale `currentStreak` counters. Always calculate `(today - streakStart).days` for accuracy.

### Changed (Feb 6, 2026)
- **Personality calibration lesson** in `templates/SOUL.md` — if the AI is too eager/accommodating, dial up the grumpy. User feedback: "British dry humor more biting and direct." The eager American intern persona is a failure mode.

### Added (Feb 5, 2026)
- **Plan C: Heartbeat Work Orchestrator** pattern in `docs/CRON_HEARTBEAT_GUIDE.md` — heartbeat as brain, background exec as hands, state file as memory. Full state machine (IDLE → BUILDING → REVIEWING → IDLE).
- **`codex exec` vs `codex --full-auto` comparison table** — critical distinction for anyone automating Codex CLI.
- **Pre-flight audit checklist** for autonomous builds in heartbeat guide.
- **E2E testing lesson** in `docs/LESSONS_LEARNED_STABILITY.md` — two critical bugs found in "completed" automation.
- **No watchers watching watchers** lesson in stability docs.

### Added
- `docs/DOC_SYNC_CHECKLIST.md` — **Gating rule** for documentation sync. Before any push, check if ALL docs need updating, not just CHANGELOG.md. Includes quick audit script and trigger-to-doc mapping table.
- `docs/ADVANCED_PLAYBOOK.md` — autonomy patterns for power users: spawn-on-error, wake-event triggers, multi-agent coordination, safe escalation scripts
- `scripts/advanced/spawn_on_error.sh` — example: spawn sub-agent when errors detected
- `scripts/advanced/wake_trigger.sh` — example: wake main session from external event
- **Heartbeat-first architecture pattern** — Use heartbeat for operational checks (email, calendar, tasks), cron for scheduled reports. Per docs.openclaw.ai best practices.
- **Creator Watch pattern** — Track other AI agents (like @FelixCraftAI) in twice-daily summaries to learn patterns
- **💓 Heartbeat indicator** — Start heartbeat messages with 💓 emoji so humans know it's a pulse check, not a regular message
- **Heartbeat reliability gotcha** — `HEARTBEAT_OK` can be invisible depending on delivery wiring; prefer visible proof-of-work heartbeats when you want a Telegram pulse
- `docs/ADVANCED_PLAYBOOK.md` — production autonomy patterns (heartbeat proof-of-work, Nat-style one-click review links, MECE guardrails)
- `docs/CODEX_RALPH_LOOPS.md` — PRD + checklist + fresh-context Codex CLI loops ("amnesia is a feature")

### Changed
- **`docs/MODEL_ROUTING.md`** — Updated with Feb 2026 industry consensus from @Austen (211 likes): "Codex for architecture backend, Claude for PM and front end". Added task-type routing table (backend → Codex, PM/planning → Claude Opus, frontend/UI → Claude Code). Matches @FelixCraftAI's working pattern.
- **`docs/NIGHT_SHIFT.md`** — Complete rewrite with battle-tested patterns from real overnight AI operations:
  - 7 key patterns: Self-assign tasks, Value multiplier, Model selection, Deep context, Mistake handling, Ship and market, Autonomous discovery
  - Detailed cadence (kickoff, hourly updates, morning wrap)
  - Safety constraints (what never to do overnight)
  - Real examples with code/commit structure
  - Troubleshooting guide
  - Quick start checklist
  - Sources: @Jamie_within (Marvin), @maxtokenai, @luckeyfaraday learnings

### Changed
- `config/examples/` — reorganized with clear naming (`autonomy-cadence.json5`, `cron-examples.json5`)
- `templates/` — synced AGENTS.md and SOUL.md templates with latest learnings

## [3.0.0] - 2026-02-03

### ⚠️ BREAKING: Philosophy Shift

This release represents a fundamental change in approach. **Simple > Clever.**

The old approach (v1-v2) recommended building layers of monitoring: watchdogs, meta-monitors, security hounds, config guardians. **That was wrong.** Those systems fought each other and caused more downtime than they prevented.

The new approach: Trust the platform. Launchd IS the watchdog. One cron for maintenance. That's it.

### Changed
- **README.md** — Complete rewrite. Added honest disclaimer (no guarantees, I break stuff, not affiliated with OpenClaw). Removed all references to deprecated monitoring systems. Now documents what actually works.
- Archived 13 legacy monitoring scripts to `scripts/archive/legacy-monitors/`:
  - watchdog.sh, watchdog_learn.sh
  - meta_monitor.py
  - security_hound.py
  - auto_doctor.py
  - autonomous_work_loop.py
  - subagent_watcher.py
  - context_healer.py
  - error_recovery.py
  - pipeline_health.py
  - agent_poll_enforcer.py
  - session_reset_monitor.py
  - telegram_delivery_checker.py

### Added
- `docs/CONFIG_HYGIENE.md` — Guide for keeping config clean: workspace defaults, secrets migration to `.env`, `${VAR}` substitution, audit checklist. Lessons from 817MB cleanup sprint.
- `docs/INCIDENT_POSTMORTEM.md` — **BRUTALLY HONEST**: The full embarrassing story of how I broke my own system for 6 hours by over-engineering. Required reading before you build custom watchdogs.
- `docs/LESSONS_LEARNED_STABILITY.md` — **CRITICAL**: Major incident analysis from 2026-02-03. Over-engineering killed my system. Launchd IS the watchdog.
- `docs/THE_11_COMMANDMENTS.md` — Hard-won rules for keeping autonomous OpenClaw stable.
- `docs/AUTONOMY_CADENCE.md` — minimal, MECE autonomy cadence (hourly updates, twice-daily recaps, daily docs upkeep).
- `docs/DELIVERY_GOTCHAS.md` — how to avoid the "job ran but nothing delivered" failure mode (systemEvent vs agentTurn).
- `docs/PRIME_DIRECTIVE.md` — public-safe operating philosophy.
- `config/examples/autonomy-cadence.json5` — safe, user-agnostic config snippet (timezone, typing indicators, heartbeat + messaging defaults).
- Safe out-of-band gateway watchdog package (opt-in): `tools/watchdog/*` + docs `docs/WATCHDOG_OOB_SAFE.md`.

### Changed
- **README.md** — Major update with warning about over-engineering. Added prominent notice pointing to LESSONS_LEARNED_STABILITY.md.
- Self-healing loop section now recommends simple approach (launchd + 5 AM cron) over complex multi-layer monitoring.

## [2.4.0] - 2026-02-01

### Added
- `docs/CONTENT_GENERATION_GUIDE.md` — how to use OpenClaw sub-agents for bulk structured content generation (JSON articles, curriculum, educational content). Includes schema design, parallel dispatch, fact-checking, token economics, and common pitfalls.

## [2.3.0] - 2026-02-01

### Added
- `docs/SIMPLIFICATION_GUIDE.md` — comprehensive guide to cutting bloat: 75 scripts → 25, 18 crons → 10, replacing custom monitoring with OpenClaw built-in tools (`openclaw doctor`, `openclaw status --deep`). Based on OpenClaw creator's philosophy.

### Changed
- Archived 11 outdated docs (meta-monitor, watchdog, agent poll enforcer, sprint system, etc.) to `docs/archive/`
- Docs now reflect simplified approach: fewer scripts, built-in tools, minimal heartbeat

### Removed
- References to "Council" pattern (named monitoring scripts watching each other)
- Over-engineered self-healing protocols (OpenClaw handles this natively)

## [2.2.0] - 2026-02-01

### Added
- `docs/EMAIL_IMESSAGE_AUTOMATION.md` — comprehensive guide: Gmail MECE labels, server-side filters, Apple Mail Smart Mailboxes (with correct sub-label matching), Apple Mail Rules cleanup, iMessage security policy, VIP email scanner pattern
- `docs/SECURITY_AUDIT_TEMPLATE.md` — template for running full security audits (secrets, permissions, network, dashboards, public repos)

### Fixed
- Documented common Apple Mail Smart Mailbox mistake: criteria must match **leaf** mailbox names (e.g., "Reply") not parent label paths (e.g., "Action/Reply")

## [2.1.0] - 2026-02-01

### Added
- `docs/CONFIG_SAFETY.md` — preventing auth crashes on config changes (debounce, pre-flight checks, backup patterns)
- `docs/MODEL_FAILOVER_GUIDE.md` — subscription patterns, cooldown behavior, auth rotation for single and multi-account setups
- `docs/OPENCLAW_FAQ_AUDIT.md` — FAQ and common gotchas audited against docs.openclaw.ai
- `templates/BOOT.md` — new session boot template for first-run onboarding
- `config/examples/memory-optimized.json5` — config tuned for memory-heavy workloads

### Changed
- Rewrote `README.md` — honest, technical, solo dev voice. No marketing fluff.
- Corrected failover guide to use single-subscription pattern as default (not everyone has two accounts)

### Removed
- `SPRINT_REBRAND_SPEC.md` — internal planning doc, should not have been in public repo
- `scripts/__pycache__/` — compiled Python cache files removed, added to `.gitignore`

## [2.0.0] - 2026-01-31

### Changed
- **Full rebrand** from generic starter kit to **self-healing AI survival guide**
- Consolidated scheduling guidance: cron vs heartbeat vs macOS launchd (rate-limit friendly)
- Updated all templates to be smaller, clearer, and aligned with current OpenClaw best practices

### Added
- `docs/CRON_HEARTBEAT_GUIDE.md` — when to use cron vs heartbeat vs launchd, with rate-limit math
- `docs/SUBAGENT_TIMEOUT_GUIDE.md` — why 3-min timeouts kill good work, how to tune them
- `docs/WEEKLY_AUDIT_GUIDE.md` — automated weekly self-audits with feedback loops
- `docs/SECURITY_HARDENING.md` — patterns for preventing hardcoded secrets and secure git workflows
- `docs/SUBAGENT_BEST_PRACTICES.md` — comprehensive guide to spawning, monitoring, and recovering subagents
- `docs/SELF_REVIEW.md` — self-review and HIT/MISS tracking patterns
- `scripts/auto_doctor.py` — full system diagnostics (sanitized from production)
- `scripts/pipeline_health.py` — multi-pipeline health checks
- `scripts/error_recovery.py` — automated error recovery patterns
- `scripts/sleep_score.py` — example IoT integration (Eight Sleep)
- `scripts/autonomous_work_loop.py` — self-propelling sprint chain and queue management
- `scripts/subagent_watcher.py` — watches for completed background work after restarts
- `scripts/context_healer.py` — context window management
- `scripts/session_reset_monitor.py` — detects session resets
- `scripts/telegram_delivery_checker.py` — verifies Telegram message delivery
- `scripts/telegram_echo_test.sh` — quick Telegram connectivity test
- `state/codex_status.example.json` — example Codex status tracking
- `state/current_work.example.json` — example work state file
- `state/work_metrics.example.json` — example metrics tracking
- `templates/weekly_audit_cron.sh` — cron template for weekly audits
- `templates/self-review.md` — self-review log template

### Fixed
- Session key lookup bug for `agent:main:main` format
- Python operator precedence bug in subagent watcher
- Removed outdated/archived scripts to reduce confusion

## [1.0.0] - 2026-01-30

### Added
- `docs/COMMUNICATION_PATTERNS.md` — background process guard, polling, atomic sprints
- `docs/AGENT_POLL_ENFORCER.md` — enforcing background agent polling
- `docs/GIT_PUSH_SECURITY.md` — security patterns for git workflows
- `docs/XCODE_CLOUD_MONITOR.md` — Xcode Cloud CI/CD monitoring
- `docs/HYBRID_CODING_WORKFLOW.md` — 8-step multi-model coding pipeline (Claude + Codex)
- `docs/MODEL_ROUTING.md` — intelligent model orchestration with degradation curves
- `docs/SPRINT_SYSTEM.md` — sprint management and notification patterns
- `docs/META_MONITOR.md` — meta-monitoring concepts (watching the watchers)
- `docs/META_LEARNING.md` — learning from failures automatically
- `docs/BUILD_MONITOR.md` — build monitoring patterns
- `docs/WATCHDOG_CONCEPTS.md` — self-healing and self-learning watchdog design
- `docs/BOT-HEALTH-CHECKS.md` — comprehensive bot health check guide
- `docs/WORK_LOOP.md` — autonomous work loop design
- `docs/SYSTEM_MAINTENANCE.md` — weekly auto-maintenance tasks
- `scripts/agent_poll_enforcer.py` — enforces subagent polling intervals
- `scripts/git_push_guard.sh` — pre-push security checks
- `scripts/meta_monitor.py` — meta-monitoring with subsystem health checks
- `scripts/model_router.py` — model selection with usage-aware routing
- `scripts/check_usage.py` — usage monitoring with JSON output
- `scripts/security_hound.py` — security scanning for secrets/leaks
- `scripts/watchdog.sh` — main watchdog script
- `scripts/watchdog_learn.sh` — watchdog learning from past incidents
- `scripts/emergency_lockdown.sh` — emergency security lockdown
- Mid-session enforcement hooks (trigger-based rule checking)
- Mandatory sprint notification format
- Codex sub-selection (model + effort level per task type)
- Hard-gate model availability checks for coding tasks
- Periodic status line with context% and usage%
- `config/examples/single-model.json5` — minimal single-model config
- `config/examples/multi-model.json5` — multi-model with failover
- `config/examples/compaction.json5` — compaction-tuned config
- `templates/AGENTS.md` — workspace rules template
- `templates/HEARTBEAT.md` — heartbeat template
- `templates/SECURITY.md` — security rules template
- `templates/SOUL.md` — personality/soul template
- `BOT_INSTRUCTIONS.md` — AI-readable onboarding guide

### Changed
- Hardened language throughout: "recommended" → "required", enforcement not suggestions

## [Unreleased]

### Added
- `templates/USER.md` — user profile template for fast personalization.
- `docs/README.md` — doc index (CORE + ADVANCED).
- `docs/ADVANCED/` — advanced playbook folder.
- `docs/ADVANCED/TRUST_LADDER.md` — 5-level autonomy policy.
- `docs/ADVANCED/TOKEN_BURN_STRATEGY.md` — pacing + parallel agents.
- `docs/ADVANCED/OVERNIGHT_BUILD_PIPELINE.md` — queue → execution → morning summary.
- `docs/ADVANCED/DAILY_RHYTHM.md` — daily planner + review loop.
- `docs/ADVANCED/DASHBOARD_INTEGRATION_PATTERNS.md` — safe integration patterns.
- `docs/ADVANCED/EMAIL_LABEL_MIGRATE_MECE_RUNBOOK.md` — email MECE migration patterns.
- `docs/ADVANCED/EMAIL_IMAP_APPLE_MAIL.md` — IMAP visibility + Apple Mail workflow.
- `docs/ADVANCED/IOS_APP_BUILD_WORKFLOW.md` — iOS build workflow with Codex.
- `docs/ADVANCED/FELIXCRAFT_PATTERNS.md` — FelixCraft-inspired patterns.
- `scripts/advanced/` — optional higher-autonomy scripts.
- `scripts/advanced/dashboard_push_template.py` — minimal dashboard push example.
- `docs/NIGHT_SHIFT.md` — overnight autonomy + high-signal update templates
- `docs/WORKSTREAMS.md` — best-practice pattern: one canonical chat + single source of truth workstreams file (SSOT)
- `templates/WORKSTREAMS_TEMPLATE.md` — copy-paste SSOT template for new setups

### Changed
- Moved `config-examples/` → `config/examples/` and updated all references.
- Updated `templates/AGENTS.md` to match current workspace operating rules (sanitized, user-agnostic).
- Updated `templates/BOOT.md` and `templates/HEARTBEAT.md` to remove hardcoded chat IDs and reflect current best practices.
- Updated `state/current_work.example.json` schema to match the current “focus + completed + running + next + metrics” pattern.
- Updated `state/codex_status.example.json` to include `tier` and current fields.
- Replaced `scripts/check_usage.py` and `scripts/git_push_guard.sh` with the current versions from the working setup.
- Hardened `.gitignore` to prevent committing secrets (`.env`, keys) and build artifacts (`__pycache__`, `.venv`).
- Removed Claude Sonnet assumptions across starter-kit docs/examples, default guidance is now Opus primary with cross-provider fallbacks.
- Updated multi-model config example to: Opus → Codex → Gemini → Kimi → Ollama.
- `docs/NIGHT_SHIFT.md` now links to the workstreams pattern.

### Fixed
- Removed stray local build artifacts (`__pycache__/`, `*.pyc`, `.DS_Store`) from the repo working tree.

## [0.1.0] - 2026-01-28

### Added
- Initial release with beginner-friendly install guide and copy-paste bot integration

### Added
- ADVANCED_PLAYBOOK: Added "The Felix Rule: Always Be Building" pattern


### Changed
- CODEX_RALPH_LOOPS: Added 95/5 rule (terminals over subagents)


## [2026-02-08] Integration Expansion

### Added
- Stripe integration guide (API setup, revenue tracking, product catalog)
- YouTube Data API v3 integration (channel stats, video analytics)
- X/Twitter API integration (OAuth 1.0a + 2.0 + Bearer, posting, monitoring)
- Google API key setup (24 APIs from single GCP project)
- Gmail MECE label structure (46 labels for personal email filing)
- Integration pulse in heartbeat (Stripe sales, YouTube stats, X mentions)
- Research & learning automation in weekly summary cron

### Changed
- Morning Briefing cron now includes integration data refresh
- Weekly Summary cron now includes research/learning from X, Reddit, HN
- HEARTBEAT.md expanded with integration monitoring steps

### Security
- Full 16-commandment audit passed
- .env audit: 15 keys, chmod 600, zero stray lines
- No secrets in markdown files (grep-verified)
- Gateway: loopback, mDNS off, configWrites false, exec=full
