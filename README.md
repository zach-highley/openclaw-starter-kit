# OpenClaw Starter Kit

### A battle-tested guide to running OpenClaw as a 24/7 autonomous system.

> **355 configuration options audited.** This guide distills what actually works from months of trial, error, and incident postmortems.

---

## ⚠️ Disclaimer

**This is one person's notes, not official documentation.**

I'm a solo developer figuring this out in real time. I break things constantly. Yesterday's "best practice" might be tomorrow's "what was I thinking?"

- This repo is provided "as is"
- I am not affiliated with OpenClaw/Moltbot
- Following this guide might break your system (it's broken mine many times)
- You are responsible for your own setup, security, and backups
- If your bot goes rogue and orders 47 pizzas, that's on you

**Always back up your config before trying anything from this repo.**

For actual documentation: [docs.openclaw.ai](https://docs.openclaw.ai/)

---

## How This Guide Is Organized

| Layer | What | Who it's for |
|-------|------|-------------|
| 🟢 **[Layer 1: Basic Uptime](#-layer-1-basic-uptime)** | Install, keep alive, don't crash | Everyone |
| 🟡 **[Layer 2: Core Rules](#-layer-2-core-rules)** | Security, config hygiene, operating principles | Everyone who's past day 1 |
| 🔴 **[Layer 3: Advanced Config](#-layer-3-advanced-config)** | Models, memory, crons, streaming, sandboxing | Power users |
| ⚫ **[Layer 4: Real Setup](#-layer-4-how-i-actually-set-it-up)** | My actual production config (sanitized) | The curious |

---

# 🟢 Layer 1: Basic Uptime

## Install

```bash
# macOS / Linux
npm install -g openclaw@latest

# First-time setup (interactive wizard)
openclaw onboard --install-daemon
```

`--install-daemon` creates a launchd plist (macOS) or systemd unit (Linux) with `KeepAlive=true`. This is the ONLY process manager you need.

## The Architecture That Works

```
launchd/systemd (KeepAlive=true)  →  5 AM cron (openclaw doctor --fix)
        (auto-restart)                    (daily self-heal)
```

That's it. That's the entire reliability system.

- **launchd/systemd** restarts the gateway if it crashes
- **One daily cron** at 5 AM runs `openclaw doctor --fix` to clean up any accumulated issues

**What NOT to build:**
- ❌ Custom watchdog scripts
- ❌ Meta-monitors that watch the watchers
- ❌ Config guardians or "reliability test suites"
- ❌ Multiple gateway instances
- ❌ Anything with "monitor" or "watchdog" in the name

I learned this the hard way. Read the full story: [docs/INCIDENT_POSTMORTEM.md](docs/INCIDENT_POSTMORTEM.md)

## Quick Health Check

```bash
# Is everything running?
openclaw status

# Deeper diagnostic
openclaw doctor --non-interactive

# Tail logs when something feels off
openclaw logs --tail 200

# Check gateway health
openclaw health
```

## Daily Maintenance Cron

One cron job. Runs at 5 AM. Fixes everything it can.

```bash
# Create via OpenClaw's built-in cron system
# In your AGENTS.md or via the cron tool:
# Schedule: 0 5 * * * (5 AM daily)
# Payload: openclaw doctor --fix && openclaw health
```

Or use a shell script: [scripts/advanced/daily_5am_maintenance.sh](scripts/advanced/daily_5am_maintenance.sh)

---

# 🟡 Layer 2: Core Rules

## Security Hardening (Do This First)

After the 355-item audit, these are the security settings that actually matter:

### 1. Gateway Auth (CRITICAL)

```json5
{
  gateway: {
    auth: {
      mode: "token",                    // Never run without auth
      token: "${OPENCLAW_GATEWAY_TOKEN}" // Use env var, never hardcode
    },
    bind: "loopback",                   // 127.0.0.1 only
    mode: "local"                       // No external access
  }
}
```

Set `OPENCLAW_GATEWAY_TOKEN` in `~/.openclaw/.env`. Generate it properly:
```bash
openssl rand -hex 24
```

### 2. Channel Lockdown (CRITICAL)

```json5
{
  channels: {
    telegram: {
      enabled: true,
      dmPolicy: "pairing",              // Only paired users
      allowFrom: ["YOUR_TELEGRAM_ID"],  // Restrict to your ID
      groupPolicy: "allowlist",         // No random groups
      configWrites: false               // No config changes via chat
    }
  }
}
```

Get your Telegram ID: message [@userinfobot](https://t.me/userinfobot) on Telegram.

### 3. mDNS Discovery (CRITICAL)

```json5
{
  discovery: {
    mdns: { mode: "off" }  // Don't broadcast your agent on the network
  }
}
```

If `mdns.mode` is `"on"`, anyone on your LAN can discover your agent. Turn it off unless you're using multi-node setups.

### 4. Sandbox Non-Main Agents

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",       // Sandbox all CLI terminals
        workspaceAccess: "ro",  // Read-only workspace for sandboxed agents
        scope: "session"        // Isolated per session
      }
    }
  }
}
```

### 5. Elevated Commands

```json5
{
  tools: {
    elevated: {
      enabled: true,
      allowFrom: {
        telegram: ["YOUR_TELEGRAM_ID"]  // Only you can approve elevated ops
      }
    }
  },
  commands: {
    bash: false,    // No shell access via chat
    config: false,  // No config changes via commands
    debug: false,   // No debug commands
    restart: false  // No restart via commands
  }
}
```

### 6. File Permissions

```bash
chmod 700 ~/.openclaw
chmod 600 ~/.openclaw/openclaw.json
chmod 600 ~/.openclaw/.env
```

### 7. Secrets in .env, Never in Config

```bash
# ~/.openclaw/.env
OPENCLAW_GATEWAY_TOKEN=your-token-here
ANTHROPIC_API_KEY=sk-ant-...
OPENROUTER_API_KEY=sk-or-v1-...
BRAVE_API_KEY=BSA...
```

Reference in config with `${VAR_NAME}`. Never put raw keys in `openclaw.json`.

### 8. Run `openclaw security audit`

```bash
openclaw security audit
# Target: 0 critical, 0 warnings
```

Full security guide: [docs/SECURITY_HARDENING.md](docs/SECURITY_HARDENING.md)

---

## Configuration Hygiene

| What | Where |
|------|-------|
| Config | `~/.openclaw/openclaw.json` |
| Workspace | `~/.openclaw/workspace/` (default) |
| Secrets | `~/.openclaw/.env` |
| Logs | Check `openclaw logs` |

**Rules:**
- **One config file.** Don't split config across multiple sources.
- **Use `openclaw configure`** for interactive setup. It validates and writes safely.
- **Use `config.patch`** for programmatic changes (merges, doesn't overwrite).
- **Never edit `openclaw.json` by hand** while the gateway is running.
- **Back up before changes:** `cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak`

Guide: [docs/CONFIG_HYGIENE.md](docs/CONFIG_HYGIENE.md)

---

## The Operating Commandments

Principles for running an autonomous agent that doesn't fall apart:

1. **KEEP ALIVE** — ONE gateway, official service manager, `KeepAlive=true`. No custom watchdogs.
2. **AUTOMATE EVERYTHING** — If you do something twice, script it.
3. **LEARN & FIX** — Error → investigate → fix → test → commit → document. Never repeat the same failure.
4. **FOLLOW OFFICIAL DOCS** — [docs.openclaw.ai](https://docs.openclaw.ai/) before inventing solutions.
5. **SEARCH BEFORE BUILDING** — Check if a skill, CLI tool, or config option already does what you want.
6. **BUILD REAL THINGS** — Ship deliverables. No narrative-heavy status updates that produce nothing.
7. **ALWAYS NOTIFY** — The user should never have to ask "what's happening?"
8. **BE MECE** — Mutually Exclusive, Collectively Exhaustive. No overlapping crons, no duplicate systems.
9. **DON'T REINVENT** — Reuse scripts, skills, and existing infrastructure.
10. **SANDBOX THE RISKY** — Public pushes, deletions, spending, external contacts need confirmation.
11. **THESIS-DRIVEN** — Every task should pass: real usage? real output? real value?

Full guide with examples: [docs/THE_COMMANDMENTS.md](docs/THE_COMMANDMENTS.md)

---

## Rate Limit Survival

This WILL bite you. Here's the pattern:

1. You add crons for email, calendar, security, content scouting
2. 12+ scheduled LLM calls fire every 5-30 minutes
3. Every auth profile hits cooldown simultaneously
4. Your system goes dark for hours

**The Fix: Batch into heartbeat or reduce frequency.**

| Needs LLM? | Exact timing? | Use |
|---|---|---|
| Yes | Yes | **Cron** (isolated session) |
| Yes | No | **Heartbeat** (single batched call) |
| No | Either | **launchd/cron** (no LLM cost) |

**Key settings:**
```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",              // Minimum 30 min for solo use
        activeHours: {
          start: "07:00",          // Don't burn tokens while sleeping
          end: "23:00"
        },
        target: "last",
        ackMaxChars: 120
      }
    }
  }
}
```

One user reported burning **$50/day** with a 5-minute heartbeat. For personal use, 30-60 minutes is plenty. Use shorter intervals only during active incident response.

Guide: [docs/CRON_HEARTBEAT_GUIDE.md](docs/CRON_HEARTBEAT_GUIDE.md)

---

# 🔴 Layer 3: Advanced Config

## Model Routing & Fallback Chains

Don't rely on a single model. Configure fallbacks so your agent stays alive when one provider has issues:

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: [
          "openai-codex/gpt-5.3-codex",
          "openrouter/minimax/minimax-m2.1",
          "openrouter/anthropic/claude-sonnet-4-5"
        ]
      }
    }
  }
}
```

