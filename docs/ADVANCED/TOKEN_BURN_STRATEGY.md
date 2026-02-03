# Token Burn Strategy — Codex-First

**Philosophy:** We pay $600/month for subscriptions (Claude MAX x2 + Codex MAX). Use EVERY token. Never pay per-token API costs.

---

## Model Allocation

| Model | Monthly Cost | Use For |
|-------|-------------|---------|
| **Codex MAX** | $200/mo | ALL backend coding — every bug fix, feature, script, refactor |
| **Claude MAX (zach@)** | $200/mo | Conversation, planning, research, content, organization |
| **Claude MAX (zachhgg@)** | $200/mo | Backup / overflow |

### Routing Rules
1. **Code work → Codex** (always). Spawn Codex sub-agents for:
   - Bug fixes
   - New features
   - Script creation
   - Refactoring
   - Test writing

2. **Everything else → Claude Opus**:
   - Planning and strategy
   - Research and analysis
   - Content creation
   - Documentation (prose)
   - Conversation with the user

3. **Fallback chain:** Codex → Claude Code (Opus) → build directly in main session
   - Never fall to trash-tier models (no Sonnet, no small models)

---

## Usage Monitoring

### Check Usage
```bash
# Claude weekly usage
codexbar usage --provider claude --format json
# Parse: .usage.secondary.usedPercent

# Codex weekly usage  
codexbar usage --provider codex --format json
# Parse: .usage.secondary.usedPercent
```

### Target Burn Rate
- **Weekly target:** 80-100% of each subscription
- **Daily target:** ~14% per day (100%/7 days)
- **If below pace:** Increase parallel work, spawn more agents

### Alerts
- **50% weekly by Wednesday:** On track
- **<30% by Wednesday:** BURN HARDER — spawn more Codex agents
- **>90% by Friday:** Slow down, preserve for weekend

---

## Parallel Execution Patterns

### When Usage is Low (Token Burn Mode)
1. **Spawn 3+ Codex agents** on real deliverables simultaneously
2. **Batch related work** into single specs (reduce spawn overhead)
3. **Prefer large tasks** with clear acceptance criteria over tiny ops tasks
4. **Never idle** — always have something building in background

### Overnight Builds
- Use `scripts/overnight_builder.py` to process `state/overnight_queue.json`
- Queue up tasks before bed
- Morning: Review results, pick up where agents left off

### Max Concurrency
- **Codex sub-agents:** 3 concurrent (per overnight_builder.py)
- **Main session:** Can run parallel to sub-agents
- **Total:** Up to 4 "threads" of work

---

## Anti-Patterns (What NOT to Do)

❌ **Don't wait for confirmation** before starting  
❌ **Don't send plans without executing**  
❌ **Don't go silent** for >5 minutes  
❌ **Don't ask "what would you like me to do?"**  
❌ **Don't build watchers to watch watchers**  
❌ **Don't over-engineer reliability systems**  
❌ **Don't pay for API tokens** when subscription has capacity  

---

## Night Shift Mode

When running overnight (after 10pm):
1. **Auto-work is OK** — no need to wait for the user
2. **Process overnight_queue.json** first
3. **If backlog empty AND below-pace:** Create new tasks every hour
4. **Morning summary:** Report what was built overnight

---

## Subscription Tracking

| Service | Tier | Renewal | Downgrades To |
|---------|------|---------|---------------|
| Claude (zach@) | MAX $200/mo | Feb 27 | PRO |
| Claude (zachhgg@) | MAX $200/mo | Feb 16 | PRO |
| Codex (zach@) | MAX $200/mo | Feb 28 | Plus |

**USE EVERY TOKEN.** Never enable billing on API keys.
