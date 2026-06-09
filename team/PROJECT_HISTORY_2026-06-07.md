# Project History — June 7, 2026

## What We Did Today

### Root Cause Fixes: `_fetch_current_price` + `curPrice` + Timezone Handling

#### Bug 1: `_fetch_current_price` returning 0 for all markets
**Root cause:** Polymarket CLOB API changed — `outcomePrices` field is now `null`, but prices are in `tokens[i]['price']`. The function was looking for the wrong field.

**Fix:** Updated `_fetch_current_price` in `src/big_win_detector.py` to read `tokens[i]['price']` as primary source:
```python
tokens = data.get("tokens", [])
for token in tokens:
    outcome = str(token.get("outcome", "")).lower()
    if outcome == "yes":
        price = token.get("price")
        if price is not None:
            return float(price)
```

#### Bug 2: `current_price` = 0 for team-name markets
**Root cause:** For markets with team names as outcomes (e.g., "Chicago Sky vs Toronto Tempo"), `_fetch_current_price` fails because `outcome == "yes"` never matches. The function only works for Yes/No markets.

**Fix:** `_open_position_to_big_win` now uses `curPrice` from Polymarket's position data as the primary current price (authoritative — it's the whale's own outcome's current price). CLOB fallback is only used when `curPrice` is0.

```python
cur_price_raw = _safe_float(raw.get('curPrice') or 0)
if cur_price_raw > 0:
    current_price = cur_price_raw
# else use the CLOB-fetched current_price parameter
```

#### Bug 3: "Now: 100.0¢" on every card
**Root cause:** Two issues:
1. `yes_price` in `format_card` was reading from CLOB enrichment which failed for old queue items (pre-fix)
2. `current_price` reference in `format_card` had a `NameError` — variable wasn't defined in scope

**Fixes:**
- Changed `format_card` to use `bw.current_price` (set from `curPrice` via `_open_position_to_big_win`)
- Fixed `NameError`: changed `current_price` → `getattr(bw, 'current_price', 0)`

#### Bug 4: Resolved markets slipping through (`endDate` filter broken)
**Root cause:** `_open_position_to_big_win` compared naive datetime (`end_dt`) with timezone-aware `datetime.now(timezone.utc)`. This raises `TypeError` which was silently caught, causing the filter to fail.

**Fix:** Normalize both datetimes to timezone-aware UTC:
```python
end_dt = datetime.fromisoformat(end_dt_str)
now_utc = datetime.now(timezone.utc)
if end_dt.tzinfo is None:
    end_dt = end_dt.replace(tzinfo=timezone.utc)
if end_dt < now_utc:
    return None
```

#### Bug 5: CLOB pre-enrichment before queuing
**Root cause:** `bw.yes_price` (used for "Now:" line) was only set during `process_queue` via `validate_and_enrich`, but queue items were stored before that enrichment step.

**Fix:** In `run()`, enrich with CLOB data before appending to queue:
```python
enriched = validate_and_enrich(bw)
if enriched and isinstance(enriched, dict):
    bw.yes_price = enriched.get('yes_price', bw.current_price)
    bw.no_price = enriched.get('no_price', 0)
    bw.accepting_orders = enriched.get('accepting_orders', True)
```

---

### Files Modified

#### `/home/ubuntu/whaletrax-public/polyshark_router.py`
- Added CLOB pre-enrichment before queuing (lines ~1220-1230)
- Fixed `format_card`: use `bw.current_price` via `getattr` instead of undefined `current_price` variable
- Router PID: 185898 (running)

#### `/home/ubuntu/whaletrax-public/src/big_win_detector.py`
- `_fetch_current_price`: read from `tokens[i]['price']` primary, `outcomePrices` fallback
- `_open_position_to_big_win`: use `curPrice` from position data as primary current price
- `_open_position_to_big_win`: fixed timezone-aware datetime comparison for `endDate` filter
- `scan_open_positions`: uses `_fetch_current_price` + `curPrice` hybrid approach

#### `/home/ubuntu/whaletrax-public/src/models.py`
- Added `percentPnl` field to `BigWin` dataclass