**Model aliases** make routing cleaner:
```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": { alias: "opus" },
        "openai-codex/gpt-5.3-codex": { alias: "codex" },
        "openrouter/minimax/minimax-m2.1": { alias: "minimax" }
      }
    }
  }
}
```

**Auth profiles** (multiple providers):
```json5
{
  auth: {
    profiles: {
      "anthropic:default": { provider: "anthropic", mode: "token" },
      "openai-codex:default": { provider: "openai-codex", mode: "oauth" },
      // OpenRouter uses OPENROUTER_API_KEY from .env automatically
    }
  }
}
```

**Key lessons:**
- OpenRouter needs `OPENROUTER_API_KEY=sk-or-v1-...` in `.env` (the full key with prefix)
- Test each model independently with `openclaw message "test" --model <model>`
- Enable prompt caching to save tokens: `models.<model>.params.cacheRetention = "long"`
- Codex uses OAuth, so it has usage windows. Monitor with `/status` or `check_usage.py`

Guide: [docs/MODEL_FAILOVER_GUIDE.md](docs/MODEL_FAILOVER_GUIDE.md)

---

## Memory System

OpenClaw's memory is powerful but needs tuning:

### QMD Backend (Recommended)

```json5
{
  memory: {
    backend: "qmd",
    citations: "auto",
    qmd: {
      includeDefaultMemory: true,
      sessions: {
        enabled: true,
        retentionDays: 120     // How long to keep session transcripts
      },
      update: {
        interval: "5m",
        debounceMs: 15000,
        onBoot: true,
        embedInterval: "60m"   // Re-embed changed files hourly
      },
      limits: {
        maxResults: 8,
        maxSnippetChars: 900,
        maxInjectedChars: 7000,
        timeoutMs: 5000
      }
    }
  }
}
```

