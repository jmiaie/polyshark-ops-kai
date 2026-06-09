# Polyshark Sniper Position Sizing Framework

**Version:** 1.0 | **Created:** 2026-06-07 | **By:** Tai 🤙
**Status:** DRAFT — For Jeff review before implementation

---

## Overview

This doc defines the position sizing tiers ("buckets") for whale sniper plays on Polymarket. Each tier maps an odds range to a recommended bankroll allocation %, risk level, and Kelly fraction.

**Core principle:** Size your position to the conviction level. Higher odds = higher confidence = larger stake. Lower odds = more speculative = smaller stake.

---

## Tier Structure

| Tier | Odds Range | Size (% Bankroll) | Kelly Fraction | Risk Level | Break-Even WR |
|------|-----------|-------------------|----------------|------------|---------------|
| **Penny** |90–99% | 8–10% | f* = 0.08–0.10 | Very Low | ≥90% |
| **Nickel** | 80–90% | 5–7% | f* = 0.05–0.07 | Low | ≥80% |
| **Dime** | 70–80% | 3–5% | f* = 0.03–0.05 | Medium | ≥70% |
| **Quarter** | 60–70% | 1–3% | f* = 0.01–0.03 | High | ≥60% |
| **Dollar** | 50–60% | 0.5–1.5% | f* = 0.005–0.015 | Very High | ≥50% |

*Bankroll = total USDC allocated to Polymarket sniping strategy*

---

## Kelly Criterion Reference

**Formula:** `f* = (Bp - q) / B`
- `B` = decimal odds - 1 (e.g., 0.90 odds → B = 0.111)
- `p` = estimated win probability (from whale data)
- `q` = 1 - p

**For Polymarket binary markets:**
- If true odds = 85% and market odds = 85% → no edge → don't play
- If true odds = 85% and market odds = 80% → positive edge → calculate Kelly

**Half-Kelly rule:** Halve the Kelly fraction for live trading. Aggressive Kelly is for backtesting; real play = half-Kelly to account for model error and odds drift.

**Example (Penny tier, 95% market odds):**
```
p = 0.95 (whale's historical WR in this odds range)
q = 0.05
B = (1/0.95) - 1 = 0.0526

Kelly = (0.0526 × 0.95 - 0.05) / 0.0526 = 0.90 →90% of bankroll
Half-Kelly =45% → cap at 8–10% for Penny tier (practical limit)
```

**Example (Dime tier, 75% market odds):**
```
p = 0.75
q = 0.25
B = (1/0.75) - 1 = 0.333

Kelly = (0.333 × 0.75 - 0.25) / 0.333 = 0.50 → 50% of bankroll
Half-Kelly = 25% → cap at 3–5% for Dime tier
```

---

## Tier-by-Tier Logic

### 🥇 Penny —90–99% Odds

**Profile:** Near-certainty. Whale has85%+ lifetime WR in this range. Market is pricing near-certainty.

**When to play:**
- Whale's historical win rate in90-99% range ≥85%
-鲸 has high confidence signal (large size, recent activity, streak)
- Market is liquid, entry slippage < 1%

**Position sizing:**
- Max8–10% of bankroll per play
- Max 2 concurrent Penny plays (20% total exposure)
- Stop loss: not applicable for binary (max loss = stake)

**Example:** $10,000 bankroll → $800–$1,000 per Penny play

---

### 🥈 Nickel — 80–90% Odds

**Profile:** Solid probability. Whale's30d WR in this range should be ≥ 75%.

**When to play:**
- Whale's30d WR in 80-90% range ≥ 75%
- Strong directional signal with size corroboration
- Market has enough liquidity for full stake

**Position sizing:**
- 5–7% of bankroll per play
- Max 2 concurrent Nickel plays (12% total exposure)
- Max combined Penny + Nickel:25% of bankroll

**Example:** $10,000 bankroll → $500–$700 per Nickel play

---

### 🪙 Dime — 70–80% Odds

**Profile:** Mid-probability. This is where conviction separates from speculation. Whale needs ≥70% actual WR to be profitable long-term here.

**When to play:**
- Whale's actual WR in70-80% range ≥ 70% (not market odds — actual outcomes)
- Strong signal: whale size >2x average for this market type
- Market is active, not a obscure binary with bad fill

**Position sizing:**
- 3–5% of bankroll per play
- Max 3 concurrent Dime plays (12% total exposure)
- Half-Kelly cap applies strictly here

**Example:** $10,000 bankroll → $300–$500 per Dime play

---

### 🪙 Quarter — 60–70% Odds

**Profile:** Speculative. Higher variance. Only play if whale has exceptional history in this range OR strong cross-signal (multiple whales piled in).

**When to play:**
- Whale's actual WR in 60-70% range ≥ 65%
- Multiple whales independently betting same direction
- External signal (analyst call, on-chain flow) corroborates

**Position sizing:**
- 1–3% of bankroll per play
- Max 2 concurrent Quarter plays (5% total exposure)
- Treat as lottery tickets — size accordingly

**Example:** $10,000 bankroll → $100–$300 per Quarter play

---

### 💵 Dollar — 50–60% Odds

**Profile:** Pure lottery. Almost no edge by definition — market is near50/50. Only play with exceptional multi-signal confirmation.

