#!/usr/bin/env python3
"""
Polyshark v1.2 Card Generator — Standalone Edition
===================================================
Ready to deploy. No external dependencies beyond Python 3.6+.
Handles: WIN cards, LOSS cards, FREE TEASER cards.

Emoji key (v1.2):
- 💵 = Size (stack of bills, NOT money bag)
- 💰 = Profit/Loss (money bag)
- 💲 = Negative ROI (stop sign)
- ✅ = Positive indicator
- 🏅 = Whale badge (inline)
- ⛓️ = Link
- 🐋 = Wallet
- 🟢🟠🔴 = WR color badges

Author: KaiOC 🌊 for Jeff Milam
Version: 1.2.0
"""

from typing import Optional, Literal

# ============================================================================
# EMOJI CONSTANTS
# ============================================================================
GREEN_CHECK = "✅"
STOP_SIGN = "💲"
WHALE_BADGE = "🏅"
FIRE = "🔥"
FIRE_ON_FIRE = "🔥🔥"
CHAINS = "⛓️"
WHALE_EMOJI = "🐋"
TARGET = "🎯"
CLOCK = "⏰"
MONEY_BAG = "💰"
BILLS = "💵"
TROPHY = "🏆"
UP_ARROW = "⬆️"
DOWN_ARROW = "⬇️"
GREEN = "🟢"
AMBER = "🟠"
RED = "🔴"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def truncate_wallet(wallet: str) -> str:
    """Truncate wallet to 0xa5ef...XXXX format."""
    if len(wallet) > 10:
        return f"{wallet[:7]}...{wallet[-6:]}"
    return wallet


def get_wr_color_badge(wr: float) -> str:
    """
    Return color badge for win rate.
    🟢 ≥65% = strong (+)
    🟠 45-64% = average (~)
    🔴 <40% = below average (-)
    """
    if wr >= 65:
        return f"{GREEN} {wr}+%"
    elif wr >= 45:
        return f"{AMBER} {wr}~%"
    else:
        return f"{RED} {wr}-%"


def format_profit(profit: float) -> str:
    """Format profit with money bag and sign."""
    sign = "+" if profit >= 0 else ""
    return f"{MONEY_BAG} {sign}${abs(profit):,.0f}"


def format_roi(roi: float) -> str:
    """Format ROI with green/red indicator."""
    if roi >= 0:
        return f"{GREEN_CHECK} +{roi}% ROI"
    else:
        return f"{STOP_SIGN} {roi}% ROI"


def format_streak(streak: int) -> str:
    """Format streak with fire emoji."""
    if streak >= 8:
        return f"{FIRE_ON_FIRE} {streak}-win streak"
    elif streak >= 5:
        return f"{FIRE} {streak}-win streak"
    return ""


def format_whale_badge(is_high_priority: bool) -> str:
    """Return inline whale badge if high priority whale."""
    if is_high_priority:
        return f"  {WHALE_BADGE} HIGH-FREQ WINNING WHALE {WHALE_BADGE}"
    return ""


# ============================================================================
# CARD GENERATORS
# ============================================================================

def generate_win_card(
    market_question: str,
    direction: Literal["UP", "DOWN"],
    outcome: str,
    entry_price: float,
    stake: float,
    profit: float,
    roi: float,
    lifetime_wr: float,
    wr_30d: float,
    trade_count: int,
    streak: int,
    size: float,
    opened: str,
    closes: str,
    polymarket_url: str,
    wallet_address: str,
    is_high_priority: bool = False,
    confidence: Optional[int] = None,
    resolved: Optional[str] = None
) -> str:
    """
    Generate a WIN card in v1.2 format.
    
    Example output:
    🎯 Will BTC exceed $100K by June?  🏅 HIGH-FREQ WINNING WHALE 🏅

    ✅ $3,704,561 | ✅ +127% ROI
    ⬆️ BET UP on YES

    🏆 🟢 71+% lifetime WR | 🔥 8-win streak
    📊 73% WR (30d) | n=47

    💰 Profit: +$3,704,561 | 💵 Size: $2,900,000
    ⏰ Opened: Apr 15 | Closes: Jun 30 | Resolved: —
    ⛓️ https://polymarket.com/event/btc-100k-june-2026
    🐋 0xa5cB...a6C8

    [Confidence: 87%]
    """
    lines = []

    # Market question with inline whale badge
    question_line = f"{TARGET} {market_question}" + format_whale_badge(is_high_priority)
    lines.append(question_line)
    lines.append("")

    # Direction
    if direction == "UP":
        lines.append(f"{UP_ARROW} BET UP on {outcome}")
    else:
        lines.append(f"{DOWN_ARROW} BET DOWN on {outcome}")
    lines.append("")

    # Profit + ROI (green/positive)
    profit_line = f"{format_profit(profit)} | {format_roi(roi)}"
    lines.append(profit_line)
    lines.append("")

    # Lifetime WR + Streak
    wr_line = f"{TROPHY} {get_wr_color_badge(lifetime_wr)} lifetime WR"
    streak_indicator = format_streak(streak)
    if streak_indicator:
        wr_line += f" | {streak_indicator}"
    lines.append(wr_line)

    # 30d WR + trade count
    lines.append(f"📊 {wr_30d}% WR (30d) | n={trade_count}")
    lines.append("")

    # Profit + Size detail
    lines.append(f"{MONEY_BAG} Profit: +${profit:,.0f} | {BILLS} Size: ${size:,.0f}")

    # Dates
    if resolved:
        lines.append(f"{CLOCK} Opened: {opened} | Closes: {closes} | Resolved: {resolved}")
    else:
        lines.append(f"{CLOCK} Opened: {opened} | Closes: {closes} | Resolved: —")

    # Polymarket link
    lines.append(f"{CHAINS} {polymarket_url}")

    # Wallet
    lines.append(f"{WHALE_EMOJI} {truncate_wallet(wallet_address)}")

    # Confidence (if available)
    if confidence is not None:
        lines.append(f"[Confidence: {confidence}%]")

    return "\n".join(lines)


