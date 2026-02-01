# 🏃 The Sprint System

Sprints are how you break big projects into small, AI-executable tasks. Each sprint has a spec file that tells the AI exactly what to build, which files to touch, and how to commit.

## Why Sprints?

AI agents work best with focused, well-defined tasks. A sprint that says "build search bar in 2 files" beats "make the app better." Small scope = fewer errors, faster completion, easier recovery if something goes wrong.

## Writing Sprint Specs

A sprint spec is a markdown file that gives the AI everything it needs:

```markdown
# Sprint S1: Search Bar Implementation
**Priority:** P1 — HIGH
**Est:** 30 min
**Files:** SearchView.swift, ContentManager.swift

## Problem
Users can't search for content. They have to scroll through everything.

## What to Build
1. Create SearchView.swift with a search bar and filtered results list
2. In ContentManager.swift, add a search() method that filters by title/tags
3. Wire up the search view to the main navigation

## Important
- Follow existing code patterns in the project
- Don't modify unrelated files
- Commit: 'feat(search): add content search bar with filtering'
```

### Spec Template

```markdown
# Sprint [ID]: [Short Title]
**Priority:** P1/P2/P3
**Est:** [time estimate]
**Files:** [files to modify]

## Problem
[What's broken or missing — 1-2 sentences]

## What to Build
[Numbered list of specific changes]

## Important
[Constraints, patterns to follow, things NOT to do]
[Commit message format]
```

### Tips for Good Specs
- **Be specific about files.** Include full paths if your project is deep.
- **Number the steps.** AI agents follow ordered lists well.
- **Include the commit message.** Consistent git history matters.
- **Say what NOT to do.** "Don't run xcodebuild" or "Don't modify the database schema" prevents common AI mistakes.
- **Keep scope small.** 1-3 files, 1 feature. If it feels big, split it into 2 sprints.

## Queuing Sprints

Add sprints to `state/current_work.json`:

```json
{
  "active": true,
  "queue": ["S1", "S2", "S3"],
  "completed": [],
  "inProgress": null,
  "specFiles": {
    "S1": "/path/to/project/SPRINT_S1_SPEC.md",
    "S2": "/path/to/project/SPRINT_S2_SPEC.md",
    "S3": "/path/to/project/SPRINT_S3_SPEC.md"
  },
  "project": "/path/to/project"
}
```

The work loop (see `docs/WORK_LOOP.md`) picks up the queue automatically on the next heartbeat.

## Model Selection

Different sprints need different models:

| Sprint Type | Best Model | Why |
|-------------|-----------|-----|
| **Coding** (new features, bug fixes) | Codex / Claude Code | Built for code |
| **Refactoring** (cleanup, patterns) | Codex / Claude Code | Needs code context |
| **Documentation** | Gemini / Opus | Writing quality |
| **Performance** (caching, optimization) | Codex | Understands runtime |
| **UI/Design** | Codex | SwiftUI/React patterns |
| **Architecture** (planning, not coding) | Opus | Deep reasoning |

Your AI should auto-select based on the sprint spec, but you can override in the spec:
```markdown
**Model:** codex
```

## Monitoring Sprints

While a sprint runs, your AI should:

1. **Check sub-agent progress** every few minutes
2. **Detect stalls** (no output for 5+ min = probably stuck)
3. **Rescue if needed** (kill stalled agent, commit any partial work, re-spawn or do it manually)
4. **Log metrics** after every sprint (see `scripts/log_sprint_metric.py`)

## Sprint Notifications (The Format)

Every sprint start and completion should notify you with full context:

**Start:**
```
🚀 Sprint S3 started — [description]
🤖 Model: [which model]
⏱️ ETA: ~[N] minutes (from historical avg)
📋 Next up: [next sprint] — [description]
📊 Progress: [done]/[total] sprints done
```

**Complete:**
```
✅ Sprint S3 COMPLETE — [what was done, commit hash]
⏱️ Duration: [actual] (est was [N] min)
```

This way you always know: what's running, how long it'll take, what's next, and overall progress. Even if you're away from your computer.

## Example: Planning a Sprint Queue

Say you're building a learning app and your AI audited the codebase. It found 8 issues. Here's how to plan:

1. **AI writes sprint specs** (one per issue, saved as markdown files)
2. **AI creates the work state** with all sprints queued
3. **You approve** (or modify the queue order/specs)
4. **AI executes** autonomously through heartbeats
5. **You get notifications** for every start/completion
6. **AI handles failures** (stall detection, rate limit fallback)
7. **Queue empties** → AI sends completion report

Total human involvement: approve the plan, then check your phone occasionally.

## Common Mistakes

- **Too-big sprints:** If a sprint touches 10+ files, split it
- **Vague specs:** "Improve performance" → which files? which function? what metric?
- **No commit message:** AI will make up something random
- **No file paths:** AI wastes time searching; give it exact paths
- **Including build steps:** `xcodebuild` and `npm run build` often hang in CI/agent environments. Tell the AI to skip build verification unless you know it works.
