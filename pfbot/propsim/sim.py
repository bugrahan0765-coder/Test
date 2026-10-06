"""Challenge / funded-account simulator and Monte Carlo.

Input is a backtest trade list (R, mae_R, entry/exit times). Trades are
grouped into trading days in the firm's timezone. Sizing is a fixed fraction
of the *initial* balance (prop limits are stated on the initial balance), so
balance = 1 + sum(risk_i * R_i).

Floating losses count towards the limits: while a trade is open its worst
point is taken to be its MAE, and trades that overlap in time are assumed to
hit their MAEs simultaneously (conservative).

Monte Carlo resamples whole trading days in blocks (stationary bootstrap), which
keeps intraday dependence and some of the volatility clustering.
"""
from __future__ import annotations

from dataclasses import dataclass

import numba
import numpy as np
import pandas as pd

from .rules import FTMO_DAY_TZ, FTMO_FUNDED, FTMO_PHASE1, FTMO_PHASE2, FundedTerms, PhaseRules, RiskPolicy

STATUS = np.array(["timeout", "pass", "fail_daily", "fail_total", "funded_end"])


@dataclass
class DayBook:
    """Trades laid out by trading day: trades of day d are rows ptr[d]:ptr[d+1]."""

    days: pd.DatetimeIndex
    ptr: np.ndarray
    R: np.ndarray
    mae: np.ndarray
    entry_ns: np.ndarray
    exit_ns: np.ndarray


def trading_days(index: pd.DatetimeIndex, tz: str = FTMO_DAY_TZ) -> pd.DatetimeIndex:
    """All dates (in the firm's timezone) on which the market had bars."""
    return pd.DatetimeIndex(index.tz_convert(tz).normalize().unique()).tz_localize(None)


def build_day_book(trades: pd.DataFrame, days: pd.DatetimeIndex, tz: str = FTMO_DAY_TZ) -> DayBook:
    """Assign trades to the trading day of their entry; days without trades stay empty."""
    t = trades.sort_values("entry_time", kind="stable")
    day = pd.DatetimeIndex(t["entry_time"]).tz_convert(tz).normalize().tz_localize(None)
    days = pd.DatetimeIndex(days)
    pos = days.get_indexer(day)
    if (pos < 0).any():
        raise ValueError("some trades fall on days missing from `days`")
    order = np.argsort(pos, kind="stable")
    counts = np.bincount(pos, minlength=len(days))
    ptr = np.concatenate([[0], np.cumsum(counts)])
    as_ns = lambda s: pd.DatetimeIndex(s).as_unit("ns").asi8[order]
    return DayBook(
        days=days,
        ptr=ptr,
        R=t["R"].to_numpy(float)[order],
        mae=np.minimum(t["mae_R"].to_numpy(float), np.minimum(t["R"].to_numpy(float), 0.0))[order],
        entry_ns=as_ns(t["entry_time"]),
        exit_ns=as_ns(t["exit_time"]),
    )


@numba.njit(cache=True)
def _run_account(seq, start, ptr, R, mae, ent, ext,
                 target, min_days, max_days, daily_lim, total_lim,
                 risk0, soft, red_at, red_mult, halt_at, payout_every, split):
    """Run one account over days seq[start:]. Returns
    (status, days_used, balance, trading_days, payouts)."""
    bal = 1.0
    tdays = 0
    payouts = 0.0
    since_payout = 0
    taken = np.zeros(R.shape[0], dtype=np.bool_)
    n = seq.shape[0]
    used = 0
    for q in range(start, n):
        if max_days > 0 and used >= max_days:
            return (4 if target <= 0.0 else 0), used, bal, tdays, payouts
        used += 1
        d = seq[q]
        dd = 1.0 - bal
        risk = 0.0
        if dd < halt_at:
            risk = risk0 * (red_mult if dd >= red_at else 1.0)
        day_pnl = 0.0
        traded = False
        a, b = ptr[d], ptr[d + 1]
        for t in range(a, b):
            taken[t] = False
        if risk > 0.0:
            for t in range(a, b):
                closed = 0.0  # pnl of trades already closed when t opens
                open_adj = 0.0  # still-open trades: swap realised R for MAE
                for e in range(a, t):
                    if taken[e]:
                        if ext[e] <= ent[t]:
                            closed += R[e]
                        else:
                            open_adj += mae[e]
                if closed * risk <= -soft:
                    continue
                taken[t] = True
                traded = True
                worst = (closed + open_adj + mae[t]) * risk
                if worst <= -daily_lim:
                    return 2, used, bal + worst, tdays + 1, payouts
                if bal + worst <= 1.0 - total_lim:
                    return 3, used, bal + worst, tdays + 1, payouts
            for t in range(a, b):
                if taken[t]:
                    day_pnl += R[t] * risk
        bal += day_pnl
        if traded:
            tdays += 1
        if target > 0.0 and bal >= 1.0 + target and tdays >= min_days:
            return 1, used, bal, tdays, payouts
        if payout_every > 0:
            since_payout += 1
            if since_payout >= payout_every:
                since_payout = 0
                if bal > 1.0:
                    payouts += split * (bal - 1.0)
                    bal = 1.0
    return (4 if target <= 0.0 else 0), used, bal, tdays, payouts


