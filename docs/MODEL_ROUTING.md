# MODEL_ROUTING.md — Intelligent Model Routing (No Lockouts)

## TL;DR

**One brain, multiple specialists.** Route by task type: Codex for backend/architecture, Claude Opus for PM/planning/content, Claude Code for frontend/UI. Always keep cross-provider fallbacks so you never get trapped in a single provider cooldown.

## The Rule (Feb 2026 Industry Consensus)

From @Austen (211 likes, 55 replies):
> "So… Codex for architecture backend, Claude for PM and front end?"

This matches @FelixCraftAI's working pattern with @nateliason.

| Task Type | Model | Why |
|-----------|-------|-----|
| **Architecture, backend, APIs, databases, infrastructure** | Codex MAX | Best for system design, code generation |
| **PM work, planning, research, content, strategy** | Claude Opus | Best for reasoning, coordination, writing |
| **Frontend, UI/UX, visual design, React/Next.js, CSS** | Claude Code | Best for design judgment, visual iteration |
| **Pure research with no code** | Claude Opus (or CLI terminal) | Memory context helps |

## Recommended Stack

| Tier | Role | Model | When It's Used |
|------|------|-------|----------------|
| T0 | 🧠 PM/Strategy | Claude Opus (`anthropic/claude-opus-4-5`) | Planning, research, content, conversation |
| T0 | 💻 Backend/Arch | Codex (`openai-codex/gpt-5.2`) | Architecture, APIs, scripts, infrastructure |
| T0 | 🎨 Frontend/UI | Claude Code (`claude-code`) | UI/UX, visual design, React, CSS |
| T2 | 📡 Bulk/background | Gemini (`google-gemini-cli/gemini-3-pro-preview`) | Summaries, bulk processing, routine heartbeats |
| T3 | ⚡ Cloud fallback | Kimi (`nvidia-nim/moonshotai/kimi-k2.5`) | When Anthropic/OpenAI are rate-limited |
| T4 | 🏠 Local emergency | Ollama (`ollama/qwen2.5:14b`) | Offline or all cloud exhausted |

**Explicit design choice:** this repo does **not** rely on Claude Sonnet. If you want Sonnet, add it yourself. The starter kit default is: *Opus always for PM work, Codex for coding, cross-provider fallbacks*.

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
