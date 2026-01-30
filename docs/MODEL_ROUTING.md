# MODEL_ROUTING.md — Intelligent Model Orchestration

## TL;DR

**Multiple models, one brain.** Your orchestrator model picks the best specialist for each task. Background tasks never touch the main model. Local fallback means you can't hit zero.

## The Stack

| Tier | Role | Model | When It's Used |
|------|------|-------|----------------|
| T0 | 🧠 Orchestrator | Claude Opus | Strategy, reasoning, decisions, main chat |
| T1 | 💻 Code Specialist | OpenAI Codex | Code generation, refactoring, scripts |
| T2 | 📡 Background/Bulk | Google Gemini | Heartbeats, summarization, bulk processing |
| T3 | ⚡ Fallback | Claude Sonnet | Cheaper reasoning, coding fallback |
| T4 | 🏠 Local Emergency | Ollama | Offline, all cloud exhausted |

## Smart Routing

The model router (`scripts/model_router.py`) handles all routing decisions:

```bash
# Show all model statuses
python3 scripts/model_router.py --show-all

# Get recommendation for a task
python3 scripts/model_router.py --task-type coding

# Mark a model as exhausted (persists across sessions)
python3 scripts/model_router.py --set-codex-status exhausted --codex-resets "2026-02-03"

# Check before spawning any subagent
python3 scripts/model_routing_check.py --task coding --json
```

## Codex CLI vs Codex Code Review

**These are different products with separate quotas:**

| Product | What it does | Quota |
|---------|-------------|-------|
| Codex CLI/API | Writes code, executes tasks | ChatGPT Plus weekly messages |
| Codex Code Review | Reviews PRs on GitHub | Separate quota entirely |

When Codex CLI is exhausted, the router automatically falls back to Claude Code (Sonnet) for coding tasks. The status persists in `state/codex_status.json` and auto-resets when the expiry date passes.

## Degradation Curve

As usage increases, cheaper models take priority:

| Usage % | Available Models |
|---------|-----------------|
| 0-70% | All models |
| 70-80% | All (watching) |
| 80-90% | Sonnet, Codex, Gemini, Local |
| 90-95% | Sonnet, Codex, Gemini, Local |
| 95-100% | Codex, Gemini, Local |
| 100% | Gemini, Local only |

## Session Boot

Every new session should run:
```bash
python3 scripts/model_router.py --show-all
python3 scripts/check_usage.py
```
This prevents using exhausted models or wasting tokens on the wrong specialist.
