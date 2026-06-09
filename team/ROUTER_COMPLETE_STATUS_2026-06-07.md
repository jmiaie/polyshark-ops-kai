# Polyshark Router — Complete Status& Rebuild Guide
**Last updated:** 2026-06-07 21:47 UTC
**Router PID:** 186691

## What Is This System?

The Polyshark Router is a daemon that monitors whale positions on Polymarket and sends Telegram alerts when whales make big trades. It runs continuously, polling open positions from the Polymarket leaderboard every ~2 minutes.

**Core flow:**
1. Scan open positions from top whale wallets
2. Filter to positions >$100K with entry <95¢
3. Check market is still open (not resolved)
4. Compute ROI and P&L from `cashPnl` and `curPrice`
5. Enrich with live CLOB prices
6. Queue cards → send to Telegram channels (PRO, Sports, Alert Hub, World)

## Current State (June 7 2026 — All 13 Bugs Fixed)

### Router Status
- PID: 186691 (running)
- Repo: /home/ubuntu/whaletrax-public
- Last commit: 12bc601 (Add no_price to bw_from_item from _clob_enriched)
- Queue: /tmp/polyshark_router_queue.json
- State: /tmp/polyshark_router_state.json
- Log: /tmp/polyshark_router.log
- Poll interval: ~2 minutes

### Channels Configured
| Channel | ID | Delay |
|---------|----|-------|
| Alert Hub | -1003786930778 | Immediate |
| PRO | -1003739747776 | 0 (immediate) |
| Sports | -1003948034686 | Category routing |
| World | -1003927756388 | WR ≥ 90% gate |
| TOP PLAYS | -1003957370508 | Auto |

### Bot
`@oc_a3bot` — token: `8484803155:AAHa2B2zrIq_GavdX6FGWcFkAPiySQef7q8`

## All 13 Bugs Found & Fixed (June 7 2026)

### Bug 1: `_fetch_current_price` returning 0 for all markets
**Symptom:** `current_price = 0` on all queue items
**Root cause:** Polymarket CLOB API changed — `outcomePrices` is now `null`, prices are in `tokens[i]['price']`
**Fix:** Read `tokens[i]['price']` as primary source, `outcomePrices` as fallback

### Bug 2: `current_price` = 0 for team-name markets
**Symptom:** Chicago Sky vs Toronto Tempo shows `current_price=0`
**Root cause:** `_fetch_current_price` checks `outcome == "yes"` which fails for team names
**Fix:** `_open_position_to_big_win` uses `curPrice` from position data (authoritative) as primary

### Bug 3: `NameError: name 'current_price' is not defined`
**Symptom:** Router crashes in `format_card`
**Root cause:** Used `current_price` variable without `getattr(bw, ...)`
**Fix:** `getattr(bw, 'current_price', 0)`

### Bug 4: Resolved markets slipping through
**Symptom:** Tampa Bay Rays card fired with `endDate=2026-05-16` (RESOLVED)
**Root cause:** Naive datetime vs timezone-aware comparison raises `TypeError` silently caught
**Fix:** Normalize both to timezone-aware UTC before comparing

### Bug 5: CLOB pre-enrichment not set at queue time
**Symptom:** "Now:" line shows stale or wrong prices
**Root cause:** `bw.yes_price` only set during `process_queue`, not during `queue.append`
**Fix:** Enrich with CLOB data before appending to queue in `run()`

### Bug 6: `profit_usdc` = cost basis instead of actual P&L
**Symptom:** Rock card showed +$200K when actual loss was -$193,800
**Root cause:** `_open_position_to_big_win` set `profit_usdc = cost` (initialValue)
**Fix:** `profit_usdc = cashPnl` (actual P&L from API)

### Bug 7: ROI sign wrong (negative positions showing positive)
**Symptom:** Rock card showed +100% when actual was -96.9%
**Root cause:** `profit_usdc = cost` (always positive) overrode correct `roi_pct`
**Fix:** Both `profit_usdc` and `roi_pct` now come from scan-computed values

