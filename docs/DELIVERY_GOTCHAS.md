# Delivery Gotchas (How to Make Automations Actually Send)

The most common failure mode in “agent automation” is boring:

> The job ran, but nothing was delivered.

This doc explains how to avoid that.

## systemEvent vs agentTurn

### systemEvent (main session)
- Injects a message into the session.
- **Does not automatically send a message to your chat**.
- Useful for nudging the agent (“check X”), especially when paired with heartbeat.

### agentTurn (isolated session)
- Runs the agent like a normal turn.
- Can **send messages** when `deliver:true` *and/or* when the agent calls the message tool.
- Best for guaranteed recaps and scheduled reporting.

## Best practice: for scheduled reports, use agentTurn + deliver:true

If you want something to show up in Telegram every time:
- use an isolated cron job
- set `deliver:true`
- and instruct the job to send via the message tool

## Best practice: for awareness, use heartbeat

If you want “tell me only if something needs attention”:
- use heartbeat
- keep HEARTBEAT.md short
- reply HEARTBEAT_OK when nothing is needed

## Debugging checklist

1) `openclaw cron list` (is the job enabled? nextRunAt?)
2) `openclaw cron runs <job-id>` (did it run? duration? errors?)
3) `openclaw status --deep` (is the channel healthy?)
4) `openclaw logs --follow` (look for tool errors)

## Avoiding redundancy

- Don’t have both a heartbeat and a cron job do the same check.
- If you must, define:
  - heartbeat = awareness
  - cron = action/report
