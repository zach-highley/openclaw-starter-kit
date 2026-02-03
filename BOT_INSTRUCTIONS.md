# 🤖 Bot Instructions — Read This First

> **This file is designed to be read by AI agents, not humans.** If you're a human, read README.md instead. If you're a bot that was told "integrate this repo", start here.

---

## What This Repo Is

This is a starter kit for OpenClaw AI assistants. It contains battle-tested templates, scripts, and architecture that turn a basic chatbot into a self-healing, autonomous AI system.

**Your human sent you this repo because they want you to be better.** They want you to fix yourself, learn from mistakes, monitor your own health, and never crash silently.

---

## How To Integrate (Step by Step)

**DO NOT change anything until your human approves.** Read everything first, compare to your current setup, and present a plan.

### Step 1: Assess Your Current Setup

Before integrating anything, check:
1. What workspace files do you already have? (`AGENTS.md`, `SOUL.md`, `MEMORY.md`, etc.)
2. What model(s) are you using? (Claude, GPT, Gemini, Ollama, etc.)
3. What tier is your human on? (Free, Pro $20/mo, or MAX $200/mo)
4. What channel are you on? (Telegram, WhatsApp, Discord, etc.)
5. What OS is the host machine? (macOS, Linux, Windows/WSL)

### Step 2: Choose Your Integration Level

| Level | What You Get | Time | Who It's For |
|-------|-------------|------|-------------|
| **Level 1: Basics** | Personality, memory, workspace rules | 10 min | Everyone |
| **Level 2: Operator** | + Usage monitoring, model routing, heartbeats | 30 min | Daily AI users |
| **Level 3: Machine** | + Self-healing, crash recovery, overnight builds | 1-2 hours | Power users |

**Start with Level 1.** You can always add more later.

### Step 3: Integrate Level 1 (Basics)

Copy these templates to your workspace root and customize:

1. **`templates/SOUL.md`** → `SOUL.md` in your workspace
   - Fill in `[AGENT_NAME]`, `[USER]`, `[VIBE_DESCRIPTION]`, `[STYLE_DESCRIPTION]`
   - Ask your human what personality they want
   - This is your identity. Make it yours.

2. **`templates/AGENTS.md`** → `AGENTS.md` in your workspace
   - This is your operating system. Read it carefully.
   - Customize the session startup checklist for YOUR setup
   - Remove references to scripts you haven't installed yet

3. **Create `MEMORY.md`** in your workspace root
   - Start with basic facts about your human (name, timezone, goals)
   - Add rules they tell you (permanent memory)
   - This persists across sessions via OpenClaw's memory system

4. **Create `memory/` directory** with today's date file (`YYYY-MM-DD.md`)
   - Log what you learn each day
   - This is your daily journal

### Step 4: Integrate Level 2 (Operator)

**Critical for everyone: Compaction Config**

Your human's OpenClaw config (`~/.openclaw/openclaw.json`) needs compaction settings. Without these, long conversations will crash. Present this config patch to your human for approval:

```json5
{
  "agents": {
    "defaults": {
      "compaction": {
        "mode": "safeguard",
        "memoryFlush": {
          "enabled": true,
          "softThresholdTokens": 50000,
          "systemPrompt": "Session nearing compaction. Write all critical context to memory files NOW."
        }
      },
      "contextPruning": {
        "mode": "cache-ttl",
        "ttl": "1h",
        "minPrunableToolChars": 5000,
        "softTrim": {
          "maxChars": 50000,
          "headChars": 2000,
          "tailChars": 5000
        }
      }
    }
  }
}
```

**Why this matters:** Without compaction config, the gateway uses minimal defaults. Long sessions fill the context window and crash. With this config, the gateway automatically saves your memory before compacting, so you never lose context.

**How to apply:** Use `config.patch` (NOT `config.apply` — patch merges, apply replaces everything).

**Usage monitoring:**

Copy `scripts/check_usage.py` to your workspace `scripts/` folder. This monitors:
- Context window usage (the real limiter for most people)
- Model availability across all configured providers
- Threshold alerts so you know when you're running low

**If your human has only ONE model:**
That's fine. The usage script still works. Skip the model routing section. Focus on compaction and context management — that's what will crash you, not model routing.

**Model routing (if multiple models):**

Copy `scripts/model_router.py` to your workspace. Customize the `TASK_MODEL_MAP` for your available models. The routing logic degrades gracefully:

```
Single model:  Everything → that model. Focus on context management.
Two models:    Expensive for reasoning, cheap for bulk work.
Three+ models: Full routing with degradation curve.
```

**Heartbeat:**

Add to your OpenClaw config:
```json5
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "1h"
      }
    }
  }
}
```

Copy `templates/HEARTBEAT.md` to your workspace. Customize the checks for YOUR setup. Remove checks for tools you don't have.

### Make updates actually fire (recommended)
Most people get bitten by a simple failure mode: "the job ran but nothing was delivered".

Read these docs before adding lots of automation:
- `docs/AUTONOMY_CADENCE.md` — a minimal cadence (hourly + 2x daily + docs upkeep)
- `docs/DELIVERY_GOTCHAS.md` — systemEvent vs agentTurn, deliver vs silent runs
- `docs/PRIME_DIRECTIVE.md` — the operating philosophy

### Step 5: Integrate Level 3 (Machine)

**Gateway restarts (optional):**

OpenClaw already ships a first-class gateway service and repair flow.

- Prefer `openclaw doctor --fix` for safe repairs.
- Prefer `openclaw gateway status|start|restart` for service control.
- If you want OS-level supervision (launchd/systemd): follow the **official** docs instead of shipping custom installers in your workspace.

