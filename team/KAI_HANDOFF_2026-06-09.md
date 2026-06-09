# Polyshark & WhaleTrax — Full System Handoff
**Documented by:** Tai (via Jeff's fallback operator access)
**Date:** 2026-06-09
**Status:** Router PAUSED — Kai to resume operations

---

## 🏗️ What These Systems Are

**Polyshark** = whale alert router. Monitors top Polymarket wallets, fires Telegram cards when whales make big trades, routes to different channels based on category and confidence.

**WhaleTrax** = the underlying wallet-scanning and big-win-detection engine that powers Polyshark.

Two bots are running:
- `@oc_a3bot` (token `848480…f7q8`) — **Polyshark router** — sends cards to Alert Hub, PRO, Sports, World, TOP PLAYS
- `@oc_a7bot` (token `867819…2BBg`) — **WhaleTrax watcher** — sends whale win alerts to Kai's direct chat

---

## 📂 Where Everything Lives

### Core Code
| Path | What It Is |
|------|-----------|
| `/home/ubuntu/whaletrax-public/` | Main repo — router, scanner, wallet profiles, big win detector |
| `/home/ubuntu/polyshark-ops/` | Team knowledge base — keywords, routing maps, card specs |
| `/home/ubuntu/team-vault/org/teams/polyshark/` | Live ops docs — router status, project history, channel routing |

### GitHub Repos (Jeff's account)
| Repo | URL | Purpose |
|------|-----|---------|
| `whaletrax` (original) | `https://github.com/jmiaie/whaletrax` | Main dev repo |
| `whaletrax-kai` | `https://github.com/jmiaie/whaletrax-kai` | **Kai's fork** — same code, his to own |
| `polyshark-ops` (original) | `https://github.com/jmiaie/polyshark-ops` | Main team knowledge base |
| `polyshark-ops-kai` | `https://github.com/jmiaie/polyshark-ops-kai` | **Kai's fork** — routing maps, keywords, docs |

### Key Files In `whaletrax-public/`
| File | Purpose |
|------|---------|
| `polyshark_router.py` | Main daemon — scans wallets, queues cards, sends to Telegram |
| `src/big_win_detector.py` | Core detection logic — converts API positions → BigWin objects |
| `src/models.py` | BigWin data model |
| `src/polymarket_client.py` | Polymarket API client |
| `whaletrax_watcher.py` | Standalone whale win alert watcher (separate from router) |
| `whaletrax_daemon.py` | Wrapper that runs `whaletrax_watcher.py` every 15 min |
| `leaderboard_tracker.py` | ⚠️ **DEPRECATED** — was firing leaderboard rank-churn spam. Disabled. |
| `tai_fallback_runner.py` | Tai's fallback — runs if main router is down |

### Key Files In `polyshark-ops/`
| File | Purpose |
|------|---------|
| `keywords/sports_teams.md` | Sports team name keyword list for routing |
| `keywords/esports_teams.md` | Esports team name keyword list for routing |
| `routing/CHANNEL_ROUTING_MAP.md` | Channel IDs, delays, routing logic |
| `routing/SNIPER_BUCKETS.md` | Penny/Nickel/Dime/Quarter/Dollar sizing tiers |
| `routing/SNIPER_POSITION_SIZING.md` | Position sizing logic |
| `card_format/CARD_SPEC.md` | Card format specification |

---

## 📡 Telegram Channels
| Channel | ID | Role |
|---------|-----|------|
| Polyshark Alert Hub | `-1003786930778` | All cards land here first — Kai monitors and forwards |
| PolysharkPro | `-1003739747776` | PRO tier — immediate |
| Sports | `-1003948034686` | Sports category routing |
| World | `-1003927756388` | High-WR filter (≥90% lifetime or 30D) |
| TOP PLAYS | `-1003957370508` | Jeff's C1 whale + auto TOP plays |
| Free | `-1003999194095` | Free teaser tier |

**Bot:** `@oc_a3bot` — token `848480…f7q8`

---

## 🔴 Current Status

**Router is PAUSED** (kill switch `/tmp/polyshark_router_paused` removed, process killed at PID 227222).

To restart:
```bash
cd /home/ubuntu/whaletrax-public
python3 polyshark_router.py &
```

To check status:
```bash
tail -5 /tmp/polyshark_router.log
```

---

## ⚠️ Known Issues / Technical Debt

### 1. Leaderboard Tracker (leaderboard_tracker.py) — DISABLED
**Problem:** Was firing every ~15 min, spamming Alert Hub with rank-churn noise. State file was wiped, causing all top-20 wallets to appear as "new entries" every run.

**Current state:** Process killed, daemon not restarted. Script still exists at `/home/ubuntu/whaletrax-public/leaderboard_tracker.py`.

**Recommended fix:** Replace with a **daily digest** — one message/day at ~9am UTC with top 10 leaderboard snapshot (rank, PnL, volume, win rate). Contact Tai to build it.

### 2. Router Queue Backup
**Queue file:** `/tmp/polyshark_router_queue.json` — **14,855 lines** (196 items). Old items from before bug fixes are still in there.

**To clear the queue** (do this after restarting):
```python
import json
json.dump([], open('/tmp/polyshark_router_queue.json', 'w'))
json.dump({'seen_keys': [], 'total_sent': 0, 'curated_sent': 0}, open('/tmp/polyshark_router_state.json', 'w'))
```

### 3. Open Positions Architecture (Fixed Jun 7)
The router was refactored to use **open positions** as the primary detection signal (not closed positions). This means cards fire when whales enter positions, not when they close them — more actionable.

- `big_win_detector.py`: `_open_position_to_big_win()` is primary, `_closed_position_to_big_win()` is stats-only
- Entry price derived as `initialValue / size` (NOT `avgPrice` which is current price)
- ROI uses `cashPnl / initialValue * 100`
- `profit_usdc = cashPnl` (actual P&L, not cost basis)

### 4. CLOB Price Fetching (Fixed Jun 7)
Polymarket changed their CLOB API — `outcomePrices` is now `null`, prices are in `tokens[i]['price']`. Fixed in `src/big_win_detector.py`.

### 5. Timezone Handling (Fixed Jun 7)
Naive datetime vs timezone-aware comparison was raising `TypeError` silently, causing the resolved-market filter to fail. Fixed by normalizing both sides to UTC.

### 6. WhaleTrax Daemon (whaletrax_daemon.py)
Runs `whaletrax_watcher.py` every 15 minutes. **Currently not running.** Kai can restart with:
```bash
cd /home/ubuntu/whaletrax-public
python3 whaletrax_daemon.py &
```

---

## 📋 Everything Tai Did (Process & History)

### What Was Fixed (Jun 5–9, 2026)

**13 bugs fixed in the router:**

1. ✅ `_fetch_current_price` returning 0 — Polymarket CLOB API changed, prices now in `tokens[i]['price']`
2. ✅ `current_price = 0` for team-name markets — `_open_position_to_big_win` now uses `curPrice` from position data as primary
3. ✅ `NameError: name 'current_price' is not defined` in `format_card`
4. ✅ Resolved markets slipping through — timezone-aware datetime comparison
5. ✅ CLOB pre-enrichment not set at queue time — now enriches before appending
6. ✅ `profit_usdc` = cost basis instead of actual P&L — now uses `cashPnl`
7. ✅ ROI sign wrong on negative positions — both `profit_usdc` and `roi_pct` now from scan-computed values
8. ✅ `curPrice` vs market CLOB price confusion — `curPrice` is authoritative for position value
9. ✅ `yes_price`/`no_price` not stored on queue items — now stored at top level
10. ✅ `O:` date fallback to `queued_at` when `timestamp` is 0
11. ✅ `C:` date plain text (no markdown link)
12. ✅ `bw.closed` added; `is_resolved` checks both `closed` and `accepting_orders`
13. ✅ QC gate: math/stats validation before every card send

**Architecture changes:**
- Open positions → primary detection signal (cards fire on entry, not close)
- Sports category routing enabled (was dead code — only logged "deferred")
- Esports → Sports channel mapping (bot not in esports channel)
- TOP PLAYS channel with Jeff's C1 whale whitelist
- World channel with ≥90% WR gate
- PRO channel delay → 0 (immediate)
- Free channel with 6hr delay

### What Was Documented
- `ROUTER_COMPLETE_STATUS_2026-06-07.md` — all 13 bugs with root causes and fixes
- `PROJECT_HISTORY_2026-06-07.md` — day-by-day what was done and why
- `CHECKPOINT_2026-06-08.md` — midnight checkpoint after major fixes
- `SNIPER_BUCKETS.md` — penny/nickel/dime/quarter/dollar tier design
- `SNIPER_POSITION_SIZING.md` — position sizing logic
- `REPO_RECONCILIATION.md` — repo structure and what lives where

---

## 🔑 Key Technical Facts

### Polymarket API Field Meanings
```
size = tokens held (not USD value)
avgPrice     = current market price (NOT entry price!)
initialValue = cost basis / entry cost (USD)
currentValue = mark-to-market value (USD)
cashPnl      = unrealized P&L (USD) — use this for profit
percentPnl   = % return
curPrice     = CLOB current price for whale's outcome
redeemable   = resolved flag
endDate      = market expiry date
conditionId  = market ID for CLOB lookup
```

### Entry Price Formula
```
entry_price = initialValue / size
```
NOT `avgPrice` — that's the current market price.

### ROI Formula for Open Positions
```
roi_pct = (cashPnl / initialValue) * 100
```

### Deduplication Key
```
seen_key = f"{market_id}_{wallet}"
```

### Router Poll Interval
~2 minutes (hardcoded `time.sleep(120)` in `run()` loop)

### Queue File
`/tmp/polyshark_router_queue.json` — array of queue items

### State File
`/tmp/polyshark_router_state.json` — `seen_keys` array + `total_sent` + `curated_sent`

### Pause / Resume
```bash
# Pause (creates kill switch file)
touch /tmp/polyshark_router_paused

# Resume (removes kill switch)
rm /tmp/polyshark_router_paused
```

---

## 🗂️ Repo Structure Reference

```
whaletrax-public/
├── polyshark_router.py       ← Router daemon (primary)
├── whaletrax_watcher.py      ← Whale win alerts (standalone)
├── whaletrax_daemon.py       ← Wrapper for whaletrax_watcher.py
├── leaderboard_tracker.py    ← ⚠️ DEPRECATED — disable before using
├── tai_fallback_runner.py    ← Tai's fallback (cron-based, no bot token needed)
├── src/
│   ├── big_win_detector.py   ← Core detection
│   ├── models.py             ← BigWin model
│   ├── polymarket_client.py ← API client
│   ├── config.py             ← Thresholds
│   ├── market_enricher.py   ← CLOB enrichment
│   └── wallet_scanner.py     ← Wallet position scanning
├── alerts/
│   └── polyshark_alert.py    ← Alert format helpers
└── wallet_tracker.db         ← SQLite — wallet profiles, stats

polyshark-ops/
├── keywords/
│   ├── sports_teams.md
│   └── esports_teams.md
├── routing/
│   ├── CHANNEL_ROUTING_MAP.md
│   ├── SNIPER_BUCKETS.md
│   ├── SNIPER_POSITION_SIZING.md
│   └── REPO_RECONCILIATION.md
├── card_format/
│   └── CARD_SPEC.md
└── operations/
    ├── ONBOARDING.md
    ├── SUBSCRIBER_MANAGEMENT.md
    └── WEBHOOK_SETUP.md
```

---

## 📞 For Kai — What To Do Next

1. **Clone your repos:**
   ```bash
   git clone https://github.com/jmiaie/whaletrax-kai.git
   git clone https://github.com/jmiaie/polyshark-ops-kai.git
   ```

2. **Clear the queue** (after restart):
   ```python
   import json
   json.dump([], open('/tmp/polyshark_router_queue.json', 'w'))
   json.dump({'seen_keys': [], 'total_sent': 0, 'curated_sent': 0}, open('/tmp/polyshark_router_state.json', 'w'))
   ```

3. **Restart the router:**
   ```bash
   cd ~/whaletrax-kai  # or your clone
   python3 polyshark_router.py &
   ```

4. **Restart the WhaleTrax daemon** (optional, for whale win alerts):
   ```bash
   python3 whaletrax_daemon.py &
   ```

5. **Decide on leaderboard_tracker.py** — it's disabled but the code is still there. Want to replace with a daily digest? Tai can build it.

6. **Check Alert Hub** — cards should start flowing again once router is running.

---

*Document created by Tai (fallback operator) on 2026-06-09. Last updated: 2026-06-09 23:34 UTC.*
