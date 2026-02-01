# Email & iMessage Automation Guide 📧

> **Bonus guide:** How to build a comprehensive email organization system and secure iMessage integration with OpenClaw.

## Overview

This guide covers:
1. **Gmail MECE Label System** — organize all email accounts with one taxonomy
2. **Gmail Filter Automation** — auto-sort incoming mail server-side
3. **Apple Mail Smart Mailboxes** — aggregate labels across all accounts into virtual folders
4. **Apple Mail Rules Cleanup** — replace legacy rules with clean automation
5. **iMessage Security Policy** — safe read/write access for AI assistants
6. **VIP Email Scanner** — proactive surfacing of important emails

## 1. Gmail MECE Label System

Create identical labels across ALL Gmail accounts for consistent organization:

```
Action/
  Reply        — needs a human response
  Review       — needs reading/evaluation
  Todo         — has an action item attached

People/
  VIP          — key contacts, family, close friends
  Fans         — audience members, subscribers
  Networking   — business contacts, potential collaborators

Financial/
  Receipts     — purchase confirmations
  Invoices     — bills to pay
  Tax          — tax documents

Projects/
  [Project1]   — per-project label
  [Project2]

Work/
  [Company]    — work-related

Automated/
  CI           — GitHub, build systems, Xcode Cloud
  Monitoring   — Sentry, uptime, security alerts
  Social       — Twitter, LinkedIn, Instagram notifications

Newsletters/
  Must-Read    — newsletters you actually read

Memories/
  Family       — emails from family members
  Warm-Fuzzy   — sentimental emails worth keeping

Travel         — bookings, itineraries
Property       — real estate related
Credentials    — password resets, verification codes
Legal          — contracts, legal documents
BlackHole      — auto-archived noise
Waiting        — sent, waiting for reply
_Archive       — manually archived
```

### Why MECE?
Every email should fit exactly ONE category. No overlaps. This makes Smart Mailboxes reliable and prevents confusion about where to find things.

### Automated Setup

Create a script that deploys identical labels across all accounts:

```python
#!/usr/bin/env python3
"""Deploy MECE labels across all Gmail accounts via gog CLI."""
import subprocess

ACCOUNTS = ["you@gmail.com", "work@yourdomain.com"]  # your accounts
LABELS = [
    "Action", "Action/Reply", "Action/Review", "Action/Todo",
    "People", "People/VIP", "People/Fans", "People/Networking",
    # ... add all labels
]

for account in ACCOUNTS:
    for label in LABELS:
        subprocess.run(["gog", "gmail", "labels", "create", label,
                       "--account", account, "--force"],
                      capture_output=True)
```

## 2. Gmail Filter Automation

Gmail filters apply server-side to incoming mail. They work even when Apple Mail isn't running.

```python
# Example: auto-label GitHub notifications
gog gmail filters create \
  --account you@gmail.com \
  --from "noreply@github.com" \
  --add-label "Automated/CI" \
  --skip-inbox \
  --mark-read
```

### Key filter categories:
| Pattern | Label | Extra |
|---------|-------|-------|
| `from:github.com` | Automated/CI | skip inbox, mark read |
| `from:sentry.io` | Automated/Monitoring | skip inbox |
| `from:twitter.com` | Automated/Social | skip inbox |
| `from:paypal.com` | Financial/Receipts | — |
| `from:substack.com` | Newsletters | — |
| Family addresses | Memories/Family | star, never spam |

### Retroactive Labeling
Filters only apply to NEW messages. For existing emails, use bulk label modification:

```bash
# Search + label existing messages
threads=$(gog gmail search "from:github.com" --account you@gmail.com --max 100 --plain | tail -n +2 | awk '{print $1}')
gog gmail labels modify $threads --account you@gmail.com --add "Automated/CI" --force
```

## 3. Apple Mail Smart Mailboxes

Smart Mailboxes aggregate messages across ALL accounts. They're virtual folders based on criteria.

### Common Mistake
Smart Mailbox criteria match against **leaf mailbox names**, not full paths. If your Gmail label is `Action/Reply`, the IMAP mailbox name is "Reply" (nested under "Action"). Use `AnyMailbox IsEqualTo "Reply"` — not `AnyMailbox IsEqualTo "Action/Reply"`.

### How to Build Them

Smart Mailboxes are stored in:
```
~/Library/Mobile Documents/com~apple~mail/Data/V4/SyncedSmartMailboxes.plist
```

This syncs via iCloud to all Apple devices (Mac + iPhone + iPad).

Use OR logic (`AllCriteriaMustBeSatisfied = false`) to match multiple sub-labels:

