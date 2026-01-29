# Self-Review Loop — Metacognition for AI Agents

Your AI makes mistakes. It defaults to safe answers. It moves too fast. It repeats errors. This system makes it **notice and fix its own patterns** over time.

## How It Works

```
heartbeat → question itself → log MISS/FIX or HIT/KEEP → restart → read log → adjust
```

1. **Every few heartbeats**, the agent asks itself three questions:
   - What sounded right but went nowhere?
   - Where did I default to consensus or lazy thinking?
   - What assumption did I not pressure test?

2. **Logs entries** to `memory/self-review.md` with tags

3. **On boot**, reads recent MISS entries. When a new task overlaps with a past MISS tag, the agent forces a counter-check before responding.

4. **Over time**, patterns emerge. Same TAG appearing 3+ times = systemic issue → update rules to fix structurally.

## The Format

```markdown
[YYYY-MM-DD] TAG: confidence
MISS: defaulted to consensus — said "looks good" without actually verifying
FIX: challenge the obvious assumption first. Verify before confirming.

[YYYY-MM-DD] TAG: speed  
MISS: added noise not signal — sent 3 status updates when 1 would do
FIX: remove anything that doesn't move the task forward

[YYYY-MM-DD] TAG: depth
HIT: caught a subtle bug by reading the full file instead of skimming
KEEP: always read the actual code, not just the description of the code
```

## Tags

| Tag | What It Catches |
|-----|----------------|
| `confidence` | Said something with certainty that was wrong. Didn't hedge when should have. |
| `uncertainty` | Was uncertain but didn't investigate. Left ambiguity unresolved. |
| `speed` | Moved too fast. Acted before thinking. Generated noise instead of signal. |
| `depth` | Skimmed when should have read deeply. Missed context. Surface-level work. |

## Setup

### 1. Create the log file

Create `memory/self-review.md`:
```markdown
# Self-Review Log

*Metacognition loop: where I went wrong, where I got it right, and what to do differently.*

Format:
[YYYY-MM-DD] TAG: [confidence|uncertainty|speed|depth]
MISS|HIT: what happened
FIX|KEEP: what to do about it

---
```

### 2. Add to HEARTBEAT.md

```markdown
## 🪞 Self-Review (every 4th heartbeat)
Read `memory/self-review.md` and reflect on recent work:

Ask yourself:
1. What sounded right but went nowhere?
2. Where did I default to consensus or lazy thinking?
3. What assumption did I not pressure test?
4. What worked well that I should keep doing?

Log entries as MISS/FIX or HIT/KEEP with tags.
When a current task overlaps with a past MISS: PAUSE and counter-check.
If same TAG appears 3+ times: update rules to fix structurally.
Prune entries older than 30 days.
```

### 3. Add to AGENTS.md (boot sequence)

Add to your "Every Session" checklist:
```markdown
6. Read recent MISS entries from `memory/self-review.md` — when a current task 
   overlaps with a past MISS tag, force a counter-check before responding.
```

## Timeline

- **Week 1:** Entries will be basic. Agent is learning what to notice.
- **Week 2-3:** Patterns start emerging. Same tags repeat.
- **Week 4+:** Sharp improvement. The agent now remembers where it lies to itself.

## Interval

More tasks = shorter interval. Adjust to your usage:
- Heavy use (20+ tasks/day): every heartbeat
- Normal use: every 4th heartbeat (~4 hours)
- Light use: daily

## Why This Works

Most AI "learning" is performative — the agent writes "I learned X" but doesn't actually change behavior. This system works because:

1. **The counter-check is mandatory.** When a task overlaps a MISS, the agent must pause and challenge itself. No skipping.
2. **Structural fixes escalate.** 3+ of the same MISS = the rules themselves change, not just a log entry.
3. **HITs reinforce good patterns.** Not just punishment — reward what works.
4. **Pruning prevents bloat.** After 30 days, lessons should be absorbed into actual rules. If they're not, that's a MISS too.
