"""D2 - Month-end USD flows into the London 4pm fix. Spec: research/hypotheses/D2_fx_month_end_fix.md

Signal table for ``pfbot.backtest.engine.run_backtest``. At most one row per month and pair:

* day: last trading day of the month = last weekday (London local date) of the month on which the FX pair has
  bars around both the entry and the exit instant (decision/fill/exit-bar tolerance below); at most the last
  ``MAX_WALKBACK`` weekdays of the month are tried, so holiday-thinned or missing last days fall back to the
  previous weekday and a longer data hole skips the month.
* signal: sign of the US500 log return from the base price (price known at 16:00 New York on the previous
  month's last trading day) to the price known at the entry instant (``harness.price_at``: close of the last
  US500 M1 bar starting before the instant; skipped if that bar is more than 30 minutes old). Positive ->
  sell USD (long EURUSD/GBPUSD/AUDUSD, short USDJPY/USDCAD/USDCHF); negative -> buy USD.
* entry: market at ``t_in`` London time; time exit at 16:01 London (just after the 16:00 fix).
* stop: 3 x ex-ante expected std of the holding window (``expected_bar_vol``, profile buckets in London time):
  the sum of the 5-minute bar variances opening in [t_in, 16:00) plus 1/5 of the 16:00 bar's variance (the
  window ends one minute into that bar), square-rooted, x entry price.

Timing (house style): the decision bar is the last M1 bar starting before the entry instant (signal ``time``);
the engine fills at the open of the first bar starting at/after the instant. The US500 price used is only
the one known at the entry instant, so nothing from after the instant enters the signal.

Interpretation notes (where the spec is silent)
* The previous month's "last trading day" for the US500 base is the last weekday of the previous month (at most
  ``MAX_WALKBACK`` weekdays back) on which US500 has a decision bar starting in [16:00-5min, 16:00) New York
  (so a US market holiday such as Good Friday falls back to the previous session); its base price is the
  close of that bar. If there is none (e.g. an excluded month) the month is skipped.
* A zero US500 return gives no trade. The 5-minute rules are those of D1 (decision bar in [T-5min, T), fill bar
  in [T, T+5min), exit bar in [T_exit, T_exit+5min)).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pfbot.features.volatility import expected_bar_vol
from pfbot.research.harness import local_times, price_at
from pfbot.strategies.d1_fx_time_of_day import (
    BAR, COLUMNS, MAX_BAR_GAP, NY, PAIRS, STOP_MULT, USD_SELL_SIDE, entry_exit_bars, window_var,
)

LONDON = "Europe/London"
FIX = "16:00"
EXIT = "16:01"
MAX_WALKBACK = 5
_EPOCH = pd.Timestamp("1970-01-01", tz="UTC")

CONFIGS = [dict(t_in=t) for t in ("10:00", "12:00", "14:00")]
PAIR_LIST = PAIRS


def _month_weekdays(bars: pd.DataFrame) -> pd.DataFrame:
    """For every month touched by the bars: the last MAX_WALKBACK weekdays, latest first
    (columns: month = Period, k = 0..MAX_WALKBACK-1 days back, date)."""
    lo = bars.index[0].tz_convert(LONDON).tz_localize(None).normalize()
    hi = bars.index[-1].tz_convert(LONDON).tz_localize(None).normalize()
    months = pd.period_range(lo.to_period("M"), hi.to_period("M"), freq="M")
    rows = []
    for m in months:
        d = pd.date_range(m.start_time, m.end_time.normalize(), freq="D")
        wd = d[d.dayofweek < 5][::-1][:MAX_WALKBACK]
        rows += [(m, k, x) for k, x in enumerate(wd)]
    return pd.DataFrame(rows, columns=["month", "k", "date"])


def _prev_close_us500(us500_bars: pd.DataFrame, months: pd.PeriodIndex):
    """Base price per month: close known at 16:00 NY of the previous month's last US500 trading day
    (NaN if none among the last MAX_WALKBACK weekdays of that month)."""
    md = _month_weekdays(us500_bars) if len(us500_bars) else pd.DataFrame(columns=["month", "k", "date"])
    out = {}
    if len(md):
        t = local_times(md["date"], FIX, NY)
        idx = us500_bars.index
        pos = idx.searchsorted(t.where(~pd.isna(t), _EPOCH), side="left") - 1
        dec = idx[np.clip(pos, 0, None)]
        ok = (pos >= 0) & ~pd.isna(t) & ((t - dec) <= MAX_BAR_GAP) & ((dec + BAR) <= t)
        px = price_at(us500_bars, t)
        md = md.assign(ok=ok & np.isfinite(px), px=px)
        first = md[md["ok"]].sort_values(["month", "k"]).drop_duplicates("month")
        out = dict(zip(first["month"], first["px"]))
    return np.array([out.get(m, np.nan) for m in months])


def signals(bars: pd.DataFrame, symbol: str, t_in: str, us500_bars: pd.DataFrame) -> pd.DataFrame:
    """D2 signal table (columns time, side, order, stop_dist, exit_time + diagnostic us500_ret) for M1
    ``bars`` of ``symbol`` (an FX pair) and the US500 M1 bars used for the month-to-date return."""
    usd_side = USD_SELL_SIDE[symbol]
    cols = COLUMNS + ["us500_ret"]
    empty = pd.DataFrame({c: pd.Series(dtype=object) for c in cols})
    if len(bars) < 2 or len(us500_bars) < 2:
        return empty

    # ---- candidate days: last MAX_WALKBACK weekdays of every month, pick the latest tradable ----
    md = _month_weekdays(bars)
    t_entry = local_times(md["date"], t_in, LONDON)
    t_exit = local_times(md["date"], EXIT, LONDON)
    dec, ok = entry_exit_bars(bars, t_entry, t_exit)
    md = md.assign(t_entry=t_entry, t_exit=t_exit, dec=dec, ok=ok)
    sel = md[md["ok"]].sort_values(["month", "k"]).drop_duplicates("month").reset_index(drop=True)
    if sel.empty:
        return empty
    t_entry = pd.DatetimeIndex(sel["t_entry"])
    t_exit = pd.DatetimeIndex(sel["t_exit"])

    # ---- US500 month-to-date return known at the entry instant ----
    p_base = _prev_close_us500(us500_bars, pd.PeriodIndex(sel["month"], freq="M") - 1)
    p_now = price_at(us500_bars, t_entry)  # NaN if the last US500 bar is more than 30 min old
    with np.errstate(invalid="ignore", divide="ignore"):
        ret = np.log(p_now / p_base)

    # ---- ex-ante stop from the expected vol of the holding window [t_in, 16:01) ----
    ev = expected_bar_vol(bars, tz=LONDON)
    t_fix = pd.DatetimeIndex(local_times(sel["date"], FIX, LONDON))
    t_fix_end = t_fix + pd.Timedelta(minutes=5)
    var_hold = window_var(ev, t_entry, t_fix) + 0.2 * window_var(ev, t_fix, t_fix_end)
    p_entry = price_at(bars, t_entry)
    with np.errstate(invalid="ignore"):
        stop_dist = STOP_MULT * np.sqrt(var_hold) * p_entry

    keep = np.isfinite(ret) & (ret != 0) & np.isfinite(stop_dist) & (stop_dist > 0)
    if not keep.any():
        return empty
    side = (usd_side * np.sign(ret[keep])).astype(int)  # ret>0: sell USD (= usd_side); ret<0: buy USD
    sig = pd.DataFrame(
        {
            "time": pd.DatetimeIndex(sel["dec"])[keep],
            "side": side,
            "order": "market",
            "stop_dist": stop_dist[keep],
            "exit_time": t_exit[keep],
            "us500_ret": ret[keep],
        }
    ).reset_index(drop=True)
    assert (sig["time"] + BAR <= t_entry[keep]).all()
    return sig
