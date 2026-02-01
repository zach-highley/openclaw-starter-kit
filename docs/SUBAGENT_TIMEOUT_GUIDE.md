# Subagent Timeouts — Why 30 Minutes Changes Everything

When you delegate coding or refactors to a “coder model” (for example: Codex or Claude Code), the fastest way to sabotage it is a tiny timeout.

## The problem with 3-minute defaults

A 3-minute ceiling sounds safe… until you ask for any of the following:

- a non-trivial refactor
- a multi-file change with tests
- a dependency migration
- a security sweep + fixes

In those scenarios, the model is usually doing real work:
- scanning the codebase
- building a plan
- searching for edge cases
- running tests / formatting

If you kill it at 180 seconds, you get:
- partial edits
- inconsistent changes
- “it almost worked” loops
- repeated re-prompts (which costs more than just waiting)

## The “trust the models” rule

For serious code work:

- give the coder model **~30 minutes**
- check in periodically (poll logs), but **don’t micromanage**
- after completion: verify with `git diff`, tests, and a short security scan

## Practical patterns

### 1) One sprint = one atomic outcome
Don’t ask for 12 things at once.
Instead:
- write a clear sprint spec
- ask for one coherent change
- commit
- repeat

### 2) Use a dual-auditor pattern
Different models catch different failures.
A robust flow:

- **Auditor model:** reviews the repo, writes the plan, finds risks
- **Coder model:** executes the plan (with enough time)

### 3) Always verify after subagent completion
A reliable post-run checklist:

- `git status` is clean
- `git diff` matches the spec
- scripts parse (`python3 -m py_compile ...`)
- docs build/render (at least visually)

## Where this shows up in OpenClaw

OpenClaw supports background work and long-running tasks (see docs):
- https://docs.openclaw.ai/start/getting-started

If you’re building an autonomous system, *timeouts are architecture*.
A system that kills its coder at 3 minutes can’t self-heal.
A system that gives it 30 minutes can.
