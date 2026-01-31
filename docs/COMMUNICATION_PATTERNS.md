# Communication Patterns

Lessons learned from real-world agent-to-human communication via Telegram/messaging.

## The Core Problem

AI agents tend to either go silent for too long or spam too many messages. Both are bad. Your human should always know what's happening, but shouldn't need to scroll through 20 messages to find the status.

## Rules

### 1. Consolidate, Don't Spam

**Bad:** 8 separate messages over 5 minutes about the same sprint.
**Good:** 1 message when work starts, 1 when it's done, with all details in each.

When multiple things happen close together, batch them into one organized message.

### 2. Never Go Silent During Active Work

If a background agent is running, poll every 60-90 seconds and update your human on progress. They should never have to ask "what's happening?"

### 3. Output Hygiene

Internal reasoning, status tracking, and tool call artifacts must NEVER leak into messages sent to your human. This happens when:
- Context gets compacted mid-conversation
- Multiple inputs arrive simultaneously (heartbeat + user message + poll results)
- You compose a message while processing other events

**Fix:** Treat message composition as an isolated atomic action. Finish processing, THEN compose the message.

### 4. Accuracy Over Speed

Every message must reflect what's ACTUALLY happening right now:
- No stale data from previous sessions
- No automated scripts sending false alarms
- No repeating information you've already sent
- Verify claims before sending (check git log, not memory)

### 5. Structure Your Updates

Use consistent formatting so your human can scan quickly:

```
✅ **Sprint [X] complete** — [what was done]
📝 Commit: [hash]
🔨 Files changed: [count]
📋 Next: [what's coming]
```

### 6. When Your Human Says "Too Many Messages"

They mean: organize better, not communicate less. Consolidate related updates into single, well-structured messages. Keep the information density high but the message count low.

## Anti-Patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| Message per file change | Noise | Batch into sprint completion message |
| Internal monologue in messages | Confusing | Separate processing from messaging |
| Repeating the same status | Annoying | Track what you've already told them |
| Going silent for 10+ min | Anxiety-inducing | Set up polling loops |
| Asking which model to use | Wasting their time | Follow the fallback chain silently |
| False alarms from scripts | Erodes trust | Validate before alerting |
