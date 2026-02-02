# HEARTBEAT.md (Template)

Runs every 1 hour. 3 checks max.

1) Usage/quota snapshot (alert only if something is close to limit)
2) Repo hygiene: if workspace is dirty, commit+push
3) If the human hasn’t heard from you in 30+ min: send one progress update

If nothing needs attention: reply HEARTBEAT_OK
