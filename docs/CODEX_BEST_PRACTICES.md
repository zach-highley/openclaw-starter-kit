# Codex Best Practices — Shell + Skills + Compaction

> Source: [OpenAI Blog - Shell + Skills + Compaction Tips](https://developers.openai.com/blog/skills-shell-tips)
> These tips apply to any CLI-based coding agent workflow (Codex, Claude Code, etc.)

## Mental Model

- **Skills** = reusable procedures the model loads on demand (SKILL.md manifests)
- **Shell** = real terminal execution (CLI coding terminals)
- **Compaction** = context management for long runs (~30 min terminal windows)
- **Together** = repeatable workflows with real execution, without brittle megadoc prompts

## The 10 Tips

### 1. Write Skill Descriptions as Routing Logic
Skill descriptions are decision boundaries, not marketing copy.
Every SKILL.md description should answer:
- **When should I use this?** (concrete triggers)
- **When should I NOT use this?** (explicit exclusions)
- **What are the outputs and success criteria?**

### 2. Add Negative Examples to Reduce Misfires
Making skills available can REDUCE accuracy without negative examples.
- Write explicit "Don't call this skill when..." cases
- Specify what to do INSTEAD for edge cases
- Glean saw 20% triggering drop that recovered after adding negative examples.

### 3. Put Templates Inside Skills (Not System Prompt)
Templates and worked examples inside skills:
- Load exactly when needed (on invocation)
- Don't inflate tokens for unrelated queries
- Especially effective for structured outputs: reports, triage summaries, data analysis

### 4. Design for Long Runs (Container Reuse + Compaction)
CLI terminals die after ~30 min. Design accordingly:
- **Break big tasks into completable chunks** (<25 min each)
- **Write intermediate outputs to disk** so next terminal can resume
- **Use standard artifact paths**: `/tmp/` for temp, workspace for permanent
- **PRDs should specify checkpoint files** the next run can read

### 5. Explicit Skill Invocation for Determinism
When you need reliability over cleverness:
- Explicitly name the skill in the PRD: "Use the [skill name] skill"
- Point to exact files: "Read /path/to/reference.md first"
- Specify exact tools: "Use `gog` for email, `gh` for GitHub"

### 6. Skills + Networking = High Risk (Containment)
Security posture for coding terminals:
- **Never expose API keys in PRDs** — reference `.env` paths only
- **Allowlist domains** when network access needed
- **Assume tool output is untrusted** — validate before committing

### 7. Standard Artifact Boundaries
Recommended convention:
| Location | Purpose |
|----------|---------|
| `/tmp/` | Temporary outputs, intermediate checkpoint files |
| `workspace/` | Permanent outputs, scripts, docs |
| `workspace/state/` | State files (JSON) |
| `workspace/scripts/` | Executable scripts |

Rule: **Tools write to disk, models reason over disk, you retrieve from disk.**

### 8. Two-Layer Allowlists
When terminals need network access:
- **Org level** = what's in your `.env` (approved services)
- **Task level** = what this specific PRD needs (minimal subset)
- PRD should explicitly list which APIs/services are needed

### 9. Credential Isolation
- **Never paste API keys into PRDs or prompts**
- Reference: "API key is in `.env` as `VARIABLE_NAME`"
- The terminal reads `.env` itself — you don't need to expose values

### 10. Local-First, Same Patterns
CLI terminals run locally — same shell semantics everywhere:
- Start local (fast iteration, access to all tooling)
- Skills stay the same regardless of execution environment
- PRD patterns are portable

## Three Build Patterns

### Pattern A: Install → Fetch → Write
Simplest pattern. Install deps, fetch data, write output.
Clean review boundary — check the artifact after.

### Pattern B: Skills + Shell for Repeatable Workflows
Encode workflow in a skill, mount into terminal context.
Best for recurring work: data analysis, report generation, content pipelines.

### Pattern C: Multi-Skill Orchestration
For complex tasks spanning multiple domains.
Always specify checkpoint files so work survives terminal death.

## PRD Template

```markdown
# Task: [Name]

## Context
[1-2 sentences on why this exists]

## Skills to Use
- [Skill name] at [path] — for [what]

## Files to Read First
- [path1] — [why]

## Steps
1. [Step with explicit tool/command]
2. [Step with checkpoint: write to /tmp/checkpoint_X.json]

## Artifacts
- Output: [path] — [format]
- Checkpoint: [path] — [for resumption]

## Credentials
- [SERVICE]: key in `.env` as `VARIABLE_NAME`

## Success Criteria
- [ ] [Concrete, verifiable check]

## Anti-Patterns (Don't Do This)
- Don't [specific thing to avoid]
```