def generate_loss_card(
    market_question: str,
    direction: Literal["UP", "DOWN"],
    outcome: str,
    entry_price: float,
    stake: float,
    loss: float,
    roi: float,
    lifetime_wr: float,
    wr_30d: float,
    trade_count: int,
    streak: int,
    size: float,
    opened: str,
    closes: str,
    polymarket_url: str,
    wallet_address: str,
    is_high_priority: bool = False,
    confidence: Optional[int] = None,
    resolved: Optional[str] = None
) -> str:
    """
    Generate a LOSS card in v1.2 format.
    
    Example output:
    🎯 Will BTC exceed $100K by June?  🏅 HIGH-FREQ WINNING WHALE 🏅

    💰 $847 | 💲 -38% ROI
    ⬇️ BET DOWN on NO

    🏆 🟠 41%~ lifetime WR
    📊 🔴 28-% 30d WR

    💰 Loss: -$847 | 💵 Size: $2,230
    ⏰ Opened: Apr 15 | Closes: Jun 30 | Resolved: —
    ⛓️ https://polymarket.com/event/btc-100k-june-2026
    🐋 0xa5cB...a6C8

    [Confidence: 72%]
    """
    lines = []

    # Market question with inline whale badge
    question_line = f"{TARGET} {market_question}" + format_whale_badge(is_high_priority)
    lines.append(question_line)
    lines.append("")

    # Loss + ROI (red)
    loss_line = f"{MONEY_BAG} ${abs(loss):,.0f} | {STOP_SIGN} {roi}% ROI"
    lines.append(loss_line)
    lines.append("")

    # Direction
    if direction == "UP":
        lines.append(f"{UP_ARROW} BET UP on {outcome}")
    else:
        lines.append(f"{DOWN_ARROW} BET DOWN on {outcome}")
    lines.append("")

    # Lifetime WR
    lines.append(f"{TROPHY} {get_wr_color_badge(lifetime_wr)} lifetime WR")

    # 30d WR
    lines.append(f"📊 {get_wr_color_badge(wr_30d)} 30d WR")
    lines.append("")

    # Loss + Size detail
    lines.append(f"{MONEY_BAG} Loss: -${abs(loss):,.0f} | {BILLS} Size: ${size:,.0f}")

    # Dates
    if resolved:
        lines.append(f"{CLOCK} Opened: {opened} | Closes: {closes} | Resolved: {resolved}")
    else:
        lines.append(f"{CLOCK} Opened: {opened} | Closes: {closes} | Resolved: —")

    # Polymarket link
    lines.append(f"{CHAINS} {polymarket_url}")

    # Wallet
    lines.append(f"{WHALE_EMOJI} {truncate_wallet(wallet_address)}")

    # Confidence (if available)
    if confidence is not None:
        lines.append(f"[Confidence: {confidence}%]")

    return "\n".join(lines)


def generate_free_teaser(
    market_question: str,
    direction: Literal["UP", "DOWN"],
    outcome: str,
    entry_price: float,
    opened: str,
    polymarket_url: str,
    resolved: Optional[str] = None
) -> str:
    """
    Generate a FREE TEASER card in v1.2 format.
    Stripped — no profit, no ROI, no win rate.
    
    Example output:
    🎯 Will BTC exceed $100K by June?
    ⬆️ BET UP on YES

    📊 Entry price: $0.560
    📅 Opened: Apr 15
    ✅ Resolved: Jun 30
    ⛓️ https://polymarket.com/event/btc-100k-june-2026
    """
    lines = []

    # Market question
    lines.append(f"{TARGET} {market_question}")

    # Direction
    if direction == "UP":
        lines.append(f"{UP_ARROW} BET UP on {outcome}")
    else:
        lines.append(f"{DOWN_ARROW} BET DOWN on {outcome}")
    lines.append("")

    # Entry price
    lines.append(f"📊 Entry price: ${entry_price:.3f}")

    # Dates
    if resolved:
        lines.append(f"📅 Opened: {opened}")
        lines.append(f"✅ Resolved: {resolved}")
    else:
        lines.append(f"📅 Opened: {opened}")

    # Polymarket link
    lines.append(f"{CHAINS} {polymarket_url}")

    return "\n".join(lines)


