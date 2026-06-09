#!/usr/bin/env python3
"""
Polyshark Card Generator — v1.2
Integrated format for Swarm2bot alerts
Built: 2026-04-25 by KaiOC 🌊

Usage:
    from card_generator import generate_card, generate_loss_card
    
    card = generate_card(
        market_question="Will Lakers win?",
        direction="UP",
        outcome="Lakers",
        entry_price=0.560,
        stake=1321,
        profit=847,
        roi=69,
        lifetime_wr=68,
        wr_30d=75,
        trade_count=47,
        streak=5,
        size=5200,
        opened="Apr 22",
        closes="Apr 26",
        polymarket_url="https://polymarket.com/event/lal-elc-mad-2026-04-22",
        wallet_address="0xa5ef1234567890abcdef1234567890abcdef12",
        is_high_priority=True,
        confidence=87
    )
    
    print(card)
"""

from typing import Optional

# ============================================================================
# COLOR INDICATORS
# ============================================================================
GREEN = "🟢"
AMBER = "🟠"
RED = "🔴"
CHECKMARK = "✅"
STOP = "💲"
WHALE = "🏅"
FIRE = "🔥"
FIRE_ON_FIRE = "🔥🔥"
CHAINS = "⛓️"
WHALE_EMOJI = "🐋"
TARGET = "🎯"
CLOCK = "⏰"
MONEY = "💰"
BILLS = "💵"  # Stack of bills — used for trade Size

# Old emojis (avoid confusion):
# 💰 = Profit/Loss (money bag - use for PnL)
# 💳 = Money bag - avoid, use 💵 for Size instead
TROPHY = "🏆"

def get_wr_color_badge(wr: float, period: str = "lifetime") -> str:
    """Return color badge for win rate."""
    if wr >= 65:
        sign = "+" if period == "lifetime" else ""
        return f"{GREEN} {wr}{sign}%"
    elif wr >= 45:
        sign = "~"
        return f"{AMBER} {wr}{sign}%"
    else:
        sign = "-" if period == "30d" else ""
        return f"{RED} {wr}{sign}%"

def get_roi_indicator(roi: float) -> str:
    """Return ROI with color."""
    if roi >= 0:
        return f"{CHECKMARK} +{roi}% ROI"
    else:
        return f"{STOP} {roi}% ROI"

def get_profit_indicator(profit: float) -> str:
    """Return profit with color."""
    if profit >= 0:
        return f"{CHECKMARK} ${abs(profit):,.0f}"
    else:
        return f"{MONEY} ${abs(profit):,.0f}"

def get_streak_indicator(streak: int) -> str:
    """Return streak with fire emoji."""
    if streak >= 8:
        return f"{FIRE_ON_FIRE} {streak}-win streak"
    elif streak >= 5:
        return f"{FIRE} {streak}-win streak"
    return ""

def get_whale_badge(is_high_priority: bool, wallet: str = "") -> str:
    """Return whale badge if high priority."""
    if is_high_priority:
        return f"{WHALE} HIGH-FREQ WINNING WHALE {WHALE}"
    return ""

def format_wallet(wallet: str) -> str:
    """Format wallet address with whale emoji."""
    if len(wallet) > 10:
        truncated = wallet[:7] + "..." + wallet[-6:]
    else:
        truncated = wallet
    return f"{WHALE_EMOJI} {truncated}"

