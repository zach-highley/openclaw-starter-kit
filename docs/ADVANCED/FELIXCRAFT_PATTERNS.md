# FelixCraftAI Research Notes

**Source:** https://felixcraft.ai/ | @FelixCraftAI
**Operator:** Nat Eliason (@nateliason)
**Platform:** Clawdbot (OpenClaw-adjacent)

## What Felix Does
- CEO of The Masinov Company
- Manages projects, writes code, handles communications, builds products
- Runs autonomously overnight
- Wrote 21-page "How to Hire an AI" playbook in one session while Nat slept

## Their Stack (same as ours!)
- SOUL.md — personality/identity
- IDENTITY.md — role definition
- MEMORY.md — long-term memory
- Three-layer memory architecture
- Sub-agent delegation
- Safety rails + trust ladder
- Daily operating rhythms

## Key Concepts

### Model Routing (Feb 2026 Update)
From @Austen (industry consensus):
- **Codex** → Architecture, backend, scripts, APIs, databases, infrastructure
- **Claude Opus** → PM work, planning, research, content, strategy
- **Claude Code** → Frontend, UI/UX, visual design, React/Next.js, CSS

### Ralph Loops (Feb 2026 - Critical Pattern)
Instead of using CLI terminals for coding:
1. Spawn **Codex CLI directly** in full-auto mode
2. Wrap in **Ralph loops** with PRD checklist as source of truth
3. Each iteration gets **completely fresh context** (discovers state from files + git, not memory)
4. Validate against checklist: "Lies? Restart. Stalls? Restart. Dies? Restart."

**Key insight:** "Amnesia is a feature. Fresh eyes every iteration means no compounding hallucinations."

Felix ran 108 tasks across 3 branches in 4 hours using this pattern.

### Trust Ladder
Graduated autonomy levels:
1. Ask before everything
2. Execute safe operations, ask on risky
3. Execute most things, report after
4. Full autonomy with periodic check-ins

### Three-Layer Memory
1. **Knowledge graph** — people and projects (not just a flat file)
2. **Daily notes** — timeline events
3. **Thinking file** — how the human thinks

One flat notes file doesn't cut it. You need something closer to how a real colleague learns you over months.

### Routines
- Morning checkins
- Nightly memory extraction
- Weekly synthesis (stale facts decay out)
- **Nightly friction-fix**: scans day for friction → picks one thing → builds it overnight

### Daily Operating Rhythms
- Morning check-in
- Autonomous work periods
- Evening summary
- Overnight builds

### Economic Agency Bottlenecks
> "The agent-first business isn't limited by what AI can do. It's limited by what the world will let AI do."

What blocks agents: identity in physical/financial world, not intelligence.

## How We Compare

| Feature | FelixCraftAI | YourBot |
|---------|--------------|------|
| SOUL.md | ✅ | ✅ |
| IDENTITY.md | ✅ | ✅ |
| MEMORY.md | ✅ | ✅ |
| Daily memory files | ? | ✅ memory/YYYY-MM-DD.md |
| Sub-agents | ✅ | ✅ (Codex, Claude Code) |
| Overnight work | ✅ | ✅ overnight builds |
| Trust ladder | Explicit | Implicit (AGENTS.md rules) |
| Wallet/payments | ✅ USDC | ❌ Not needed |

## What We Could Adopt

1. **Explicit trust ladder** — Document autonomy levels in AGENTS.md
2. **Overnight work templates** — Structured overnight build specs
3. **Playbook monetization** — the user could sell similar (starter-kit?)

## Business Insight
Nat sold this playbook for $29 and reportedly made $200k in a week teaching AI.
Our openclaw-starter-kit is free + open source. Could be monetized if desired.

---
*Researched: 2026-02-03*

---

## Action Plan: FelixCraft-Style Capabilities

### Phase 1: Foundation (Already Done ✅)
- [x] SOUL.md — YourBot personality
- [x] IDENTITY.md — Role definition
- [x] MEMORY.md — Long-term memory
- [x] memory/YYYY-MM-DD.md — Daily session logs
- [x] Sub-agent delegation (Codex, Claude Code)
- [x] Overnight build pipeline (OC-014)

### Phase 2: Trust Ladder (TODO)
Document explicit autonomy levels in AGENTS.md:

| Level | Name | Behavior |
|-------|------|----------|
| 1 | Cautious | Ask before everything |
| 2 | Safe | Execute safe ops, ask on risky |
| 3 | Trusted | Execute most, report after (CURRENT) |
| 4 | Autonomous | Full autonomy, periodic check-ins |
| 5 | Night Shift | Create own tasks, no check-ins |

### Phase 3: Economic Agency (BP-250)
Like Felix, we should be able to:
- [ ] Accept payments (Stripe integration?)
- [ ] Track invoices/revenue
- [ ] Generate revenue reports
- [ ] Eventually: autonomous revenue generation

### Phase 4: Content/Education Product
Felix monetizes via playbooks. We could:
- [ ] Package openclaw-starter-kit as paid tier
- [ ] Create "How to Build Your Own AI Butler" course
- [ ] Sell SOUL.md templates for different personas

### Immediate Actions
1. **Add Trust Ladder to AGENTS.md** ← Do this now
2. **Night Shift self-tasking** ← Already added to rules
3. **Dashboard should show autonomy level** ← Future

### Phase 5: Agent-to-Agent Economy (NEW — Feb 2026)
See [AGENT_ECONOMY.md](./AGENT_ECONOMY.md) for the full pattern.

Key insight: Build products FOR other agents, not just humans.
- Battle Arenas (agents compete)
- Agent directories (agents register)
- Reputation systems (agents build trust)
- API marketplaces (agents buy/sell services)

Felix Week 1 Revenue: $41,526 (book sales + WETH trading fees)
The agent economy is real and growing.

---

*Updated: 2026-02-06*
