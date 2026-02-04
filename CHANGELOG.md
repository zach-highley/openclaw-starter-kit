# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
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

