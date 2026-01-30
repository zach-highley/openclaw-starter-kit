# Hybrid Coding Workflow — Multi-Model Strategy

*How to use Claude + Codex together for maximum coding velocity.*
*Validated against: Addy Osmani (Google), Faros.ai (200+ devs), Northflank, WaveSpeed AI*

## The Problem

Using a single AI model for everything leaves performance on the table:
- Claude is fast and creative but can miss edge cases
- Codex is methodical and thorough but slower
- Neither alone catches everything

## The 8-Step Hybrid Workflow

### Step 1: Claude Opus — Assess Overall Plan
- Understand the goal, analyze codebase state, identify priorities
- Output: High-level assessment with scope and approach

### Step 2: Claude Code — Validate Plan Against Codebase
- Read actual source files, check technical feasibility
- Output: "This plan works" or "These parts need adjustment because..."

### Step 3: Codex — Assess the Plan
- Review from a different perspective, find gaps and edge cases
- Output: Plan critique with recommended changes

### Step 4: Codex — Implement
- Execute the refined plan: write all code, build, test
- Output: Working code, committed and pushed

### Step 5: Claude — Orchestrate Autonomous Execution
- Break into sprint chunks, set up self-checking pipeline
- Build verification after each change, commit after each batch
- Monitor for failures and auto-recover

### Step 6: Code Review
- Automated PR review on every push (GitHub Actions, Codex Code Review, etc.)
- Third pair of eyes catches what both models missed

### Step 7: Update Documentation
- Sprint plan, memory files, project tracker
- Full audit trail of what changed and why

### Step 8: Move to Next Task
- Pick next item from queue, loop back to Step 1
- Zero downtime: always building, always shipping

## Why This Works

From the research:

**Addy Osmani (Google):** "Begin by defining the problem and planning a solution... compile into a comprehensive spec. This upfront investment pays off enormously."

**Northflank:** "Choose Claude Code for deep codebase analysis and local development workflows, or Codex for autonomous task delegation."

**Faros.ai:** "Codex has re-emerged as a serious, agent-first coding tool. Claude remains the most agreed-upon answer for best AI for coding in abstract terms."

**Anthropic:** 90% of Claude Code's own codebase is written by Claude Code itself.

## Model Allocation

| Step | Model | Role |
|------|-------|------|
| 1. Assess | Claude Opus | Fast creative reasoning |
| 2. Validate | Claude Code | Deep codebase awareness |
| 3. Critique | Codex 5.2 | Methodical gap-finding |
| 4. Execute | Codex 5.2 | The coding master |
| 5. Orchestrate | Claude Opus | Sprint management |
| 6. Review | Code Review (GitHub) | Third pair of eyes |
| 7. Document | Claude Opus | Writing, synthesis |
| 8. Next | Claude Opus | Decision-making |

## Quick Tasks

Single file changes, small scripts, quick fixes can skip straight to Codex (Step 4). The full 8-step process is for non-trivial work: new features, major refactors, multi-file changes.

## Key Principles

1. **Spec before code** — write requirements before implementation
2. **Small iterative chunks** — sprint-sized tasks, not monolithic asks
3. **Multiple review passes** — at least 3 perspectives before shipping
4. **Autonomous with checkpoints** — self-running but self-verifying
5. **Context packing** — always feed models the full relevant context

## Sources
- [Addy Osmani — My LLM Coding Workflow Going Into 2026](https://addyosmani.com/blog/ai-coding-workflow/)
- [Faros.ai — Best AI Coding Agents for 2026](https://www.faros.ai/blog/best-ai-coding-agents-2026)
- [Northflank — Claude Code vs OpenAI Codex 2026](https://northflank.com/blog/claude-code-vs-openai-codex)