def _phase_args(rules: PhaseRules, policy: RiskPolicy, funded: FundedTerms | None):
    return (
        rules.profit_target or 0.0,
        rules.min_trading_days,
        rules.max_days or 0,
        rules.max_daily_loss,
        rules.max_total_loss,
        policy.risk_per_trade,
        policy.daily_soft_stop,
        policy.dd_reduce_at,
        policy.dd_reduce_mult,
        policy.dd_halt_at,
        funded.payout_every if funded else 0,
        funded.profit_split if funded else 0.0,
    )


def run_phase(book: DayBook, seq: np.ndarray, rules: PhaseRules, policy: RiskPolicy,
              start: int = 0, funded: FundedTerms | None = None) -> dict:
    """Run one phase over a sequence of day indices into ``book``."""
    status, used, bal, tdays, pay = _run_account(
        np.asarray(seq, np.int64), start, book.ptr, book.R, book.mae, book.entry_ns, book.exit_ns,
        *_phase_args(rules, policy, funded),
    )
    return dict(status=STATUS[status], days=used, balance=bal, trading_days=tdays, payouts=pay)


def block_bootstrap_days(n_days: int, length: int, mean_block: float, rng: np.random.Generator) -> np.ndarray:
    """Stationary bootstrap of day indices (circular)."""
    out = np.empty(length, np.int64)
    p = 1.0 / mean_block
    cur = rng.integers(n_days)
    for i in range(length):
        if i > 0 and rng.random() < p:
            cur = rng.integers(n_days)
        out[i] = cur
        cur = (cur + 1) % n_days
    return out


def monte_carlo(
    book: DayBook,
    policy: RiskPolicy,
    n_paths: int = 5000,
    phase1: PhaseRules = FTMO_PHASE1,
    phase2: PhaseRules = FTMO_PHASE2,
    funded_rules: PhaseRules = FTMO_FUNDED,
    funded: FundedTerms = FundedTerms(),
    challenge_patience: int = 120,
    mean_block: float = 5.0,
    seed: int = 0,
) -> dict:
    """Simulate phase 1 -> phase 2 -> funded on resampled day sequences.

    ``challenge_patience`` caps each challenge phase in trading days (timeouts
    count as failures for our purposes even though FTMO has no time limit).
    Payouts are fractions of the account size.
    """
    rng = np.random.default_rng(seed)
    p1 = PhaseRules(**{**phase1.__dict__, "max_days": challenge_patience})
    p2 = PhaseRules(**{**phase2.__dict__, "max_days": challenge_patience})
    fr = PhaseRules(**{**funded_rules.__dict__, "max_days": funded.horizon_days})
    length = 2 * challenge_patience + funded.horizon_days
    n_days = len(book.days)
    a1, a2, af = _phase_args(p1, policy, None), _phase_args(p2, policy, None), _phase_args(fr, policy, funded)

    res = np.zeros((n_paths, 6))  # pass1, pass2, days1, days2, payouts, funded_survived
    fail_reasons = {}
    for i in range(n_paths):
        seq = block_bootstrap_days(n_days, length, mean_block, rng)
        args = (book.ptr, book.R, book.mae, book.entry_ns, book.exit_ns)
        s1, u1, *_ = _run_account(seq, 0, *args, *a1)
        res[i, 2] = u1
        if s1 != 1:
            fail_reasons[f"p1_{STATUS[s1]}"] = fail_reasons.get(f"p1_{STATUS[s1]}", 0) + 1
            continue
        res[i, 0] = 1
        s2, u2, *_ = _run_account(seq, u1, *args, *a2)
        res[i, 3] = u2
        if s2 != 1:
            fail_reasons[f"p2_{STATUS[s2]}"] = fail_reasons.get(f"p2_{STATUS[s2]}", 0) + 1
            continue
        res[i, 1] = 1
        sf, uf, bal, _, pay = _run_account(seq, u1 + u2, *args, *af)
        res[i, 4] = pay
        res[i, 5] = sf == 4
    passed = res[:, 1] == 1
    return {
        "risk_per_trade": policy.risk_per_trade,
        "p_phase1": res[:, 0].mean(),
        "p_phase2_given_1": res[res[:, 0] == 1, 1].mean() if res[:, 0].any() else 0.0,
        "p_funded": passed.mean(),
        "median_days_phase1": float(np.median(res[res[:, 0] == 1, 2])) if res[:, 0].any() else np.nan,
        "mean_payout_if_funded": res[passed, 4].mean() if passed.any() else 0.0,
        "p_survive_funded_horizon": res[passed, 5].mean() if passed.any() else 0.0,
        "expected_payout_per_attempt": res[:, 4].mean(),
        "fail_reasons": {k: v / n_paths for k, v in sorted(fail_reasons.items())},
    }


def expected_value(mc: dict, account_size: float, fee: float, fee_refunded: bool = True) -> float:
    """Expected profit of buying one challenge, in account currency."""
    refund = fee * mc["p_funded"] if fee_refunded else 0.0
    return mc["expected_payout_per_attempt"] * account_size + refund - fee


def risk_sweep(book: DayBook, risks, base: RiskPolicy = RiskPolicy(), **mc_kwargs) -> pd.DataFrame:
    """Monte Carlo for each risk-per-trade level; one row per level."""
    rows = []
    for r in risks:
        pol = RiskPolicy(**{**base.__dict__, "risk_per_trade": r})
        mc = monte_carlo(book, pol, **mc_kwargs)
        mc.pop("fail_reasons")
        rows.append(mc)
    return pd.DataFrame(rows).set_index("risk_per_trade")