def generate_consolidated_card(
    market_question: str,
    direction: Literal["UP", "DOWN"],
    outcome: str,
    total_profit: float,
    combined_roi: float,
    num_trades: int,
    total_size: float,
    lifetime_wr: float,
    wr_30d: float,
    trade_count: int,
    streak: int,
    opened: str,
    closes: str,
    polymarket_url: str,
    wallet_address: str,
    is_high_priority: bool = False
) -> str:
    """
    Generate a CONSOLIDATED card for same wallet + same market dedup.
    Shows combined metrics across multiple trades.
    """
    lines = []

    # Market question with consolidated tag and whale badge
    badge = format_whale_badge(is_high_priority)
    lines.append(f"{TARGET} {market_question}{badge}")
    lines.append(f"📦 CONSOLIDATED — {num_trades} trades")
    lines.append("")

    # Profit + ROI (green/positive)
    profit_line = f"{format_profit(total_profit)} | {format_roi(combined_roi)}"
    lines.append(profit_line)
    lines.append("")

    # Direction
    if direction == "UP":
        lines.append(f"{UP_ARROW} BET UP on {outcome}")
    else:
        lines.append(f"{DOWN_ARROW} BET DOWN on {outcome}")
    lines.append("")

    # Total size + trade count
    lines.append(f"{BILLS} Total Size: ${total_size:,.0f} ({num_trades} trades)")
    lines.append("")

    # Lifetime WR + Streak
    wr_line = f"{TROPHY} {get_wr_color_badge(lifetime_wr)} lifetime WR"
    streak_indicator = format_streak(streak)
    if streak_indicator:
        wr_line += f" | {streak_indicator}"
    lines.append(wr_line)

    # 30d WR + trade count
    lines.append(f"📊 {wr_30d}% WR (30d) | n={trade_count}")

    # Dates
    lines.append(f"{CLOCK} Opened: {opened} | Closes: {closes}")
    lines.append(f"{CHAINS} {polymarket_url}")
    lines.append(f"{WHALE_EMOJI} {truncate_wallet(wallet_address)}")

    return "\n".join(lines)


# ============================================================================
# STANDALONE TEST / EXAMPLE
# ============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("POLYSHARK CARD GENERATOR v1.2.0 — STANDALONE EDITION")
    print("=" * 60)
    print()

    # WIN card example
    print("WIN CARD:")
    print("-" * 40)
    win = generate_win_card(
        market_question="Will BTC exceed $100K by June 2026?",
        direction="UP",
        outcome="YES",
        entry_price=0.442,
        stake=2900000,
        profit=3704561,
        roi=127,
        lifetime_wr=71,
        wr_30d=73,
        trade_count=47,
        streak=8,
        size=2900000,
        opened="Apr 15",
        closes="Jun 30",
        polymarket_url="https://polymarket.com/event/btc-100k-june-2026",
        wallet_address="0xa5cB1234567890abcdef1234567890abcdef12",
        is_high_priority=True,
        confidence=87
    )
    print(win)
    print()

    # LOSS card example
    print("LOSS CARD:")
    print("-" * 40)
    loss = generate_loss_card(
        market_question="Will ETH exceed $5K by end of year?",
        direction="DOWN",
        outcome="NO",
        entry_price=0.38,
        stake=2230,
        loss=847,
        roi=-38,
        lifetime_wr=41,
        wr_30d=28,
        trade_count=47,
        streak=0,
        size=2230,
        opened="Apr 20",
        closes="Dec 31",
        polymarket_url="https://polymarket.com/event/eth-5k-2026",
        wallet_address="0xa5cB1234567890abcdef1234567890abcdef12",
        is_high_priority=False,
        confidence=72
    )
    print(loss)
    print()

    # FREE TEASER example
    print("FREE TEASER CARD:")
    print("-" * 40)
    teaser = generate_free_teaser(
        market_question="Will Lakers win the championship?",
        direction="UP",
        outcome="Lakers",
        entry_price=0.380,
        opened="Apr 15",
        polymarket_url="https://polymarket.com/event/lakers-championship-2026",
        resolved=None
    )
    print(teaser)
    print()

    # CONSOLIDATED example
    print("CONSOLIDATED CARD (same wallet + same market):")
    print("-" * 40)
    consolidated = generate_consolidated_card(
        market_question="Will BTC exceed $100K by June 2026?",
        direction="UP",
        outcome="YES",
        total_profit=8547,
        combined_roi=89,
        num_trades=3,
        total_size=3963,
        lifetime_wr=71,
        wr_30d=73,
        trade_count=47,
        streak=5,
        opened="Apr 15",
        closes="Jun 30",
        polymarket_url="https://polymarket.com/event/btc-100k-june-2026",
        wallet_address="0xa5cB1234567890abcdef1234567890abcdef12",
        is_high_priority=False
    )
    print(consolidated)
    print()

    print("=" * 60)
    print("READY FOR DEPLOYMENT")
    print("=" * 60)