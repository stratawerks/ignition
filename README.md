# StrataOS Ignition

Setup wizard and management dashboard for StrataOS — the AI agent appliance by [StrataWerks](https://stratawerks.ai).

## Install

On your StrataOS unit, open the terminal and run:

```bash
curl -fsSL https://raw.githubusercontent.com/stratawerks/ignition/main/install.sh | bash
```

Then open the URL it prints in your browser.

## What It Does

Ignition is a two-screen setup wizard that gets your AI agent running in under 2 minutes:

1. **Connect your bot** — paste your Telegram bot token
2. **Choose your AI** — select a provider and API key
3. **Done** — your agent is live

After setup, Ignition becomes a persistent management dashboard:

- Live agent status
- Gateway restart
- Links to terminal and advanced settings
- License status
- Discover 1,200+ integrations

## Requirements

- StrataOS (FreeBSD + bhyve + NixOS)
- OpenClaw gateway
- Telegram account
- AI provider API key (OpenRouter recommended — free tier available)

---

© 2026 StrataWerks, LLC
