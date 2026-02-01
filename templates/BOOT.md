# BOOT.md - Gateway Restart Startup

On gateway restart, verify critical systems are healthy:

1. Check state files exist and are valid JSON
2. Run background work watcher — report any completions
3. Verify memory files exist: `memory/$(date +%Y-%m-%d).md`, `MEMORY.md`
4. **ALWAYS message the user** confirming restart is complete (context %, worker health, any issues)
5. **IMMEDIATELY resume work** — read your task list, pick the highest-priority incomplete item, and start executing. Restarts are invisible speed bumps, not stop signs. The restart notification and first work action happen in the SAME response.
6. If anything failed, include failure details in your message

Keep this tiny. Full checks happen in HEARTBEAT.md.
