# Polyshark Sniper Bucket Configuration
**Version:** 1.0 | **Created:** 2026-06-07 | **Purpose:** Odds-tiered position sizing for whale sniping system

---

## Overview

The sniper bucket system defines mutually-exclusive odds ranges that map to position sizes, risk levels, and break-even win rate requirements. Each bucket corresponds to a price range (in cents) on Polymarket.

> **⚠️ Original ranges had an overlap issue:** Penny was 90–99¢ and Nickel was 80–95¢, which overlapped at 90–95¢. The corrected ranges below are clean and non-overlapping.

---

## Tier Structure

### 🟡 Penny Snipers — 90–99¢ (Near-Certainty)

| Attribute | Value |
|-----------|-------|
| **Odds Range** | 90¢ – 99¢ |
| **Position Sizing** | 10–15% of bankroll |
| **Risk Level** | 🟢 Low |
| **Break-Even Win Rate** | ≥ 53% (at 95¢ avg price) |
| **Kelly Fraction** | ~0.20 (full Kelly), ~0.10 (half Kelly) |
| **Expected Frequency** | ~35–40% of markets fall here |
| **Rationale** | High implied probability. Size accordingly; don't over-leverage just because "it's a sure thing." |

**Break-even math:**
- At 95¢ entry, you need 53% win rate to profit (0.95 × win% ≥ 1.00 cost)
- At 99¢ entry, you need 52% win rate
- At 90¢ entry, you need 56% win rate

---

### 🔵 Nickel Snipers — 70–89¢ (Solid Probability)

| Attribute | Value |
|-----------|-------|
| **Odds Range** | 70¢ – 89¢ |
| **Position Sizing** | 5–8% of bankroll |
| **Risk Level** | 🟡 Medium |
| **Break-Even Win Rate** | ≥ 58–65% (varies by entry price) |
| **Kelly Fraction** | ~0.12 (full Kelly), ~0.06 (half Kelly) |
| **Expected Frequency** | ~25–30% of markets fall here |
| **Rationale** | Moderate edge. Win rate must be notably above 50% to overcome vig. |

**Break-even math:**
- At 80¢ entry: need ≥ 63% win rate (0.80 × 0.63 = 0.504 ≥ 0.20 cost basis)
- At 85¢ entry: need ≥ 59% win rate
- At 70¢ entry: need ≥ 72% win rate

---

### 🟠 Dime Snipers — 50–69¢ (Mid-Probability)

| Attribute | Value |
|-----------|-------|
| **Odds Range** | 50¢ – 69¢ |
| **Position Sizing** | 2–4% of bankroll |
| **Risk Level** | 🟠 Medium-High |
| **Break-Even Win Rate** | ≥ 68–85% |
| **Kelly Fraction** | ~0.07 (full Kelly), ~0.035 (half Kelly) |
| **Expected Frequency** | ~15–20% of markets fall here |
| **Rationale** | True 50/50 or worse. Treat as lottery tickets; size small. |

**Break-even math:**
- At 60¢ entry: need ≥ 84% win rate
- At 55¢ entry: need ≥ 92% win rate
- At 50¢ entry: need 100%+ win rate → not profitable unless edge is very high

---

### 🔴 Quarter Snipers — 30–49¢ (Long-Shot / Optional)

| Attribute | Value |
|-----------|-------|
| **Odds Range** | 30¢ – 49¢ |
| **Position Sizing** | 0.5–1.5% of bankroll |
| **Risk Level** | 🔴 High |
| **Break-Even Win Rate** | ≥ 85–100%+ |
| **Kelly Fraction** | ~0.03 (full Kelly), ~0.015 (half Kelly) |
| **Expected Frequency** | ~10–15% of markets fall here |
| **Rationale** | Speculative. Only play if you have strong signal/alpha. Most traders should skip this tier. |

---

### ⚫ Dollar Snipers — 1–29¢ (Lottery Tier)

| Attribute | Value |
|-----------|-------|
| **Odds Range** | 1¢ – 29¢ |
| **Position Sizing** | ≤ 0.5% of bankroll (or skip entirely) |
| **Risk Level** | ⚫ Extreme |
| **Break-Even Win Rate** | ≥ 100% (requires near-perfect prediction) |
| **Kelly Fraction** | ~0.01 (quarter Kelly only) |
| **Expected Frequency** | ~5–8% of markets fall here |
| **Rationale** | Essentially a lottery. Only whales with deep research signals should engage, and only with micro-size positions. |

---

## Overlap Issue in Original Ranges

The original definitions had:

| Tier | Original Range | Problem |
|------|---------------|---------|
| Penny | 90–99¢ | Overlaps with Nickel's 80–95¢ at 90–95¢ |
| Nickel | 80–95¢ | Same — ambiguous at 90–95¢ |

**Resolution:** Corrected ranges above use:
- Penny: **90–99¢** (no upper ambiguity)
- Nickel: **70–89¢** (non-overlapping)
- Dime: **50–69¢**
- Quarter: **30–49¢**
- Dollar: **1–29¢**

