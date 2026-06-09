# Polyshark Repo Reconciliation Report

**Date:** 2026-06-07  
**Compiled by:** Tai (repo-reconciler subagent)

---

## Executive Summary

The polyshark-ops repo is essentially a **pliamem-focused repository** with 23 local commits that have nothing to do with whale sniping. The actual production router code lives in `/home/ubuntu/whaletrax-public` (symlinked as `workspace/repos/whaletrax`), which is a completely separate, operational codebase. Kai's `~/work/polyshark/` on his VM is nearly empty. The team-vault has planning docs but not running code.

---

## 1. polyshark-ops Git State

**Local commits ahead of origin/main: 23**  
**Remote commits ahead of HEAD: 5**

### Local 23 commits (origin/main → HEAD):
All 23 commits are **pliamem and infrastructure-related** — zero whale sniping code. Notable commits:
- `93e7451` Tai: team vault updates + AI stack reviews (2026-06-02)
- `edef00b` chore: bump to v1.0.1 for PyPI documentation update
- `6567121` refactor: rename ZTB Protocol to MTB Protocol
- `b8d5372` feat: complete v0.9 cloud memory management with sync and prune
- `b09326d` feat: add @heyputer/puter.js dependency
- `32ebe02` feat: Phase 1 — complete v0.1 foundation

**None of these contain router, sniper, bucket, or card generation code.**

### Remote 5 commits (HEAD → origin/main):
These are team-vault documentation and v1.2 card spec additions:
- `3568cdd` feat: add BUILD_PROTOCOL.md - team build harness
- `1d56f3b` Tai: mark whale-001 C1 in progress — repo created, Kai commits next
- `b5a8ea5` Tai: update repo URL to whaletrax_private, mark C1 repo creation done
- `7e23cce` Tai: consolidate team changes May 2026 (pliamem, agnostic-obsidian, micap-ai, benchmarks, riser-fitness)
- `f0c0b26` v1.2 card spec: emoji rules, color system, reject rules, free no-link (original Polyshark v1.2 spec from J. Milam, Apr 25 2026)

**Assessment:** The 5 remote commits contain the original v1.2 card spec and team documentation. The 23 local commits are pliamem development. These histories are effectively unrelated.

---

## 2. Where the Actual Router Code Lives

### Primary: `/home/ubuntu/whaletrax-public/` (linked as `workspace/repos/whaletrax`)

This is the **live production system**. Key files:

| File | Size | Purpose |
|------|------|---------|
| `polyshark_router.py` | 62KB | Main router daemon — scan, queue, send loop |
| `card_generator.py` | 11.5KB | Card formatting (in card_format/) |
| `alert_log.py` | 10.6KB | Alert logging and deduplication |
| `polyshark_sender.py` | 6.4KB | Telegram sending logic |
| `polyshark_memory.py` | 10KB | OMPA brain ingestion |
| `src/wallethound/` | — | Compounders, consistent_winners, deposit_tracker, scanner |
| `wallet_tracker.db` | 2.7MB | SQLite DB with whale positions |

### Secondary: `/home/ubuntu/team-vault/org/teams/polyshark/`

Contains **planning docs and reference implementations**, not running code:
- `routing/CHANNEL_ROUTING_MAP.md` — routing rules (out of date vs actual router)
- `card_format/card_generator.py` — reference only, not used by production
- `card_format/CARD_SPEC.md` — v1.2 spec (describes what production does)
- `operations/alert_log.py` — simplified reference, not used by production

---

## 3. Bucket/Tier/Sniper Configuration Status

### TOP PLAYS Channel (auto-routing tier)

Defined in `polyshark_router.py` lines 1168-1214:

```python
TOP_PLAYS_WHITELIST = {
    '0x492442eab586f242b53bda933fd5de859c8a3782': {'name': 'Whale A', 'wr': 100.0, 'positions': 200, 'pnl': 49_796_390},
    '0x2a2c53bd278c04da9962fcf96490e17f3dfb9bc1': {'name': 'Whale B', 'wr': 100.0, 'positions': 200, 'pnl': 20_009_550},
    '0x24c8cf69a0e0a17eee21f69d29752bfa32e823e1': {'name': 'Whale C', 'wr': 100.0, 'positions': 50,  'pnl': 17_467_534},
    '0x6a72f61820b26b1fe4d956e17b6dc2a1ea3033ee': {'name': 'Whale D', 'wr': 100.0, 'positions': 50,  'pnl': 16_867_771},
    '0xfe787d2da716d60e8acff57fb87eb13cd4d10319': {'name': 'Whale E', 'wr': 100.0, 'positions': 5000,'pnl': 15_823_457},
}

TOP_PLAYS_CONFIG = {
    'max_entry_price': 0.60,  # <60¢: <50¢ = high priority, 50-60¢ = secondary
    'min_wr': 95.0,           # Wallet must have 95%+ lifetime WR
    'require_30d_activity': True,
}
```

