# Documentation Sync Checklist

Before pushing ANY changes to this repo, run through this checklist.

## Mandatory Checks

### 1. CHANGELOG.md ✅
- [ ] Added entry under `[Unreleased]`
- [ ] Description matches what actually changed

### 2. Docs Sync Audit ✅
Ask: "Does any documentation need updating based on what I learned or changed?"

**Trigger → Doc to Update:**

| If you learned/changed... | Update this doc |
|---------------------------|-----------------|
| Model routing (Codex vs Claude) | `docs/MODEL_ROUTING.md` |
| Felix/Nat patterns | `docs/ADVANCED/FELIXCRAFT_PATTERNS.md` |
| Token burn strategy | `docs/ADVANCED/TOKEN_BURN_STRATEGY.md` |
| Subagent vs CLI patterns | `docs/SUBAGENT_BEST_PRACTICES.md` |
| Cron/heartbeat patterns | `docs/CRON_HEARTBEAT_GUIDE.md` |
| Config/hygiene patterns | `docs/CONFIG_HYGIENE.md` |
| Stability/incident learnings | `docs/LESSONS_LEARNED_STABILITY.md` |
| Overnight build patterns | `docs/ADVANCED/OVERNIGHT_BUILD_PIPELINE.md` |
| Trust/autonomy levels | `docs/ADVANCED/TRUST_LADDER.md` |
| Email automation | `docs/EMAIL_IMESSAGE_AUTOMATION.md` |
| Security patterns | `docs/SECURITY_HARDENING.md` |
| Migration/setup | `docs/MIGRATION.md`, `docs/BEGINNER_START_HERE.md` |

### 3. Cross-Reference Check
- [ ] If you updated one doc, check if related docs need updates too
- [ ] Search for mentions of updated concepts: `grep -r "<concept>" docs/`

## Quick Audit Script

```bash
#!/bin/bash
# Run from repo root
echo "=== Docs last modified ==="
find docs -name "*.md" -type f -exec stat -f "%m %N" {} \; | sort -rn | head -20 | while read ts file; do
  date -r $ts "+%Y-%m-%d %H:%M" | tr '\n' ' '
  echo "$file"
done

echo ""
echo "=== Docs mentioning recent topics ==="
for topic in "Codex" "Claude" "Ralph" "subagent" "heartbeat" "Felix"; do
  count=$(grep -rl "$topic" docs/ 2>/dev/null | wc -l | tr -d ' ')
  echo "$topic: $count docs"
done
```

## When to Skip

You can skip the full audit if:
- Change is typo-only
- Change is to archive/ folder only
- Change is CHANGELOG.md only

But ALWAYS update CHANGELOG.md regardless.

## Emergency Bypass

```bash
SKIP_DOC_SYNC=1 git commit -m "..."
```

If you bypass, create a follow-up PR for doc sync within 24 hours.
