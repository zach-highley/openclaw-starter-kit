# Integration Guide — Connecting External Services

## Overview

OpenClaw can connect to external services via API keys stored securely in `~/.openclaw/.env`.

## Supported Integrations

### Stripe (Revenue Tracking)
```bash
echo 'STRIPE_SECRET_KEY=sk_live_xxx' >> ~/.openclaw/.env
echo 'STRIPE_PUBLIC_KEY=pk_live_xxx' >> ~/.openclaw/.env
```
- Track product sales, revenue, subscriptions
- Alert on new charges via heartbeat
- Requires: Stripe account → Developers → API Keys

### YouTube Data API v3
```bash
echo 'GOOGLE_API_KEY=xxx' >> ~/.openclaw/.env
```
- Channel stats (subscribers, views, videos)
- Recent video performance
- Requires: GCP Console → Credentials → API Key → Restrict to YouTube Data API v3

### X/Twitter API
```bash
cat >> ~/.openclaw/.env << 'XEOF'
X_BEARER_TOKEN=xxx
X_CONSUMER_KEY=xxx
X_CONSUMER_SECRET=xxx
X_ACCESS_TOKEN=xxx
X_ACCESS_TOKEN_SECRET=xxx
X_CLIENT_ID=xxx
X_CLIENT_SECRET=xxx
XEOF
```
- Post tweets, read mentions, monitor engagement
- Requires: developer.twitter.com → Create App → Generate all keys

### Gmail (Real-Time via PubSub)
- Uses `gog` CLI with OAuth (no API key needed)
- Real-time push notifications via Google Cloud PubSub
- See `docs/gmail-pubsub.md` for full setup

## Security Rules
1. **Never store keys in markdown, memory, or git-tracked files**
2. **Always use `~/.openclaw/.env`** (chmod 600, encrypted at rest via FileVault)
3. **Delete Telegram messages containing keys** immediately after storing
4. **Restrict API keys** to only the APIs they need (least privilege)
5. **Rotate keys** if compromise is suspected