def generate_card(
    market_question: str,
    direction: str,
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
    Generate a PRO card in integrated format v1.2.
    
    Args:
        market_question: Full market question text
        direction: "UP" or "DOWN"
        outcome: Outcome name (e.g., "Lakers", "YES", "NO")
        entry_price: Entry price from on-chain
        stake: Stake amount in USDC
        profit: Realized PnL in USD
        roi: ROI percentage
        lifetime_wr: Lifetime win rate percentage
        wr_30d: 30-day win rate percentage
        trade_count: Total trades for this whale
        streak: Current win streak
        size: Trade size in USDC
        opened: Market open date
        closes: Market close date
        polymarket_url: Full Polymarket URL
        wallet_address: Full wallet address
        is_high_priority: Show whale badge
        confidence: Optional confidence score (0-100)
        resolved: Optional resolution date
    """
    lines = []
    
    # Whale badge inline with market question (if high priority)
    badge = get_whale_badge(is_high_priority)
    question_line = f"{TARGET} {market_question}"
    if badge:
        question_line += f"  {badge}"
    lines.append(question_line)
    lines.append("")
    
    # Direction arrow based on UP/DOWN
    if direction.upper() == "UP":
        direction_emoji = "⬆️"
        direction_text = "BET UP"
    else:
        direction_emoji = "⬇️"
        direction_text = "BET DOWN"
    
    # Profit + ROI on one line
    profit_line = f"{get_profit_indicator(profit)} | {get_roi_indicator(roi)}"
    lines.append(profit_line)
    
    # Direction with outcome
    lines.append(f"{direction_emoji} {direction_text} on {outcome}")
    lines.append("")
    
    # Lifetime WR + Streak
    wr_line = f"{TROPHY} {get_wr_color_badge(lifetime_wr, 'lifetime')} lifetime WR"
    streak_indicator = get_streak_indicator(streak)
    if streak_indicator:
        wr_line += f" | {streak_indicator}"
    lines.append(wr_line)
    
    # 30d WR + trade count
    lines.append(f"📊 {wr_30d}% WR (30d) | n={trade_count}")
    lines.append("")
    
    # Profit + Size detail line
    lines.append(f"{MONEY} Profit: +${profit:,.0f} | {BILLS} Size: ${size:,.0f}")
    
    # Dates
    if resolved:
        lines.append(f"{CLOCK} Opened: {opened} | Closes: {closes} | Resolved: {resolved}")
    else:
        lines.append(f"{CLOCK} Opened: {opened} | Closes: {closes}")
    
    # Polymarket link
    lines.append(f"{CHAINS} {polymarket_url}")
    
    # Wallet
    lines.append(format_wallet(wallet_address))
    
    # Confidence (if available)
    if confidence is not None:
        lines.append(f"[Confidence: {confidence}%]")
    
    return "\n".join(lines)


def generate_loss_card(
    market_question: str,
    direction: str,
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
    Generate a LOSS card in integrated format v1.2.
    
    Same as generate_card but loss indicators are red/stop sign.
    """
    lines = []
    
    # Whale badge inline with market question (if high priority)
    badge = get_whale_badge(is_high_priority)
    question_line = f"{TARGET} {market_question}"
    if badge:
        question_line += f"  {badge}"
    lines.append(question_line)
    lines.append("")
    
    # Direction arrow based on UP/DOWN
    if direction.upper() == "UP":
        direction_emoji = "⬆️"
        direction_text = "BET UP"
    else:
        direction_emoji = "⬇️"
        direction_text = "BET DOWN"
    
    # Loss + ROI (red with stop sign)
    loss_line = f"{MONEY} ${abs(loss):,.0f} | {STOP} {roi}% ROI"
    lines.append(loss_line)
    
    # Direction with outcome
    lines.append(f"{direction_emoji} {direction_text} on {outcome}")
    lines.append("")
    
    # Lifetime WR (amber for average, red for below avg)
    lines.append(f"{TROPHY} {get_wr_color_badge(lifetime_wr, 'lifetime')} lifetime WR")
    
    # 30d WR (if significantly different or important)
    lines.append(f"📊 {get_wr_color_badge(wr_30d, '30d')} 30d WR")
    lines.append("")
    
    # Loss + Size detail line
    lines.append(f"{MONEY} Loss: -${abs(loss):,.0f} | {BILLS} Size: ${size:,.0f}")
    
    # Dates
    if resolved:
        lines.append(f"{CLOCK} Opened: {opened} | Closes: {closes} | Resolved: {resolved}")
    else:
        lines.append(f"{CLOCK} Opened: {opened} | Closes: {closes}")
    
    # Polymarket link
    lines.append(f"{CHAINS} {polymarket_url}")
    
    # Wallet
    lines.append(format_wallet(wallet_address))
    
    # Confidence (if available)
    if confidence is not None:
        lines.append(f"[Confidence: {confidence}%]")
    
    return "\n".join(lines)


def generate_free_teaser(
    market_question: str,
    direction: str,
    outcome: str,
    entry_price: float,
    opened: str,
    polymarket_url: str,
    resolved: Optional[str] = None
) -> str:
    """
    Generate a Free Teaser card (stripped format).
    Shows: Play, Direction, Entry Price, Opened Date, Link only.
    """
    lines = []
    
    # Market question
    lines.append(f"{TARGET} {market_question}")
    
    # Direction with outcome
    if direction.upper() == "UP":
        direction_emoji = "⬆️"
        direction_text = "BET UP"
    else:
        direction_emoji = "⬇️"
        direction_text = "BET DOWN"
    
    lines.append(f"{direction_emoji} {direction_text} on {outcome}")
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


# ============================================================================
# TEST / EXAMPLE
# ============================================================================
if __name__ == "__main__":
    # WIN card example
    win_card = generate_card(
        market_question="Will Club Atlético de Madrid win on 2026-04-22?",
        direction="UP",
        outcome="YES",
        entry_price=0.560,
        stake=1321,
        profit=847,
        roi=69,
        lifetime_wr=68,
        wr_30d=75,
        trade_count=47,
        streak=5,
        size=5200,
        opened="Apr 22",
        closes="Apr 26",
        polymarket_url="https://polymarket.com/event/lal-elc-mad-2026-04-22",
        wallet_address="0xa5ef1234567890abcdef1234567890abcdef12",
        is_high_priority=False,
        confidence=87
    )
    
    print("=" * 50)
    print("WIN CARD EXAMPLE")
    print("=" * 50)
    print(win_card)
    print()
    
    # LOSS card example
    loss_card = generate_loss_card(
        market_question="Will Bitcoin exceed $100K by June 2026?",
        direction="DOWN",
        outcome="NO",
        entry_price=0.42,
        stake=1100,
        loss=420,
        roi=-38,
        lifetime_wr=41,
        wr_30d=28,
        trade_count=47,
        streak=0,
        size=1100,
        opened="Apr 20",
        closes="Jun 30",
        polymarket_url="https://polymarket.com/event/btc-100k-june-2026",
        wallet_address="0xa5ef1234567890abcdef1234567890abcdef12",
        is_high_priority=False,
        confidence=72
    )
    
    print("=" * 50)
    print("LOSS CARD EXAMPLE")
    print("=" * 50)
    print(loss_card)
    print()
    
    # Free teaser example
    free_teaser = generate_free_teaser(
        market_question="Will Lakers win the championship?",
        direction="UP",
        outcome="Lakers",
        entry_price=0.38,
        opened="Apr 15",
        polymarket_url="https://polymarket.com/event/lakers-championship-2026"
    )
    
    print("=" * 50)
    print("FREE TEASER EXAMPLE")
    print("=" * 50)
    print(free_teaser)