```python
import plistlib, uuid

def make_smart_mailbox(name, leaf_names):
    """Build a smart mailbox matching any of the given leaf mailbox names."""
    criteria = []
    for leaf in leaf_names:
        criteria.append({
            "CriterionUniqueId": str(uuid.uuid4()),
            "Expression": leaf,
            "Header": "AnyMailbox",
            "Qualifier": "IsEqualTo"
        })
    
    return {
        "MailboxName": name,
        "MailboxType": 7,  # smart mailbox
        "MailboxAllCriteriaMustBeSatisfied": True,
        "MailboxCriteria": [
            # Standard filters
            {"Header": "NotInTrashMailbox", ...},
            {"Header": "NotInJunkMailbox", ...},
            # OR compound for leaf names
            {
                "AllCriteriaMustBeSatisfied": False,  # OR logic
                "Criteria": criteria,
                "Header": "Compound",
            }
        ],
        ...
    }
```

### Recommended Smart Mailboxes
| Name | Matches | Notes |
|------|---------|-------|
| 🔴 Action | Reply, Review, Todo + Flagged | Things needing human attention |
| 👥 People / VIP | VIP, Fans, Networking + key sender addresses | Important contacts |
| 📰 Newsletters | Newsletters, Must-Read | Subscriptions |
| 💰 Financial | Financial, Receipts, Tax, Invoices + sender matching | Money stuff |
| 📋 Projects | Per-project labels | All project emails |
| 🤖 Automated | CI, Monitoring, Social | Noise (but organized) |
| ✈️ Travel | Travel + airline/hotel sender matching | Bookings |
| 🫶 Memories | Family, Warm-Fuzzy + family sender addresses | Sentimental |
| 💼 Work | Work, Company-specific labels | Professional |

## 4. Apple Mail Rules Cleanup

Legacy rules accumulate over years. Audit and clean them:

```applescript
tell application "Mail"
    -- List all rules
    repeat with r in rules
        log (name of r) & " [" & (enabled of r) & "]"
    end repeat
    
    -- Delete useless ones
    delete (first rule whose name is "Rule 2")
end tell
```

**Keep:** Rules that handle things Gmail filters can't (local notifications, specific flagging).
**Delete:** Old catch-all rules, disabled rules, anything with names like "Rule 2" or "misc".

## 5. iMessage Security Policy

If your OpenClaw setup has iMessage access (via `imsg` skill), enforce strict security:

### Tier System
1. **Tier 1 (READ-ONLY):** List chats, read history, watch for new messages. No sending.
2. **Tier 2 (APPROVED SEND):** Sending allowed only with explicit human approval per message.
3. **Tier 3 (AUTO-SEND):** Future capability. Requires 30+ days without incident at Tier 2.

### Mandatory Rules
- Every send requires human approval via your messaging channel (Telegram, Discord, etc.)
- Content scanning for sensitive data (SSN, credit card, API key patterns)
- Rate limiting: 5 sends/hour, 20/day maximum
- Logging: Every read and send to an audit file
- Recipient restrictions: No auto-sends to work contacts or group chats

### Example Policy File
```markdown
# iMessage Security Policy
- Status: Tier 1 (READ-ONLY)
- All sends require explicit approval
- Content scanning: enabled
- Rate limit: 5/hr, 20/day
- Audit log: memory/imessage-audit.md
```

## 6. VIP Email Scanner

Build a heartbeat-triggered scanner that surfaces important emails to your messaging channel:

```python
# Pseudo-code for VIP scanner
def scan_vip_emails():
    for account in accounts:
        # Search for unread messages from VIP senders
        results = gog_search(f"is:unread from:({vip_addresses})", account)
        
        for msg in results:
            if not already_reported(msg.id):
                notify_user(f"📧 VIP email from {msg.sender}: {msg.subject}")
                mark_reported(msg.id)
```

Add to your heartbeat (every 1-2 hours) for proactive email surfacing without spam.

## Tips

1. **Start with filters, end with Smart Mailboxes.** Get the sorting right first, then build views.
2. **Test with `--max 1` first.** Don't bulk-label 10,000 emails before verifying the query is correct.
3. **Use `--force` for bulk operations.** Skips confirmation prompts.
4. **Restart Apple Mail** after modifying the Smart Mailbox plist. It reads the file at launch.
5. **iCloud syncs Smart Mailboxes** — changes appear on iPhone/iPad within minutes.
6. **Back up the plist** before modifications: `cp SyncedSmartMailboxes.plist SyncedSmartMailboxes.plist.bak`

---

*Guide based on real-world setup across 5 Gmail accounts with 77 MECE labels, 70 filters, and 9 Smart Mailboxes. No personal information included.*
