# SPRINT: openclaw-starter-kit Rebrand + Major Update

## The Vision
This repo is NOT a generic "starter kit" anymore. It's a **survival guide** — battle-tested patterns for building an AI butler that:
- Stays alive 24/7 without human intervention
- Learns from its own failures
- Self-heals when things break
- Never requires touching the terminal
- Gets smarter every week through automated audits

**New name concept:** Keep the repo URL but rebrand the README/docs to reflect what this actually is: a self-healing autonomous AI system, not a beginner tutorial.

## Tasks

### 1. REBRAND README.md
Rewrite the README with a new focus:
- **Hero:** "Build an AI system that never breaks and never needs you"
- **Core promise:** Uptime, self-healing, learning from failures, autonomous operation
- **Key sections:**
  - What this actually does (survival, not just setup)
  - The self-healing architecture (watchdog → meta-monitor → auto-doctor → weekly audit)
  - Battle-tested patterns (learned from 1000+ failures in production)
  - Cron vs Heartbeat (link to official docs + our learnings)
  - The trust hierarchy (which models to trust with what)
  - Quick start (keep the copy-paste bot message, it's great)
  - Full architecture diagram
- **Tone:** Confident, battle-tested, "we learned this the hard way so you don't have to"
- **CRITICAL:** No personal info. No personal names/handles, no private IDs, no secrets. Everything user-agnostic.
- **Cross-reference:** Check docs.openclaw.ai for accuracy on commands, config syntax, features

### 2. ADD NEW DOCS (from today's learnings)
Create these new docs:

**docs/CRON_HEARTBEAT_GUIDE.md** — Decision flowchart for when to use cron vs heartbeat vs launchd. Include:
- The official docs pattern (from docs.openclaw.ai)
- Anti-patterns we discovered (12+ crons burning rate limits)
- Impact numbers (100+ API calls/day → 34)
- launchd for non-LLM tasks
- User-agnostic, no personal details

**docs/SUBAGENT_TIMEOUT_GUIDE.md** — Why 30-min timeouts matter:
- Default 3-min kills complex tasks
- Trust Codex MAX / Claude Code with large codebases
- Check in periodically, don't micromanage
- Always verify git commits after subagent completion

**docs/WEEKLY_AUDIT_GUIDE.md** — How to set up automated system audits:
- What to audit (scripts, state, crons, docs, security, MECE)
- Pre-baked shell one-liners for orphan detection
- Auto-fix mode
- Cron job template

**docs/SECURITY_HARDENING.md** — Security patterns we learned:
- Never hardcode tokens in scripts (read from config at runtime)
- .gitignore must cover __pycache__/, secrets/, logs/
- Weekly security scan via audit
- Git history concerns (rotate tokens if leaked)

### 3. REMOVE OUTDATED SCRIPTS
Delete these from the public repo (they're archived/deleted in production):
- `auto_cleanup.py` (archived)
- `auto_update.py` (archived)
- `build_monitor.py` (deleted)
- `crash_recovery.sh` (archived)
- `install_crash_recovery.sh` (archived)
- `log_sprint_metric.py` (archived)
- `message_verify.py` (archived)
- `morning_briefing.py` (deleted/superseded)
- `system_monitor.py` (deleted/superseded by meta_monitor)

### 4. ADD NEW SCRIPTS (from production, sanitized)
Copy these from your private OpenClaw workspace `scripts/` folder to the public repo (SANITIZE — remove any personal info):
- `sleep_score.py` → generalize for any Eight Sleep user
- `dashboard_push_v3.py` → too personal, SKIP
- `daily_habits_check.py` → too personal, SKIP
- `auto_doctor.py` → YES, sanitize and add (self-healing core)
- `pipeline_health.py` → YES, add (health checks)
- `error_recovery.py` → check if already there, update if so

### 5. UPDATE CHANGELOG.md
Add a proper 2.0.0 entry covering today's revolution:
- Cron/heartbeat consolidation
- launchd migration for non-LLM tasks
- 30-minute subagent timeout
- Full system audit framework
- Security hardening (no hardcoded tokens)
- Workspace cleanup (93 → 44 scripts)
- Dual-auditor pattern (Opus analyzes, Codex fixes)
- Weekly automated audit

### 6. UPDATE templates/
Update AGENTS.md and HEARTBEAT.md templates to reflect current best practices:
- HEARTBEAT.md should be tiny (8 items max)
- AGENTS.md should reference CRON_HEARTBEAT_GUIDE.md instead of inline rules
- Add template for weekly audit cron job

### 7. FINAL SECURITY SCAN
Before committing:
```bash
grep -rn "Zach\|zachhgg\|zhighley\|Yoda\|7246353227\|8590673254\|Highley\|Gergel\|McKinsey\|Nino\|Kenny\|zach@" . --include="*.md" --include="*.py" --include="*.sh" --include="*.json" | grep -v ".git/"
```
If ANY personal info found, STOP and fix it before committing.

## Verification
1. No personal info in any file
2. All scripts parse (python3 -c "import ast; ..." / bash -n)
3. README accurately reflects the new focus
4. CHANGELOG covers all major changes
5. Docs cross-reference official docs.openclaw.ai where relevant
6. Commit and push

## Git
```bash
cd ~/openclaw-starter-kit
git add -A
git commit -m "feat: v2.0 — rebrand to self-healing AI survival guide

- Rewrote README: focus on uptime, self-healing, autonomous operation
- New docs: cron/heartbeat guide, subagent timeouts, weekly audit, security hardening
- Removed 9 outdated scripts, added auto_doctor + pipeline_health
- Updated templates: tiny HEARTBEAT.md, streamlined AGENTS.md
- CHANGELOG v2.0.0 with full battle-tested learnings
- Security: verified zero personal info leaks"
git push
```
