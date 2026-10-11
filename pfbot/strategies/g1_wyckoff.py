"""G1 - Wyckoff spring / upthrust (pre-registered in research/hypotheses/G1_wyckoff_spring_upthrust.md).

Signals are computed on M5 bars resampled from the M1 input; the engine fills on M1.
Information set: the trading range uses bars t-L .. t-1, ATR is the value at t-1, and
the spring/upthrust test uses bar t's high/low/close, all known at the close of M5 bar t.
The signal row ``time`` is the start of the last M1 bar inside M5 bar t, so the order
becomes active on the first M1 bar after the M5 close.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

from pfbot.data.schema import resample_bars
from pfbot.research.harness import local_times

HYPOTHESIS = "G1"
NY = "America/New_York"

ER_MAX = 0.30
W_MIN, W_MAX = 3.0, 15.0      # range width in ATR
EDGE = 0.2                    # edge zone as a fraction of the width
MIN_TOUCHES = 3
PIERCE_MAX = 1.0              # max penetration beyond the edge, in ATR
STOP_BUF = 0.25               # stop buffer beyond the spring/upthrust extreme, in ATR
ATR_LEN = 14

CONFIGS: list[dict] = [dict(L=L, target=t) for L in (48, 96) for t in ("range", "2R")]

COLUMNS = ["time", "side", "order", "stop_price", "target_price", "exit_time"]


def wyckoff_events(b5: pd.DataFrame, L: int) -> pd.DataFrame:
    """Spring (+1) / upthrust (-1) events on M5 bars with the range that produced them."""
    o, h, l, c = (b5[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    n = len(b5)
    prev = np.r_[np.nan, c[:-1]]
    tr = np.nanmax(np.vstack([h - l, np.abs(h - prev), np.abs(l - prev)]), axis=0)
    atr = pd.Series(tr).rolling(ATR_LEN).mean().shift(1).to_numpy()

    hi = pd.Series(h).shift(1).rolling(L).max().to_numpy()
    lo = pd.Series(l).shift(1).rolling(L).min().to_numpy()
    w = hi - lo
    cs = pd.Series(c)
    num = (cs.shift(1) - cs.shift(L)).abs().to_numpy()
    den = cs.diff().abs().shift(1).rolling(L - 1).sum().to_numpy()
    with np.errstate(invalid="ignore", divide="ignore"):
        er = num / den
        wa = w / atr

    base = (er <= ER_MAX) & (wa >= W_MIN) & (wa <= W_MAX) & (atr > 0)
    spring = base & (l < lo) & (l >= lo - PIERCE_MAX * atr) & (c > lo)
    upthr = base & (h > hi) & (h <= hi + PIERCE_MAX * atr) & (c < hi)
    cand = np.flatnonzero(spring | upthr)
    cand = cand[cand >= L]
    if len(cand):
        hw = sliding_window_view(h, L)[cand - L]   # bars t-L .. t-1
        lw = sliding_window_view(l, L)[cand - L]
        n_lo = (lw <= (lo[cand] + EDGE * w[cand])[:, None]).sum(1)
        n_hi = (hw >= (hi[cand] - EDGE * w[cand])[:, None]).sum(1)
        cand = cand[(n_lo >= MIN_TOUCHES) & (n_hi >= MIN_TOUCHES)]
    side = np.where(spring[cand], 1, -1)
    return pd.DataFrame({"side": side, "close": c[cand], "high": h[cand], "low": l[cand],
                         "range_hi": hi[cand], "range_lo": lo[cand], "atr": atr[cand]},
                        index=b5.index[cand])


def signals(bars: pd.DataFrame, symbol: str = "", L: int = 48, target: str = "range") -> pd.DataFrame:
    b5 = resample_bars(bars, "5min")
    ev = wyckoff_events(b5, L)
    ny = ev.index.tz_convert(NY)
    hhmm = ny.strftime("%H:%M")
    ev = ev[(hhmm >= "10:00") & (hhmm <= "15:00")]
    if ev.empty:
        return pd.DataFrame({k: pd.Series(dtype=object) for k in COLUMNS})
    long = ev["side"].to_numpy() == 1
    stop = np.where(long, ev["low"] - STOP_BUF * ev["atr"], ev["high"] + STOP_BUF * ev["atr"])
    risk = np.abs(ev["close"].to_numpy() - stop)
    if target == "range":
        tgt = np.where(long, ev["range_hi"], ev["range_lo"])
        ok = np.abs(tgt - ev["close"].to_numpy()) >= risk
    elif target == "2R":
        tgt = ev["close"].to_numpy() + np.where(long, 2.0, -2.0) * risk
        ok = np.ones(len(ev), bool)
    else:
        raise ValueError(target)
    dates = ev.index.tz_convert(NY).tz_localize(None).normalize()
    sig = pd.DataFrame({
        "time": ev.index + pd.Timedelta(minutes=4),
        "side": ev["side"].to_numpy(),
        "order": "market",
        "stop_price": stop,
        "target_price": tgt,
        "exit_time": local_times(dates, "15:55", NY),
    })
    return sig[ok].reset_index(drop=True)
