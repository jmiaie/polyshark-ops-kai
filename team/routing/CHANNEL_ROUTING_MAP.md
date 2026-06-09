# Polyshark Channel Routing Map
**Version:** 1.0 | **Updated:** 2026-04-25

---

## Alert Flow Overview

```
Big Win Detected (Polymarket)
        │
        ▼
   PRO Channel (Hub)
   ────────────────────── 3-min delay
   Alert Hub / Kai receives first
        │
        ▼
   1 Category Channel (highest confidence)
   ────────────────────── 10-min delay
   Sports | eSports | Crypto | Weather | Politics | World | Econ
        │
        ▼
   Free Teaser Channel
   ────────────────────── 15 min (curated) or 90 min (standard)
   Free tier sees FULL PRO card for curated picks
```

---

## Channel Map

| Channel Name | Channel ID | Tier | Purpose |
|-------------|-----------|------|---------|
| Polyshark Alert Hub | `-1003786930778` | PRO | All cards received here first. Kai monitors and forwards. |
| PolysharkPro | `-1003739747776` | PRO | Legacy Pro channel (cards also go here after 3-min delay) |
| Sports | `-1003948034686` | Category | Physical sports: NBA, NFL, NHL, MLB, Soccer, Tennis, F1 |
| eSports | `-1003700788085` | Category | Competitive video gaming: CS2, Valorant, LoL, Dota 2, etc. |
| Crypto | `-1003999731708` | Category | Bitcoin, Ethereum, DeFi, etc. |
| Weather | `-1003532326443` | Category | Weather events, storms, climate |
| World | `-1003927756388` | Category | Geopolitical, international, war |
| Politics | `-1003935178097` | Category | Elections, Trump/Biden, Congress |
| Econ | `-1003868008293` | Category | Fed, GDP, inflation, rates |
| Polyshark Free | `-1003999194095` | Free | Teaser channel — stripped card for free users |
| Polyshark Chat | `-1003860830659` | Chat | General discussion group |

---

## Confidence-Based Category Routing

Every alert is scored against keyword lists. The category with the **most keyword matches** wins.

### Scoring Rules

| Category | Keywords (sample) | Score = |
|----------|------------------|---------|
| **Sports** | nba, nfl, nhl, mlb, soccer, football, basketball, tennis, hockey, falcons, lakers, rockets, hurricanes, sabres, bruins... | Count of matching keywords |
| **eSports** | esports, cs2, csgo, valorant, league of legends, dota 2, rocket league, team liquid, cloud9, g2, t1, fnatic, faze, navi... | Count of matching keywords |
| **Crypto** | bitcoin, btc, ethereum, eth, crypto, solana, dogecoin, coin, nft... | Count of matching keywords |
| **Weather** | weather, rain, snow, storm, temperature, climate, flood, tornado, heat wave, cold wave, tropical, monsoon, blizzard, drought, cyclone, typhoon, **hurricane ** (space after = weather event only) | Count of matching keywords |
| **Politics** | election, trump, biden, congress, senate, vote, political, republican, democrat, parliament, president, governor, supreme court | Count of matching keywords |
| **World** | world, global, international, war, g7, g20, oil, geopolitical | Count of matching keywords |
| **Econ** | gdp, inflation, fed, rate, interest, recession, economy, unemployment | Count of matching keywords |

### Tie-Breaker
If two categories tie in score → send to the one that appears first alphabetically (`econ` before `sports`). This is deterministic, no randomness.

### Confirmed — confidence scoring is internal only (Jeff approved 2026-04-25)

- Router logs confidence score internally (for debugging/audit)
- When Kai forwards to public channels — confidence metadata is scrubbed
- Score is NEVER shown in public-facing cards unless Jeff explicitly approves a public feature in the future
- The score still determines routing decisions internally, but subscribers/free users never see it
- Jeff is keeping this controlled while the system is validated

### Confusion Fallback
If the router cannot determine the best category → send to the category with the highest score. If still ambiguous → log as `unknown` and send to PRO channel only.

