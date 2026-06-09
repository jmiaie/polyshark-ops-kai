# 🚨 CRITICAL UPDATE: Card Format v1.2 — All Agents Must Implement

**Issued:** 2026-04-25 19:49 UTC
**From:** KaiOC 🌊 (for Jeff Milam)
**Priority:** HIGH — Implement before next alert cycle
**Status:** APPROVED & FINAL

---

## What Changed

### Card Format Spec (v1.2) — Integrated Jeff's Formatting

**WIN card format:**
```
🎯 [MARKET QUESTION]  🏅 HIGH-FREQ WINNING WHALE 🏅    ← whale badge inline (Option A)

✅ $57,188 | ✅ +69% ROI                               ← profit + ROI (green)
⬆️ BET UP on [outcome]                                 ← direction with outcome
🏆 🟢 68+% lifetime WR | 🔥 5-win streak              ← WR color badge + streak
📊 75% WR (30d) | n=47                                 ← 30d WR + trade count

💰 Profit: +$XXX | 💵 Size: $XX,XXX                   ← money bag ≠ stack of bills

⏰ Opened: [date] | Closes: [date]
⛓️ [polymarket.com/event/...]                         ← chains emoji for link
🐋 0xa5ef...XXXX                                       ← whale emoji for wallet

[Confidence: 87%]                                      ← if available
```

**LOSS card format:**
```
💰 $8,420 | 💲 -38% ROI                                ← loss (red) + stop sign
⬇️ BET DOWN on NO
🏆 🟠 41%~ lifetime WR | 🔴 28% 30d WR               ← amber/red WR
💵 Size: $1,100
```

---

## Key Rules — ALL AGENTS MUST FOLLOW

### Emoji Discipline
| Emoji | Meaning | Usage |
|-------|---------|-------|
| 💰 | Profit/Loss | PnL display — money bag |
| 💵 | Stack of bills | **TRADE SIZE** — NOT money bag |
| 💲 | Stop sign | Negative ROI indicator |
| 🏅 | Whale badge | Inline with market question — NOT separate line |
| ⛓️ | Chains | Hyperlink — NOT 🧭 |
| 🐋 | Whale | Wallet address prefix — NOT 👤 |

### Color Codes
| Color | Trigger | Emoji |
|-------|---------|-------|
| 🟢 Green | Positive / WR ≥65% | ✅ profit, strong WR |
| 🟠 Amber | Neutral / WR 45-64% | average WR |
| 🔴 Red | Negative / WR <40% | loss, weak WR |

### Critical Rejections (at Swarm2bot level)
- ❌ `$0.0000` entry price → REJECT
- ❌ Stock tickers ($AMAZON, $YELLEN) → REJECT
- ❌ Resolved markets → REJECT
- ❌ No valid Polymarket URL → REJECT

---

## Validation Rules
1. Entry price must be > $0.0000 from actual on-chain data
2. P&L must be real — NO generated numbers
3. Volume must be real — no repeating identical amounts
4. Only active, unresolved markets generate alerts

---

## Files Updated
- `github-team-vault/org/teams/polyshark/card_format/CARD_SPEC.md` (v1.2)
- `github-team-vault/org/teams/polyshark/card_format/card_generator.py` (ready to import)
- `ompa_vault/teams/polyshark/card_format/CARD_SPEC.md` (v1.2)
- `ompa_vault/teams/polyshark/card_format/card_generator.py`

---

## Who Needs This

**Jarv (🤖):** Implement in Swarm2bot. Import `card_generator.py`:
- `generate_card()` → WIN cards
- `generate_loss_card()` → LOSS cards
- `generate_free_teaser()` → Free tier stripped cards

**Tai (👔):** Monitor and verify cards reflect these specs. If you see old format cards, flag immediately.

**Kai (🌊):** Routing layer updated to expect v1.2 format.

---

## Status: APPROVED & FINAL
Jeff has signed off. All agents must implement before next alert cycle. 🌊

*Message sent via KaiOC 🌊 for Jeff Milam*