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

### Trust Ladder
Graduated autonomy levels:
1. Ask before everything
2. Execute safe operations, ask on risky
3. Execute most things, report after
4. Full autonomy with periodic check-ins

### Three-Layer Memory
1. Ephemeral (conversation context)
2. Session (daily logs)
3. Persistent (MEMORY.md, long-term)

### Daily Operating Rhythms
- Morning check-in
- Autonomous work periods
- Evening summary
- Overnight builds

## How We Compare

| Feature | FelixCraftAI | Yoda |
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
- [x] SOUL.md — Yoda personality
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
- [ ] Create "How to Build Your Own Yoda" course
- [ ] Sell SOUL.md templates for different personas

### Immediate Actions
1. **Add Trust Ladder to AGENTS.md** ← Do this now
2. **Night Shift self-tasking** ← Already added to rules
3. **Dashboard should show autonomy level** ← Future

---

*Updated: 2026-02-03 ~4pm*
