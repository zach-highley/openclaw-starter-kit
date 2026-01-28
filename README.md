# 🐸 The Moltbot Starter Kit
### Turn Moltbot Into a Self-Healing, Multi-Model Autonomous AI System

> *"Within 48 hours you can have an AI that fixes itself at 3 AM, routes tasks across 5 models, monitors your security, and builds you apps while you sleep."*

---

# 📋 WHAT YOU NEED (Before You Start)

## Hardware

Any computer that stays on. That's it. No server rack, no cloud VM, no special hardware.

| Setup | Machine | Works? |
|-------|---------|--------|
| **Ideal** | Mac (M-series recommended) or Linux desktop/laptop | ✅ Best experience |
| **Fine** | Older Mac (Intel) or any Linux box | ✅ Works great |
| **Possible** | Windows via WSL2 | ⚠️ Works but rougher edges |
| **Not needed** | Cloud servers, VPS, Raspberry Pi | Skip it. Run it on your daily driver. |

**Minimum specs:** 8GB RAM, 20GB free disk space. If you want to run local AI models (Ollama), 16GB+ RAM helps.

## Software

| What | Why | Cost |
|------|-----|------|
| **Node.js 18+** | Runs Moltbot | Free |
| **Telegram** | Your primary chat interface | Free |
| **Homebrew** (Mac) | Installs dependencies | Free |
| **Git** | Clone this repo | Free |
| **Ollama** (optional) | Local AI fallback so you never hit zero | Free |

## AI Model Accounts (The Actual Brain)

This is where it gets interesting. You need at least ONE AI provider. More providers = smarter routing and better uptime.

| Provider | What It Does | Cost | Required? |
|----------|-------------|------|-----------|
| **Anthropic (Claude)** | Main brain. Best reasoning. | Free tier available, Pro is $20/mo | Pick at least one |
| **OpenAI (Codex/GPT)** | Code specialist. Writes your scripts. | Free tier available, Plus is $20/mo | Pick at least one |
| **Google (Gemini)** | Background tasks, heartbeats, bulk work | Free tier available | Optional but recommended |
| **Ollama (Local)** | Offline backup. Never hit zero. | Free forever | Optional but recommended |

**Bottom line on cost:**
- 🆓 **Level 1 (Free):** Use free tiers of Claude or Gemini. Limited but functional.
- 💰 **Level 2 (~$20/mo):** One paid subscription (Claude Pro OR ChatGPT Plus). Solid daily driver.
- 🚀 **Level 3 (~$40-60/mo):** Multiple providers (Claude Pro + ChatGPT Plus + Gemini). Full multi-model routing, never hit rate limits, the whole system fires on all cylinders.

You can start at Level 1 and upgrade as you see the value. Everything in this kit works at every level.

---

# 🏗️ THE THREE LEVELS

Not everyone needs the full setup. Pick your level:

### Level 1: The Basics (30 minutes)
**What you get:** A smart chatbot on Telegram that remembers things and has a personality.

- Install Moltbot
- Connect Telegram
- Drop in `AGENTS.md` + `SOUL.md` templates
- Done. You have a useful AI assistant.

**Good for:** People who want a better ChatGPT that lives in Telegram, remembers context, and has character.

### Level 2: The Operator (2 hours)
**Everything in Level 1, plus:**

