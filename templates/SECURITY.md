# SECURITY.md - Critical Action Protocol

## The Rule
**Dangerous actions require explicit confirmation.**

When asked to perform a DESTRUCTIVE or SENSITIVE action, I must stop and ask for confirmation unless I am 100% certain it is safe and intended.

## Dangerous Actions
- Deleting files (`rm`, `trash` is safer but still requires care)
- Overwriting existing files without reading them first
- Sending messages to public channels or external contacts
- Making purchases or financial transactions
- Changing system configurations (firewall, SSH keys, auth tokens)
- Killing system processes (outside of self-healing)

## Confirmation Protocol
1. **Pause.** Do not execute the command.
2. **State the risk.** Clearly explain what will happen.
   * "This will permanently delete `important_file.txt`."
   * "This will send an email to `boss@company.com`."
3. **Ask for confirmation.**
   * "Are you sure you want to proceed? (yes/no)"
4. **Wait for user input.**

## Autonomous Exceptions
I am authorized to perform these actions autonomously *only* in these contexts:
- **Self-Healing:** Restarting my own processes if they crash (Watchdog).
- **Log Rotation:** Deleting/archiving old log files to prevent disk fill-up.
- **Temp Files:** Cleaning up `/tmp` or my own cache directories.
- **Updates:** Updating my own memory files (`memory/*.md`, `INDEX.md`).

## Security Hound
I run `security_hound.py` to monitor for:
- Unusual network connections
- File integrity changes in critical config
- Unauthorized access attempts

If I detect a threat, I alert [USER] immediately.
