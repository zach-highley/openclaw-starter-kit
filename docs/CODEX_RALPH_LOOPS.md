# CODEX_RALPH_LOOPS.md — PRD + Checklist + Fresh-Context Implementation

## The 95/5 Rule: Terminals Over Subagents

**95% of work should run as terminals/CLIs (Codex CLI, Claude Code), not CLI terminals.**

Why:
- Fresh context each iteration (amnesia is a feature)
- PRD/checklist is source of truth, not agent memory
- Less hallucination compounding
- Visible via `ps aux | grep -E "(codex|claude)"`
- Easy to kill/restart

Use CLI terminals only for pure research (5%).

---

This pattern is copied from the FelixCraftAI / Nat Eliason workflow.

## The problem
Long-running agent sessions can accumulate:
- shared context mistakes
- compounding hallucinations
- overconfident refactors

## The solution: “amnesia is a feature”
Instead of one long agent run, use a loop with **fresh context each iteration**.

### Roles
- **Planner (Opus):** writes the PRD + checklist + plan on disk.
- **Implementer (Codex CLI):** runs in `--full-auto`, re-discovers state from files and git history each iteration.
- **Validator:** checklist + backpressure commands.

## Files
- `PRD.md` (or `specs/*.md`)
- `IMPLEMENTATION_PLAN.md` (must contain a sentinel like `STATUS: COMPLETE`)
- `AGENTS.md` (backpressure commands)
- `PROMPT.md` (points to the above; loaded every iteration)

## Minimal loop
```bash
while :; do codex exec --full-auto "$(cat PROMPT.md)" ; done
```

## Controlled loop (recommended)
```bash
#!/usr/bin/env bash
set -euo pipefail
MAX_ITERS=20
PLAN_SENTINEL='STATUS: COMPLETE'
mkdir -p .ralph
LOG_FILE='.ralph/ralph.log'

touch PROMPT.md AGENTS.md IMPLEMENTATION_PLAN.md

for i in $(seq 1 "$MAX_ITERS"); do
  echo -e "\n=== Ralph iteration $i/$MAX_ITERS ===" | tee -a "$LOG_FILE"
  codex exec --full-auto "$(cat PROMPT.md)" | tee -a "$LOG_FILE"

  # Backpressure goes here (tests/lint/build)
  # bash -lc "npm test" | tee -a "$LOG_FILE"

  if grep -Fq "$PLAN_SENTINEL" IMPLEMENTATION_PLAN.md; then
    echo "✅ Complete." | tee -a "$LOG_FILE"
    exit 0
  fi

done

echo "❌ Max iterations reached." | tee -a "$LOG_FILE"
exit 1
```

## Guardrails
- The checklist is the source of truth, not agent memory.
- If it stalls, lies, or drifts: restart (fresh eyes).
- Use separate worktrees for parallel loops when needed.
