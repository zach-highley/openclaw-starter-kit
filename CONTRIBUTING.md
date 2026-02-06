# Contributing to OpenClaw Starter Kit

## Document Categories

Before pushing any learnings, they must fit one of these categories:

### 1. Core Best Practices (Universal)
Everyone benefits from these:
- Memory and context management
- Uptime and reliability patterns
- Security hardening
- Notification systems
- Cron/heartbeat patterns

**Location:** Root docs (`docs/*.md`)

### 2. Advanced Patterns (Optional)
Power-user features not everyone needs:
- Model failover strategies
- Ralph loops / Codex integration
- Complex automation chains
- Multi-agent patterns

**Location:** `docs/ADVANCED/`

### 3. Example Preferences (Take It or Leave It)
Personal setup examples from contributors. Others can adopt or ignore:
- Personality styles (British humor, grumpy grandpa, etc.)
- Hardware integrations (Eight Sleep, Hue lights, cameras)
- Platform-specific setups

**Location:** `examples/preferences/`

## Before You Push

Ask yourself:
1. **Which category?** If none, don't push.
2. **Is it user-agnostic?** Replace personal info with `[USER]`, `[EMAIL]`, etc.
3. **Is it helpful?** Skip internal debugging notes.
4. **Is it secure?** No tokens, IDs, real emails, or paths.

## Privacy Checklist

- [ ] No real names (use `[USER]`)
- [ ] No emails (use `[EMAIL]`)
- [ ] No Telegram IDs (use `[CHAT_ID]`)
- [ ] No API keys or tokens
- [ ] No personal file paths (use `~` or `[HOME]`)
