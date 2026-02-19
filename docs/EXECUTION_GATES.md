# Execution Gates (Mandatory)

These four rules are mandatory on every task.

1) **Short Prompts**
- Default to short prompts for small tasks.
- Use PRDs only for larger, multi-step work.

2) **Blast Radius First**
- Estimate file count + expected duration before edits.
- If scope is large, split before execution.

3) **CLI-First**
- Prefer CLI/tooling workflows first.
- Use browser/UI only when CLI is unavailable or unsafe.

4) **Post-Task Refactor**
- Before declaring done, ask: "What can we simplify/refactor now?"
- Execute at least one cleanup pass.

## Completion Rule
If any gate is skipped, the task is not complete.
