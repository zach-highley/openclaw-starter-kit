# Security Hardening — Complete Guide

> Based on a 355-item audit of every OpenClaw configuration option, plus community reports from MSP operators running 30+ agents.

This repo is public. Your workspace should assume attackers can read **everything** in git.

---

## Priority Order

1. 🔴 **Critical** — Do immediately, security risk
2. 🟡 **Recommended** — Do soon, significant improvement
3. 🟢 **Optional** — Nice to have

---

## 🔴 Critical Security Settings

### 1. Gateway Authentication

**Never run without auth.** Without a token, any local process can control your agent.

```json5
{
  gateway: {
    auth: {
      mode: "token",
      token: "${OPENCLAW_GATEWAY_TOKEN}",  // From .env
      allowTailscale: false                 // Unless you need it
    },
    bind: "loopback",                       // 127.0.0.1 only
    mode: "local",
    trustedProxies: ["127.0.0.1"]
  }
}
```

Generate a strong token:
```bash
openssl rand -hex 24
# Store in ~/.openclaw/.env as OPENCLAW_GATEWAY_TOKEN=<value>
```

### 2. Channel Lockdown

```json5
{
  channels: {
    telegram: {
      dmPolicy: "pairing",                  // Only paired users
      allowFrom: ["YOUR_TELEGRAM_ID"],       // Restrict to your ID only
      groupPolicy: "allowlist",              // No random groups
      configWrites: false                    // No config changes via chat
    }
  }
}
```

**Why `configWrites: false`?** If someone gains access to your chat, they can't modify your config. Defense in depth.

### 3. mDNS Discovery

```json5
{
  discovery: {
    mdns: { mode: "off" }
  }
}
```

With `mode: "on"`, anyone on your local network can discover your agent. This is fine for intentional multi-node setups, but dangerous for personal machines on shared networks (coffee shops, coworking spaces, apartments).

### 4. Command Restrictions

```json5
{
  commands: {
    bash: false,      // No shell access via chat
    config: false,    // No config changes via commands
    debug: false,     // No debug commands
    restart: false    // No restart via commands
  }
}
```

### 5. Sandbox Non-Main Agents

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        workspaceAccess: "ro",
        scope: "session"
      }
    }
  }
}
```

Sub-agents and isolated sessions get read-only workspace access and session-scoped sandboxing. Prevents a compromised CLI terminal from writing to your workspace.

### 6. Elevated Command Restrictions

```json5
{
  tools: {
    elevated: {
      enabled: true,
      allowFrom: {
        telegram: ["YOUR_TELEGRAM_ID"]
        // Do NOT add webchat wildcards
      }
    }
  }
}
```

Never add wildcard `"*"` to `allowFrom.webchat`. Anyone with dashboard access could approve elevated operations.

### 7. File Permissions

```bash
chmod 700 ~/.openclaw
chmod 600 ~/.openclaw/openclaw.json
chmod 600 ~/.openclaw/.env
chmod 600 /tmp/openclaw/openclaw.log  # If using file logging
```

### 8. Secrets Management

**NEVER put secrets in:**
- `openclaw.json` (loaded into prompts)
- `HEARTBEAT.md` (loaded every heartbeat cycle into prompt context)
- `MEMORY.md` or any workspace markdown file
- Git-tracked files

**ALWAYS put secrets in:**
- `~/.openclaw/.env` (loaded by gateway, not in prompts)
- Environment variables
- Credential stores (keyring, 1Password CLI, etc.)

Reference secrets in config: `"${VARIABLE_NAME}"`

---

## 🟡 Recommended Settings

### 9. Exec Approvals

```json5
{
  approvals: {
    exec: {
      enabled: true,
      mode: "both",
      targets: [{
        channel: "telegram",
        to: "YOUR_TELEGRAM_ID"
      }]
    }
  }
}
```

Every `exec` command requires your approval. Trade-off: security vs. autonomous operation speed.

### 10. Plugin Allowlist

```json5
{
  plugins: {
    allow: ["telegram", "memory-core"]  // Only what you need
  }
}
```

Don't load plugins you don't use. Each plugin is code that runs with gateway privileges.

### 11. Log Redaction

```json5
{
  logging: {
    redactSensitive: "tools"  // Redact sensitive tool output in logs
  }
}
```

### 12. Skill Security

Before installing any skill from ClawHub:
```bash
# Scan for credential leaks
mcp-scan <skill-path>
```

Community audit found **7.1% of skills have credential leaks.** Always scan before installing.

### 13. Security Audit

Run regularly:
```bash
openclaw security audit
# Target: 0 critical, 0 warnings
```

### 14. Git Push Guard

Before pushing to any public repo:
```bash
# Check repo visibility
scripts/git_push_guard.sh /path/to/repo