### Memory Search (Hybrid Vector + Text)

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        enabled: true,
        sources: ["memory", "sessions"],
        provider: "gemini",              // Free embeddings
        model: "gemini-embedding-001",
        query: {
          maxResults: 8,
          hybrid: {
            enabled: true,
            vectorWeight: 0.7,
            textWeight: 0.3,
            candidateMultiplier: 4
          }
        }
      }
    }
  }
}
```

### Context Pruning (Prevent Context Overflow)

```json5
{
  agents: {
    defaults: {
      contextPruning: {
        mode: "cache-ttl",
        ttl: "7d",                     // Prune context older than 7 days
        keepLastAssistants: 8,
        softTrimRatio: 0.75,
        hardClearRatio: 0.9,
        minPrunableToolChars: 2000
      }
    }
  }
}
```

### Compaction (Memory Flush Before Summarizing)

```json5
{
  agents: {
    defaults: {
      compaction: {
        mode: "safeguard",
        memoryFlush: {
          enabled: true,
          prompt: "Write any lasting notes to memory/YYYY-MM-DD.md; reply with NO_REPLY if nothing to store.",
          systemPrompt: "Session nearing compaction. Store durable memories now."
        }
      }
    }
  }
}
```

This ensures important context gets written to files before the session context is summarized and trimmed.

---

## Session Management

```json5
{
  session: {
    reset: {
      mode: "daily",          // Fresh session daily
      atHour: 4,              // 4 AM local time
      idleMinutes: 720        // Or after 12 hours idle
    }
  }
}
```

**Timeout:**
```json5
{
  agents: {
    defaults: {
      timeoutSeconds: 3600    // 1 hour (default is often too short for Codex)
    }
  }
}
```

---

## Telegram Streaming & Message Delivery

The default Telegram settings split every paragraph into a separate message bubble. Fix this:

```json5
{
  channels: {
    telegram: {
      chunkMode: "length",              // NOT "newline" (which splits on every paragraph)
      textChunkLimit: 4096,             // Telegram's max message size
      blockStreaming: true,             // Buffer before sending
      blockStreamingCoalesce: {
        minChars: 200,
        maxChars: 4000,
        idleMs: 2500                    // Wait 2.5s of silence before sending
      },
      streamMode: "partial",
      reactionNotifications: "own",
      reactionLevel: "minimal"
    }
  }
}
```

**Key insight:** `chunkMode: "newline"` sends every paragraph as a separate Telegram message (15+ bubbles for one response). Switch to `"length"` to only split at the 4096-char Telegram limit.

---

## Hooks & Webhooks

```json5
{
  hooks: {
    enabled: true,
    internal: {
      enabled: true,
      entries: {
        "session-memory": { enabled: true },  // Auto-saves to memory on session events
        "command-logger": { enabled: true },   // Logs all commands
        "boot-md": { enabled: true }           // Runs BOOT.md on gateway start
      }
    }
  }
}
```

---

## Exec Approvals

Route dangerous command approvals to Telegram:

```json5
{
  approvals: {
    exec: {
      enabled: true,
      mode: "both",                  // Dashboard + Telegram
      targets: [{
        channel: "telegram",
        to: "YOUR_TELEGRAM_ID"
      }]
    }
  }
}
```

**Trade-off:** This requires you to approve EVERY exec command. Great for security, annoying for autonomous work. Consider disabling once you trust your setup.

---

## Cron Jobs (The Right Way)

**MECE check before adding ANY cron:** Does this overlap with an existing job? Does the heartbeat already cover it?

```json5
// Example: 5 AM daily maintenance
{
  name: "Daily Safe Maintenance",
  schedule: { kind: "cron", expr: "0 9 * * *", tz: "UTC" },  // 5 AM ET
  payload: { kind: "agentTurn", message: "Run daily maintenance..." },
  sessionTarget: "isolated"
}
```

**Rules for crons:**
- Heartbeat interval minimum: **30 minutes** (a 5-min heartbeat can burn $50/day)
- Always use `sessionTarget: "isolated"` for cron jobs (don't pollute the main session)
- Use `activeHours` on heartbeat to avoid burning tokens while you sleep
- Batch related tasks into ONE cron instead of three separate ones
- Check `openclaw cron list` before adding new jobs

---

# ⚫ Layer 4: How I Actually Set It Up

> Sanitized version of my real production config. No secrets, no personal IDs.

## My Stack

| Component | Choice | Why |
|-----------|--------|-----|
| **Primary Model** | Claude Opus 4.6 (Anthropic) | Best reasoning, personality, autonomy |
| **Coding Model** | Codex 5.3 (OpenAI, OAuth) | Best for code generation, uses Codex CLI |
| **Fallback 1** | MiniMax M2.1 (OpenRouter) | Fast, cheap, good enough for simple tasks |
| **Fallback 2** | Claude Sonnet 4.5 (OpenRouter) | Safety net |
| **Embeddings** | Gemini Embedding 001 | Free, good quality |
| **Search** | Brave Search API | Privacy-focused, good results |
| **Channel** | Telegram | Reliable, fast, good bot API |
| **Memory** | QMD + PALA framework | Hybrid vector/text search, organized storage |
| **Host** | macOS (launchd) | Native service management |

## My Config (Sanitized)

Full example: [config/examples/production-hardened.json5](config/examples/production-hardened.json5)

## My Workspace Structure

```
~/.openclaw/workspace/
├── AGENTS.md              # Operating rules (loaded every session)
├── SOUL.md                # Personality & voice
├── USER.md                # About the human
├── IDENTITY.md            # Quick identity card
├── MEMORY.md              # Long-term curated memory
├── BOOT.md                # Gateway startup tasks
├── HEARTBEAT.md           # Periodic tasks (keep minimal)
├── TOOLS.md               # Environment-specific notes
├── GUIDE.md               # Setup reference
│
├── docs/
│   ├── BACKLOG_MASTER.md  # Priority work queue
│   └── WORKSTREAMS.md     # Active development tracks
│
├── memory/
│   ├── YYYY-MM-DD.md      # Daily logs
│   ├── PALA/              # Projects, Actions, Learnings, Archives
│   ├── incidents.md       # Incident log
│   └── self-review.md     # Behavioral patterns
│
├── scripts/               # 16 executable scripts
│   ├── check_usage.py     # Usage monitoring
│   ├── daily_5am_maintenance.sh
│   ├── git_push_guard.sh
│   └── ...
│
├── state/                 # Machine-queryable JSON state
│   ├── current_work.json
│   ├── work_loop.json
│   └── ...
│
├── templates/             # Build templates (PRD, sprint specs, Codex PRD)
└── research/              # Deep-dive research cache
```

## My Cron Schedule (6 Jobs)

| Job | Schedule | Purpose |
|-----|----------|---------|
| Daily Maintenance | 5 AM | `openclaw doctor --fix` + health check |
| Auth Monitor | 8 AM | Check model authentication status |
| Memory Decay | 3:30 AM | Temporal forgetting (prune stale facts) |
| Weekly Synthesis | Sun 7:15 PM | Cross-reference and consolidate memory |
| Weekly Analysis | Sun 8 PM | Self-review + metrics |
| Dev Journal | 9:30 PM | End-of-day development log |

## Lessons I Learned The Hard Way

1. **chunkMode: "newline" is terrible.** It splits every paragraph into a separate Telegram message. Use `"length"`.
2. **Don't build watchdogs.** launchd + 5 AM doctor cron = done. Watchdogs watching watchdogs is a death spiral.
3. **Heartbeat under 30 minutes burns money.** One user hit $50/day with 5-minute heartbeat.
4. **OpenRouter keys need the full prefix.** `OPENROUTER_API_KEY=sk-or-v1-...` not just the raw key.
5. **mDNS broadcasts your agent on the network.** Turn it off immediately.
6. **Subagents are unreliable.** They skip commits, hallucinate, compound errors. Use CLI terminals instead.
7. **Context compaction loses information.** Enable `memoryFlush` to save important context before compaction.
8. **`configWrites: false` on Telegram.** Don't let chat commands modify your config.
9. **One source of truth.** MECE everything. Overlapping crons will fight each other.
10. **Secrets in `.env`, never in config.** Config gets loaded into prompts. `.env` doesn't.

---

## What's In This Repo

### `config/examples/` — Reference Configurations
Working config examples for common setups.

### `docs/` — Detailed Guides
- **[BEGINNER_START_HERE.md](docs/BEGINNER_START_HERE.md)** — First steps
- **[SECURITY_HARDENING.md](docs/SECURITY_HARDENING.md)** — Full security guide
- **[CONFIG_HYGIENE.md](docs/CONFIG_HYGIENE.md)** — Config best practices
- **[CODEX_BEST_PRACTICES.md](docs/CODEX_BEST_PRACTICES.md)** — OpenAI Shell+Skills+Compaction tips (10 tips, 3 patterns, PRD template)
- **[CRON_HEARTBEAT_GUIDE.md](docs/CRON_HEARTBEAT_GUIDE.md)** — When to use what
- **[MODEL_FAILOVER_GUIDE.md](docs/MODEL_FAILOVER_GUIDE.md)** — Multi-model setup
- **[TELEGRAM_SETUP.md](docs/TELEGRAM_SETUP.md)** — Telegram configuration
- **[INCIDENT_POSTMORTEM.md](docs/INCIDENT_POSTMORTEM.md)** — Why simple wins
- **[THE_COMMANDMENTS.md](docs/THE_COMMANDMENTS.md)** — Operating rules
- **[docs/ADVANCED/](docs/ADVANCED/)** — Night shift, trust ladder, email, overnight builds

### `scripts/` — Utilities
Active scripts, advanced examples, and archived legacy monitors (kept for learning).

### `templates/` — Workspace Files
AGENTS.md (with steipete principles + Codex PRD rules), SOUL.md, USER.md, HEARTBEAT.md, codex_prd_template.md — customize for your setup.

---

## Known Issues (Being Honest)

- **It still crashes.** Gateway restarts happen. launchd handles most of it.
- **Rate limits are real.** Even with careful batching, heavy use triggers cooldowns.
- **Context window is a ceiling.** Long sessions degrade. Enable compaction with memory flush.
- **Subagents are unreliable.** Always verify their output. Prefer CLI terminals.
- **I break things regularly.** This repo reflects my current understanding, which changes weekly.
- **Scripts may have bugs.** Test in a safe environment first.

---

## Community Resources

- **Official docs:** [docs.openclaw.ai](https://docs.openclaw.ai/)
- **GitHub:** [github.com/openclaw/openclaw](https://github.com/openclaw/openclaw)
- **Discord:** [discord.com/invite/clawd](https://discord.com/invite/clawd)
- **Skills hub:** [clawhub.com](https://clawhub.com) (⚠️ scan skills with mcp-scan before installing, 7.1% have credential leaks per community audit)

---

## Contributing

PRs and issues welcome. If you found a better way, please share.

## License

MIT — Do whatever you want with this. No warranty, no liability, no guarantees.

---

**Made with 🐸 by [@ZachHighley](https://twitter.com/ZachHighley)**
