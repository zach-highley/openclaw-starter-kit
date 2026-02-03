# SUBAGENT_TIMEOUT_GUIDE

This starter kit uses **background sub-agents** for longer-running work (coding, research, audits). By default, many setups ship with conservative timeouts, which can cause sub-agents to be killed mid-task.

This guide explains:
- what the timeout is,
- why it matters,
- how to pick sane values,
- and how to avoid “silent failures”.

## What is a sub-agent timeout?
A sub-agent timeout is a hard cap on how long an isolated/background run is allowed to execute before the Gateway stops it.

Timeouts exist to prevent:
- runaway costs (API usage),
- hung tools/processes,
- infinite loops.

But if the timeout is too short, you get the worst outcome: **partial work with no useful deliverable**.

## Symptoms of a too-short timeout
- The sub-agent starts, writes a plan, then dies before doing any work.
- You see messages like “timed out”, “run cancelled”, or no message at all.
- Long tasks (repo-wide refactors, multi-file changes, large diffs, CI debugging) never finish.

## Recommended timeout ranges
Use these as starting points:

### Quick tasks (single-shot)
- **30–120 seconds**
- Examples: small summaries, tiny edits, single command runs.

### Normal coding tasks
- **10–30 minutes**
- Examples: implement a small feature, fix a bug, write a script, add tests.

### Heavy tasks (overnight)
- **45–120 minutes** per run (and split into multiple runs if needed)
- Examples: migrations, large refactors, generating lots of content, multi-repo audits.

If you are running “night shift” style automation, bias toward **longer timeouts** with **hard safety rails** (see below).

## Safety rails (more important than the exact timeout)
Instead of keeping timeouts tiny, keep timeouts reasonable and add guardrails:

1) **Allowlist what can be touched**
   - Example: only allow edits under `docs/` or `scripts/` unless explicitly approved.

2) **Kill switch**
   - One env var or file flag that stops spawning sub-agents immediately.

3) **Budget limits**
   - Cap number of runs per hour/night.
   - Cap max concurrent runs.

4) **Audit logs**
   - Record: start time, end time, objective, files changed, outcome.

5) **Chunking**
   - Prefer 3 x 20-minute runs with checkpoints over 1 giant run with no check-ins.

## Where to configure timeouts
OpenClaw timeouts can be set in a few places depending on how you spawn sub-agents:

- **Cron jobs** (`gateway cron`): set the job’s `timeoutSeconds` (or equivalent) for agent runs.
- **Session spawn APIs/CLI**: set `runTimeoutSeconds` when spawning a sub-agent.

If you are using this starter kit’s templates, search for:
- `timeoutSeconds`
- `runTimeoutSeconds`
- `timeout`

## Practical default for this starter kit
If you want a safe “works for most people” default:
- **runTimeoutSeconds: 1800 (30 minutes)** for coding sub-agents
- **runTimeoutSeconds: 600 (10 minutes)** for small ops tasks

Then rely on safety rails (allowlists + kill switch + audit logs) rather than tiny timeouts.

## If you still hit timeouts
- Split the task into slices with explicit acceptance criteria.
- Move expensive steps (tests, builds) to separate runs.
- Add progress checkpoints so partial work is still useful.

---

If you found this guide missing, you’re right, it was referenced but not committed. This file exists now.