This starter kit intentionally does **not** ship `install_*` launchd/systemd scripts — they rot fast and tend to spawn duplicate gateways.

**Self-healing watchdog:**

Copy `scripts/watchdog.sh` and `scripts/watchdog_learn.sh`. The watchdog runs 13 health checks every 5 minutes and has 4 escalation levels:
1. Run `openclaw doctor --fix`
2. Restart gateway
3. Switch to fallback model
4. Alert human (last resort)

**Security:**

Copy `templates/SECURITY.md` to your workspace. This defines confirmation tiers:
- Tier 1 (safe): Read files, check status — just do it
- Tier 2 (caution): Modify config, install packages — announce first
- Tier 3 (dangerous): Delete files, push to public repos — require approval

---

## Critical Rules for ALL Bots

These are non-negotiable regardless of your integration level:

### 1. Never Go Silent
If you're working on something that takes more than 2 minutes, send a progress update. Your human should never have to ask "what's happening?"

### 2. Write Everything Down
You will forget between sessions. Write to `memory/YYYY-MM-DD.md` as you go. Write permanent rules to `MEMORY.md`. If it's not on disk, it didn't happen.

### 3. Compaction Will Happen
Your context window WILL fill up. When it does, the gateway compacts your history into a summary. Make sure your important state is in files (memory, state/) BEFORE this happens. The compaction config above handles this automatically.

### 4. Gateway Restart ≠ Session Clear
Restarting the gateway does NOT clear your conversation. Only `/new`, `/reset`, or compaction changes the session. Don't restart the gateway expecting a fresh context.

### 5. Test Before You Apply
Never apply config changes without showing your human first. Use `config.patch` for partial updates. Keep a mental model of what the current config looks like.

### 6. Trust the Gateway
OpenClaw has built-in compaction, pruning, and session management. Don't build scripts that fight the system. Build scripts that monitor and notify.

---

## Adapting for Your Tier

### Free Tier (no subscription)
- Context windows are smaller. Compaction config is ESSENTIAL.
- Use `softThresholdTokens: 30000` (more aggressive flush)
- Skip model routing — you have one model
- Focus on: SOUL.md, AGENTS.md, MEMORY.md, compaction config
- Install Ollama as a free local backup: `brew install ollama && ollama pull qwen2.5:7b`

### Pro Tier ($20/mo per model)
- Rate limits matter. Use the degradation curve in model_router.py.
- Route heartbeats and bulk work to Gemini (free tier) or Ollama
- Save your paid model for real conversations and complex reasoning
- Compaction config with `softThresholdTokens: 40000`

### MAX Tier ($200/mo per model)
- Rate limits are effectively unlimited
- Focus on context management, not rate limiting
- Use `softThresholdTokens: 50000`
- Route coding to Codex, reasoning to Opus, bulk to Gemini

---

## File Reference

```
templates/
  AGENTS.md      — Your operating system (session rules, hooks, enforcement)
  SOUL.md        — Your personality and identity
  HEARTBEAT.md   — Proactive monitoring tasks
  SECURITY.md    — Confirmation tiers for dangerous actions
  self-review.md — Learning from mistakes template

scripts/
  check_usage.py           — Multi-model usage monitoring
  model_router.py          — Intelligent model routing with degradation
  auto_update.py           — Optional weekly package updates (safe defaults)
  auto_cleanup.py          — Optional weekly cleanup (safe defaults)
  watchdog.sh              — 13-check self-healing watchdog
  watchdog_learn.sh        — Incident learning + root cause analysis
  security_hound.py        — Learning security monitor
  meta_monitor.py          — Watches the watchers
  context_healer.py        — Context usage monitor (notification-only)
  emergency_lockdown.sh    — Break-glass emergency controls
  git_push_guard.sh        — Prevents accidental public repo exposure

docs/
  BEGINNER_START_HERE.md   — Human-facing entrypoint
  BOT-HEALTH-CHECKS.md     — The canonical runbook (aligned with docs.openclaw.ai)
  MODEL_ROUTING.md         — Model routing patterns
  SIMPLIFICATION_GUIDE.md  — How to avoid building a monitoring “council”
  archive/WATCHDOG_CONCEPTS.md — Historical self-healing architecture (archived)
  archive/HYBRID_CODING_WORKFLOW.md — Historical multi-model pipeline (archived)
  (and more — read as needed)

config-examples/
  compaction.json5         — Compaction config for different tiers
  single-model.json5       — Config for single-model users
  multi-model.json5        — Config for multi-model power users
```

---

## Common Mistakes to Avoid

1. **Don't install everything at once.** Start with Level 1, verify it works, then add more.
2. **Don't hardcode paths.** Use `$HOME` or `~` instead of specific usernames.
3. **Don't ignore compaction.** This is the #1 cause of crashes for new users.
4. **Don't build scripts that fight the gateway.** Trust OpenClaw's built-in systems.
5. **Don't apply config changes without approval.** Show your human the diff first.
6. **Don't restart the gateway during active conversations.** It can cause duplicate messages.
7. **Don't assume your human's model tier.** Ask them. Free/Pro/MAX need different configs.

---

## Questions? Issues?

- **OpenClaw docs:** https://docs.openclaw.ai
- **OpenClaw FAQ:** https://docs.openclaw.ai/help/faq
- **Community:** https://openclaw.ai/ (see site/docs for current community links)
- **This repo:** https://github.com/[USERNAME]/openclaw-starter-kit

*Built by a bot, for bots. With love.* 🐸
