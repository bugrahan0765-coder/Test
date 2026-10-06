"""A2 - opening range momentum (pre-registered in research/hypotheses/A2_opening_range.md).

One trade per session at most. The opening range is the M1 bars in [open, open + N);
the trade direction is sign(C - O) of that range, the stop is the opposite end of the
range and the position is flattened at the end-of-session time exit.

Information set: everything used for the signal of a given day (range O/H/L/C, the
expected-vol forecast from ``expected_bar_vol``) is known at the close of the last M1
bar of the range. The signal row ``time`` is the start of that bar, so the engine
activates the order from open + N (the next bar).

Engine detail: for ``candle`` (market) orders the engine computes its own intended entry
as the range close C plus half the spread of that bar, and sizes R from it. Because the
target is passed as an absolute ``target_price`` computed from the *spread-free* C
(tR x |C - stop|, as in the spec), the realised target multiple is tR x |C - stop| /
(|C - stop| + spread/2) of the engine's R, i.e. marginally below tR (a few percent for
N=5 on a quiet day). Breakout orders are unaffected (intended entry = trigger price).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pfbot.features.volatility import expected_bar_vol
from pfbot.research.harness import SESSIONS, local_times, session_dates, window_stats

HYPOTHESIS = "A2"

# (local "HH:MM" session-end time exit, local "HH:MM" breakout order expiry) per timezone
_EXIT_LOCAL = {"America/New_York": "15:55", "Europe/Berlin": "17:25"}
_EXPIRY_LOCAL = {"America/New_York": "12:00", "Europe/Berlin": "11:30"}

MIN_RANGE_COVERAGE = 0.80  # fraction of the N minutes that must have an M1 bar
DEGENERATE_FRAC = 0.25  # skip if H - L < 0.25 x expected std of the window (price terms)
_VOL_FREQ_MIN = 5  # expected_bar_vol default grid; N must be a multiple of it

COLUMNS = ["time", "side", "order", "price", "expiry", "stop_price", "target_price", "exit_time"]

CONFIGS: list[dict] = (
    [dict(N=N, tR=tR, entry="candle") for N in (5, 15, 30) for tR in (None, 3, 10)]
    + [dict(N=15, tR=tR, entry="breakout") for tR in (None, 3, 10)]
)


def _empty() -> pd.DataFrame:
    return pd.DataFrame({
        "time": pd.DatetimeIndex([], tz="UTC"),
        "side": np.array([], dtype=int),
        "order": pd.Series([], dtype=object),
        "price": pd.Series([], dtype=float),
        "expiry": pd.DatetimeIndex([], tz="UTC"),
        "stop_price": pd.Series([], dtype=float),
        "target_price": pd.Series([], dtype=float),
        "exit_time": pd.DatetimeIndex([], tz="UTC"),
    })[COLUMNS]


def signals(
    bars: pd.DataFrame,
    symbol: str,
    N: int,
    tR: float | None,
    entry: str,
    exp_vol: pd.Series | None = None,
) -> pd.DataFrame:
    """Engine signal table for A2 on M1 ``bars`` (canonical schema, UTC index).

    ``exp_vol`` optionally passes a precomputed ``expected_bar_vol(bars, tz=<session tz>)``
    (saves recomputation across the grid); it must come from the same bars.
    """
    if entry not in ("candle", "breakout"):
        raise ValueError(f"entry must be 'candle' or 'breakout', got {entry!r}")
    if N % _VOL_FREQ_MIN or N <= 0:
        raise ValueError(f"N must be a positive multiple of {_VOL_FREQ_MIN} minutes")
    sess = SESSIONS[symbol]
    tz = sess.tz
    if tz not in _EXIT_LOCAL:
        raise ValueError(f"A2 is not defined for {symbol}")

    dates = session_dates(bars, sess)  # days with a bar exactly at the open minute
    if len(dates) == 0:
        return _empty()
    opens = local_times(dates, sess.open, tz)
    keep = ~pd.isna(opens)
    dates, opens = dates[keep], opens[keep]
    ends = opens + pd.Timedelta(minutes=N)

    st = window_stats(bars, opens, ends)
    O, H, L, C = (st[k].to_numpy() for k in ("open", "high", "low", "close"))
    n_present = st["n"].to_numpy()
    idx = bars.index
    # start time of the last M1 bar inside each window (NaT-safe: windows with n == 0 are dropped)
    last_pos = idx.searchsorted(ends, side="left") - 1
    first_pos = idx.searchsorted(opens, side="left")
    ok = (n_present >= MIN_RANGE_COVERAGE * N) & (last_pos >= 0)
    first_at_open = np.zeros(len(opens), bool)
    in_range = first_pos < len(idx)
    first_at_open[in_range] = idx[first_pos[in_range]] == opens[in_range]
    ok &= first_at_open
    sig_time = idx[np.clip(last_pos, 0, None)]

    # expected std of the window: sqrt(sum of 5-min bar variances) in log-return units
    if exp_vol is None:
        exp_vol = expected_bar_vol(bars, tz=tz)
    k = N // _VOL_FREQ_MIN
    ev = np.column_stack([
        exp_vol.reindex(opens + pd.Timedelta(minutes=_VOL_FREQ_MIN * i)).to_numpy(float) for i in range(k)
    ])
    exp_std = np.sqrt((ev ** 2).sum(axis=1)) * C  # NaN if any bin is missing / warm-up
    with np.errstate(invalid="ignore"):
        ok &= ~np.isnan(exp_std) & ~((H - L) < DEGENERATE_FRAC * exp_std)

    with np.errstate(invalid="ignore"):
        side = np.sign(C - O).astype(int)
    ok &= side != 0

    stop = np.where(side > 0, L, H)
    if entry == "candle":
        intended = C
        order, trig = "market", np.full(len(opens), np.nan)
    else:
        intended = np.where(side > 0, H, L)
        order, trig = "stop", intended.copy()
    with np.errstate(invalid="ignore"):
        ok &= side * (intended - stop) > 0  # stop strictly on the protective side

    if tR is None:
        target = np.full(len(opens), np.nan)
    else:
        target = intended + side * tR * np.abs(intended - stop)

    exit_time = local_times(dates, _EXIT_LOCAL[tz], tz)
    expiry = local_times(dates, _EXPIRY_LOCAL[tz], tz) if entry == "breakout" else pd.DatetimeIndex([pd.NaT] * len(opens), tz="UTC")
    ok &= ~pd.isna(exit_time)

    out = pd.DataFrame({
        "time": sig_time,
        "side": side,
        "order": order,
        "price": trig,
        "expiry": expiry,
        "stop_price": stop,
        "target_price": target,
        "exit_time": exit_time,
    })[COLUMNS]
    out = out[ok].sort_values("time", kind="stable").reset_index(drop=True)
    return out
