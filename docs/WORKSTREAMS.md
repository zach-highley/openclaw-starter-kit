# WORKSTREAMS.md — One Canonical Chat, Many Workstreams (SSOT)

If your assistant is running a lot of automation (cron, heartbeat, subagents, UI control), splitting work across many chat threads tends to increase failure modes: duplicated context, conflicting instructions, and more chances to poke config in inconsistent ways.

The pattern that actually scales is:

- **One canonical chat** for decisions, approvals, and receipts.
- **One Single Source of Truth (SSOT)** for workstream status (a file in your repo).
- Optional: a **logs feed** that never contains decisions.

This keeps your brain in one place while still letting the agent run parallel streams.

---

## Recommended Structure

### 1) Canonical chat (Telegram, iMessage, Slack)
Use the canonical chat for:
- Decisions and prioritization
- Approvals for sensitive actions (posting publicly, sending messages, deleting, payments)
- Receipts: links, screenshots, commit hashes, file paths

Avoid:
- Long logs
- Multiple overlapping threads about the same work

### 2) SSOT workstreams file (repo)
Create a file such as:
- `docs/WORKSTREAMS.md` (this file)
- or `state/current_work.json` (machine-readable queue)

Each workstream should have:
- **Goal**
- **Status** (BLOCKED / IN PROGRESS / DONE)
- **Next 3 steps**
- **Blockers**
- **Receipts** (links, screenshots, commits)

### 3) Optional logs feed
If you want more visibility without polluting the canonical chat:
- Create a second chat/channel purely for logs.
- Rule: **no decisions** in the logs channel.

---

## Template

Copy this section into your own SSOT file:

```md
## Workstream: <name>
**Goal:** <what success looks like>

**Status:** <BLOCKED|IN PROGRESS|DONE>

**Receipts:**
- <commit hash / PR>
- <file path>
- <screenshot path>

**Next:**
1) <next step>
2) <next step>
3) <next step>

**Blockers:**
- <blocker>
```

---

## Why this works

- **Prevents context fragmentation:** the canonical chat stays stable.
- **Reduces agent thrash:** fewer cross-thread contradictions.
- **Makes progress auditable:** workstreams always point to receipts.
- **Supports parallel work:** multiple streams, one brain.
