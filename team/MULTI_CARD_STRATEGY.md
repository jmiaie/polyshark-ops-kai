# Polyshark Multi-Card Strategy Protocol

**Version:** 1.0 | **Updated:** 2026-04-25 19:50 UTC
**From:** KaiOC 🌊 (for Jeff Milam)
**Status:** DRAFT — Pending Implementation

---

## Overview

When Swarm2bot detects whale activity, multiple alerts may trigger for the same wallet across same or different markets. This protocol defines how to separate, group, and route individual cards vs multi-card bundles.

---

## Core Principles

### 1. One Alert = One Card
Each qualifying alert generates its own card. Do NOT combine multiple alerts into a single card unless explicitly specified below.

### 2. Same Wallet + Same Market = Single Card (Dedup)
If the same wallet trades the same market multiple times within a short window, consolidate into one card showing:
- The most recent/largest position
- Total size across all trades
- Combined P&L if available

### 3. Same Wallet + Different Markets = Separate Cards
Each market gets its own card. These are sent individually but may be batched for efficiency.

### 4. Grouping Threshold
**5+ cards within 10 minutes** for the same wallet = group into a "digest" card sent as a single message with all plays listed.

---

## Card Types by Scenario

### Scenario A: Single Alert → Single Card
```
🎯 [MARKET QUESTION]  🏅

✅ $847 | ✅ +69% ROI
⬆️ BET UP on YES
...
```
**Rule:** Standard flow. One alert = one card.

---

### Scenario B: Same Wallet + Same Market (Within 5 min)
```
🎯 [MARKET QUESTION]  🏅
📦 CONSOLIDATED — 3 trades

✅ $2,541 | ✅ +89% ROI (combined)
⬆️ BET UP on YES
💵 Total Size: $3,963 (3 trades)
📊 75% WR (30d) | n=47
...
```
**Rule:** Dedup and consolidate. Show combined metrics.

---

### Scenario C: Same Wallet + Different Markets (Within 5 min)
```
🎯 [MARKET A]  🏅
✅ $847 | ✅ +69% ROI
⬆️ BET UP on YES
💵 Size: $1,321

──────────────────────────────────

🎯 [MARKET B]  🏅
✅ $423 | ✅ +41% ROI
⬆️ BET DOWN on NO
💵 Size: $1,033
...
```
**Rule:** Send as separate cards in sequence. Each card stands alone.

---

### Scenario D: Group Digest (5+ cards same wallet within 10 min)
When a wallet is very active, bundle into a digest:

```
🏅 HIGH-FREQ WINNING WHALE 🏅
📦 WHALE DIGEST — 7 plays today

1️⃣ 🎯 [MARKET A] — ✅ +$847 | ⬆️ UP
2️⃣ 🎯 [MARKET B] — ✅ +$423 | ⬇️ DOWN
3️⃣ 🎯 [MARKET C] — 💰 -$120 | ⬇️ DOWN
4️⃣ 🎯 [MARKET D] — ✅ +$891 | ⬆️ UP
5️⃣ 🎯 [MARKET E] — ✅ +$234 | ⬆️ UP
6️⃣ 🎯 [MARKET F] — ✅ +$567 | ⬆️ UP
7️⃣ 🎯 [MARKET G] — 💰 -$89 | ⬇️ DOWN

📊 Net: +$2,753 | 📈 71% WR | n=47
⏰ Last updated: 19:45 UTC
⛓️ [View all plays]
```

**Rule:** Use numbered list format. Show net summary. Link to full play history.

---

### Scenario E: Category Split (Sports + eSports)
When the same alert could route to multiple categories:

```
🎯 [MARKET QUESTION]  🏅

✅ $847 | ✅ +69% ROI
⬆️ BET UP on Cloud9
🏆 🟢 68+% lifetime WR | 🔥 5-win streak
⛓️ polymarket.com/event/...
🐋 0xa5ef1...cdef12
```
**Rule:** Route to BOTH Sports AND eSports if team appears in both databases. Tag with `📍Sports` or `📍eSports` prefix.

---

## Routing Logic

```
Alert Triggered
      ↓
[Check: Same wallet + same market within 5 min?]
      ↓ YES → CONSOLIDATE → Single Card
      ↓ NO
[Check: Same wallet + 5+ markets within 10 min?]
      ↓ YES → DIGEST → Group Card
      ↓ NO
[Check: Multiple category matches?]
      ↓ YES → SPLIT → Send to each category
      ↓ NO
[Check: Single alert?]
      ↓ YES → STANDARD → Single Card
```

---

## Rate Limiting Rules

| Scenario | Time Window | Action |
|----------|------------|--------|
| Same wallet + same market | 5 min | Dedup → consolidate |
| Same wallet + different markets | 5 min | Include both (separate cards) |
| Same wallet + 5+ markets | 10 min | Digest bundle |
| Different wallets + same market | Any | Always include separately |

---

## KaiOC Dedup Layer

KaiOC will maintain an in-memory dedup cache:
- `wallet_address + market_slug` as key
- Timestamp of last seen
- Decision: consolidate, digest, or forward

**Dedup cache cleared:** Every 15 minutes
**Log output:** `[KaiOC Dedup] wallet=0xa5ef... market=btc-100k action=consolidate`

---

## Implementation Checklist

- [ ] Swarm2bot implements dedup logic (same wallet + same market = consolidate)
- [ ] Swarm2bot implements digest bundle (5+ cards = group)
- [ ] Swarm2bot tags cards with `📍Sports` or `📍eSports` for category routing
- [ ] KaiOC dedup layer logs all decisions
- [ ] Card generator supports `consolidated=True` flag for Scenario B
- [ ] Card generator supports digest format for Scenario D

---

## Example Outputs

### Single Card (Standard)
```
🎯 Will BTC exceed $100K by June?  🏅

✅ $847 | ✅ +69% ROI
⬆️ BET UP on YES
🏆 🟢 68+% lifetime WR | 🔥 5-win streak
📊 75% WR (30d) | n=47
💰 Profit: +$847 | 💵 Size: $1,321
⛓️ polymarket.com/event/btc-100k-june-2026
🐋 0xa5ef1...cdef12
[Confidence: 87%]
```

### Consolidated Card (Same Wallet + Same Market)
```
🎯 Will BTC exceed $100K by June?  🏅
📦 CONSOLIDATED — 3 trades

✅ $2,541 | ✅ +89% ROI
⬆️ BET UP on YES
💵 Total Size: $3,963 (3 trades)
🏆 🟢 68+% lifetime WR | 🔥 5-win streak
📊 75% WR (30d) | n=47
⛓️ polymarket.com/event/btc-100k-june-2026
🐋 0xa5ef1...cdef12
```

### Digest Card (5+ Cards)
```
🏅 HIGH-FREQ WINNING WHALE 🏅
📦 WHALE DIGEST — 7 plays

1️⃣ BTC > $100K — ✅ +$847 | ⬆️ UP
2️⃣ ETH > $4K — ✅ +$423 | ⬆️ UP
3️⃣ SOL > $200 — 💰 -$120 | ⬇️ DOWN
4️⃣ ADA yes — ✅ +$891 | ⬆️ UP
5️⃣ MATIC no — ✅ +$234 | ⬇️ DOWN
6️⃣ AVAX yes — ✅ +$567 | ⬆️ UP
7️⃣ DOT no — 💰 -$89 | ⬇️ DOWN

📊 Net: +$2,753 | 71% WR | n=47
⏰ 19:45 UTC
```

---

*Protocol version 1.0 — Built 2026-04-25 by KaiOC 🌊*
*Pending: Jarv implementation + Tai verification*