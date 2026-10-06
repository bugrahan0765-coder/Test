"""B1 - Turn-of-the-month effect. Spec: research/hypotheses/B1_turn_of_month.md

Long at market at 15:55 ET on trading day ``d_in`` relative to the month end (-1 = last trading day
of the month, -2 = the one before); time exit at 15:55 ET on trading day ``d_out`` of the next month
(+1 = first trading day). Protective stop ``k`` x sqrt(HAR daily variance forecast at entry x number
of trading days held) x entry-decision price (price terms).

Interpretation notes
* Trading days = NY cash-session dates in the data (``daily_common.ny_trading_dates``). Days held =
  difference of the exit and entry positions in that calendar (e.g. d_in=-1, d_out=+2 -> 2).
* The month calendar is derived from the data, so a trade is skipped when the data cannot be trusted
  to contain the true month end / month start: the last session date of the entry month must be
  within 5 days of the calendar month end, the next month must be the calendar-next month (excluded
  months drop trades), its first session date within 5 days of the month start, and no gap between
  consecutive session dates from entry to exit may exceed 5 calendar days.
* Entry needs a decision bar within 5 min before 15:55 ET and a fill bar within 5 min after; the exit
  uses the half-day rule of ``daily_common.exit_instants``. Missing price / forecast -> skipped.
* Signal ``time`` is the start of the last M1 bar before the entry instant (as A1), so the engine
  fills at the open of the first bar at/after 15:55 ET.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pfbot.research import harness
from pfbot.research.harness import SESSIONS, local_times
from pfbot.strategies import daily_common as dc

CONFIGS = harness.grid(d_in=[-2, -1], d_out=[2, 3], k=[2, 3])

MAX_GAP_DAYS = 5
COLUMNS = ["time", "side", "order", "stop_dist", "exit_time", "date", "exit_date", "n_days"]


def month_pairs(dates: pd.DatetimeIndex, d_in: int, d_out: int) -> pd.DataFrame:
    """Positions (into ``dates``) of the entry and exit session dates for every month with a valid
    calendar (see module docstring)."""
    assert d_in < 0 and d_out > 0
    n = len(dates)
    month = dates.to_period("M")
    first = pd.Series(np.arange(n)).groupby(month.asi8).min()
    last = pd.Series(np.arange(n)).groupby(month.asi8).max()
    gap = np.diff(dates.values).astype("timedelta64[D]").astype(int)  # gap[i] = dates[i+1]-dates[i]
    rows = []
    for m in first.index:
        f, l = int(first[m]), int(last[m])
        if (m + 1) not in first.index:
            continue  # next month absent (end of data or excluded month)
        nf = int(first[m + 1])
        e, x = l + 1 + d_in, nf + d_out - 1
        if e < f or x >= int(last[m + 1]) + 1 or x >= n:
            continue
        p = month[l]
        if (p.end_time.normalize() - dates[l]).days > MAX_GAP_DAYS:
            continue
        if (dates[nf] - month[nf].start_time).days > MAX_GAP_DAYS:
            continue
        if gap[e:x].max() > MAX_GAP_DAYS:
            continue
        rows.append((e, x))
    return pd.DataFrame(rows, columns=["e", "x"], dtype=int)


def signals(bars: pd.DataFrame, symbol: str, d_in: int, d_out: int, k: float) -> pd.DataFrame:
    """B1 signal table (time, side, order, stop_dist, exit_time + diagnostics date / exit_date /
    n_days) for M1 ``bars`` of ``symbol``."""
    assert symbol in SESSIONS, symbol
    empty = pd.DataFrame({c: pd.Series(dtype=object) for c in COLUMNS})
    dates = dc.ny_trading_dates(bars)
    if len(dates) < 5:
        return empty
    pr = month_pairs(dates, d_in, d_out)
    if pr.empty:
        return empty
    e_dates, x_dates = dates[pr["e"].to_numpy()], dates[pr["x"].to_numpy()]
    n_days = (pr["x"] - pr["e"]).to_numpy()

    t_entry = local_times(e_dates, dc.DECISION_TIME, dc.NY)
    dec, _fill, entry_ok = dc.decision_bar(bars, t_entry)
    p_entry = dc.daily_closes(bars, e_dates)
    exit_time, exit_ok = dc.exit_instants(bars, x_dates, dc.DECISION_TIME)
    fc = dc.daily_variance_forecast(bars, e_dates)

    with np.errstate(invalid="ignore"):
        stop_dist = k * np.sqrt(fc * n_days) * p_entry
    keep = entry_ok & exit_ok & np.isfinite(stop_dist) & (stop_dist > 0)
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
            "n_days": n_days[keep],
        }
    ).reset_index(drop=True)
    assert (sig["time"] + dc.BAR <= t_entry[keep]).all()  # deciding bar closed by the entry instant
    return sig