# Scan for secrets
rg -n "(api[_-]?key|token|secret|password|BEGIN [A-Z ]+PRIVATE KEY)" .
```

### 15. Safe Update Checklist

When updating OpenClaw:
1. Pause automation (disable heartbeat, cron)
2. Back up config + workspace
3. `openclaw gateway stop`
4. `npm i -g openclaw@latest`
5. `openclaw doctor --fix`
6. Smoke test: `openclaw message "Test"`
7. Re-enable automation
8. `openclaw gateway restart`

---

## 🟢 Optional / Advanced

### 16. CVE Awareness

Stay current with OpenClaw releases. Known past issues:
- CVE-2026-25253 (patched in versions after v2026.1.29)

Update promptly when security releases are announced.

### 17. Tailscale Mode

If not using Tailscale for remote access:
```json5
{
  gateway: {
    tailscale: { mode: "off" },
    auth: { allowTailscale: false }
  }
}
```

### 18. Control UI Security

```json5
{
  gateway: {
    controlUi: {
      allowInsecureAuth: false,
      dangerouslyDisableDeviceAuth: false
    }
  }
}
```

Both should always be `false` in production.

### 19. Prompt Injection Awareness

When the agent browses the web or reads untrusted files, malicious content can contain hidden instructions. OpenClaw wraps external content in security notices, but be aware:
- Untrusted web content is automatically wrapped with injection warnings
- Sandbox mode for web research adds isolation
- Never have the agent execute commands found in web content without review

### 20. OpenClaw Analyzer (Third-Party)

The Guardz team built an open-source analyzer that catches things the built-in audit might miss:
- Plaintext secrets in config
- Identity/context leaks
- mDNS broadcast risks
- Tool over-privilege

```bash
git clone https://github.com/guardzcom/security-research-labs
cd security-research-labs/openclaw-security-analyzer
```

---

## Security Incident Response

If you suspect compromise:

1. **Stop the gateway immediately:** `openclaw gateway stop`
2. **Rotate ALL tokens:** gateway, API keys, bot tokens
3. **Check git history:** `git log --all --oneline` for unauthorized commits
4. **Review chat logs:** Look for messages you didn't send
5. **Check .env and config:** Look for modified secrets
6. **Fresh install if uncertain:** `openclaw configure` from scratch
7. **Document what happened:** `memory/incidents.md`

Don't try to "clean" a compromised system. Wipe and rebuild. It's faster and more certain.

---

## Quick Checklist

```
[ ] Gateway auth token set (strong, from .env)
[ ] Gateway bound to loopback
[ ] Telegram allowFrom set to your ID only
[ ] configWrites: false on all channels
[ ] mDNS discovery: off
[ ] commands.bash/config/debug/restart: false
[ ] Elevated allowFrom: your Telegram ID only (no wildcards)
[ ] Sandbox: non-main, read-only workspace
[ ] File permissions: 700 on ~/.openclaw, 600 on config files
[ ] No secrets in workspace markdown files
[ ] All secrets in .env with ${VAR} references
[ ] openclaw security audit: 0 critical, 0 warnings
[ ] .gitignore covers .env, secrets/, logs/
```