### Bug 8: `curPrice` for YES outcomes vs market price confusion
**Symptom:** "Now:" line showed wrong number for team-name markets
**Root cause:** `curPrice` from position data IS the whale's outcome price — but was being confused with market CLOB price
**Fix:** `curPrice` is authoritative for position value; CLOB only used as fallback

### Bug 9: `format_card` recomputed roi_pct/profit_usdc from entry price
**Symptom:** All open position cards showed wrong ROI/profit (recomputed from `1/entry_px-1`)
**Root cause:** Lines 444-447 in `format_card` overwrote scan-computed values with `roi_pct = (1/entry_px-1)*100`
**Fix:** Only recompute for closed positions; use scan-computed values for open

### Bug 10: Router `seen` set blocked re-queuing
**Symptom:** After clearing queue, no new cards appeared
**Root cause:** `seen_keys` in state file persisted across queue clears
**Fix:** Clear both `/tmp/polyshark_router_queue.json` AND `/tmp/polyshark_router_state.json`

### Bug 11: Router bytecode stale despite `__pycache__` clearing
**Symptom:** Code changes not taking effect after clearing cache
**Root cause:** Python imports bytecode at process start; clearing cache mid-run doesn't help
**Fix:** Kill and restart router process after each code change

### Bug 12: "Now:" line used `bw.current_price` instead of enriched price
**Symptom:** "Now:" showed scan-time value instead of fresher CLOB data
**Fix:** `now_price = getattr(bw, 'yes_price', 0) or getattr(bw, 'current_price', 0)`

### Bug 13: "Now:" line showed YES price for NO bets
**Symptom:** Knicks NBA Finals NO bet showed "Now: 78.1¢" (YES price, wrong)
**Root cause:** `format_card` used `yes_price` for all bets, ignoring whale's actual outcome side
**Fix:** YES bet → show `yes_price`. NO bet → show `no_price`

## Key Data Field Reference

| Field | Source | Meaning |
|-------|--------|---------|
| `avgPrice` (API) | Position data | Whale's entry price (e.g., 0.50 = 50¢ entry) |
| `curPrice` (API) | Position data | Whale's outcome's CURRENT price (NOT market price) |
| `initialValue` (API) | Position data | Cost basis = `size × avgPrice` |
| `currentValue` (API) | Position data | Mark-to-market value = `size × curPrice` |
| `cashPnl` (API) | Position data | **ACTUAL unrealized P&L** = `currentValue - initialValue` |
| `percentPnl` (API) | Position data | % return = `(cashPnl / initialValue) × 100` |
| `outcome` (API) | Position data | Whale's chosen outcome ("Yes", "Knicks", "Over", etc.) |
| `redeemable` (API) | Position data | `True` = market resolved |
| `yes_price` (CLOB) | `market_enricher` | Current YES outcome price from CLOB |
| `no_price` (CLOB) | `market_enricher` | Current NO outcome price from CLOB |