---

### Bug 6: `profit_usdc` = cost basis ($200K) instead of actual P&L (-$193,800)
**Root cause:** `_open_position_to_big_win` was setting `profit_usdc = cost` (cost basis). For The Rock position: cost = $200,000, actual cashPnl = -$193,800. The card was showing +$200K as "profit" when the whale was down $193,800.

**Fix:** `profit_usdc = unrealized_pnl = cashPnl` from position data. cashPnl is negative for losses, positive for gains — this drives the correct display sign.

**Bug 7: `roi_pct` was mathematically correct but `profit_usdc` had wrong sign**
- `roi_pct = -96.9%` (correct)
- `profit_usdc = +$200,000` (wrong — should be -$193,800)
- Card showed: `💰 +$200,000 (+100.00% potential ROI)` — both wrong sign and wrong magnitude
- Actual: `💰 -$193,800 (-96.90% potential ROI)`

**Bug 8: `current_price` for YES outcomes = whale's YES outcome price (1.55¢), not NO price**
- For YES/NO binary markets, `curPrice` from position data is the whale's **outcome price**, not the market's overall price
- Whale bet YES on The Rock at 50¢. `curPrice = 1.55¢` (YES outcome price, their side)
- The card was treating `curPrice` as the market price and showing it as-is — which rendered as 1.55¢ for the "Now:" line
- The "Now: 98.5¢" that Jeff saw was from an earlier version of the code; after the `curPrice` fix, it shows 1.6¢ correctly for this position
- For team-name markets, `curPrice` is the team's outcome price which IS the right display price

| Field | Source | Meaning |
|-------|--------|---------|
| `avg_price` | `initialValue / size` (derived) | Whale's actual entry price |
| `current_price` | `curPrice` from position data | Whale's outcome current price |
| `roi_pct` | `(current_price - avg_price) / avg_price * 100` | Unrealized ROI |
| `profit_usdc` | `initialValue` (cost basis) | Position size/cost |
| `unrealized_pnl` | `cashPnl` from API | Actual P&L in USDC |
| `percentPnl` | `percentPnl` from API | % return |
| `redeemable` | `redeemable` from API | Market resolved flag |

---

### Current Router Status

- **PID:** 185898 (running)
- **Queue:** Empty (no qualifying big wins this cycle)
- **Scan results (top 5 by size):**
  - Washington Nationals vs Arizona Diamondbacks: entry=55.8¢, current=53.5¢, roi=-4.1%, size=$120,730
  - New York Mets vs San Diego Padres: entry=50.0¢, current=49.5¢, roi=-1.0%, size=$100,000
  - Chicago White Sox vs Philadelphia Phillies: entry=60.0¢, current=88.5¢, roi=+47.6%, size=$63,654
  - Kansas City Royals vs Minnesota Twins: entry=51.7¢, current=95.5¢, roi=+84.6%, size=$56,541
  - Seattle Mariners vs Detroit Tigers: entry=47.0¢, current=62.5¢, roi=+33.0%, size=$23,222

---

### Git Status

#### whaletrax-public (`/home/ubuntu/whaletrax-public`)
```
modified:   main.py
modified:   polyshark_router.py
modified:   src/big_win_detector.py
modified:   src/models.py
modified:   wallet_tracker.db
untracked:  backfill_wallets.py, card_stats.db, src/lockins_detector.py, src/lockins_display.py
```
**Not yet committed.** Needs review before pushing.

#### polyshark-ops (`/home/ubuntu/polyshark-ops`)
- 23 local commits ahead of origin/main
- `team/action-items.md` untracked
- Needs `git pull --rebase` then push

---

### To Do Before Pushing

1. **whaletrax-public:** Review changes to `main.py`, `polyshark_router.py`, `big_win_detector.py`, `models.py` — confirm all intentional
2. **polyshark-ops:** `git pull --rebase` then push
3. **Commit all team vault docs** to polyshark-ops

---

## Context: What These Fixes Mean for the Card

