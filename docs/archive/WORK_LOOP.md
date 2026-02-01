# 🔄 The Autonomous Work Loop

The work loop is the core engine that lets your AI work through a queue of tasks autonomously — spawning sub-agents, tracking progress, recovering from failures, and reporting results. It survives crashes, session resets, and context clears because everything is stored in a JSON state file.

## How It Works (Simple Version)

```
You define tasks → AI picks the next one → spawns the right model →
monitors progress → logs result → picks next task → repeat
```

That's it. You go shower, sleep, or work on other things. Your AI keeps building.

## The State File: `state/current_work.json`

This is the brain. Everything the work loop needs to know lives here:

```json
{
  "active": true,
  "task": "my-project-sprints",
  "description": "Build features for my app",
  "queue": ["S3", "S4", "S5"],
  "completed": ["S1", "S2"],
  "inProgress": "S3",
  "specFiles": {
    "S1": "/path/to/SPRINT_S1_SPEC.md",
    "S2": "/path/to/SPRINT_S2_SPEC.md",
    "S3": "/path/to/SPRINT_S3_SPEC.md"
  },
  "project": "/path/to/your/project",
  "notifyUser": true,
  "retryOnRateLimit": true,
  "rateLimitRetryMinutes": 15,
  "maxRetries": 3,
  "autoNewAfterSprints": 3,
  "log": []
}
```

### Key Fields

| Field | What It Does |
|-------|-------------|
| `queue` | Tasks waiting to be done (first = next) |
| `completed` | Tasks that are done |
| `inProgress` | The task currently being worked on |
| `specFiles` | Maps each task to its spec file (instructions for the AI) |
| `autoNewAfterSprints` | Reset session after N completions (keeps context fresh) |
| `retryOnRateLimit` | If a model hits its limit, wait and retry |
| `log` | Append-only log of everything that happened |

### Smart Work Detection

No manual toggle needed:
- **Queue has items** = work mode ON
- **Queue is empty** = work mode OFF

## The Heartbeat Loop

Every heartbeat (typically every 30-60 min), your AI checks the work state:

1. Read `state/current_work.json`
2. If queue has items → pick next task
3. Read the sprint spec file
4. Spawn the right model (Codex for coding, Gemini for docs, etc.)
5. Send you a notification: what started, which model, ETA
6. Monitor the sub-agent for completion or stalling
7. On success: update state, notify you, start next task
8. On failure: retry or skip, notify you
9. After N completions: save state, reset session for fresh context

## Sprint Notifications

Every sprint start and completion sends a structured message:

### Sprint Start:
```
🚀 Sprint S3 started — Search bar implementation
🤖 Model: Codex (gpt-5.2)
⏱️ ETA: ~12 minutes (based on avg from metrics)
📋 Next up: S4 — Deep dive linking
📊 Progress: 2/8 sprints done
```

### Sprint Complete:
```
✅ Sprint S3 COMPLETE — Search bar. Commit abc1234
⏱️ Duration: 8 min (est was 12 min)
[then the next sprint's start notification]
```

## Stall Detection (3-Strikes Rule)

Sometimes agents get stuck (infinite loops, hanging builds, wrong file paths). The work loop handles this:

- **Strike 1-2:** Kill the stalled agent, re-spawn with better instructions
- **Strike 3:** Deep dive analysis:
  1. Read the sprint spec + all related source files
  2. Identify WHY it keeps stalling
  3. Fix the root cause and re-spawn, do it yourself, or skip with explanation
  4. Notify: "⚠️ Sprint S3 stalled 3 times. Root cause: [X]. Action: [Y]"

### Common Stall Causes
- Agent tries to run a build/compile step that hangs → tell it to skip builds
- Wrong file path → verify paths before spawning
- Agent enters infinite polling loop → kill after 5 min timeout

## Rate Limit Handling

When a model hits its usage cap:
1. Log it with a `rateLimitedUntil` timestamp
2. Set a cron/reminder to resume when the limit resets
3. Optionally fall back to a different model (e.g., Opus does the work while Codex is down)
4. Notify you: "⚡ Codex rate limited. Resets in ~2 hours. Falling back to Opus."

## Metrics & Learning

Every sprint logs to `state/work_metrics.json`:
- Which agent was used
- How long it took
- Success or failure
- Error type if failed

Over time, you learn:
- Which agent is fastest for which task type
- Average completion times (for better ETAs)
- Failure patterns to avoid

Use `python3 scripts/log_sprint_metric.py --summary` to see your stats.

## Session Reset Protocol

When context gets full (~85%), the work loop:
1. Saves highlights to daily memory file
2. Saves work state (already persistent in the JSON)
3. Resets the session
4. New session boots, reads state, resumes exactly where it left off
5. Every step is narrated to you — no silent resets

## Getting Started

1. Write sprint spec files (see `docs/SPRINT_SYSTEM.md`)
2. Create `state/current_work.json` (see `state/current_work.example.json`)
3. Add the work loop check to your `HEARTBEAT.md`
4. Let it run!

The work loop doesn't need you. It needs a queue and a heartbeat.