**Critical insight:** For YES/NO binary markets:
- Whale bet YES → `curPrice` = YES price (whale's outcome)
- Whale bet NO → `curPrice` = NO price (whale's outcome)

For team markets:
- Whale bet "Chicago Sky" → `curPrice` = Chicago Sky price (their team)

**The `curPrice` field is always the whale's OWN outcome price, not the opposite.**

## Lessons Learned

### 1. The Polymarket API is not what you think
- `avgPrice` = entry price, NOT current price
- `curPrice` = whale's outcome price, NOT market price
- `initialValue` = cost basis, NOT profit
- `cashPnl` = actual P&L (use this)
- `outcomePrices` in CLOB is always `null` — prices are in `tokens[i]['price']`

### 2. Team-name markets break the "Yes/No" assumption
- Outcomes are "Chicago Sky", "Toronto Tempo" — not "Yes/No"
- `_fetch_current_price` fails because `outcome == "yes"` never matches
- Always use `curPrice` from position data for team markets

### 3. Python bytecode caching is a silent trap
- `__pycache__` cleared ≠ running code updated
- Python imports at process start and caches the bytecode
- Always kill and restart the process after code changes

### 4. The `seen` set is more persistent than the queue
- Clearing the queue file doesn't clear `seen_keys`
- Every restart needs `rm /tmp/polyshark_router_state.json` too

### 5. `format_card` was silently overwriting correct values
- The override for open positions (`roi_pct = 1/entry_px-1`) was destroying the correct computed values
- This was the most damaging bug — made every card show wrong numbers

### 6. CLOB enrichment happens twice and can conflict
- Once in `run()` before queuing (`validate_and_enrich`)
- Once in `process_queue` when sending
- If `current_price` gets overwritten with wrong CLOB data, the "Now:" line breaks

### 7. `profit_usdc` must come from `cashPnl`, not cost basis
- `profit_usdc = cost` (initialValue) is always wrong for open positions
- `cashPnl` is the actual unrealized P&L — positive for gains, negative for losses

### 8. For NO bets, show the NO price in "Now:", not YES
- The whale chose NO, their position is worth the NO price
- Showing the YES price is completely backwards and confusing

## Efficiency Tricks & Tips

### Restart the router cleanly (always do this after code changes)
```bash
kill <PID> 2>/dev/null
sleep 2
find /home/ubuntu/whaletrax-public -name "*.pyc" -delete
find /home/ubuntu/whaletrax-public -name "__pycache__" -exec rm -rf {} + 2>/dev/null
echo "[]" > /tmp/polyshark_router_queue.json
rm /tmp/polyshark_router_state.json 2>/dev/null
cd /home/ubuntu/whaletrax-public && nohup python3 polyshark_router.py > /tmp/polyshark_router.log 2>&1 &
echo "PID: $!"
```

### Test a card render locally (without waiting for router cycle)
```python
import sys, json
sys.path.insert(0, '/home/ubuntu/whaletrax-public')
from polyshark_router import format_card, CHANNELS, bw_from_item

q = json.load(open('/tmp/polyshark_router_queue.json'))
for item in q:
    if 'Market Name' in item.get('question',''):
        bw = bw_from_item(item)
        if bw:
            card = format_card(bw, 'pro', CHANNELS['pro'])
            print(card)
        break
```

### Check raw position data quickly
```python
from src import polymarket_client as pm
positions = pm.get_user_positions('0xWALLET')
for p in positions:
    if 'Market' in p.get('title',''):
        print(f"outcome={p.get('outcome')} entry={float(p.get('avgPrice'))*100:.1f}¢ cur={float(p.get('curPrice'))*100:.1f}¢ cashPnl={p.get('cashPnl')}")
```

### Check CLOB prices for a market
```python
import json, urllib.request
mid = 'MARKET_ID'
url = f'https://clob.polymarket.com/markets/{mid}'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=5) as resp:
    data = json.loads(resp.read())
for t in data.get('tokens', []):
    print(f"  {t.get('outcome')}: price={t.get('price')}")
```

### Clear bytecode and restart in one command
```bash
kill $(pgrep -f polyshark_router) 2>/dev/null; sleep 2; find /home/ubuntu/whaletrax-public -name "*.pyc" -delete; find /home/ubuntu/whaletrax-public -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null; rm /tmp/polyshark_router_queue.json /tmp/polyshark_router_state.json 2>/dev/null; cd /home/ubuntu/whaletrax-public && nohup python3 polyshark_router.py > /tmp/polyshark_router.log 2>&1 & echo "PID: $!"
```

## Complete Rebuild Walkthrough

### Prerequisites
- Python 3.10+
- Access to Polymarket API
- Telegram bot token (`@oc_a3bot`)
- GitHub repos: `whaletrax-public`, `polyshark-ops`, `team-vault`

### Step 1: Clone Repos
```bash
git clone https://github.com/jmiaie/whaletrax.git /home/ubuntu/whaletrax-public
git clone https://github.com/jmiaie/polyshark-ops.git /home/ubuntu/polyshark-ops
git clone https://github.com/jmiaie/micap-ai-team-vault.git /home/ubuntu/team-vault
```

### Step 2: Directory Structure
```
whaletrax-public/
├── polyshark_router.py     # Main daemon
├── src/
│   ├── big_win_detector.py # Open position scanning + conversion
│   ├── models.py           # BigWin dataclass
│   ├── polymarket_client.py # Polymarket API wrapper
│   ├── market_enricher.py   # CLOB price enrichment
│   └── config.py           # Settings
├── wallet_profiles.py      # Wallet stats
├── polyshark_memory.py     # OMPA brain ingestion
└── queue.json             # Runtime queue (/tmp/polyshark_router_queue.json)
```

### Step 3: Key Configuration
```python
# In src/config.py
BIG_WIN_MIN_TRADE_SIZE_USDC = 100    # Minimum position size
BIG_WIN_MIN_ROI_PCT = 50             # Minimum ROI to qualify
LEADERBOARD_TOP_N = 20               # How many leaderboard wallets to scan
POLL_TOP_N = 20                      # How many wallets per scan run

# In polyshark_router.py
PRO_DELAY = 0           # Fire immediately
FREE_DELAY = 21600      # 6 hour delay for free channel
BOT_TOKEN = '8484803155:AAHa2B2zrIq_GavdX6FGWcFkAPiySQef7q8'
CHANNELS = {
    'alert': -1003786930778,   # Alert Hub
    'pro': -1003739747776,      # PRO
    'sports': -1003948034686,   # Sports
    'world': -1003927756388,    # World
    'top_plays': -1003957370508 # TOP PLAYS
}
```

### Step 4: Core Architecture

**Primary detection flow:**
```
scan_open_positions()
  → _leaderboard_wallet_to_open_positions()
    → pm.get_user_positions(wallet)
    → _open_position_to_big_win()     # Filter + convert
    → _fetch_current_price()           # CLOB fallback
  → big_wins list

run() loop:
  → scan_open_positions()             # Get fresh BigWins
  → filter seen (state['seen_keys'])
  → validate_and_enrich()              # CLOB validation
  → CLOB pre-enrichment before queue
  → queue.append()
  → seen.add(key)
  → save_state()

process_queue():
  → For each item: delay check → bw_from_item() → format_card() → send_telegram()
```

**BigWin data flow:**
```
Polymarket API → _open_position_to_big_win() → BigWin object
  avg_price = initialValue/size (entry)
  current_price = curPrice (whale's outcome)
  roi_pct = (curPrice - avgPrice)/avgPrice
  profit_usdc = cashPnl (actual P&L)
  ↓
validate_and_enrich() (CLOB enrichment)
  ↓
queue.append()
  ↓
bw_from_item() (restore from queue)
  ↓
format_card() → Telegram
```

### Step 5: Start the Router
```bash
cd /home/ubuntu/whaletrax-public
python3 polyshark_router.py &
# Check logs
tail -f /tmp/polyshark_router.log
# Check if running
ps aux | grep polyshark_router
```

### Step 6: Verify It's Working
```bash
cat /tmp/polyshark_router.log
# Should see: "Open positions scanned: N"
python3 -c "import json; q=json.load(open('/tmp/polyshark_router_queue.json')); print(f'Queue: {len(q)}')"
```

### Step 7: Test a Card Send (Manual)
```python
import sys
sys.path.insert(0, '/home/ubuntu/whaletrax-public')
from polyshark_router import format_card, CHANNELS, bw_from_item

q = json.load(open('/tmp/polyshark_router_queue.json'))
for item in q:
    bw = bw_from_item(item)
    print(format_card(bw, 'pro', CHANNELS['pro']))
```

## Git History (June 7 2026 Commits)

```
whaletrax-public:
12bc601 Add no_price to bw_from_item from _clob_enriched
f2be57a Fix Now: line for NO bets — show NO price not YES price
ee9b85f Fix format_card: use scan-computed roi