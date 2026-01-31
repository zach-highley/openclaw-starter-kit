# Subagent Best Practices

*Battle-tested patterns for efficient AI agent delegation.*

## The Problem

Every subagent spawn costs ~20,000 tokens of overhead before actual work begins. Spawning 5 subagents for 5 small tasks = 100K tokens of wasted overhead. One subagent doing all 5 = 20K overhead.

If you're spawning subagents like confetti, you're burning context on orchestration instead of work.

## Core Principles

### 1. Fewer, Bigger Tasks

Bundle related work into a single comprehensive task. One subagent should handle a full feature or a full category of fixes, not individual items.

**Bad:** "Fix the button color" → "Fix the padding" → "Fix the hover state"
**Good:** "Complete UI polish sprint: fix button color, padding, hover state, and border. Here's the spec..."

### 2. Write a Spec First (No Spec = No Spawn)

Every subagent task MUST include:
- **Objective:** What does "done" look like?
- **Context:** What files exist, what's the architecture, what was tried before
- **Requirements:** Numbered list of every change needed
- **Constraints:** What NOT to touch, review gates, build verification
- **Verification:** How to test (build commands, expected output)
- **Completion:** What to run when done (git commit, push, completion script)

The agent should be able to execute autonomously from the spec alone.

### 3. Define Your Model Hierarchy

Decide which models handle which tasks and stick to it:
- **Best model** → ALL coding (bug fixes, features, scripts, refactors)
- **Second best** → Fallback for coding only when primary unavailable
- **Conversation model** → Planning, research, content, organization
- **Everything else** → Don't use for real work

If your top coding models are both unavailable: build directly in the main session. Don't fall back to weaker models that produce nothing and waste time.

### 4. One Feature Per Sprint, But Make It Complete

Research from Anthropic's engineering team found that agents fail when:
- Tasks are too broad (tries to one-shot everything, runs out of context mid-work)
- Tasks are too granular (overhead costs exceed work value)

The sweet spot:
- One feature or logical unit per subagent
- Include ALL related changes (code + tests + docs + config)
- Require incremental git commits with descriptive messages
- Require a progress file for multi-step work

### 5. Spec File Pattern

For any coding subagent, write a `SPRINT_SPEC.md` in the target repo:

```markdown
# Sprint: [Name]

## Objective
[1-2 sentences of what "done" looks like]

## Files to Modify
- `path/to/file1.tsx` — [what changes]
- `path/to/file2.ts` — [what changes]

## Requirements
1. [Specific, testable requirement]
2. [Specific, testable requirement]

## Constraints
- DO NOT modify [files/systems]
- Build must pass: `[build command]`
- No hardcoded secrets

## Verification
- [ ] Build passes
- [ ] Feature works as described
- [ ] Git committed and pushed
```

### 6. When to Subagent vs Build Directly

**Spawn a subagent when:**
- Task is well-defined coding work with a clear spec
- Main session context is precious (save it for orchestration)
- Task can run independently without back-and-forth

**Build directly in main session when:**
- Task needs real-time decision-making or research
- Subagent models are in cooldown or unavailable
- Task is small enough (< 5 min of work)

### 7. Avoid Spawn Storms

Rate limiters (both provider-side and orchestrator-side) trigger cooldowns on rapid spawns even when capacity remains. Space out spawns by at least 5 minutes.

### 8. Salvage Protocol

When a subagent dies mid-work:
1. Check `git diff` in target repo for uncommitted changes
2. If changes exist: verify build passes, commit, push
3. Assess remaining work
4. Re-fire with a NEW spec covering only remaining items
5. Never retry the exact same scope that failed

## The 3-Strike Research Rule

If you notice **3+ errors, bugs, or mistakes on the same topic**, STOP coding and research:
1. Search official developer docs for best practices
2. Search community forums (Reddit, Stack Overflow, GitHub Issues)
3. Search social media (X/Twitter) for recent developer discussions
4. Synthesize findings into permanent memory
5. THEN continue fixing with proper understanding

This prevents fixing symptoms without understanding root causes.

## Anti-Patterns

- ❌ Spawning a subagent for each individual fix
- ❌ Spawning without a spec
- ❌ Falling back to weak models for coding work
- ❌ Spawning 3+ subagents within 5 minutes
- ❌ Retry loops on the same failed task
- ❌ Subagents that need to communicate with each other
- ❌ Using subagents for research/planning (do that in main session)

## Sources

- [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Anthropic: Claude Code best practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Addy Osmani: How to write a good spec for AI agents](https://addyosmani.com/blog/good-spec/)
- [Claude Code: When to use task tool vs subagents](https://amitkoth.com/claude-code-task-tool-vs-subagents/)
- [sshh.io: How I Use Every Claude Code Feature](https://blog.sshh.io/p/how-i-use-every-claude-code-feature)
