# Task: [NAME]

## Context
[1-2 sentences: why this exists, what problem it solves]

## Skills to Use
- [Skill name] at [path] — for [what]
- (or "None — standalone task")

## Files to Read First
- [path1] — [why this file matters]
- [path2] — [context it provides]

## Steps
1. [Step with explicit tool/command to use]
2. [Step with expected output format]
3. [Step with checkpoint: write progress to /tmp/checkpoint_TASKNAME.json]
4. [Final step with artifact output]

## Artifacts
- Primary output: [path] — [format description]
- Checkpoint: /tmp/checkpoint_TASKNAME.json — [for resumption if terminal dies]

## Credentials (by reference only)
- [SERVICE]: key in `~/.openclaw/.env` as `VARIABLE_NAME`
- (NEVER paste actual key values here)

## Network Access (if needed)
- Allowed: [domain1.com], [api.domain2.com]
- Not needed: [explicit exclusion if relevant]

## Success Criteria
- [ ] [Concrete, verifiable check #1]
- [ ] [Concrete, verifiable check #2]
- [ ] [Test command that proves it works]

## Anti-Patterns (Don't Do This)
- Don't [specific mistake to avoid]
- Don't [another thing that would waste time]
- Don't [common misfire for this type of task]

## Notes
- Terminal lifespan: ~30 min. Task MUST complete within this window.
- If task is too big: break into subtasks with checkpoints at /tmp/checkpoint_TASKNAME_stepN.json
