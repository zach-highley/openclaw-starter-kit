# Security Audit Template 🔒

Run this audit periodically (monthly recommended) to verify your OpenClaw setup is secure.

## Checklist

### 1. Secrets Scan
```bash
# Search for hardcoded secrets in your workspace
grep -rn "api_key\|apiKey\|secret\|Bearer \|sk-\|token=" \
  ~/your-workspace/scripts/ ~/your-workspace/docs/ ~/your-workspace/state/ \
  --include="*.py" --include="*.sh" --include="*.json" \
  | grep -v "placeholder\|example\|REDACTED"
```
✅ **Pass:** No hardcoded API keys or tokens. All secrets in environment variables.

### 2. Environment File Permissions
```bash
ls -la ~/.zshenv ~/.bashrc ~/.env 2>/dev/null
# Should be 600 (owner read/write only) if they contain secrets
chmod 600 ~/.zshenv
```

### 3. Git History
```bash
cd ~/your-workspace
git log --diff-filter=A --name-only --pretty=format: -20 | sort -u | grep -iE "key|secret|token|password|credential|\.env"
```
✅ **Pass:** No secret files ever committed.

### 4. OpenClaw Config
```bash
grep -n "api_key\|apiKey\|token\|secret\|password" ~/.openclaw/config.yaml | grep -v "#\|null"
```
✅ **Pass:** Config references env vars, not raw secrets.

### 5. Network Security
```bash
# Check firewall
/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
# Check open ports
lsof -i -P -n | grep LISTEN
```
✅ **Pass:** Firewall enabled, no unexpected listeners.

### 6. SSH Keys
```bash
ls -la ~/.ssh/
# Private keys should be 600, public keys 644
```

### 7. Public Repository Check
```bash
# Scan for personal info in public repos
grep -rn "your-name\|your-email\|your-phone\|SSN\|password" ~/public-repo/ \
  --include="*.md" --include="*.yaml" --include="*.json"
```
✅ **Pass:** No personal information in public repos.

### 8. Dashboard Exposure
```bash
# Check if private endpoints are accessible
curl -s -o /dev/null -w "%{http_code}" https://your-dashboard.com/api/private
# Should return 401 or 404
```

### 9. Script Permissions
```bash
# Security-sensitive scripts should be 700 (owner only)
# Example patterns (customize to your naming):
chmod 700 ~/your-workspace/scripts/*secure*.sh
chmod 700 ~/your-workspace/scripts/*passphrase*.py
```

### 10. LaunchD Agents
```bash
ls ~/Library/LaunchAgents/
# Verify all agents are expected
```

## Scoring

| Score | Meaning |
|-------|---------|
| 10/10 | Perfect — all checks pass, proactive monitoring in place |
| 8-9/10 | Good — minor issues fixed during audit |
| 6-7/10 | Needs work — permission or config issues found |
| <6/10 | Urgent — secrets exposed or critical misconfigurations |

## Automation

Add security checks to your heartbeat (every 4 hours):
```python
# In your auto-doctor or health check script
def security_quick_check():
    # Check .zshenv permissions haven't regressed
    # Verify no new LISTEN ports
    # Scan recent git commits for secrets
    # Check firewall still enabled
    pass
```

---

*Template. Customize paths and URLs for your setup.*
