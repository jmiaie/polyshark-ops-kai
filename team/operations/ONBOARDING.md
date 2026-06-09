# New Agent Onboarding — Polyshark

**For:** Jarv, Kai, and Tai

---

## What is Polyshark?

Polyshark is a paid subscription service that routes Polymarket whale alert cards to tiered Telegram channels. Subscribers pay for early access to high-conviction trades by successful Polymarket whales.

**Revenue model:** Pro $50/mo, Category $30/mo, Free delayed tier
**Stack:** Python router, SQLite DB, OMPA memory, Telegram bots

---

## System Overview

```
Polymarket API (whale feed)
        ↓
polyshark_router.py (scans every ~2 min)
        ↓
[PRO/HUB channel] — immediate
        ↓
[Category channel] — 7 min delay (eSports, Sports, Crypto, Weather, etc.)
        ↓
[Free channel] — 30 min delay (teaser cards)
```

---

## Key Files

| File | Purpose |
|------|---------|
| `polyshark_router.py` | Main router: scanning, queuing, sending |
| `wallet_profiles.py` | Per-wallet cumulative stats (win rates, streaks) |
| `polyshark_subs.py` | Subscriber DB and tier management |
| `polyshark_webhook.py` | Stripe + PayPal webhook handler |
| `polyshark_memory.py` | OMPA brain ingestion |
| `whale_tags.json` | High-priority whale badges |

---

## Key Directories

| Path | Purpose |
|------|---------|
| `ompa_vault/teams/polyshark/` | Team knowledge vault (this vault) |
| `ompa_vault/brain/polyshark/whales/` | Per-wallet profile files |
| `ompa_vault/teams/polyshark/keywords/` | Sports + esports team databases |
| `ompa_vault/teams/polyshark/routing/` | Routing map + split guide |

---

## How to Check System Health

### Is router running?
```bash
ps aux | grep polyshark_router | grep -v grep
```

### Recent router log
```bash
tail -20 /tmp/polyshark_router.log
```

### Recent faults
```bash
cat /tmp/polyshark_faults.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'{len(d)} faults'); [print(f'  {f[\"type\"]}: {f[\"detail\"][:60]}') for f in d[-5:]]"
```

### Wallet profiles
```bash
cat /tmp/wallet_profiles.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'{len(d)} wallets tracked')"
```

---

## Common Tasks

### Restart the router
```bash
kill $(cat /home/ubuntu/.openclaw/workspace/whaletrax_watcher.pid) 2>/dev/null
cd /home/ubuntu/.openclaw/workspace/repos/whaletrax
nohup python3 polyshark_router.py >> /tmp/polyshark_router.log 2>&1 &
echo $! > /home/ubuntu/.openclaw/workspace/whaletrax_watcher.pid
sleep 5
tail -5 /tmp/polyshark_router.log
```

### Check a whale's win rate
```bash
cat /tmp/wallet_profiles.json | python3 -c "
import json,sys
d=json.load(sys.stdin)
w = input('wallet: ').strip().lower()
if w in d:
    p=d[w]
    print(f'LT WR: {p[\"win_rate\"]}% | 30d: {p[\"win_rate_30d\"]}% | 90d: {p[\"win_rate_90d\"]}% | 6m: {p[\"win_rate_6m\"]}%')
    print(f'Positions: {p[\"total_positions\"]} | Streak: {p[\"current_streak\"]}')
else:
    print('Not found')
"
```

### Add a new whale to watchlist
Edit `whale_tags.json` — add wallet address and badge label.

### Update keyword lists
Edit `SPORTS_KW` and `ESPORTS_KW` directly in `polyshark_router.py`. After save, restart router.

---

## Routing Rules

- **Sports** requires a context anchor (e.g., `vs`, `game`, `score`) alongside the team name
- **eSports** requires no anchor — team/org names are inherently gaming context
- Categories are scored simultaneously — highest score wins
- **Confidence scores are internal only** — never shown in public cards
- All changes to routing require Jeff's approval

---

## Escalation

If something is broken and you can't fix it:
1. Document what broke, when, and what you tried
2. Ping Jeff via Telegram with the details
3. If the router is stuck in a loop, `kill` the PID and restart

---

*Built 2026-04-25*