- Multi-model routing (don't burn expensive tokens on simple tasks)
- Heartbeat monitoring (your AI checks in proactively)
- Usage tracking (know when you're running low)
- Local Ollama fallback (never hit zero)

**Good for:** People who use AI daily and want it smarter, cheaper, and always available.

### Level 3: The Machine (4+ hours, then it evolves itself)
**Everything in Level 2, plus:**

- Self-healing watchdog (fixes itself at 3 AM)
- Learning security monitor (detects threats, learns your patterns)
- Overnight builds (AI builds tools while you sleep)
- Personal learning loop (AI learns your habits and anticipates needs)
- Emergency controls (kill switch when needed)

**Good for:** People who want an autonomous AI employee that runs 24/7 and gets smarter every day.

---

## ⚡ Quick Start (5 Minutes to Live)

```bash
# 1. Install
npm install -g clawdbot

# 2. Setup (connects Telegram + your AI model)
clawdbot init

# 3. Send a message on Telegram. You're live.
```

That gives you a chatbot. Everything below turns it into an **employee**.

---

## What's In This Kit

```
moltbot-starter-kit/
├── README.md                      ← You are here (the deep guide)
├── templates/                     ← Copy these to your workspace
│   ├── AGENTS.md                  — Operating system for your AI
│   ├── SOUL.md                    — Personality & identity template
│   ├── HEARTBEAT.md               — Proactive monitoring tasks
│   └── SECURITY.md                — Confirmation protocols
├── scripts/                       ← Drop these in your scripts/ folder
│   ├── watchdog.sh                — Self-healing watchdog (13 checks, 4 escalation levels)
│   ├── watchdog_learn.sh          — Incident learning & root cause analysis
│   ├── security_hound.py          — Learning security monitor (file integrity, network, processes)
│   ├── check_usage.py             — Rate limit monitoring with threshold alerts
│   └── emergency_lockdown.sh      — Break-glass emergency controls
└── docs/                          ← Reference documentation
    ├── MODEL_ROUTING.md           — Multi-model routing logic
    └── WATCHDOG_CONCEPTS.md       — Self-healing system architecture
```

**How to use it:** Clone this repo, copy `templates/` into your Moltbot workspace root, copy `scripts/` into your workspace scripts folder, customize the `[PLACEHOLDERS]`, and go.

---

# 🧠 THE ARCHITECTURE

## Level 1: The Brain (AGENTS.md + SOUL.md)

Most people install Moltbot and just... chat with it. That's like hiring an employee and never giving them a job description.

**AGENTS.md** is the operating system. It tells your AI:
- What to do when it wakes up (session startup checklist)
- How to organize files (MECE rules)
- When to use which AI model (routing decisions)
- How to handle errors (escalation philosophy)
- What to do proactively (overnight builds, heartbeat tasks)

**SOUL.md** is the personality. Without it, you get generic AI responses. With it, you get a character — dry wit, honest feedback, anticipates your needs instead of waiting for commands.

### The Prime Directives

These five rules govern everything the system does:

1. **Run Silently** — Handle errors, heal problems, no spam. If something breaks at 3 AM, fix it. The human wakes up to a working system.
2. **Learn Continuously** — Track patterns, preferences, goals. Get smarter every day.
3. **Anticipate Needs** — Don't wait to be asked. See the problem coming and act.
4. **Create Value** — Build tools, automate tasks, save time. Every minute saved matters.
5. **Stay Invisible** — The best assistant is one you forget exists. Until you need them.

### MECE File Organization

This sounds boring. It's actually the difference between a system that scales and one that collapses into a mess of duplicate files.

**MECE = Mutually Exclusive, Collectively Exhaustive**

Before your AI creates ANY file, it must:
1. Check the INDEX — does a home already exist?
2. Check for overlap — does another file cover this?
3. Choose the right level — root is for config only, everything else in subfolders
4. Update the INDEX after changes

Without this rule, your workspace balloons into 20+ root files with massive overlap. With it, every file has ONE purpose that no other file shares.

```
workspace/
├── Root (config only)     — AGENTS.md, SOUL.md, SECURITY.md, HEARTBEAT.md
├── notes/                 — Knowledge base by category
├── projects/              — Code projects (subfolders)
├── scripts/               — Automation scripts
├── docs/                  — Reference documentation
├── memory/                — Daily logs, state files
└── INDEX.md               — Master navigation
```

→ **Template:** [`templates/AGENTS.md`](templates/AGENTS.md) | [`templates/SOUL.md`](templates/SOUL.md)

---

## Level 2: Multi-Model Routing

This is the single biggest upgrade you can make. Instead of burning one expensive model on everything, route tasks to the right specialist.

### The Stack

| Tier | Role | Model | What It Does |
|------|------|-------|-------------|
| T0 | 🧠 Orchestrator | Claude Opus | Strategy, reasoning, main conversation |
| T1 | 💻 Code Specialist | OpenAI Codex | Writes all code, scripts, apps |
| T2 | 📡 Bulk/Background | Google Gemini | Heartbeats, summaries, monitoring |
| T3 | 🏠 Local Emergency | Ollama (local) | Runs on your machine when cloud is down |

### Why This Matters

Without routing, your best model handles everything — you burn through rate limits by noon. With routing:
- **Opus thinks and delegates** — architecture, strategy, complex reasoning
- **Codex writes code** — spawned as a sub-agent, doesn't touch your main session
- **Gemini does grunt work** — heartbeats, bulk summaries, monitoring tasks
- **Ollama is always there** — even if every cloud API goes down, you're never at zero

### The Routing Decision Flow

```
1. Is this CODING?           → Spawn Codex sub-agent
2. Is this SUMMARIZATION?    → Spawn Gemini sub-agent
3. Is this DEEP RESEARCH?    → Handle directly (Opus is best)
4. Is this IMAGE GENERATION? → Use specialized image model
5. Is this COMPLEX/QUICK?    → Handle directly (Opus)
```

### Degradation Curve

As usage increases, the system automatically becomes more conservative:

```
Usage %    Behavior
0-80%      All models freely available
80-90%     Prefer cheaper models for applicable tasks
90-95%     Only Codex + Gemini (minimize expensive model)
95-100%    Codex + Gemini only
100%+      Gemini + Local (never hit zero)
```

### Setup

Install a local fallback (your safety net):
```bash
brew install ollama
ollama pull qwen2.5:14b
```

Configure heartbeat model to Gemini in your Moltbot config — saves your best model for real work.

→ **Full reference:** [`docs/MODEL_ROUTING.md`](docs/MODEL_ROUTING.md)

---

## Level 3: Self-Healing Watchdog

This is what separates a toy from a production system. The watchdog runs every 5 minutes and fixes problems before you notice them.

### 13 Health Checks Per Cycle

| # | Check | What It Does |
|---|-------|-------------|
| 1 | **Gateway process** | Is Moltbot running? If not, start it. |
| 2 | **Memory usage** | >2GB? Kill and restart (memory leak). |
| 3 | **Process uptime** | >48 hours? Routine restart (prevents drift). |
| 4 | **Health endpoint** | Can it respond? Track consecutive failures. |
| 5 | **Proactive doctor** | Run `clawdbot doctor` every 6h to catch issues early. |
| 6 | **Heartbeat response** | No response for 60+ min? Alert — may be stuck. |
| 7 | **Disk space** | >95%? Auto-clean old logs. |
| 8 | **Local LLM** | Is Ollama running? If not, start it (your backup). |
| 9 | **Predictive analysis** | Scan patterns, predict failures before they happen. |
| 10 | **Model health** | Are AI APIs responding? Track error rates. |
| 11 | **External ping** | Optional: ping an uptime monitor (UptimeRobot, etc). |
| 12 | **Error recovery** | Scan logs, auto-apply known fixes. |
| 13 | **Pipeline health** | Full message flow check (send → process → respond). |

### The 4-Level Escalation Ladder

```
Problem detected
    ↓
Level 1: Run clawdbot doctor --fix
         (fixes auth expiry, config issues, 90% of problems)
    ↓ (if that didn't work)
Level 2: Restart gateway
         (kills process, starts fresh)
    ↓ (if still broken)
Level 3: Switch to fallback model
         (keeps running on alternative AI)
    ↓ (nuclear option — all else failed)
Level 4: Alert human
         (ONE notification with context, not spam)
```

### The Learning Part (Machine Learning Lite)

Every intervention is logged and analyzed. The system tracks:
- **Which fixes work for which errors** (success rates per fix type)
- **Pattern detection** (3+ of the same problem = not a fluke, adapt)
- **Root cause analysis** (check trigger first, then scan logs for clues)
- **Prevention rules** (automatically applied based on learned patterns)

This means the watchdog gets smarter over time. Month 1, it might restart the gateway for an auth issue. Month 2, it knows to run `doctor --fix` first, which is faster and less disruptive.

### Setup

```bash
# 1. Copy the watchdog scripts to your workspace
cp scripts/watchdog.sh ~/clawd/scripts/
cp scripts/watchdog_learn.sh ~/clawd/scripts/
chmod +x ~/clawd/scripts/watchdog*.sh

# 2. Create a launchd plist (macOS) — runs every 5 minutes
cat > ~/Library/LaunchAgents/com.moltbot.watchdog.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.moltbot.watchdog</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>REPLACE_WITH_YOUR_PATH/scripts/watchdog.sh</string>
    </array>
    <key>StartInterval</key>
    <integer>300</integer>
    <key>StandardOutPath</key>
    <string>/tmp/watchdog-stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/watchdog-stderr.log</string>
</dict>
</plist>
EOF

# 3. Load it
launchctl load ~/Library/LaunchAgents/com.moltbot.watchdog.plist
```

For Linux, use a cron job instead:
```bash
# Run every 5 minutes
*/5 * * * * /bin/bash /path/to/scripts/watchdog.sh >> /tmp/watchdog.log 2>&1
```

→ **Full code:** [`scripts/watchdog.sh`](scripts/watchdog.sh) | [`scripts/watchdog_learn.sh`](scripts/watchdog_learn.sh)
→ **Architecture:** [`docs/WATCHDOG_CONCEPTS.md`](docs/WATCHDOG_CONCEPTS.md)

---

## Level 4: Learning Security Monitor

A lightweight "security hound" that learns what's normal on your system and barks when something isn't.

### What It Monitors

**File Integrity (SHA256)**
Hashes critical config files on first run (baseline). Every scan, it re-hashes and compares. If someone modifies `.zshrc`, `authorized_keys`, `/etc/hosts`, or your Moltbot config, you know instantly.

**Network Connections**
Monitors active connections via `lsof`. Learns which processes normally connect where. Alerts on new, unusual outbound connections from unknown processes. Over time, builds a model of what "normal" looks like for your machine.

**Suspicious Processes**
Scans the process list for known-bad patterns: crypto miners, keyloggers, backdoors, reverse shells. Simple but catches the obvious stuff.

**Alert Deduplication**
Won't repeat the same alert within 60 minutes. No notification spam.

**Learning**
When an alert is a false positive, mark it:
```bash
python3 security_hound.py --learn-fp "New connection: node → 127.0.0.1:3000"
```
The hound remembers and won't bark at that pattern again. Over time, it goes from noisy to precise.

### Setup

```bash
cp scripts/security_hound.py ~/clawd/scripts/
chmod +x ~/clawd/scripts/security_hound.py

# Test it
python3 ~/clawd/scripts/security_hound.py | jq .
```

Add to your HEARTBEAT.md so it runs every hour automatically.

→ **Full code:** [`scripts/security_hound.py`](scripts/security_hound.py)

---

## Level 5: Proactive Heartbeats

Heartbeats transform your AI from reactive (waits for commands) to proactive (checks in, does work, reaches out).

### How It Works

Moltbot polls your AI at a set interval (e.g., every hour). The AI reads `HEARTBEAT.md` for instructions on what to check. Use a cheap model (Gemini) — don't burn your best model on monitoring.

### What To Check

```markdown
## Every Heartbeat
- Usage monitoring (alert at 80%, 90%, 95%)
- Security scan (security_hound.py)

## Every 4th Heartbeat (~4 hours)
- System health (disk, memory, process health)
- Personal learning loop (pattern detection)

## Weekly
- Auto-update packages (brew update)
- Clean temp files
- Full security audit
```

### The Usage Alert System

Tracks Claude rate limits and alerts at thresholds:

| Threshold | Action |
|-----------|--------|
| 80% | ⚠️ "Running low!" |
| 90% | 🚨 Code Red alert |
| 95% | "Almost out!" |
| 100% | "Limit hit — wait for reset" |

On each heartbeat, `check_usage.py` compares current usage against previously-alerted thresholds. Only notifies on NEW threshold crossings, not repeats.

→ **Template:** [`templates/HEARTBEAT.md`](templates/HEARTBEAT.md)
→ **Usage script:** [`scripts/check_usage.py`](scripts/check_usage.py)

---

## Level 6: Emergency Controls

Sometimes you need to pull the plug. The emergency lockdown gives you instant control:

```bash
# Kill all Moltbot processes immediately
emergency_lockdown.sh kill

# Shut down the entire computer in 60 seconds
emergency_lockdown.sh shutdown

# Cancel a pending shutdown
emergency_lockdown.sh cancel

# Check status
emergency_lockdown.sh status
```

### Security Confirmation Protocol

For sensitive operations (sending emails, financial transactions, file deletions), set up a confirmation system:

**Tiered approach:**
- **Critical** (financial, public posts): Requires passphrase + Telegram confirmation
- **High** (emails, file changes): Requires Telegram confirmation
- **Medium** (internal operations): AI proceeds but logs the action
- **Low** (reading, organizing): No confirmation needed

→ **Template:** [`templates/SECURITY.md`](templates/SECURITY.md)
→ **Script:** [`scripts/emergency_lockdown.sh`](scripts/emergency_lockdown.sh)

---

## Level 7: Overnight Builds

The flex. While you sleep, your AI builds things.

### How It Works
1. Maintain a "build queue" in your workspace
2. Set a 2 AM cron job:
   ```
   clawdbot cron add --schedule "0 2 * * *" --text "Check PROJECTS.md build queue, pick something small, build it"
   ```
3. AI picks a task, builds it, stages for review
4. You wake up to new tools

### Rules
- **Scope: 1-2 hours max.** One focused improvement.
- **Never push live.** Stage everything for human review.
- **Report in the morning.** Include what was built.
- **Safety rails.** No deletions, no external sends, no production commits.

What's been built overnight so far: web apps, research documents, analytics tools, automation scripts.

---

## Level 8: Personal Learning Loop

The system doesn't just work for you — it *learns* you.

### What It Tracks
- **Goal mentions** — which goals come up most? Which ones are stale?
- **Emotional signals** — stress, loneliness, overwhelm (detected via language patterns)
- **Decision patterns** — what you say you'll do vs. what you actually do
- **Preferences** — communication style, tools, topics, schedule patterns

### How It Works
A Python script (`personal_learner.py`) scans your memory files for patterns. It builds a JSON model:

```json
{
  "goals": {
    "fitness": {"frequency": "daily", "sentiment": "positive", "last_mentioned": "2026-01-28"},
    "dating": {"frequency": "weekly", "sentiment": "mixed", "last_mentioned": "2026-01-27"}
  },
  "patterns": {
    "most_productive_hours": "9am-12pm",
    "stress_triggers": ["deadlines", "social situations"],
    "preferred_communication": "direct, no fluff"
  }
}
```

The AI references this model to:
- Nudge you about forgotten goals (7+ days stale)
- Adapt its communication style to your mood
- Anticipate what you need before you ask
- Surface insights at the right time

---

# 📊 SUGGESTED SETUP ORDER

Follow this sequence for the smoothest experience:

| Phase | What To Do | Time |
|-------|-----------|------|
| **1. Go Live** | Install Moltbot, connect Telegram, send first message | ~15 min |
| **2. Give It a Brain** | Copy `AGENTS.md` + `SOUL.md` templates, customize personality | ~30 min |
| **3. Multi-Model** | Set up model routing (Opus + Codex/Gemini + Ollama fallback) | ~30 min |
| **4. Self-Healing** | Install watchdog scripts, set up launchd/cron | ~45 min |
| **5. Security** | Deploy security hound, set up heartbeat monitoring | ~30 min |
| **6. Organize** | Create INDEX.md, set up folder structure, MECE rules | ~15 min |
| **7. Overnight Builds** | Set up 2 AM cron job, create build queue | ~10 min |
| **8. Evolve** | Personal learning loop, smart home, custom integrations | Ongoing |

**What you'll have when you're done:**
- Self-healing system that fixes problems without you touching it
- Multiple AI models routing intelligently (never hit zero capacity)
- 24/7 security and health monitoring
- AI that builds tools while you sleep
- Learns your patterns and anticipates your needs
- 13-point health check every 5 minutes

---

# 🚀 GET STARTED

```bash
# 1. Install Moltbot
npm install -g clawdbot

# 2. Init (Telegram + model setup)
clawdbot init

# 3. Clone this kit
git clone https://github.com/[USERNAME]/moltbot-starter-kit.git

# 4. Copy templates to your workspace
cp moltbot-starter-kit/templates/* ~/clawd/

# 5. Copy scripts
mkdir -p ~/clawd/scripts
cp moltbot-starter-kit/scripts/* ~/clawd/scripts/
chmod +x ~/clawd/scripts/*.sh

# 6. Install local LLM fallback
brew install ollama && ollama pull qwen2.5:14b

# 7. Set up the watchdog (see Level 3 for launchd setup)

# 8. Customize the templates
# Edit SOUL.md with your AI's personality
# Edit AGENTS.md with your rules
# Edit HEARTBEAT.md with your check tasks

# 9. Send a message. Watch it come alive.
```

---

# 📚 Resources

- **Moltbot Docs:** [docs.molt.bot](https://docs.molt.bot)
- **Moltbot GitHub:** [github.com/moltbot/moltbot](https://github.com/moltbot/moltbot)
- **Discord Community:** [discord.com/invite/clawd](https://discord.com/invite/clawd)
- **Skills Hub:** [clawdhub.com](https://clawdhub.com)

---

---

# 🔧 TROUBLESHOOTING

Real problems you'll hit, and how to fix them. All of these were discovered in the first 48 hours of running this system.

## Telegram Issues

**Bot doesn't respond to messages:**
- Run `clawdbot health` — check if "Telegram: ok" shows
- If not: `clawdbot gateway restart`
- Still broken? `clawdbot doctor --fix` — often catches expired auth
- Nuclear option: stop gateway, delete session files, restart fresh

**Bot responds but very slowly (30+ seconds):**
- Context is probably bloated. Your AI's conversation history is too long.
- Fix: Reset the session — `clawdbot gateway restart` or set up a daily session reset cron
- Prevention: Add a 5:30 AM daily session reset cron job

**"Context overflow" or "prompt too large" errors:**
- Session context has grown too big for the model
- Fix: Restart gateway (clears active session)
- Prevention: Set `cache-ttl` mode in config, or schedule daily resets
- Long-term: After big projects, ask the AI to summarize and reset

## Claude / Model Issues

**"Unknown model" errors (e.g., `claude-sonnet-4` not found):**
- Some models may not be available in your Clawdbot version
- Fix: Switch to a model you know works: `clawdbot config` and update the model name
- Common: If you configured Sonnet for heartbeats/subagents but it's unavailable, switch to Gemini
- This silently breaks heartbeats and cron jobs — you won't notice until something doesn't fire

**Auth token expired / OAuth errors:**
- `clawdbot doctor --fix` resolves 90% of these
- If recurring: consider API-key auth instead of OAuth (more stable)
- The watchdog's proactive doctor run (every 6h) catches these automatically

**Rate limiting (429 errors):**
- You've hit your usage limit. Check with your usage monitoring script.
- Degradation curve kicks in — system should automatically shift to cheaper models
- If ALL models are rate-limited: Ollama local fallback keeps you running
- Prevention: Route heartbeats/bulk work to Gemini, save your main model for real conversations

**LLM request timeouts:**
- Complex tasks (deep research, large code generation) can exceed the default timeout
- The watchdog will log these but they're usually transient
- If recurring: break complex tasks into smaller chunks when prompting

**"All models failed" error:**
- Every model in your fallback chain is down or rate-limited
- Check: Is Ollama running? (`pgrep ollama` — if not, `ollama serve`)
- Check: Are you on wifi? Network issues take out all cloud models at once
- The watchdog should auto-start Ollama, but verify it's configured

## Watchdog Issues

**Watchdog isn't running:**
- Check: `launchctl list | grep moltbot` (macOS) or `crontab -l` (Linux)
- Verify the plist/cron points to the correct path for watchdog.sh
- Check logs: `cat ~/.moltbot/logs/watchdog.log | tail -20`

**Getting spammed with notifications:**
- Old watchdog versions would send separate alerts for each error type
- Fix: The v2 learning script batches related errors into ONE notification
- Set a 30-minute global notification cooldown in the watchdog config

**Triple notification spam for one incident:**
- Classic v1 bug: the health check, model check, and doctor each triggered separate alerts
- Fix: v2 checks trigger FIRST, then logs. Uses batched escalation.
- Already fixed in the scripts included in this kit

## General Tips

**"It deleted my config!"**
- Always back up `~/.moltbot/config.yaml` before asking your AI to modify configs
- Better: tell the AI "show me the config change first, don't apply it until I approve"
- The SECURITY.md template includes confirmation tiers for exactly this reason

**Things break when you switch models rapidly:**
- Each model has different context handling. Switching mid-conversation can confuse state.
- Best practice: finish a task on one model, reset session, then switch

**Session corruption after long use:**
- Long sessions (12+ hours of heavy use) can accumulate malformed context
- Prevention: Daily 5:30 AM session reset cron
- Recovery: Stop gateway, archive sessions folder, restart fresh

```bash
# Daily session reset cron (add via clawdbot)
clawdbot cron add --schedule "30 5 * * *" --text "Summarize yesterday, write to memory, then /new"
```

---

*Built in 48 hours. Improving itself every hour since.* 🐸
