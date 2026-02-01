# Meta-Learning Systems

How your AI learns from mistakes, adapts to patterns, and gets smarter over time.

---

## Philosophy

> *"Architecture beats instructions. If a process can't reliably follow rules, don't write better rules. Remove its ability to trigger the wrong action."*

Your system doesn't just fix problems. It learns *which fixes work*, tracks success rates, adapts strategy over time, and prevents the same mistake from happening twice.

---

## The Six Learning Layers

```
┌──────────────────────────────────────────────────────────────┐
│                    LAYER 6: META-MONITOR                      │
│         Watches all systems, detects systemic failures        │
├──────────────────────────────────────────────────────────────┤
│                    LAYER 5: SELF-REVIEW                       │
│         Metacognition loop (MISS/HIT tagging)                │
├──────────────────────────────────────────────────────────────┤
│                    LAYER 4: INCIDENT LEARNING                 │
│         Post-mortems, root cause analysis                     │
├──────────────────────────────────────────────────────────────┤
│                    LAYER 3: PERSONAL LEARNER                  │
│         User pattern detection, preference learning           │
├──────────────────────────────────────────────────────────────┤
│                    LAYER 2: WATCHDOG LEARNING                 │
│         Fix success rates, pattern matching                   │
├──────────────────────────────────────────────────────────────┤
│                    LAYER 1: ERROR RECOVERY                    │
│         Automated pattern detection, auto-fix                 │
└──────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Error Recovery

**Script:** `scripts/error_recovery.py` (included in this kit)

**What it does:** Scans gateway error logs, matches errors against known patterns, applies auto-fixes, tracks success/failure.

**The Fluke Rule:**
- First occurrence: log it, don't fix (might be a fluke)
- Second occurrence: apply auto-fix, monitor result
- Third+ in 24h: NOT a fluke — permanent adaptation

**Learning output:** Success rate per fix type (e.g., auth-fix: 100%, restart: 80%). Over time, the system learns to prefer fixes with higher success rates.

---

## Layer 2: Watchdog Learning

**Script:** `scripts/watchdog_learn.sh` (included in this kit)

**What it does:** After every intervention, analyzes what happened, logs the incident, detects patterns, and updates metrics.

**Key metrics:**
```json
{
  "fixes": {
    "doctor-fix": { "attempted": 9, "succeeded": 9, "rate": 1.0 },
    "gateway-restart": { "attempted": 3, "succeeded": 2, "rate": 0.67 }
  }
}
```

**Adaptive behavior:** If a fix type has a low success rate, the system stops trying it first and escalates to alternatives.

---

## Layer 3: Personal Learner

**Script:** `scripts/personal_learner.py` (reference implementation)

**What it does:** Scans memory files for patterns about the user:
- Goal mentions (which goals are active vs forgotten)
- Emotional signals (stress, excitement, frustration)
- Decision follow-ups (what gets done, what doesn't)
- Communication preferences

**Proactive triggers:**
- Goal not mentioned in 7+ days → nudge
- Stress signals spiking → check in
- Decision follow-up overdue → remind

**Output:** A user model JSON file that your AI references for better personalization.

---

## Layer 4: Incident Learning

**Template:** `templates/self-review.md` (included in this kit)

**What it does:** Every significant failure gets a post-mortem:

```markdown
## YYYY-MM-DD — Incident Title

### What Happened
[Description]

### Root Causes
[Why it failed, not just what failed]

### Fixes Applied
[What was done]

### Lessons (PERMANENT)
[Rules extracted from this incident]
```

**The key insight:** Document *root causes*, not symptoms. "The script crashed" is a symptom. "Python `None` converts to string 'None' in bash, which reads as non-empty" is a root cause.

---

## Layer 5: Self-Review (Metacognition)

**Template:** `templates/self-review.md` (included in this kit)

Your AI reflects on its own performance using MISS/HIT tags:

```
[2026-01-29] TAG: confidence
MISS: Updated rules text but didn't fix the architecture. Model kept violating rules.
FIX: Don't rewrite rules for weak models — remove their access to dangerous actions.
```

**Counter-check rule:** When a current task overlaps with a past MISS tag, force a counter-check. Challenge the first instinct before acting.

**Pattern detection:** If the same TAG appears 3+ times in MISSes, it's systemic. Update the rules or architecture, not just the documentation.

---

## Layer 6: Meta-Monitor

**Script:** `scripts/meta_monitor.py` (included in this kit)

**What it does:** Watches all other systems. Detects when watchers themselves are broken.

**Key features:**
- Per-system health thresholds (customizable)
- Fencing tokens to prevent restart races
- Escalation at 3+ simultaneous system failures
- Context usage tracking

See `docs/META_MONITOR.md` for full setup.

---

## The Learning Chain

```
Incident occurs
    → Error Recovery detects + fixes (Layer 1)
    → Watchdog logs + learns fix outcome (Layer 2)
    → Incident documented with root cause (Layer 4)
    → Self-Review reflects on what went wrong (Layer 5)
    → Meta-Monitor validates all systems healthy (Layer 6)
    → Rules/scripts updated to prevent recurrence
    → System is smarter than yesterday
```

---

## Permanent Lessons (Battle-Tested)

These rules were extracted from real incidents:

1. **Architecture > Instructions** — If a process can't follow rules (dying session, weak model), don't write better rules. Build external enforcement.

2. **Test with null/empty values** — Every script must handle null gracefully. `None` in Python ≠ empty string in bash.

3. **Test the actual thing** — Don't parse logs about message delivery. Send an actual test message and verify the response.

4. **Verify delivery, don't assume it** — Use explicit target IDs. Scan for confirmation. Auto-retry on failure.

5. **Fix success rates guide strategy** — Track which fixes actually work. Stop using fixes with 0% success rate.

6. **Fluke vs pattern** — One failure = log and wait. Three failures in 24h = adapt permanently.

7. **Never auto-refire failed tasks** — Failed automation should alert, not retry indefinitely. Infinite loops are worse than failures.

8. **External monitoring for critical notifications** — A dying process can't notify about its own death. Use an external watchdog.

---

## Setting It Up

### Minimum viable learning:

1. **Add `self-review.md` to your templates** (already included)
2. **Add self-review to your HEARTBEAT.md** — every 4th heartbeat, reflect on recent work
3. **Enable watchdog learning** — `watchdog_learn.sh` runs automatically after interventions
4. **Document incidents** — when something breaks, write a post-mortem with root cause + lesson

### Full learning stack:

1. All of the above, plus:
2. **Deploy meta-monitor** — `scripts/meta_monitor.py` watches everything
3. **Add personal learner** — `scripts/personal_learner.py` learns user patterns
4. **Track fix success rates** — watchdog metrics accumulate automatically
5. **Set counter-check rules** — AI reviews past MISSes before acting on similar tasks

The learning systems bootstrap themselves. Start with the minimum, and the system grows smarter with every incident it handles.

---

*"The goal isn't to never make mistakes. It's to never make the same one twice."*
