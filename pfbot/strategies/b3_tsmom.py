"""B3 - Weekly time-series momentum. Spec: research/hypotheses/B3_time_series_momentum.md

Decision = last trading day of each ISO week at 15:55 ET; daily closes are prices known at 15:55 ET.
Signal = sign of the log return from the close ``L`` trading days earlier to the decision close
(``long_only`` keeps only positive signals; a zero return gives no trade). Entry at market at the
decision time, time exit at the next week's decision instant (the re-entry, if the new signal is
non-zero, is a separate trade). Stop = ``k`` x sqrt(5 x HAR daily variance forecast) x decision
price (price terms).

Interpretation notes
* Trading days = NY cash-session dates (``daily_common.ny_trading_dates``); ``L`` counts positions in
  that calendar (the date ``L`` session dates before the decision date), and the span must be at most
  ``L * 7 / 5 + 10`` calendar days (excluded months make a lookback invalid -> skipped).
* A week's decision date is its last session date in the data, required to fall on Thu/Fri and to
  be followed by a later session date (the data must show the week ended). A trade needs the next
  week to be the immediately following ISO week; its exit is that week's decision instant (15:55 ET, or
  the half-day rule: last bar of that session) whether or not a new signal is taken then. The
  final week of the data has no exit and is not traded.
* Entry on a day without a bar within 5 min of 15:55 ET (early-close days such as the day after
  Thanksgiving) has no decision price (``price_at`` is NaN) and is skipped, per spec.
* ENGINE BUSY RULE: the engine drops a signal whose first active bar index i0 <= the exit bar index
  of the previous trade. The previous trade exits at the open of the 15:55 bar and the next
  entry would be active from that same bar, so back-to-back weekly trades would be dropped. The signal
  ``time`` is therefore set to the start of the first bar at/after the entry instant (the 15:55
  bar, one M1 bar later than a plain A1-style decision bar), so the re-entry fills at the open of
  the 15:56 bar, one minute after the exit. Information used is still only bars that closed at or
  before 15:55 (decision price = ``price_at`` 15:55); the stop distance uses that price.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pfbot.research import harness
from pfbot.research.harness import SESSIONS, local_times
from pfbot.strategies import daily_common as dc

CONFIGS = harness.grid(L=[20, 60, 120], k=[2, 3], long_only=[False, True])

WEEK_DAYS = 5
COLUMNS = ["time", "side", "order", "stop_dist", "exit_time", "date", "exit_date", "mom"]


def weekly_decisions(dates: pd.DatetimeIndex) -> np.ndarray:
    """Positions of each week's decision date (last session date of the ISO week, Thu/Fri, with a
    later session date present)."""
    n = len(dates)
    monday = (dates - pd.to_timedelta(np.asarray(dates.dayofweek), unit="D")).to_numpy()
    last = np.zeros(n, bool)
    last[:-1] = monday[:-1] != monday[1:]
    return np.flatnonzero(last & (np.asarray(dates.dayofweek) >= 3))


def signals(bars: pd.DataFrame, symbol: str, L: int, k: float, long_only: bool) -> pd.DataFrame:
    """B3 signal table (time, side, order, stop_dist, exit_time + diagnostics date / exit_date / mom)
    for M1 ``bars`` of ``symbol``."""
    assert symbol in SESSIONS, symbol
    empty = pd.DataFrame({c: pd.Series(dtype=object) for c in COLUMNS})
    dates = dc.ny_trading_dates(bars)
    n = len(dates)
    D = weekly_decisions(dates)
    if len(D) < 2:
        return empty
    monday = (dates - pd.to_timedelta(np.asarray(dates.dayofweek), unit="D")).to_numpy()
    nxt_ok = (monday[D[1:]] - monday[D[:-1]]) == np.timedelta64(7, "D")  # next decision = next ISO week
    i, j = D[:-1][nxt_ok], D[1:][nxt_ok]  # decision position / exit-decision position
    enough = i >= L  # need L earlier session dates
    i, j = i[enough], j[enough]
    if len(i) == 0:
        return empty
    d_dec, d_exit, d_back = dates[i], dates[j], dates[i - L]
    span_ok = np.asarray((d_dec - d_back).days) <= int(L * 7 / 5 + 10)

    t_entry = local_times(d_dec, dc.DECISION_TIME, dc.NY)
    _dec, fill, entry_ok = dc.decision_bar(bars, t_entry)
    p_now = dc.daily_closes(bars, d_dec)
    p_back = dc.daily_closes(bars, d_back)
    exit_time, exit_ok = dc.exit_instants(bars, d_exit, dc.DECISION_TIME)
    fc = dc.daily_variance_forecast(bars, d_dec)

    with np.errstate(invalid="ignore", divide="ignore"):
        mom = np.log(p_now / p_back)
        stop_dist = k * np.sqrt(WEEK_DAYS * fc) * p_now
    side = np.sign(mom)
    keep = (
        span_ok & entry_ok & exit_ok & np.isfinite(mom) & (side != 0)
        & np.isfinite(stop_dist) & (stop_dist > 0)
    )
    if long_only:
        keep &= side > 0
    if not keep.any():
        return empty
    sig = pd.DataFrame(
        {
            "time": fill[keep],  # see "ENGINE BUSY RULE" in the module docstring
            "side": side[keep].astype(int),
            "order": "market",
            "stop_dist": stop_dist[keep],
            "exit_time": exit_time[keep],
            "date": d_dec[keep],
            "exit_date": d_exit[keep],
            "mom": mom[keep],
        }
    ).reset_index(drop=True)
    assert (sig["time"] >= t_entry[keep]).all() and (sig["exit_time"] > sig["time"]).all()
    return sig
