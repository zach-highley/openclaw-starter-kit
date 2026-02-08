# Complete Setup Checklist

> Distilled from a 355-item audit of every OpenClaw config option.
> Check off as you go. Priority order: Security > Simplicity > Uptime > Automation > Memory.

---

## 🔴 Phase 1: Security (Do First)

### Gateway & Auth
- [ ] Set `gateway.auth.mode: "token"` with strong token from `.env`
- [ ] Set `gateway.bind: "loopback"` (127.0.0.1 only)
- [ ] Set `gateway.mode: "local"`
- [ ] Set `gateway.trustedProxies: ["127.0.0.1"]`
- [ ] Set `gateway.controlUi.allowInsecureAuth: false`
- [ ] Set `gateway.controlUi.dangerouslyDisableDeviceAuth: false`
- [ ] Set `gateway.auth.allowTailscale: false` (unless using Tailscale)
- [ ] Set `gateway.tailscale.mode: "off"` (unless using Tailscale)

### Channels
- [ ] Set `channels.<channel>.dmPolicy: "pairing"`
- [ ] Set `channels.<channel>.allowFrom: ["YOUR_ID"]`
- [ ] Set `channels.<channel>.groupPolicy: "allowlist"`
- [ ] Set `channels.<channel>.configWrites: false`

### Discovery
- [ ] Set `discovery.mdns.mode: "off"`

### Commands
- [ ] Set `commands.bash: false`
- [ ] Set `commands.config: false`
- [ ] Set `commands.debug: false`
- [ ] Set `commands.restart: false`

### Elevated
- [ ] Set `tools.elevated.allowFrom` to your Telegram ID only
- [ ] Remove any webchat wildcards from `allowFrom`

### Sandbox
- [ ] Set `agents.defaults.sandbox.mode: "non-main"`
- [ ] Set `agents.defaults.sandbox.workspaceAccess: "ro"`

### Secrets
- [ ] All API keys in `~/.openclaw/.env` (not in config)
- [ ] No secrets in workspace markdown files
- [ ] No secrets in `HEARTBEAT.md`
- [ ] `.gitignore` covers `.env`, `secrets/`, `logs/`
- [ ] `chmod 700 ~/.openclaw && chmod 600 ~/.openclaw/openclaw.json`

### Verify
- [ ] `openclaw security audit` → 0 critical, 0 warnings

---

## 🟡 Phase 2: Core Setup

### Service Management
- [ ] `openclaw onboard --install-daemon` (launchd/systemd)
- [ ] Verify `KeepAlive=true` in plist/unit
- [ ] Test restart: kill gateway, verify auto-restart

### Model Configuration
- [ ] Primary model set (e.g., `anthropic/claude-opus-4-6`)
- [ ] At least one fallback configured
- [ ] Test each model: `openclaw message "test" --model <model>`
- [ ] Model aliases configured for convenience
- [ ] Prompt caching enabled: `models.<model>.params.cacheRetention: "long"`

### Auth Profiles
- [ ] Primary provider auth configured (token or OAuth)
- [ ] Fallback provider auth configured
- [ ] OpenRouter key in `.env` with `OPENROUTER_API_KEY=` prefix (if using)

### Workspace Files
- [ ] `AGENTS.md` — operating rules
- [ ] `SOUL.md` — personality
- [ ] `USER.md` — about the human
- [ ] `IDENTITY.md` — quick identity card
- [ ] `MEMORY.md` — long-term memory
- [ ] `BOOT.md` — gateway startup tasks
- [ ] `HEARTBEAT.md` — periodic tasks (keep minimal or empty)
- [ ] `TOOLS.md` — environment-specific notes

### Session Management
- [ ] `session.reset.mode: "daily"` (recommended)
- [ ] `session.reset.atHour` set to off-hours (e.g., 4 AM)
- [ ] `agents.defaults.timeoutSeconds: 3600` (or higher for long tasks)

### Messages
- [ ] `messages.ackReaction` set (emoji shown when message received)

---

## 🟢 Phase 3: Automation

### Heartbeat
- [ ] `heartbeat.every: "30m"` (minimum, prevents token burn)
- [ ] `heartbeat.activeHours` set to waking hours
- [ ] `heartbeat.target: "last"`

### Cron Jobs
- [ ] MECE check: no overlapping jobs
- [ ] Daily maintenance cron (5 AM, `openclaw doctor --fix`)
- [ ] All crons use `sessionTarget: "isolated"` (don't pollute main session)

### Hooks
- [ ] `hooks.enabled: true`
- [ ] `session-memory` hook enabled
- [ ] `boot-md` hook enabled
- [ ] `command-logger` hook enabled (optional)

### Approvals (Optional)
- [ ] `approvals.exec.enabled` — decide based on trust level
- [ ] Approval targets configured (Telegram or dashboard)

---

## 🔵 Phase 4: Memory & Context

### Memory Backend
- [ ] `memory.backend: "qmd"` (recommended)
- [ ] `qmd.sessions.enabled: true`
- [ ] `qmd.sessions.retentionDays` set (60-120 days)
- [ ] `qmd.update.onBoot: true`

### Memory Search
- [ ] `memorySearch.enabled: true`
- [ ] Embedding provider configured (e.g., Gemini — free)
- [ ] Hybrid search enabled (vector + text)
- [ ] Extra memory paths added if using PALA/custom dirs

### Context Pruning
- [ ] `contextPruning.mode: "cache-ttl"` (recommended)
- [ ] TTL set (7d is good default)
- [ ] `keepLastAssistants` set (8 is good default)

### Compaction
- [ ] `compaction.mode: "safeguard"`
- [ ] `memoryFlush.enabled: true` (saves context before compaction)

---

## ⚪ Phase 5: Quality of Life

### Telegram Delivery
- [ ] `chunkMode: "length"` (NOT "newline")
- [ ] `textChunkLimit: 4096`
- [ ] `blockStreaming: true`
- [ ] `blockStreamingCoalesce` configured

### Logging
- [ ] `logging.level: "info"`
- [ ] `logging.redactSensitive: "tools"`
- [ ] Log file permissions locked

### Tools
- [ ] Web search enabled (Brave API recommended)
- [ ] Web fetch enabled
- [ ] Only needed plugins in `plugins.allow`

### Concurrency
- [ ] `maxConcurrent: 10` (or appropriate for your usage)
- [ ] `CLI terminals.maxConcurrent: 10`

### Thinking & Verbosity
- [ ] `thinkingDefault: "high"` (for best reasoning)
- [ ] `verboseDefault: "on"` (see what the agent sees)

---

## Verification

After completing all phases:

```bash
# Health check
openclaw status
openclaw doctor --non-interactive
openclaw health

# Security audit
openclaw security audit

# Test message delivery
openclaw message "Setup complete. All systems operational."

# Check cron jobs
openclaw cron list

# Verify no overlapping jobs
# Each job should serve a unique, non-overlapping purpose
```

---

## Maintenance Schedule

| Frequency | What |
|-----------|------|
| Daily (automated) | `openclaw doctor --fix` at 5 AM |
| Weekly | Review cron jobs, check for overlap |
| Monthly | `openclaw security audit`, review memory retention |
| On update | Follow safe update checklist (pause → backup → update → verify) |
| On incident | Document in `memory/incidents.md`, update configs |
