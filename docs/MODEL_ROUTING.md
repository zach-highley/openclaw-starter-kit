# MODEL_ROUTING.md — Intelligent Model Routing (No Lockouts)

## TL;DR

**One brain, multiple specialists.** Keep Claude Opus as your primary conversational model, route coding to Codex, and always keep cross-provider fallbacks so you never get trapped in a single provider cooldown.

## Recommended Stack

| Tier | Role | Model | When It's Used |
|------|------|-------|----------------|
| T0 | 🧠 Primary chat | Claude Opus (`anthropic/claude-opus-4-5`) | Strategy, reasoning, day-to-day conversation |
| T1 | 💻 Code specialist | Codex (`openai-codex/gpt-5.2`) | Implementation, refactors, scripts |
| T2 | 📡 Bulk/background | Gemini (`google-gemini-cli/gemini-3-pro-preview`) | Summaries, bulk processing, routine heartbeats |
| T3 | ⚡ Cloud fallback | Kimi (`nvidia-nim/moonshotai/kimi-k2.5`) | When Anthropic/OpenAI are rate-limited |
| T4 | 🏠 Local emergency | Ollama (`ollama/qwen2.5:14b`) | Offline or all cloud exhausted |

**Explicit design choice:** this repo does **not** rely on Claude Sonnet. If you want Sonnet, add it yourself. The starter kit default is: *Opus always, then cross-provider fallbacks*.

## Router Script

The model router (`scripts/model_router.py`) is a lightweight helper for humans and bots:

```bash
# Show all model statuses
python3 scripts/model_router.py --show-all

# Get recommendation for a task
python3 scripts/model_router.py --task-type coding
```

## Degradation Curve

As usage or rate limits kick in, prefer models that keep the system alive:

| Claude usage % | Allowed models |
|---------------|----------------|
| 0-80% | Opus, Codex, Gemini, Kimi, Local |
| 80-95% | Codex, Gemini, Kimi, Local |
| 95-100% | Gemini, Kimi, Local |
| 100% | Local only (or whatever still authenticates) |

## Session Boot

Every new session should run:

```bash
python3 scripts/model_router.py --show-all
python3 scripts/check_usage.py --json
```

This prevents accidentally using a provider that is already in cooldown.
