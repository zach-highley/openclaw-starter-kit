# OpenClaw FAQ & Best Practices Audit
*Deep comparison of docs.openclaw.ai against a production system*

What we're doing right, what we're doing better than built-in, what we were missing, and what we were reinventing.

---

## ✅ USING BUILT-IN FEATURES CORRECTLY

| Feature | Status | Details |
|---------|--------|---------|
| Memory layout (MEMORY.md + memory/YYYY-MM-DD.md) | ✅ | Matches docs exactly |
| memorySearch (vector + embeddings) | ✅ | Local provider + cloud fallback |
| Session memory (experimental) | ✅ | `experimental.sessionMemory: true` |
| Memory flush before compaction | ✅ | Custom prompt saves to state files too |
| Heartbeat (1h batched checks) | ✅ | HEARTBEAT.md follows cron-vs-heartbeat guide |
| Cron for exact timing | ✅ | Isolated crons for scheduled tasks |
| Workspace files (AGENTS/SOUL/USER/TOOLS/HEARTBEAT.md) | ✅ | Full layout |
| Context pruning (cache-ttl) | ✅ | Soft trim + hard clear |
| Internal hooks (boot-md, session-memory, command-logger) | ✅ | All enabled |
| Subagent model routing | ✅ | Primary model + intentional fallback chain |
| Web search + fetch | ✅ | Brave API |
| Skills ecosystem | ✅ | 30+ skills active |

## 🏆 THINGS WORTH BUILDING ON TOP OF BUILT-IN

These are custom systems that genuinely improve on OpenClaw's built-in features:

| Custom System | Built-In Equivalent | Why It's Better |
|--------------|---------------------|-----------------|
| **Model Router** | Basic `model.primary` + `fallbacks` | Tracks usage curves, degradation, task-type routing, weekly burn rates. Built-in does linear failover. |
| **Usage Monitor** | None | Granular weekly burn rate, pace indicators, context %, multi-provider tracking |
| **Meta Monitor** | `openclaw doctor` (one-shot) | Watches N subsystems continuously, auto-recovers stalled components. Doctor is one-shot. |
| **Self-Healing Script** | `openclaw doctor --fix` | Autonomous: saves state → git commit → restart. Doctor requires manual invocation. |
| **Task Persistence (JSON)** | Session memory + compaction | Structured JSON with priorities, status, blockers. Survives compaction perfectly. |
| **Sprint Orchestration** | `sessions_spawn` | Full pipeline: spec → spawn → poll → verify → commit → notify → next sprint |
| **Compaction memoryFlush prompt** | Default "store durable memories" | Custom prompt explicitly saves to both memory AND state files |

## ⚠️ COMMON GAPS — CHECK YOUR SETUP

### 1. Hybrid Search (BM25 + Vector) — Likely NOT Enabled
**Impact: HIGH** — If your memory search only uses vector similarity, you're missing BM25 keyword matching. Much better for exact tokens (commit hashes, script names, error strings, IDs).

**Fix:** Add to your config:
```json5
memorySearch: {
  query: {
    hybrid: {
      enabled: true,
      vectorWeight: 0.7,
      textWeight: 0.3,
      candidateMultiplier: 4
    }
  }
}
```

### 2. Session Transcript Indexing — Often Misconfigured
**Impact: MEDIUM** — Having `experimental.sessionMemory: true` isn't enough. Check that `sources` includes `"sessions"`:
```json5
memorySearch: {
  sources: ["memory", "sessions"]
}
```
Without this, your session history isn't searchable via memory_search.

### 3. IDENTITY.md — Often Left Blank
**Impact: LOW** — OpenClaw derives `mentionPatterns` and `ackReaction` from agent identity. Fill it in:
```markdown
# IDENTITY.md
- **Name:** YourBotName
- **Emoji:** 🤖
- **Vibe:** One-line personality summary
```

### 4. BOOT.md — Often Missing
**Impact: MEDIUM** — If you have the `boot-md` hook enabled but no BOOT.md file, you're wasting a restart. Create one:
```markdown
# BOOT.md - Gateway Restart Startup
1. Check state files exist and are valid JSON
2. Check for completed background work
3. Verify memory files exist
4. Send a message confirming you're back online
5. IMMEDIATELY resume work from your task list
```
The key insight: **restarts should be invisible speed bumps, not stop signs.** Your bot should come back online, notify the user, and resume work in the SAME response.

### 5. Embedding Cache — Worth Enabling
**Impact: LOW** — Docs mention `memorySearch.cache` for faster reindexing. Configure explicitly:
```json5
memorySearch: {
  cache: {
    maxEntries: 50000
  }
}
```

### 6. Heartbeat activeHours — Consider Setting
**Impact: LOW** — Default heartbeat runs 24/7. If you don't need overnight monitoring, restrict to waking hours to save API calls:
```json5
heartbeat: {
  activeHours: { start: "08:00", end: "22:00" }
}
```
Skip this if you run overnight autonomous work.

### 7. Lobster Workflows — Worth Investigating
**Impact: MEDIUM** — Deterministic workflow pipelines with approval gates. Good for deployment pipelines, multi-step automations, or anything that needs human-in-the-loop approval at specific stages.

## 🔄 COMMON REINVENTION TRAPS

Things people build custom that already exist in OpenClaw:

| What People Build | What Already Exists |
|------------------|-------------------|
| Custom memory search | `memorySearch` with vector + BM25 hybrid |
| Manual compaction handling | `compaction.memoryFlush` with custom prompts |
| Session persistence scripts | `session-memory` hook + `experimental.sessionMemory` |
| Complex cron job networks | Single heartbeat + HEARTBEAT.md checklist |
| Manual restart detection | `boot-md` hook + BOOT.md |

**Rule of thumb:** Before building a custom system, check if OpenClaw already has a hook, plugin, or config option for it. Build ON TOP of the built-in features, don't replace them.

## 📋 QUICK SETUP CHECKLIST

Run through these after any fresh OpenClaw install:

- [ ] Enable hybrid search (BM25 + vector)
- [ ] Set memorySearch sources to include sessions
- [ ] Fill in IDENTITY.md with bot name/emoji
- [ ] Create BOOT.md with restart checklist
- [ ] Enable embedding cache
- [ ] Set heartbeat activeHours (or leave 24/7 for autonomous work)
- [ ] Configure compaction memoryFlush with a custom prompt
- [ ] Enable boot-md, session-memory, and command-logger hooks
- [ ] Set up HEARTBEAT.md to batch all periodic checks into one heartbeat

## Summary

**After auditing docs.openclaw.ai against a production system running 30+ skills, 10 monitoring subsystems, and 60+ scripts:**

The built-in features cover 90% of what you need. The remaining 10% is where custom scripts add real value: usage tracking with burn rate calculations, multi-subsystem health monitoring with auto-recovery, structured task persistence that survives compaction, and sprint orchestration that chains work automatically.

**Don't reinvent the wheel.** Use the built-in memory, heartbeat, cron, and compaction systems. Build custom systems for the things OpenClaw doesn't natively provide: usage economics, multi-model routing intelligence, and autonomous work orchestration.
