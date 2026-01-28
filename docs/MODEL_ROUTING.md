# MODEL_ROUTING.md — Intelligent Model Orchestration

*"Use the right tool for the job. A butler doesn't use a sledgehammer to hang a picture frame."*

## TL;DR

**Orchestrate with the smartest. Execute with the cheapest/fastest.** 
Opus/Brain model orchestrates. Specialists execute. Background tasks never touch the main model. Local fallback means you can't hit zero.

**Current usage:** Check via `python3 ~/clawd/scripts/check_usage.py`

---

## The Stack

| Tier | Role | Model | When It's Used |
|------|------|-------|----------------|
| T0 | 🧠 Orchestrator | Claude Opus / High-IQ Model | Strategy, reasoning, decisions, main chat |
| T1 | 💻 Code Specialist | Codex / Claude Code | Code generation, refactoring, scripts |
| T2 | 📡 Background/Bulk | Gemini / Flash Model | Heartbeats, summarization, bulk processing |
| T3 | ⚡ Fallback | Claude Sonnet / GPT-4o | Backup when main models down |
| T4 | 🏠 Local Emergency | Local (Ollama/Llama) | Offline, all cloud exhausted |

```
┌────────────────────────────────────────────────────────────┐
│  ORCHESTRATOR: Smartest Model (e.g. Claude Opus)           │
│  → Strategic decisions, complex reasoning, main chat       │
│  → "What should we build?" / "Debug this architecture"     │
├────────────────────────────────────────────────────────────┤
│  CODE SPECIALIST: Coding Model (e.g. Codex/Claude Code)    │
│  → Raw code generation, refactoring, scripts               │
│  → Orchestrator plans architecture, Specialist writes code │
├────────────────────────────────────────────────────────────┤
│  BACKGROUND: Fast/Cheap Model (e.g. Gemini/Flash)          │
│  → Heartbeats, summarization, bulk text processing         │
│  → Keeps system "alive" without touching main models       │
├────────────────────────────────────────────────────────────┤
│  LOCAL FALLBACK: Local Model (e.g. Ollama)                 │
│  → Offline operation, unlimited capacity, privacy tasks    │
│  → Auto-starts on boot, always available                   │
└────────────────────────────────────────────────────────────┘
```

---

## Task → Model Routing (MANDATORY)

```
ORCHESTRATOR (thinking)      SPECIALIST (coding)
├─ deep research             ├─ new apps/scripts
├─ complex analysis          ├─ refactoring
├─ strategy & planning       ├─ debugging
├─ architecture decisions    ├─ API integrations
├─ orchestration             └─ multi-file changes
└─ quick tasks/file ops      

BACKGROUND (bulk)            SPECIALIZED
├─ summarization             ├─ image gen
├─ heartbeat checks          ├─ voice/audio
├─ bulk text processing      └─ specialized agents
└─ formatting/conversion     

LOCAL (emergency only)
└─ when ALL cloud is exhausted
```

### Decision Flow

```
1. Is this CODING?           → Spawn Coding Agent
2. Is this SUMMARIZATION?    → Spawn Background Agent
3. Is this DEEP RESEARCH?    → Handle directly (Orchestrator)
4. Is this IMAGE GENERATION? → Use image skill
5. Is this COMPLEX/QUICK?    → Handle directly (Orchestrator)
```

### Real Examples

| Request | Model | Why |
|---------|-------|-----|
| "Plan out the architecture for a new app" | Orchestrator | Strategic, deep reasoning |
| "Write a Python script to parse JSON" | Specialist | Code specialist |
| "Summarize this doc in the background" | Background | Bulk text work |
| "Check email, calendar, usage" (heartbeat) | Background | Lightweight monitoring |

---

## Complex Coding Workflow

For bigger coding tasks (new apps, major refactors, multi-file changes):

1. **Orchestrator plans** — architecture, approach, tradeoffs
2. **Compare approaches** — how would different models tackle it?
3. **Prompt [USER]** — "Here's the plan, approve?"
4. **Specialist executes** — write the actual code

Quick tasks (single file, small fix) → skip straight to Specialist.

---

## Degradation Curve (Usage-Based)

| Usage % | Available Models | Behavior |
|---------|-----------------|----------|
| 0-80% | All freely available | Normal operation |
| 80-90% | Prefer Cheaper Models | Orchestrator for critical only |
| 90-95% | Cheaper Models Only | Minimize Orchestrator |
| 95-100% | Background Only | Save remaining tokens for emergency |
| 100%+ | Local Only | Never hit zero |

---

## What Runs Where

| Task | Model | How |
|------|-------|-----|
| Main conversation | Orchestrator | Direct |
| Deep research | Orchestrator | Direct |
| Code writing | Specialist | `sessions_spawn` |
| Summarization | Background | `sessions_spawn` |
| Heartbeat checks | Background | Moltbot config |
| Daily security audit | Background | cron |
| Extreme fallback | Local | Only when all else fails |

---

## Usage Monitoring
```bash
python3 ~/clawd/scripts/check_usage.py
```
