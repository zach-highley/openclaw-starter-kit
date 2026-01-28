# 🐸 The Moltbot Starter Kit
### Turn Moltbot Into a Self-Healing, Multi-Model Autonomous AI System

**What is Moltbot?** It's a free, open-source tool that connects AI models (like Claude, ChatGPT, Gemini) to your phone via Telegram, WhatsApp, or Discord. Instead of going to a website to chat with AI, it comes to YOU — in your pocket, 24/7. This starter kit turns that basic chatbot into an autonomous AI employee.

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
| **Node.js 22+** | Runs Moltbot (don't worry, the installer handles this) | Free |
| **Telegram** | Your primary chat interface | Free |
| **Homebrew** (Mac) | Installs dependencies | Free |
| **Git** | Clone this repo (or just paste the link to your bot — see below) | Free |
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

### Never opened a terminal before? Start here.

<details>
<summary><strong>🍎 Mac: Open Terminal</strong> (click to expand)</summary>

1. Press `Cmd + Space`, type **Terminal**, hit Enter
2. You're in. That black/white window is your terminal.

**Install Node.js** (required, one-time):
```bash
# This installs Homebrew (Mac package manager) + Node.js
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install node
```
</details>

<details>
<summary><strong>🪟 Windows: Install WSL2 first</strong> (click to expand)</summary>

1. Open PowerShell as Admin
2. Run: `wsl --install`
3. Restart your computer
4. Open "Ubuntu" from Start menu
5. Now follow the Linux steps below
</details>

<details>
<summary><strong>🐧 Linux: You probably already have a terminal</strong></summary>

Install Node.js if you don't have it:
```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
```
</details>

### Now install Moltbot:

```bash
# 1. Install (one command)
curl -fsSL https://molt.bot/install.sh | bash

# 2. Run the setup wizard (connects Telegram, picks your AI model, everything)
moltbot onboard

# 3. Send a message on Telegram. You're live.
```

That gives you a chatbot. Everything below turns it into an **employee**.

### 🚀 Skip the repo cloning — just tell your bot

Don't know Git? Don't want to clone repos? Once your bot is running, just send it this message:

> "Hey, can you take a look at this repo and integrate everything it suggests? Think hard about it, make sure it works with our current setup, and don't change anything until I give the OK. Also, point out anything that looks wrong or doesn't apply to us: https://github.com/[USERNAME]/moltbot-starter-kit"

Your bot will read the repo, understand the templates and scripts, and walk you through what to adopt. No terminal skills needed beyond the initial install.

### ❓ Stuck? Something not working?

The official docs have answers to basically everything:
- **[FAQ & Troubleshooting](https://docs.molt.bot/help/faq)** — covers install issues, auth problems, Telegram setup, model errors, Windows quirks, and more
- **[Getting Started guide](https://docs.molt.bot/start/getting-started)** — step-by-step from zero
- **[Discord community](https://discord.com/invite/clawd)** — real people who can help

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

**How to use it:** Either clone this repo and copy the files manually (Option A in the Get Started section), OR just paste the repo link to your bot on Telegram and let it do the work for you (Option B — no Git needed). Your **workspace** is the folder where Moltbot stores its files — by default it's `~/clawd/` in your home directory.

---

# 🧠 THE ARCHITECTURE (Deep Dive)

Everything below explains *how* each piece works. You don't need to read it all — just the sections that match the level you picked above.

## The Brain (AGENTS.md + SOUL.md)

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

## Multi-Model Routing

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

## Self-Healing Watchdog

This is what separates a toy from a production system. The watchdog runs every 5 minutes and fixes problems before you notice them.

### 13 Health Checks Per Cycle

| # | Check | What It Does |
|---|-------|-------------|
| 1 | **Gateway process** | Is Moltbot running? If not, start it. |
| 2 | **Memory usage** | >2GB? Kill and restart (memory leak). |
| 3 | **Process uptime** | >48 hours? Routine restart (prevents drift). |
| 4 | **Health endpoint** | Can it respond? Track consecutive failures. |
| 5 | **Proactive doctor** | Run `moltbot doctor` every 6h to catch issues early. |
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
Level 1: Run moltbot doctor --fix
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

**The easy way:** Just tell your bot: *"Set up the watchdog from the moltbot-starter-kit repo. Run it every 5 minutes."* It will create the scripts and schedule them for you.

**The manual way** (if you prefer):

<details>
<summary><strong>🍎 Mac setup</strong> (click to expand)</summary>

```bash
# 1. Copy the watchdog scripts to your workspace
cp scripts/watchdog.sh ~/clawd/scripts/
cp scripts/watchdog_learn.sh ~/clawd/scripts/
chmod +x ~/clawd/scripts/watchdog*.sh

# 2. Create a scheduled task that runs the watchdog every 5 minutes
# (This is a "launchd plist" — Mac's way of scheduling background tasks)
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
        <string>REPLACE_WITH_YOUR_HOME_FOLDER/clawd/scripts/watchdog.sh</string>
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

# 3. Tell Mac to start running it
launchctl load ~/Library/LaunchAgents/com.moltbot.watchdog.plist
```
</details>

<details>
<summary><strong>🐧 Linux setup</strong> (click to expand)</summary>

```bash
# 1. Copy scripts
cp scripts/watchdog.sh ~/clawd/scripts/
cp scripts/watchdog_learn.sh ~/clawd/scripts/
chmod +x ~/clawd/scripts/watchdog*.sh

# 2. Add to cron (runs every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * /bin/bash $HOME/clawd/scripts/watchdog.sh >> /tmp/watchdog.log 2>&1") | crontab -
```
</details>

→ **Full code:** [`scripts/watchdog.sh`](scripts/watchdog.sh) | [`scripts/watchdog_learn.sh`](scripts/watchdog_learn.sh)
→ **Architecture:** [`docs/WATCHDOG_CONCEPTS.md`](docs/WATCHDOG_CONCEPTS.md)

---

## Learning Security Monitor

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

**The easy way:** Tell your bot: *"Set up the security hound from the moltbot-starter-kit repo."* Done.

**Manual:**
```bash
# Copy the script to your workspace
cp scripts/security_hound.py ~/clawd/scripts/

# Test it (you should see a JSON report with no alerts)
python3 ~/clawd/scripts/security_hound.py
```

Then add it to your `HEARTBEAT.md` so it runs automatically every hour.

→ **Full code:** [`scripts/security_hound.py`](scripts/security_hound.py)

---

## Proactive Heartbeats

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

## Emergency Controls

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

## Overnight Builds

The flex. While you sleep, your AI builds things.

### How It Works
1. Maintain a "build queue" in your workspace
2. Set a 2 AM cron job:
   ```
   moltbot cron add --schedule "0 2 * * *" --text "Check PROJECTS.md build queue, pick something small, build it"
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

## Personal Learning Loop

The system doesn't just work for you — it *learns* you.

### What It Tracks
- **Goal mentions** — which goals come up most? Which ones are stale?
- **Emotional signals** — stress, loneliness, overwhelm (detected via language patterns)
- **Decision patterns** — what you say you'll do vs. what you actually do
- **Preferences** — communication style, tools, topics, schedule patterns

### How It Works
Your bot automatically scans its memory files for patterns and builds a model of you over time. You don't need to set this up manually — just tell your bot about it and it handles the rest. Here's what the model looks like under the hood:

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

### Option A: The Terminal Way (for people comfortable with command line)

```bash
# 1. Install Moltbot
curl -fsSL https://molt.bot/install.sh | bash

# 2. Run the setup wizard
moltbot onboard

# 3. Clone this kit
git clone https://github.com/[USERNAME]/moltbot-starter-kit.git

# 4. Copy templates to your workspace
cp moltbot-starter-kit/templates/* ~/clawd/

# 5. Copy scripts
mkdir -p ~/clawd/scripts
cp moltbot-starter-kit/scripts/* ~/clawd/scripts/
chmod +x ~/clawd/scripts/*.sh

# 6. Install local LLM fallback (optional but recommended)
brew install ollama && ollama pull qwen2.5:14b

# 7. Set up the watchdog (see Level 3 for launchd setup)

# 8. Customize the templates
# Edit SOUL.md with your AI's personality
# Edit AGENTS.md with your rules
# Edit HEARTBEAT.md with your check tasks

# 9. Send a message. Watch it come alive.
```

### Option B: Let Your Bot Do It (no Git needed)

Once Moltbot is installed and running, just send your bot this message on Telegram:

> "Hey, can you take a look at this repo and integrate everything it suggests? Think hard about it, make sure it works with our current setup, and don't change anything until I give the OK: https://github.com/[USERNAME]/moltbot-starter-kit"

Your bot reads the repo, understands the architecture, and walks you through adopting each piece. It handles the file creation, script installation, and customization. You just approve.

---

# 📚 Resources

- **Moltbot Docs:** [docs.molt.bot](https://docs.molt.bot)
- **Getting Started:** [docs.molt.bot/start/getting-started](https://docs.molt.bot/start/getting-started)
- **FAQ & Troubleshooting:** [docs.molt.bot/help/faq](https://docs.molt.bot/help/faq)
- **Moltbot GitHub:** [github.com/moltbot/moltbot](https://github.com/moltbot/moltbot)
- **Discord Community:** [discord.com/invite/clawd](https://discord.com/invite/clawd)
- **Skills Hub:** [clawdhub.com](https://clawdhub.com)

---

# 🔧 TROUBLESHOOTING

Real problems you'll hit, and how to fix them. All of these were discovered the hard way.

**Before anything else:** Run these two commands in your terminal. They fix 90% of issues:
```bash
moltbot doctor --fix
moltbot gateway restart
```

**Still stuck?** Check the [official FAQ](https://docs.molt.bot/help/faq) or ask in the [Discord](https://discord.com/invite/clawd).

## Telegram Issues

**Bot doesn't respond to messages:**
- Run `moltbot health` — check if "Telegram: ok" shows
- If not: `moltbot gateway restart`
- Still broken? `moltbot doctor --fix` — often catches expired auth
- Nuclear option: stop gateway, delete session files, restart fresh

**Bot responds but very slowly (30+ seconds):**
- Context is probably bloated. Your AI's conversation history is too long.
- Fix: Reset the session — `moltbot gateway restart` or set up a daily session reset cron
- Prevention: Add a 5:30 AM daily session reset cron job

**"Context overflow" or "prompt too large" errors:**
- Session context has grown too big for the model
- Fix: Restart gateway (clears active session)
- Prevention: Set `cache-ttl` mode in config, or schedule daily resets
- Long-term: After big projects, ask the AI to summarize and reset

## Claude / Model Issues

**"Unknown model" errors (e.g., `claude-sonnet-4` not found):**
- Some models may not be available in your Moltbot version
- Fix: Switch to a model you know works: `moltbot config` and update the model name
- Common: If you configured Sonnet for heartbeats/subagents but it's unavailable, switch to Gemini
- This silently breaks heartbeats and cron jobs — you won't notice until something doesn't fire

**Auth token expired / OAuth errors:**
- `moltbot doctor --fix` resolves 90% of these
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
- Check logs: `cat ~/.clawdbot/logs/watchdog.log | tail -20`

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
- Always back up your Moltbot config before asking your AI to modify it
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
# Daily session reset cron (add via moltbot)
moltbot cron add --schedule "30 5 * * *" --text "Summarize yesterday, write to memory, then /new"
```

---

# ⚠️ DISCLAIMERS

**Use at your own risk.** This starter kit is provided "as is" with no warranties of any kind. By using these templates, scripts, and configurations, you accept full responsibility for what happens on your system.

**Security is YOUR responsibility.** The scripts in this kit (watchdog, security hound, emergency lockdown) are monitoring tools, not replacements for real security practices. They catch common issues but they are NOT enterprise-grade security software. If you're handling sensitive data, consult an actual security professional.

**AI makes mistakes.** These systems give your AI significant autonomy — running scripts, modifying files, monitoring your system. AI models can and will occasionally do unexpected things. Always review changes before deploying to production. The SECURITY.md template exists for a reason — use it.

**No liability for data loss, security breaches, or damages.** The authors of this starter kit are not responsible for any data loss, unauthorized access, system damage, financial loss, or any other damages resulting from the use of these tools. You are granting AI models access to your computer. Understand what that means.

**Not legal, financial, or security advice.** Nothing in this kit constitutes professional advice of any kind.

**Third-party services.** This kit references third-party AI providers (Anthropic, OpenAI, Google, etc.) and tools (Moltbot, Ollama, etc.). We have no control over their services, pricing, terms, or availability. Check their individual terms of service.

**Open source, community-contributed.** This is a community resource shared in good faith to help people get more out of their AI setup. It is not an official product. There is no support team. There is no SLA. If something breaks, the [Discord community](https://discord.com/invite/clawd) and [official docs](https://docs.molt.bot/help/faq) are your best bet.

**TL;DR:** Cool tools, free to use, not our fault if something goes wrong. Be smart, review what your AI does, and don't blindly trust any automated system with anything you can't afford to lose.

---

*Built in 48 hours. Improving itself every hour since.* 🐸