**Criteria for TOP PLAYS auto-route:**
- Wallet 95%+ WR AND 20+ positions, OR in hardcoded whitelist
- Entry price < 60¢
- Market OPEN (accepting_orders=True)
- Not already sent this session

### Curated vs Free Tier

- **Curated delay:** 5 minutes (`CURATED_DELAY = timedelta(minutes=5)`)
- **Free delay:** 21,600 seconds / 6 hours (default, configurable via `POLYSHARK_FREE_DELAY_SECONDS` env var)
- **Curated criteria** (any one): ROI ≥ 100%, Profit ≥ $10K, Win streak ≥ 5, Top 3 by profit in session
- **Max curated per session:** 4

### Current Channel Status (from router code)

```
⚡ Free channel disabled during v2.0 rollout: Hub + PRO only.
⚠️ Keep queued items for downstream review, but do not emit to free channels.
```

Currently active: Alert Hub + PRO + TOP PLAYS US. Free channel is disabled.

### Channel IDs (from router)

```python
CHANNELS = {
    'alert':     -1003786930778,  # Polyshark Alert Hub
    'pro':       -1003739747776,  # PolysharkPro
    'top_plays': -1003957370508,  # Polyshark TOP PLAYS US
    'sports':    -1003948034686,
    'esports':   -1003700788085,
    'weather':   -1003532326443,
    'crypto':    -1003999731708,
    'politics':  -1003935178097,
    'econ':      -1003868008293,
    'world':     -1003927756388,
    'free':      -1003999194095,  # Polyshark Free (disabled)
    'free_chat': -1003860830659,
}
```

---

## 4. Kai's VM Directory (`~/work/polyshark/`)

**Status: Essentially empty.**

Contains only an `index.md` (99 bytes) with a placeholder note:
```
# Polyshark — Polymarket Whale Tracking
[placeholder — Tai is reference clone only]
```

Kai's actual working code is in `/home/ubuntu/whaletrax-public` on this (Tai's) machine. The symlink `workspace/repos/whaletrax → /home/ubuntu/whaletrax-public` points to the right place.

---

## 5. High Priority Whales

Both `team-vault/org/teams/polyshark/high_priority_whales.json` and `whaletrax-public/high_priority_whales.json` are **identical** (no diff). The listed whales:

```json
[
  {"address": "0x63a51cbb37341837b873bc29d05f482bc2988e33", "name": "Xaoo", "rank": 2, "pnl": 4400000, "wr": 85.3},
  {"address": "0x492442eab586f242b53bda933fd5de859c8a3782", "name": "Whale A", "rank": 1, "pnl": 49796390, "wr": 100},
  ...
]
```

---

## 6. What Needs to Happen to Get Routers Flowing

### Current Production State

The router at `/home/ubuntu/whaletrax-public/polyshark_router.py` is the active system. The daemon loop runs every 120 seconds, scanning for new big wins and routing to:
1. **Alert Hub** — immediate
2. **PRO channel** — 3-minute delay
3. **TOP PLAYS US** — auto-route for qualifying wallets (< 60¢ entry, 95%+ WR)

### Issues / Gaps

1. **Free channel disabled** — v2.0 rollout has Hub + PRO only. Free tier users are not getting cards.
2. **Category routing deferred to Hub** — comment in router says "Category routing deferred to Hub" but Hub routing implementation needs verification.
3. **polyshark-ops is pliamem repo** — it should NOT be the home for whale sniping code. The actual code is in `whaletrax-public`.
4. **No git backup of whaletrax-public** — the production code isn't in any git repo (Kai's private `whaletrax_private` exists but hasn't been pushed to). Critical gap for disaster recovery.
5. **No bucket config for sub-$0.10 entries** — the TOP_PLAYS config only has `max_entry_price: 0.60`. There's no separate "deep snipe" bucket for < 10¢ entries.

