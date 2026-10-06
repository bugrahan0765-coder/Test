"""Prop firm rule sets and the bot's own risk policy.

All money amounts are fractions of the *initial* account balance, which is how
FTMO states its limits. Verify against the firm's current rules page before
paying for a challenge; these change.
"""
from __future__ import annotations

from dataclasses import dataclass

# FTMO resets the daily loss limit at midnight CE(S)T.
FTMO_DAY_TZ = "Europe/Prague"


@dataclass(frozen=True)
class PhaseRules:
    name: str
    profit_target: float | None  # None = funded account (no target)
    max_daily_loss: float = 0.05  # equity may not fall this far below the day's starting balance
    max_total_loss: float = 0.10  # equity may not fall below 1 - this
    min_trading_days: int = 4
    max_days: int | None = None  # our own patience cap in trading days; FTMO has no limit


FTMO_PHASE1 = PhaseRules("ftmo_phase1", profit_target=0.10)
FTMO_PHASE2 = PhaseRules("ftmo_phase2", profit_target=0.05)
FTMO_FUNDED = PhaseRules("ftmo_funded", profit_target=None, min_trading_days=0)


@dataclass(frozen=True)
class RiskPolicy:
    """How the bot sizes and throttles itself (hard-coded into the live bot too)."""

    risk_per_trade: float = 0.0075  # loss at the stop, fraction of initial balance
    daily_soft_stop: float = 0.03  # no new trades today once the day's pnl reaches -this
    dd_reduce_at: float = 0.06  # halve risk once balance is this far below initial
    dd_reduce_mult: float = 0.5
    dd_halt_at: float = 0.08  # stop trading entirely below this drawdown


@dataclass(frozen=True)
class FundedTerms:
    payout_every: int = 10  # trading days between withdrawals (FTMO: on request, ~bi-weekly)
    profit_split: float = 0.8
    horizon_days: int = 250  # how long we evaluate the funded account