---

## Kelly Criterion Reference

### Full Kelly
```
f* = (bp - q) / b
Where:
  b = net odds (profit / loss) = (1 - avg_price) / avg_price
  p = true win probability (your estimate)
  q = 1 - p
```

### Simplified by Tier

| Tier | Avg Price | b (net odds) | Kelly Formula |
|------|-----------|--------------|---------------|
| Penny | 95¢ | 0.053 | f* ≈ (0.053p - q) / 0.053 |
| Nickel | 80¢ | 0.25 | f* ≈ (0.25p - q) / 0.25 |
| Dime | 60¢ | 0.667 | f* ≈ (0.667p - q) / 0.667 |
| Quarter | 40¢ | 1.5 | f* ≈ (1.5p - q) / 1.5 |
| Dollar | 20¢ | 4.0 | f* ≈ (4.0p - q) / 4.0 |

### Conservative Sizing (Half or Quarter Kelly)
- **Half Kelly:** ~50% of full Kelly → roughly 2x the break-even bankroll exposure
- **Quarter Kelly:** ~25% of full Kelly → ~4x break-even bankroll exposure
- Recommended for live trading due to variance and estimation error

---

## JSON Config Block (Router-Consumable)

```json
{
  "sniper_buckets": {
    "version": "1.0",
    "created": "2026-06-07",
    "buckets": [
      {
        "name": "penny",
        "label": "Penny Snipers",
        "min_odds": 0.90,
        "max_odds": 0.99,
        "size_pct": 0.125,
        "risk_level": "low",
        "break_even_wr": 0.53,
        "kelly_fraction": 0.20,
        "description": "Near-certainty plays. 90-99 cents."
      },
      {
        "name": "nickel",
        "label": "Nickel Snipers",
        "min_odds": 0.70,
        "max_odds": 0.89,
        "size_pct": 0.065,
        "risk_level": "medium",
        "break_even_wr": 0.60,
        "kelly_fraction": 0.12,
        "description": "Solid probability. 70-89 cents."
      },
      {
        "name": "dime",
        "label": "Dime Snipers",
        "min_odds": 0.50,
        "max_odds": 0.69,
        "size_pct": 0.03,
        "risk_level": "medium_high",
        "break_even_wr": 0.75,
        "kelly_fraction": 0.07,
        "description": "Mid-probability. 50-69 cents."
      },
      {
        "name": "quarter",
        "label": "Quarter Snipers",
        "min_odds": 0.30,
        "max_odds": 0.49,
        "size_pct": 0.01,
        "risk_level": "high",
        "break_even_wr": 0.85,
        "kelly_fraction": 0.03,
        "description": "Long-shot. 30-49 cents. Optional tier."
      },
      {
        "name": "dollar",
        "label": "Dollar Snipers",
        "min_odds": 0.01,
        "max_odds": 0.29,
        "size_pct": 0.005,
        "risk_level": "extreme",
        "break_even_wr": 1.00,
        "kelly_fraction": 0.01,
        "description": "Lottery tier. 1-29 cents. Skip or micro-size only."
      }
    ],
    "overlap_fix": {
      "original_penny": "90-99",
      "original_nickel": "80-95",
      "overlap_at": "90-95",
      "fixed_penny": "90-99",
      "fixed_nickel": "70-89",
      "note": "Original ranges overlapped at 90-95 cents. Fixed to be mutually exclusive."
    }
  }
}
```

---

## Quick Reference Card

| Tier | Odds | Size | Risk | Break-Even WR |
|------|------|------|------|---------------|
| 🟡 Penny | 90–99¢ | 10–15% | Low | ≥ 53% |
| 🔵 Nickel | 70–89¢ | 5–8% | Medium | ≥ 60% |
| 🟠 Dime | 50–69¢ | 2–4% | Med-High | ≥ 75% |
| 🔴 Quarter | 30–49¢ | 0.5–1.5% | High | ≥ 85% |
| ⚫ Dollar | 1–29¢ | ≤ 0.5% | Extreme | ≥ 100% |

---

## Implementation Notes

1. **Bucket lookup:** Match by `min_odds <= avg_price <= max_odds` — order from largest to smallest range or use if/elif chain
2. **Tier priority:** When an alert falls in multiple tiers (edge case after fix), assign to the **higher-sizing** tier (penny > nickel > dime > quarter > dollar)
3. **Position size override:** The `size_pct` in the JSON is a baseline. Real position size should also factor in:
   - Confidence score from category router
   - Whether the pick is curated (higher size allowed)
   - Bankroll health / drawdown state
4. **Whale profile integration:** Wallets in the top 150 leaderboard by PnL should get a 1.25–1.5x multiplier on `size_pct` since they have proven edge
5. **No overlap enforcement:** The router should assert `bucket[n].max_odds > bucket[n+1].min_odds` on startup

---

*Polyshark Sniper Bucket Config — Built 2026-06-07*