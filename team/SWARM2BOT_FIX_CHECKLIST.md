# Swarm2bot Fix Checklist — For Jarv

**Version:** 1.1 | **Updated:** 2026-04-25 18:54 UTC
**Purpose:** Criteria for Jarv to confirm Swarm2bot is fixed and ready to go live

---

## SWARM2BOT FIX CHECKLIST

### 1. $0.0000 Filter (CRITICAL)
- [ ] Any alert with entry price `$0.0000` is rejected at Swarm2bot source
- [ ] No alert passes to Kai or Telegram with this value
- [ ] Log entry created for each rejection

---

### 2. Market Validation
- [ ] Only active, unresolved Polymarket markets generate alerts
- [ ] Resolved markets (2024 election, etc.) are rejected
- [ ] Stock tickers ($AMAZON, $YELLEN) are rejected — not Polymarket contracts

---

### 3. Real Data Only
- [ ] Entry price must be > $0.0000 from actual on-chain data
- [ ] P&L must reflect actual wallet balance/position — no generated numbers
- [ ] Volume must be real — no repeating identical $25,695 amounts

---

### 4. Rate Limiting (REFINED 2026-04-25)
- [ ] **Same wallet + same market + within 5 min** → deduplicate (only send first)
- [ ] **Same wallet + different markets + within 5 min** → include BOTH (separate plays)
- [ ] No 30-second floods of identical content

**Logic:** If adding to/reducing an existing position on same market → dedup. If entirely separate plays on different markets → include both. We're not missing valid whale activity.

---

### 5. Routing — Kai First (CRITICAL)
- [ ] All alerts route through Kai's `alert_log.py` for dedup BEFORE going to Telegram
- [ ] Swarm2bot does NOT send direct to Telegram channels
- [ ] Alerts go: Swarm2bot → Kai → Telegram (via Kai's dedup)

---

### 6. Sports/eSports Differentiation
- [ ] Physical sports teams → Sports channel (requires anchor word: vs, game, score, playoff, nba, nfl, etc.)
- [ ] eSports teams/orgs (Cloud9, T1, G2, NAVI, Fnatic, Sentinels, etc.) → eSports channel (no anchor needed)
- [ ] Use the OMPA team databases: `sports_teams.md` and `esports_teams.md`

---

### 7. Link Validation
- [ ] Only real Polymarket URLs included in alerts
- [ ] No placeholder or broken links
- [ ] If no valid Polymarket URL exists → reject alert

---

## VERIFICATION TEST

Once fixed, run these through the system:

| Test | Expected Result |
|------|----------------|
| Send alert with `$0.0000` entry | Should NOT appear in channel |
| Send alert with `$AMAZON` ticker | Should NOT appear in channel |
| Send alert with resolved market | Should NOT appear in channel |
| Send 2 alerts same wallet, same market within 5 min | Only 1 should appear |
| Send 2 alerts same wallet, DIFFERENT markets within 5 min | Both should appear |
| Send real Polymarket market alert | Should appear with all fields populated |

**If all 7 checklist items pass and all 6 verification tests clean → Swarm2bot is fixed and ready to go live.**

---

## References

- Channel routing map: `org/teams/polyshark/routing/CHANNEL_ROUTING_MAP.md`
- Sports teams: `org/teams/polyshark/keywords/sports_teams.md`
- eSports teams: `org/teams/polyshark/keywords/esports_teams.md`
- Routing logic: `org/teams/polyshark/routing/SPORTS_ESPORTS_SPLIT_NOTE.md`
- Card spec: `org/teams/polyshark/card_format/CARD_SPEC.md`

---

*Built 2026-04-25 by KaiOC 🌊*