**Before these fixes:**
- "Now: 100.0¢" on every card (CLOB price fetch failing)
- "Entry: 86.7¢" for US x Iran (using `curPrice` instead of derived entry price)
- Resolved markets appearing as open positions
- ROI calculations using wrong price references

**After these fixes:**
- "Now: X.X¢" shows the whale's actual outcome's current price (from `curPrice`)
- "Entry: X.X¢" shows whale's actual entry price (from `initialValue / size`)
- ROI correctly shows unrealized gain/loss
- Resolved markets filtered out via `endDate` check + `redeemable` + `percentPnl`

---

## Bugs9-12 (discovered during card audit)

### Bug 9: `format_card` recomputed roi_pct and profit_usdc from entry price for all open positions
**Root cause:** Lines 444-447 in `format_card`:
```python
if is_open:
    roi_pct = (1.0 / entry_px - 1) * 100
    if trade_size > 0:
        profit_usdc = (trade_size / entry_px) - trade_size
```
This OVERWROTE the correct scan-computed `roi_pct` and `profit_usdc` (from `cashPnl` and `curPrice`) with mathematically derived "potential ROI" based on entry price alone.

For The Rock position (entry=50¢, curPrice=1.55¢):
- Scan computed: `roi_pct=-96.9%, profit_usdc=-$193,800` ✅
- format_card overwrote to: `roi_pct=+100%, profit_usdc=+$200,000` ❌

**Fix:** Only recompute for closed positions. For open positions, use scan-computed values as-is.

### Bug 10: Router `seen` set blocked all re-queuing
Router state file `/tmp/polyshark_router_state.json` persists `seen_keys` across restarts. Clearing the queue file did NOT clear `seen_keys`. All positions already queued were blocked from re-queuing even after queue was cleared.

**Fix:** Clear both queue and state file when restarting fresh.

### Bug 11: Router bytecode stale despite `__pycache__` clearing
Python imports bytecode at process start. Clearing `__pycache__` after the router starts doesn't affect the running process. Router was running old code from before fixes were committed.

**Fix:** Kill and restart the router process after each code change.

### Bug 12: `format_card` "Now:" line used wrong field
`format_card` used `bw.current_price` (scan-time value) instead of `bw.yes_price` (CLOB-enriched fresher value).

**Fix:** `now_price = getattr(bw, 'yes_price', 0) or getattr(bw, 'current_price', 0)`

---

## All Bugs Fixed (2026-06-07)
1. ✅ `_fetch_current_price` tokens[i]['price']
2. ✅ `_open_position_to_big_win` curPrice primary
3. ✅ `format_card` NameError current_price
4. ✅ `_open_position_to_big_win` timezone endDate
5. ✅ CLOB pre-enrichment before queuing
6. ✅ profit_usdc = cashPnl (not cost basis)
7. ✅ roi_pct sign correct (negative for losses)
8. ✅ curPrice for YES outcomes (whale's outcome price)
9. ✅ format_card: use scan-computed roi/profit for open
10. ✅ Router seen set cleared on fresh start
11. ✅ Router bytecode fresh on restart
12. ✅ format_card Now: line uses yes_price (enriched)

## Router Status (after all fixes)
- PID: 186512 (running)
- All12 bugs fixed and committed
- Rock card now correctly shows: `💰 -$193,800 (-96.90% potential ROI)` ✅

---

## Bug 13: "Now:" line showed YES price for NO bets
**Root cause:** `format_card` used `yes_price` for the "Now:" line regardless of whether the whale bet YES or NO. For NO bets, `yes_price` is the OPPOSITE outcome's price — completely backwards.

**Example:** Knicks NBA Finals NO bet (70.2¢ entry, NO worth 21.9¢ now):
- Card showed: `Now: 78.1¢` → YES price (Knicks WIN probability)
- Should show: `Now: 21.9¢` → NO price (whale's actual position value)

**Fix:** If whale bet YES → show `yes_price`. If whale bet NO → show `no_price`.

## Router Status (after Bug 13 fix)
- PID: 186646 (running)
- All 13 bugs fixed and committed
- whaletrax-public: commit f2be57a
