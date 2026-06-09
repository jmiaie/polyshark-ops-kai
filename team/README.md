# Polyshark Ops — Team Knowledge Base

Central repository for the Polyshark whale alert team. All agents (Jarv, Kai, Tai) and Jeff pull from here.

## Structure

```
polyshark-ops/
├── keywords/          — Sports and esports team name databases
│   ├── sports_teams.md
│   └── esports_teams.md
├── routing/           — Channel routing maps and split logic
│   ├── CHANNEL_ROUTING_MAP.md
│   └── SPORTS_ESPORTS_SPLIT_NOTE.md
├── card_format/       — Card format specifications
│   └── CARD_SPEC.md
├── operations/        — Subscriber management, webhooks, onboarding
│   ├── ONBOARDING.md
│   ├── SUBSCRIBER_MANAGEMENT.md
│   └── WEBHOOK_SETUP.md
├── whales/            — Per-wallet profile files (auto-generated)
└── high_priority_whales.json
```

## Agents

- **Jarv** (Heavy) — Router logic, OMPA writes, strategic decisions
- **Kai** (Lite) — Monitors Alert Hub, forwards to category channels
- **Tai** (Lite) — Router control, card formatting, OMPA builds
- **Jeff** — Final authority on all routing and business decisions

## Rules

1. All agents have read access to `keywords/`, `routing/`, `card_format/`, `operations/`
2. Whale profiles are auto-written — do not manually edit
3. All routing changes require Jeff's approval
4. Confidence scores are internal only — never in public cards

## Staying in Sync

Pull latest before each session:
```bash
git pull origin main
```

Push changes after edits:
```bash
git add . && git commit -m 'description' && git push
```

## GitHub
https://github.com/jmiaie/polyshark-ops

*Built 2026-04-25*