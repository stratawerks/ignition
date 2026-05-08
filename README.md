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

## Browser URLs

Once Ignition is running, use these addresses in your browser (replace `<ip>` with your unit's IP address):

| URL | What it does |
|---|---|
| `http://<ip>:18792` | Ignition setup wizard & dashboard |
| `http://<ip>:18789` | OpenClaw gateway dashboard |
| `http://<ip>:18790` | Terminal (command line access) |

## Requirements

- StrataOS unit on your local network
- Telegram account
- AI provider API key (OpenRouter recommended — free tier available at openrouter.ai)

---

© 2026 StrataWerks, LLC