**When to play:**
-3+ independent signals all pointing same direction
- Whale has >70% actual WR in 50-60% range (rare)
- Timing signal (late-season info, market-moving event imminent)

**Position sizing:**
- 0.5–1.5% of bankroll per play
- Max 1 concurrent Dollar play (1.5% total exposure)
- Treat as entertainment — expected value is marginal

**Example:** $10,000 bankroll → $50–$150 per Dollar play

---

## Overlap Resolution Rules

**Problem:** Original Penny (90-99) and Nickel (80-95) overlapped at 90-95. A92-cent play could be either.

**Solution — Tier Priority (highest tier wins):**
1. If odds are in Penny range → Penny rules apply
2. If odds are in Nickel range → Nickel rules apply (only if NOT in Penny)
3. And so on down the priority list

**Overlap rule:** If a play falls in two tiers, assign it to the **higher-conviction tier** (Penny > Nickel > Dime > Quarter > Dollar).

**Overlap band (90-95):** These odds get routed to Penny by default since the market is already pricing very high probability. The risk of over-sizing a Nickel-tier play in the 90-95 band outweighs the benefit.

---

## Combined Exposure Limits

| Concurrent Tier | Max Total Exposure |
|----------------|-------------------|
| Penny + Nickel | 25% of bankroll |
| Penny + Nickel + Dime | 35% |
| All tiers active | 45% (hard cap) |

**Rule:** Never exceed 45% total bankroll deployed at once. If approaching limit, pause new lower-conviction plays until positions resolve.

---

## Bankroll Recommendations by Tier

| Bankroll | Penny Max | Nickel Max | Dime Max | Quarter Max | Dollar Max |
|----------|-----------|------------|----------|------------|------------|
| $5,000 | $500/play | $350/play | $200/play | $100/play | $50/play |
| $10,000 | $1,000/play | $700/play | $400/play | $200/play | $100/play |
| $25,000 | $2,500/play | $1,750/play | $1,000/play | $500/play | $250/play |
| $50,000 | $5,000/play | $3,500/play | $2,000/play | $1,000/play | $500/play |

---

## JSON Config (Router-Compatible)

```json
{
  "sniper_tiers": [
    {
      "name": "penny",
      "min_odds": 90,
      "max_odds": 99,
      "size_pct_min": 0.08,
      "size_pct_max": 0.10,
      "kelly_fraction": 0.5,
      "risk_level": "very_low",
      "break_even_wr": 90,
      "max_concurrent": 2,
      "max_total_exposure_pct": 0.20
    },
    {
      "name": "nickel",
      "min_odds": 80,
      "max_odds": 90,
      "size_pct_min": 0.05,
      "size_pct_max": 0.07,
      "kelly_fraction": 0.5,
      "risk_level": "low",
      "break_even_wr": 80,
      "max_concurrent": 2,
      "max_total_exposure_pct": 0.12
    },
    {
      "name": "dime",
      "min_odds": 70,
      "max_odds": 80,
      "size_pct_min": 0.03,
      "size_pct_max": 0.05,
      "kelly_fraction": 0.5,
      "risk_level": "medium",
      "break_even_wr": 70,
      "max_concurrent": 3,
      "max_total_exposure_pct": 0.12
    },
    {
      "name": "quarter",
      "min_odds": 60,
      "max_odds": 70,
      "size_pct_min": 0.01,
      "size_pct_max": 0.03,
      "kelly_fraction": 0.5,
      "risk_level": "high",
      "break_even_wr": 60,
      "max_concurrent": 2,
      "max_total_exposure_pct": 0.05
    },
    {
      "name": "dollar",
      "min_odds": 50,
      "max_odds": 60,
      "size_pct_min": 0.005,
      "size_pct_max": 0.015,
      "kelly_fraction": 0.5,
      "risk_level": "very_high",
      "break_even_wr": 50,
      "max_concurrent": 1,
      "max_total_exposure_pct": 0.015
    }
  ],
  "global_limits": {
    "max_total_exposure_pct": 0.45,
    "half_kelly_only": true,
    "tier_priority": ["penny", "nickel", "dime", "quarter", "dollar"]
  }
}
```

---

## Key Insights

1. **Tight ranges beat loose ones.** The original Penny 90-99 and Nickel 80-95 had overlap at 90-95. New structure: Penny 90-99, Nickel 80-90, Dime 70-80 — no gaps, no overlaps.

2. **Half-Kelly is non-negotiable.** Full Kelly in live markets with odds drift, slippage, and model error will blow up your bankroll. Half-Kelly is the right number for all tiers.

3. **Break-even is not the goal.** Break-even WR just means you don't lose. The goal is WR well above break-even for each tier. Penny needs90%+, Nickel80%+, Dime 70%+ to be worth the capital lock.

4. **Dollar tier is lottery.**50-60% odds market is basically a coin flip. Only play with exceptional multi-signal confirmation. Size it accordingly.

5. **Exposure caps protect against correlation risk.** Multiple positions in the same market or correlated outcomes can wipe you out. The45% hard cap on total exposure is the backstop.

---

*Draft by Tai 🤙 — 2026-06-07*
*For Jeff review: Does the tier structure match how you're thinking about the sniper plays?*
