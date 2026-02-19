# OpenClaw Concepts Pass — 2026-02-18

Full pass over official concepts docs completed.

## Scope

Source index: `https://docs.openclaw.ai/llms.txt`

Concept pages reviewed: **28**

- agent-loop
- agent-workspace
- agent runtime
- architecture
- compaction
- context
- features
- markdown-formatting
- memory
- messages
- model-failover
- model-providers
- models
- multi-agent routing
- oauth
- presence
- queue
- retry
- session-pruning
- session-tool
- session
- sessions
- streaming
- system-prompt
- timezone
- typebox
- typing-indicators
- usage-tracking

## What we integrated into starter-kit

1. **Stronger session discipline in templates**
   - Explicit startup reads (`SOUL.md`, `USER.md`, `TODO.md`, memory)
   - Main-session-only handling for sensitive `MEMORY.md`

2. **Terminal/coding execution guardrails**
   - `exec` + `pty:true` for interactive CLIs
   - `workdir` required
   - long-run process polling rules

3. **Config hygiene and safety defaults**
   - `gateway config.patch` over manual config writes
   - clearer critical-rule sections for incident prevention

4. **Messaging/formatting reliability**
   - Telegram-first formatting guidance
   - single dense update default, no bubble spam

5. **Heartbeat simplification**
   - practical 4-step health/context/memory/cron baseline

## Operational takeaway

When in doubt, return to basics:

- simplify automation,
- clarify ownership,
- tighten session and memory discipline,
- then scale back up deliberately.
