"""E1 - VIX term structure and VIX spikes as conditioning information for index exposure.
Spec: research/hypotheses/E1_vix_term_structure.md

Every trading day (long only, one position at most): decision on the CBOE closes of the previous trading
day d, entry at market at 09:35 ET on trading day e = d+1, time exit at 09:30 ET on the next trading day
x after e. Stop = 3 x sqrt(HAR daily variance forecast for e) x price at the entry instant (the hold
09:35 -> 09:30 spans one full trading day, so the variance scale is 1.0).

Variants
  ts      long when VIX(d) / VIX3M(d) < th
  spike   long when VIX(d) / VIX(d-1) - 1 >= jump   (compared with 1e-12 tolerance for float noise)
  always  benchmark (report only, not a hypothesis): long every day

Alignment / no look-ahead
* "Trading days" are the NY cash-session dates of the bars (``daily_common.ny_trading_dates``). The VIX
  values used for entry date e are those of the trading day d immediately preceding e (d = the previous
  trading date present in the bars); equivalently a VIX close of date d is first usable at 09:35 ET on the
  next trading date. The entry instant is strictly after the 16:15 ET publication time of d.
* The VIX value of d must exist, and d must be the last date of the VIX series before e (so a missing VIX
  value for the immediately preceding trading day, or a hole in the bars between d and e, skips the day;
  nothing is carried forward). A day is also skipped when the VIX series has a print strictly between the
  entry and the exit date (the next trading day of the calendar is missing from the bars, so the hold would
  silently be longer than one day; the benchmark has no VIX calendar and relies on the 4-day gap rule).
  Same for VIX3M (ts) and for VIX(d-1), which must be the previous trading
  date's value (spike).
* Signals depend only on VIX data of dates < e, bars before 09:35 ET of e (price at the entry instant
  and the HAR forecast, which uses only RV of trading days ending before e) and, for the exit, the
  existence of a bar at the exit instant (the exit date is calendar information).

Interpretation notes
* Signal ``time`` is the start of the last M1 bar before 09:35 ET (the 09:34 bar); the engine fills at the
  open of the 09:35 bar. Exit at the 09:30 ET bar of the next trading date; there is no early-close
  fallback for a morning exit, the day is skipped when that bar is missing (as in B2). Entries whose next
  trading date is more than 4 calendar days later (data holes) are skipped.
* The benchmark ``always`` needs no VIX data (days without a VIX value are NOT skipped), so it is the
  unconditional exposure of the same entry/exit/stop machinery.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pfbot.data import cboe
from pfbot.research import harness
from pfbot.research.harness import SESSIONS, local_times
from pfbot.strategies import daily_common as dc

CONFIGS = (
    [dict(variant="ts", th=th) for th in (0.90, 0.95, 1.00)]
    + [dict(variant="spike", jump=j) for j in (0.10, 0.20)]
)
BENCHMARK = dict(variant="always")

T_IN = "09:35"
T_OUT = "09:30"
STOP_MULT = 3.0
HOLD_FRACTION = 1.0  # 09:35 -> next 09:30 is ~one full trading day
MAX_GAP_DAYS = 4
EPS = 1e-12
COLUMNS = ["time", "side", "order", "stop_dist", "exit_time", "date", "exit_date", "vix_date", "metric"]


def _lookup(s: pd.Series, dates: pd.DatetimeIndex) -> np.ndarray:
    """Value of ``s`` on exactly each date (NaN if absent)."""
    return s.reindex(dates).to_numpy(float)


def _last_before(s: pd.Series, dates: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """Last date of ``s`` strictly before each of ``dates`` (NaT if none)."""
    pos = s.index.searchsorted(dates, side="left") - 1
    out = s.index[np.clip(pos, 0, None)]
    return pd.DatetimeIndex(np.where(pos >= 0, out, pd.NaT))


def _no_print_between(s: pd.Series, a: pd.DatetimeIndex, b: pd.DatetimeIndex) -> np.ndarray:
    """True where no date of ``s`` lies strictly between a[i] and b[i]."""
    lo = s.index.searchsorted(a, side="right")
    hi = s.index.searchsorted(b, side="left")
    return (hi - lo) <= 0


def conditioning(variant: str, dates: pd.DatetimeIndex, th=None, jump=None, vix=None, vix3m=None):
    """(go, metric) per entry date ``dates[i]`` for i >= 1; entry i=0 has no previous trading day.

    ``go`` is True where the variant says long and all the information is present; ``metric`` is the
    VIX/VIX3M ratio (ts) or the VIX one-day change (spike), NaN for ``always``.
    """
    n = len(dates)
    go = np.zeros(n, bool)
    metric = np.full(n, np.nan)
    if n < 2:
        return go, metric
    prev = dates[:-1]  # trading day d preceding entry date e = dates[1:]
    e = dates[1:]
    if variant == "always":
        go[1:] = True
        return go, metric
    if variant == "ts":
        if th is None or vix is None or vix3m is None:
            raise ValueError("variant 'ts' needs th, vix and vix3m")
        v, v3 = _lookup(vix, prev), _lookup(vix3m, prev)
        ok = (_last_before(vix, e) == prev) & (_last_before(vix3m, e) == prev) & np.isfinite(v) & np.isfinite(v3)
        with np.errstate(invalid="ignore", divide="ignore"):
            ratio = np.where(ok, v / v3, np.nan)
        go[1:] = ok & (ratio < th)
        metric[1:] = ratio
        return go, metric
    if variant == "spike":
        if jump is None or vix is None:
            raise ValueError("variant 'spike' needs jump and vix")
        v = _lookup(vix, prev)
        d2 = pd.DatetimeIndex(np.concatenate([[pd.NaT], np.asarray(dates[:-2])]))  # trading day before d
        v0 = _lookup(vix, d2)
        ok = (_last_before(vix, e) == prev) & (_last_before(vix, prev) == d2) & np.isfinite(v) & np.isfinite(v0)
        with np.errstate(invalid="ignore", divide="ignore"):
            chg = np.where(ok, v / v0 - 1.0, np.nan)
        go[1:] = ok & (chg >= jump - EPS)
        metric[1:] = chg
        return go, metric
    raise ValueError(f"unknown variant {variant!r}")


def signals(bars: pd.DataFrame, symbol: str, variant: str, th: float | None = None, jump: float | None = None,
            vix: pd.Series | None = None, vix3m: pd.Series | None = None) -> pd.DataFrame:
    """E1 signal table (time, side, order, stop_dist, exit_time + diagnostics date / exit_date /
    vix_date / metric) for M1 ``bars`` of ``symbol``. ``vix`` / ``vix3m`` default to the CBOE files."""
    assert symbol in SESSIONS, symbol
    empty = pd.DataFrame({c: pd.Series(dtype=object) for c in COLUMNS})
    if variant not in ("ts", "spike", "always"):
        raise ValueError(f"unknown variant {variant!r}")
    if variant != "always":
        if vix is None:
            vix = cboe.load_vix("VIX")
        if variant == "ts" and vix3m is None:
            vix3m = cboe.load_vix("VIX3M")
    dates = dc.ny_trading_dates(bars)
    if len(dates) < 3:
        return empty
    go, metric = conditioning(variant, dates, th=th, jump=jump, vix=vix, vix3m=vix3m)
    fc_all = dc.daily_variance_forecast(bars, dates)

    e_dates, x_dates = dates[:-1], dates[1:]  # entry date, next trading date (exit)
    gap = np.asarray((x_dates - e_dates).days)
    t_entry = local_times(e_dates, T_IN, dc.NY)
    dec, _fill, entry_ok = dc.decision_bar(bars, t_entry)
    p_entry = dc.price_at(bars, t_entry)
    exit_time, exit_ok = dc.exit_instants(bars, x_dates, T_OUT, early_close_fallback=False)

    with np.errstate(invalid="ignore"):
        stop_dist = STOP_MULT * np.sqrt(fc_all[:-1] * HOLD_FRACTION) * p_entry
    keep = (go[:-1] & (gap <= MAX_GAP_DAYS) & entry_ok & exit_ok
            & np.isfinite(stop_dist) & (stop_dist > 0))
    if variant != "always":
        # the exit date must be the next trading day of the calendar, not just of the bars: a VIX print
        # strictly between entry and exit date means a day is missing from the bars (data hole)
        keep &= _no_print_between(vix, e_dates, x_dates)
    if not keep.any():
        return empty
    vix_date = np.concatenate([[pd.NaT], np.asarray(dates[:-1])])[:-1]  # trading day d of each entry date
    sig = pd.DataFrame(
        {
            "time": dec[keep],
            "side": 1,
            "order": "market",
            "stop_dist": stop_dist[keep],
            "exit_time": exit_time[keep],
            "date": e_dates[keep],
            "exit_date": x_dates[keep],
            "vix_date": pd.DatetimeIndex(vix_date)[keep],
            "metric": metric[:-1][keep],
        }
    ).reset_index(drop=True)
    assert (sig["time"] + dc.BAR <= t_entry[keep]).all()
    return sig
