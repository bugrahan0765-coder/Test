"""D1 - FX time-of-day effect: a currency weakens during its own home trading hours.
Spec: research/hypotheses/D1_fx_time_of_day.md

Signal table for ``pfbot.backtest.engine.run_backtest``. One row per weekday (local date of the window) at most:

* window start / end are local wall-clock times in the window's time zone (DST aware via ``local_times``):
  ``US`` 08:00 America/New_York; ``home``: EUR/CHF 08:00 Europe/Berlin, GBP 08:00 Europe/London, JPY 09:00
  Asia/Tokyo, AUD 09:00 Australia/Sydney (CAD has no ``home`` window). The window lasts ``H`` hours.
* entry: market at the window start, always in the same direction (no signal conditioning):
    - ``US`` window: sell USD  -> long EURUSD/GBPUSD/AUDUSD (USD is the quote), short USDJPY/USDCAD/USDCHF;
    - ``home`` window: sell the home currency -> short EURUSD/GBPUSD/AUDUSD, long USDJPY/USDCHF.
* time exit at window start + H; protective stop 3 x ex-ante expected std of the holding window
  (square root of the sum of ``expected_bar_vol`` variances of the 5-minute bars opening in
  [start, end), profile buckets in the window's own time zone) x entry price.

Timing (house style, see a1_intraday_momentum): the decision bar is the last M1 bar starting before the entry
instant (the signal's ``time``); the engine fills at the open of the first bar starting at/after the instant.

Interpretation notes (where the spec is silent)
* "Weekdays only" is applied to the local date of the window (so the Sydney Monday window starts on Sunday
  evening UTC); bars decide whether it can be traded.
* "Skip if a bar is missing within 5 minutes of entry or exit": the entry needs a decision bar starting in
  [T-5min, T) and a fill bar starting in [T, T+5min); the exit needs a bar starting in [T_exit, T_exit+5min).
* A day is skipped if any 5-minute bar of the holding window has no vol forecast (warm-up / missing bucket).
  Holiday thin days are not skipped, nothing but bar availability filters them.
* The vol model's trading day rolls at 17:00 New York for every pair; only the time-of-day profile buckets
  use the window's time zone.
* ``H`` is the number of hours (2 or 4).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pfbot.features.volatility import expected_bar_vol
from pfbot.research.harness import local_times, price_at

NY = "America/New_York"
BAR = pd.Timedelta(minutes=1)
MAX_BAR_GAP = pd.Timedelta(minutes=5)
STOP_MULT = 3.0
_EPOCH = pd.Timestamp("1970-01-01", tz="UTC")

PAIRS = ["EURUSD", "GBPUSD", "AUDUSD", "USDJPY", "USDCAD", "USDCHF"]

# +1 = long the pair = sell USD (USD is the quote currency); -1 = short the pair (USD is the base).
USD_SELL_SIDE = {"EURUSD": 1, "GBPUSD": 1, "AUDUSD": 1, "USDJPY": -1, "USDCAD": -1, "USDCHF": -1}

# window -> (time zone, local start "HH:MM")
US_WINDOW = (NY, "08:00")
HOME_WINDOW = {
    "EURUSD": ("Europe/Berlin", "08:00"),
    "USDCHF": ("Europe/Berlin", "08:00"),
    "GBPUSD": ("Europe/London", "08:00"),
    "USDJPY": ("Asia/Tokyo", "09:00"),
    "AUDUSD": ("Australia/Sydney", "09:00"),
}  # USDCAD deliberately absent: CAD hours overlap the US window

CONFIGS_BY_SYMBOL = {
    s: [dict(window=w, H=h) for w in (["US", "home"] if s in HOME_WINDOW else ["US"]) for h in (2, 4)]
    for s in PAIRS
}


def window_spec(symbol: str, window: str) -> tuple[str, str]:
    """(time zone, local start HH:MM) of the window for the pair."""
    if window == "US":
        return US_WINDOW
    if window == "home":
        if symbol not in HOME_WINDOW:
            raise ValueError(f"{symbol} has no home window")
        return HOME_WINDOW[symbol]
    raise ValueError(f"unknown window {window!r}")


def side_for(symbol: str, window: str) -> int:
    """+1 long / -1 short: US window sells USD, home window sells the other currency (buys USD)."""
    return USD_SELL_SIDE[symbol] * (1 if window == "US" else -1)


def shift_hhmm(hhmm: str, minutes: int) -> str:
    t = int(hhmm[:2]) * 60 + int(hhmm[3:]) + minutes
    return f"{t // 60:02d}:{t % 60:02d}"


def local_weekdays(bars: pd.DataFrame, tz: str) -> pd.DatetimeIndex:
    """Weekday local dates (tz-naive, sorted) from the day before the first bar to the day after the last
    bar, in time zone ``tz``; the caller discards days without bars."""
    lo = bars.index[0].tz_convert(tz).tz_localize(None).normalize() - pd.Timedelta(days=1)
    hi = bars.index[-1].tz_convert(tz).tz_localize(None).normalize() + pd.Timedelta(days=1)
    d = pd.date_range(lo, hi, freq="D")
    return d[d.dayofweek < 5]


def window_var(exp_vol: pd.Series, starts: pd.DatetimeIndex, ends: pd.DatetimeIndex) -> np.ndarray:
    """Sum of expected variances of the 5-min bars opening in [start, end); NaN if the window is empty
    or any bar in it has no forecast."""
    v = exp_vol.to_numpy(float) ** 2
    bad = np.isnan(v)
    cs = np.concatenate([[0.0], np.cumsum(np.where(bad, 0.0, v))])
    cb = np.concatenate([[0], np.cumsum(bad)])
    ok = ~(pd.isna(starts) | pd.isna(ends))
    a = exp_vol.index.searchsorted(starts.where(ok, _EPOCH), side="left")
    b = exp_vol.index.searchsorted(ends.where(ok, _EPOCH), side="left")
    out = cs[b] - cs[a]
    good = ok & (b > a) & ((cb[b] - cb[a]) == 0)
    return np.where(good, out, np.nan)


def entry_exit_bars(bars: pd.DataFrame, t_entry: pd.DatetimeIndex, t_exit: pd.DatetimeIndex):
    """Decision-bar start times and a validity mask for entry instants / exit instants (UTC).

    ok requires a decision bar starting in [T-5min, T) that has closed by T, a fill bar starting in
    [T, T+5min) and an exit bar starting in [T_exit, T_exit+5min). ``dec`` is the start of the decision bar.
    """
    idx = bars.index
    valid = ~(pd.isna(t_entry) | pd.isna(t_exit))
    te = t_entry.where(valid, _EPOCH)
    tx = t_exit.where(valid, _EPOCH)
    pos = idx.searchsorted(te, side="left") - 1  # last bar starting strictly before entry
    has_dec = pos >= 0
    dec = idx[np.clip(pos, 0, None)]
    has_fill = (pos + 1) < len(idx)
    fill = idx[np.clip(pos + 1, None, len(idx) - 1)]
    ex = idx.searchsorted(tx, side="left")  # first bar at/after the exit instant
    has_exit = ex < len(idx)
    exit_bar = idx[np.clip(ex, None, len(idx) - 1)]
    ok = (
        valid & has_dec & has_fill & has_exit
        & ((te - dec) <= MAX_BAR_GAP)
        & ((fill - te) < MAX_BAR_GAP)
        & ((exit_bar - tx) < MAX_BAR_GAP)
        & ((dec + BAR) <= te)
    )
    return dec, np.asarray(ok)


COLUMNS = ["time", "side", "order", "stop_dist", "exit_time"]


def signals(bars: pd.DataFrame, symbol: str, window: str, H: int) -> pd.DataFrame:
    """D1 signal table (columns time, side, order, stop_dist, exit_time) for M1 ``bars`` of ``symbol``."""
    tz, start = window_spec(symbol, window)
    side = side_for(symbol, window)
    empty = pd.DataFrame({c: pd.Series(dtype=object) for c in COLUMNS})
    if len(bars) < 2:
        return empty

    dates = local_weekdays(bars, tz)
    t_entry = local_times(dates, start, tz)
    t_exit = local_times(dates, shift_hhmm(start, 60 * H), tz)
    dec, ok = entry_exit_bars(bars, t_entry, t_exit)

    ev = expected_bar_vol(bars, tz=tz)
    var_hold = window_var(ev, t_entry, t_exit)
    p_entry = price_at(bars, t_entry)

    with np.errstate(invalid="ignore"):
        stop_dist = STOP_MULT * np.sqrt(var_hold) * p_entry
    keep = ok & np.isfinite(stop_dist) & (stop_dist > 0)
    if not keep.any():
        return empty
    sig = pd.DataFrame(
        {
            "time": dec[keep],
            "side": side,
            "order": "market",
            "stop_dist": stop_dist[keep],
            "exit_time": t_exit[keep],
        }
    ).reset_index(drop=True)
    # no look-ahead guarantee: the deciding bar closed at or before the entry instant
    assert (sig["time"] + BAR <= t_entry[keep]).all()
    return sig
