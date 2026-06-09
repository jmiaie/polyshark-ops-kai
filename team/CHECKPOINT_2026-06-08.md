# 2026-06-07 → 2026-06-08 Midnight Checkpoint

## Router Fixes Summary (Post-Midnight Push)

All fixes committed to `whaletrax-public` main branch:

| Commit | Description |
|--------|-------------|
| `0a37b86` | Store yes_price/no_price on queue items for bw_from_item |
| `e4918df` | Fix O: date fallback to queued_at; ensure C: is plain text |
| `52ef383` | Add bw.closed; is_resolved checks both closed and accepting_orders; store closed on queue items |

## Router State
- **PID:** 187463 (running)
- **Repo:** whaletrax-public @ `52ef383`
- **Restarted:** 2026-06-08 00:16 UTC
- Queue and state cleared at restart

## What Was Fixed Tonight
1. `yes_price`/`no_price` stored at top level of queue item dict (not just in `_clob_enriched`)
2. `O:` date now falls back to `queued_at` when `timestamp` is 0
3. `C:` date is plain text (no markdown link)
4. `bw.closed` added; `is_resolved` checks both `closed` and `accepting_orders`
5. `closed` stored on queue items; read back via `bw_from_item`

## Key Insight
Dodgers card (forwarded at 00:01 from PolysharkWorld) showed correct loss math (-$57K/-95%). 
Dodgers lost to Angels. The P&L was accurate — only the "Now:" line was stale.
For resolved markets, "Now:" is meaningless (market closed, price is $0 or $1).

## Current Queue (as of 00:26)
- Knicks NBA Finals card (NO bet, live market)
- Rock 2028 Presidential card (YES bet, live market)
- Both have proper O: dates and closed=False

## Next Scan
Router runs every ~2 min. Queue should fire fresh items with all fixes active.