### Log Evidence (Internal Only)
Router logs which category won and why:
```
Category forward (sports): Seattle Mariners vs. St. Louis Cardinals  [score=3]
Category forward (crypto): Bitcoin exceeds $100,000 by June 2026  [score=2]
```
Jeff can review these logs on demand. Scores do NOT appear in public Telegram cards.

---

## Timing Delays

| Send Stage | Delay | Notes |
|-----------|-------|-------|
| PRO / Hub send | 3 min after detection | Full PRO card |
| Category forward | 10 min after PRO send | Highest confidence category only |
| Curated → Free | 15 min after PRO send | ★ Curated picks only (ROI≥100% or profit≥$10K or streak≥5) |
| Standard → Free | 90 min after PRO send | Non-curated, free teaser card |

---

## Curated Picks System

**Goal:** Convert free tier users → paid subscriptions by giving them a taste of the real PRO card.

### Selection Criteria (any one qualifies)
- ROI ≥ 100%
- Profit ≥ $10,000
- Win streak ≥ 5 consecutive wins
- Top 3 by profit in scan session

### Max per session: 4

### What happens
- Curated picks go to the **free channel** after **15 minutes**
- They show the **FULL PRO card** (not the stripped free teaser)
- Non-curated picks show the standard free teaser after 90 minutes

---

## Batching Rules (Kai's alert_log.py)

| Cards at once | Action |
|-------------|--------|
| 1 card | Single message |
| 2–5 cards same channel | Combined multi-card message |
| 5+ cards | Split into chunks of max 5 |

Combined messages use format:
```
🃏 MULTI-CARD ALERT

Card 1: [content]
Card 2: [content]
...

💡 Cards can be added or removed from this message as needed.
```

**Inter-card spacing:** 30–60 seconds between Telegram API calls.

---

## OMPA Memory Structure

All alerts, faults, streaks, and rank changes are written to:

```
ompa_vault/brain/polyshark/
  alerts/          — Every whale win card
  faults/          — Every send failure, 429, exception
  whales/          — Per-wallet profiles
  streaks/         — Streak events (≥5 wins)
  rank-changes/    — Leaderboard rank movements
  markets/         — Resolved market records
```

Query with: `memory_search("whale wins this week")`

---

## Restart Procedures

### Router
```bash
kill $(cat /home/ubuntu/.openclaw/workspace/whaletrax_watcher.pid)
cd /home/ubuntu/.openclaw/workspace/repos/whaletrax && nohup python3 polyshark_router.py >> /tmp/polyshark_router.log 2>&1 & echo $! > /home/ubuntu/.openclaw/workspace/whaletrax_watcher.pid
```

### Webhook Server
```bash
kill $(cat /tmp/whale_hound_webhook.pid) 2>/dev/null
cd /home/ubuntu/.openclaw/workspace/repos/whaletrax && python3 run_webhook_server.py &
```

### Check Status
```bash
ps aux | grep polyshark_router | grep -v grep
tail -10 /tmp/polyshark_router.log
```

---

## Common Error Patterns & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `Chat not found` | Bot removed from channel | Re-invite bot to channel |
| `Too Many Requests` | Telegram rate limit | Router auto-retries with backoff; wait 30–60s |
| `Bad Gateway` | Polymarket API issue | Wait for next scan cycle |
| Queue buildup | 429s blocking sends | Restart router to clear backlog |
| `NameError: 'bw' not defined` | Bug in queue processing | Restart router (patched) |

---

## Key Files

| File | Purpose |
|------|---------|
| `polyshark_router.py` | Main router — scanning, queuing, sending |
| `polyshark_memory.py` | OMPA brain ingestion |
| `polyshark_subs.py` | Subscriber DB (SQLite) |
| `whale_tags.py` | High-priority whale tags |
| `polyshark_webhook.py` | Stripe/PayPal webhook handler |
| `run_webhook_server.py` | Webhook server on port 8080 |

---

*Polyshark Channel Routing Map — Built 2026-04-25*
*See also: `SPORTS_ESPORTS_SPLIT_NOTE.md` — routing maintenance guide*
