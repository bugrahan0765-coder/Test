"""B2 - Overnight drift. Spec: research/hypotheses/B2_overnight_drift.md

Long at market at ``t_in`` ET on each trading day (Mon-Thu, plus Friday when ``fri``); time exit at
``t_out`` ET on the next trading day. Stop = 3 x expected std of the overnight window in price terms:
sqrt(HAR daily variance forecast for the entry date x overnight variance share) x entry-decision price.

Overnight variance share (previous 60 trading days only)
  * Window j: entry date s_j at ``t_in`` -> next session date s_{j+1} at ``t_out``. Its realized
    variance is the sum of squared 5-minute log returns (``intraday_returns``, same grid and
    conventions as the daily RV, so gaps over the maintenance break / weekend are excluded in both)
    over 5-minute bars that lie entirely in the window (open >= t_in and open + 5min <= t_out).
  * Denominator = daily RV of the trading day s_{j+1} (17:00 NY roll, labelled by its end date),
    which contains most of the window (18:00 -> t_out); it is also a completed day by then.
  * share on date d = sum(window RV) / sum(daily RV) pooled over the windows whose exit date is
    one of the 60 session dates strictly before d (exit date <= previous session date, so every
    window has finished and its RV is known at the 15:55/16:10 decision of d). Pooling (ratio of
    sums) rather than a mean of ratios keeps it stable. At least 40 of the 60 windows must be valid,
    else the date is skipped. All windows are pooled, whatever ``fri`` (a Friday window includes the
    weekend but not the weekend gap).
  * Window variance = HAR forecast for the entry date (``daily_common.daily_variance_forecast``) x share.

Interpretation notes
* Entry needs a decision bar within 5 min before ``t_in`` and a fill bar within 5 min after (so a
  half-day with no bar at 15:55/16:10 is skipped). The exit needs a bar in [t_out, t_out + 5min) on
  the next session date; there is no early-close fallback for a morning exit (it would mean holding
  all day), the date is skipped instead.
* "Next trading day" is the next session date in the data; entries whose next session date is more
  than 4 calendar days later (data holes) are skipped. Friday = weekday of the entry date.
* Signal ``time`` is the start of the last M1 bar before ``t_in`` (as A1).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pfbot.features.volatility import daily_realized_vol, intraday_returns
from pfbot.research import harness
from pfbot.research.harness import SESSIONS, local_times
from pfbot.strategies import daily_common as dc

CONFIGS = harness.grid(t_in=["15:55", "16:10"], t_out=["09:31", "09:45"], fri=[False, True])

STOP_MULT = 3.0
SHARE_WINDOWS = 60
MIN_SHARE_WINDOWS = 40
MAX_GAP_DAYS = 4
GRID = pd.Timedelta(minutes=5)
COLUMNS = ["time", "side", "order", "stop_dist", "exit_time", "date", "exit_date", "share"]


def overnight_share(bars: pd.DataFrame, dates: pd.DatetimeIndex, t_in: str, t_out: str,
                    rv: pd.Series | None = None) -> np.ndarray:
    """Overnight variance share usable at the entry on each ``dates[p]`` (NaN if unavailable);
    see the module docstring for the definition and alignment."""
    n = len(dates)
    out = np.full(n, np.nan)
    if n < 3:
        return out
    if rv is None:
        rv = daily_realized_vol(bars)
    ir = intraday_returns(bars, "5min")
    r2 = (ir["r"] ** 2).to_numpy(float)
    cs = np.concatenate([[0.0], np.cumsum(np.nan_to_num(r2))])
    idx = ir.index

    t0 = local_times(dates[:-1], t_in, dc.NY)  # window j starts at dates[j]
    t1 = local_times(dates[1:], t_out, dc.NY)  # and ends at dates[j+1]
    ok = ~(pd.isna(t0) | pd.isna(t1)) & (t1 > t0)
    t0f, t1f = t0.where(ok, dc._EPOCH), t1.where(ok, dc._EPOCH)
    a = idx.searchsorted(t0f, side="left")
    b = idx.searchsorted(t1f - GRID, side="right")  # bars with open <= t_out - 5min
    ok &= b > a
    ss = np.where(ok, cs[np.clip(b, 0, len(cs) - 1)] - cs[np.clip(a, 0, len(cs) - 1)], np.nan)
    day_rv = rv.reindex(dates[1:]).to_numpy(float)  # RV of the exit date's trading day
    ok = ok & np.isfinite(ss) & np.isfinite(day_rv) & (day_rv > 0)
    ss_v, rv_v = np.where(ok, ss, 0.0), np.where(ok, day_rv, 0.0)

    c_ss = np.concatenate([[0.0], np.cumsum(ss_v)])
    c_rv = np.concatenate([[0.0], np.cumsum(rv_v)])
    c_ok = np.concatenate([[0], np.cumsum(ok.astype(int))])
    # windows j in [p - 61, p - 2]  (exit dates p-60 .. p-1)
    for p in range(SHARE_WINDOWS + 1, n):
        lo, hi = p - SHARE_WINDOWS - 1, p - 2
        cnt = c_ok[hi + 1] - c_ok[lo]
        den = c_rv[hi + 1] - c_rv[lo]
        if cnt >= MIN_SHARE_WINDOWS and den > 0:
            out[p] = (c_ss[hi + 1] - c_ss[lo]) / den
    return out


def signals(bars: pd.DataFrame, symbol: str, t_in: str, t_out: str, fri: bool) -> pd.DataFrame:
    """B2 signal table (time, side, order, stop_dist, exit_time + diagnostics date / exit_date /
    share) for M1 ``bars`` of ``symbol``."""
    assert symbol in SESSIONS, symbol
    empty = pd.DataFrame({c: pd.Series(dtype=object) for c in COLUMNS})
    dates = dc.ny_trading_dates(bars)
    if len(dates) < SHARE_WINDOWS + 3:
        return empty
    rv = daily_realized_vol(bars)
    share = overnight_share(bars, dates, t_in, t_out, rv)
    fc_all = dc.daily_variance_forecast(bars, dates, rv)

    e_dates, x_dates = dates[:-1], dates[1:]
    gap = np.asarray((x_dates - e_dates).days)
    dow = np.asarray(e_dates.dayofweek)
    day_ok = (dow <= 3) | ((dow == 4) & fri)
    t_entry = local_times(e_dates, t_in, dc.NY)
    dec, _fill, entry_ok = dc.decision_bar(bars, t_entry)
    p_entry = dc.price_at(bars, t_entry)
    exit_time, exit_ok = dc.exit_instants(bars, x_dates, t_out, early_close_fallback=False)

    with np.errstate(invalid="ignore"):
        var = fc_all[:-1] * share[:-1]
        stop_dist = STOP_MULT * np.sqrt(var) * p_entry
    keep = day_ok & (gap <= MAX_GAP_DAYS) & entry_ok & exit_ok & np.isfinite(stop_dist) & (stop_dist > 0)
    if not keep.any():
        return empty
    sig = pd.DataFrame(
        {
            "time": dec[keep],
            "side": 1,
            "order": "market",
            "stop_dist": stop_dist[keep],
            "exit_time": exit_time[keep],
            "date": e_dates[keep],
            "exit_date": x_dates[keep],
            "share": share[:-1][keep],
        }
    ).reset_index(drop=True)
    assert (sig["time"] + dc.BAR <= t_entry[keep]).all()
    return sig
