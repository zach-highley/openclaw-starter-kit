# Email IMAP → Apple Mail Smart Mailboxes

## Overview
Gmail labels appear as IMAP folders when "Show in IMAP" is enabled.
Apple Mail Smart Mailboxes query these IMAP folders to organize email.

## How It Works

### Gmail Side
1. Gmail labels have a `labelListVisibility` setting:
   - `labelShow` → Visible in IMAP as a folder
   - `labelHide` → Hidden from IMAP
   - `labelShowIfUnread` → Show only if unread messages exist

2. User labels (like `Example/Family`) appear under `[Gmail]/` prefix in IMAP

### Apple Mail Side
1. Apple Mail sees IMAP folders, not Gmail labels
2. Smart Mailboxes can query:
   - Specific folders (e.g., "Message is in Example/Family")
   - Subject/From/To fields
   - Date ranges
   - Read/Unread status
   - Flagged status

### Creating Apple Mail Smart Mailboxes

**To create a Smart Mailbox in Apple Mail:**
1. Mailbox → New Smart Mailbox
2. Set conditions (e.g., "Message is in folder [Gmail]/Example/Family")
3. Name it (e.g., "Family Emails")

**Recommended Smart Mailboxes for MECE system:**
- Action/Respond → Emails needing replies
- Action/Review → Emails to read
- Action/Waiting → Awaiting someone else
- People/<Name> → Per-person folders
- Projects/<Name> → Per-project folders

## MECE Label System

Our labels (from scripts/email_categorize.py):
- Action/Respond, Action/Review, Action/Waiting, Action/Delegate
- People/<Name>
- Projects/<Name>
- Work/McKinsey, Work/Consulting
- Financial/Banking, Financial/Investments, Financial/Taxes
- Travel/Flights, Travel/Hotels, Travel/Reservations
- Newsletters/<Name>
- Notifications/Social, Notifications/Marketing
- Automated/Receipts, Automated/Confirmations
- Memories (photos, videos, important moments)
- Property, Legal, Credentials
- BlackHole (permanently ignore)
- _Archive (done, don't need to see)

## Audit Script
Run `python3 ~/openclaw-workspace/scripts/email_imap_audit.py` to check which labels are IMAP-visible.

## Apple Mail Sync Issues

**Common problems:**
1. Label not appearing → Check "Show in IMAP" in Gmail settings
2. Smart Mailbox empty → Verify folder path matches exactly
3. Slow sync → Gmail IMAP can be slow for large labels

**Fix:**
- Gmail → Settings → Labels → Toggle "Show in IMAP" checkbox
- Or use gog CLI: requires Gmail API label update (not available yet)

## Next Steps
1. Run IMAP audit to identify hidden labels
2. Enable IMAP visibility for MECE labels
3. Create Apple Mail Smart Mailboxes
4. Test Smart Mailbox queries

---
*Created: 2026-02-03*