### Recommended Actions

1. **Decide if polyshark-ops should contain whale code** — it currently doesn't and shouldn't (it's pliamem). Consider renaming or leaving as-is.
2. **Enable free channel** — flip the flag in router to re-enable free tier sends.
3. **Verify Hub category routing** — check if Hub is actually processing deferred category sends.
4. **Push whaletrax-public to git** — Kai should push to `whaletrax_private` as backup.
5. **Add sub-10¢ bucket** — if Jeff wants even faster routing for deep snipes, add a new tier/bucket in `is_top_play()` or a separate function.

---

## 7. File Locations Reference

| What | Where |
|------|-------|
| Production router | `/home/ubuntu/whaletrax-public/polyshark_router.py` |
| Card generator | `/home/ubuntu/whaletrax-public/card_format/card_generator.py` |
| Alert log | `/home/ubuntu/whaletrax-public/alerts/alert_log.py` (or `operations/alert_log.py` reference) |
| Channel routing map | `/home/ubuntu/team-vault/org/teams/polyshark/routing/CHANNEL_ROUTING_MAP.md` |
| Card spec v1.2 | `/home/ubuntu/team-vault/org/teams/polyshark/card_format/CARD_SPEC.md` |
| High priority whales | `/home/ubuntu/whaletrax-public/high_priority_whales.json` (same as team-vault) |
| whaletrax repo symlink | `/home/ubuntu/.openclaw/workspace/repos/whaletrax → /home/ubuntu/whaletrax-public` |
| Polyshark ops repo | `/home/ubuntu/polyshark-ops` (pliamem only, NOT router code) |

---

*End of report*
## 2026-06-07: Open Positions Architecture Refactor

### What Changed
The router's primary detection path shifted from **closed positions** to **open positions**.

**Before:** `bwd.scan_big_wins_from_leaderboard()` → calls `get_user_closed_positions()` → emit cards → market already resolved by detection time

**After:** `bwd.scan_open_positions()` → calls `get_user_positions()` → emit cards → market still live at detection time

### Why
Jeff noticed cards were firing with current price at $1.00 and "✅ RESOLVED" labels even when the whale entered at $0.40–$0.60. The detection lag was structural — scanning closed trades means the market has already moved and often resolved before we see the whale's entry.

### Files Changed
- `src/big_win_detector.py` — full rewrite: `_open_position_to_big_win()` (primary), `_closed_position_to_big_win()` (stats-only), `scan_open_positions_from_leaderboard()` (new public API)
- `src/models.py` — `BigWin` dataclass: added `is_open: bool`, `current_price: float`, `unrealized_pnl: float`
- `polyshark_router.py` — `run()`: primary calls `scan_open_positions()`, stats-only calls `scan_big_wins_from_leaderboard()`. Category routing for 'world' channel filters on `wr >= 90% AND wr_30d >= 90%`
- `wallet_profiles.py` — unchanged (correct, no bugs found)

### New BigWin Fields
- `is_open=True` — open position detected from `get_user_positions()`
- `is_open=False` — closed/resolved position detected from `get_user_closed_positions()`
- `current_price` — CLOB price at detection time (for open positions)
- `unrealized_pnl` — `(current_price - avg_price) * size` for open positions
- `profit_usdc` for open positions = `cost_basis` (entry cost, not realized P&L)

### Stats-Only Path
`scan_big_wins_from_leaderboard()` now returns empty list — its only job is to call `update_profile()` on each leaderboard wallet to keep win rates and PnL current.

### World Channel Filter
`world` category channel: only fires if `profile.win_rate >= 90 AND profile.win_rate_30d >= 90`. Logged as `World filtered (WR {wr}%/{wr30}% < 90%)`.

### PolysharkWorld Channel
- Channel ID: `-1003927756388` (configured in CHANNELS)
- Bot added as admin by Jeff — awaiting first message to confirm channel
- Routing: via category routing with 90% WR gate

### Math Verification (completed 2026-06-07)
All win rate and PnL calculations verified correct end-to-end:
- Lifetime WR = `total_wins / total_positions` ✓
- 30D WR = `_wins_30d / _positions_30d` ✓
- `losses = total_positions - total_wins` ✓
- PnL summed directly from `_pos_history` ✓
- `fmt_wr()` derives WR from raw wins/total counts, not from pre-calculated float ✓
