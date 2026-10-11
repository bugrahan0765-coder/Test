"""F2 - fractal AMD maze (pre-registered in research/hypotheses/F2_fractal_maze.md).

At the close of M5 bar t the AMD maze model is fitted to the last 60 M5 bars and to the last 60 M1 bars
(the M1 window ends with the last M1 bar inside t). A signal needs the same consistent scenario
A(F) -> M(x) -> D(y), x opposite to y, on both timeframes and a correlation >= rho between the two
5-SMA paths. Everything used is known at the M5 close; the signal ``time`` is the last M1 bar inside t,
so the engine fills on the next M1 bar.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pfbot.data.schema import resample_bars
from pfbot.features.amd_maze import fit_amd
from pfbot.research.harness import local_times

HYPOTHESIS = "F2"
NY = "America/New_York"
WINDOW = 60
WARM = 20             # extra bars for SMA / ATR warm-up inside fit_amd
STOP_ATR = 1.5
HOLD = pd.Timedelta(minutes=60)
OPP = {"U": "D", "D": "U"}

CONFIGS: list[dict] = [dict(rho=r, exit=e) for r in (0.8, 0.9) for e in ("2R", "time")]
COLUMNS = ["time", "side", "order", "stop_dist", "target_dist", "exit_time"]

_cache: dict = {}


def _atr(b: pd.DataFrame, n: int = 14) -> np.ndarray:
    prev = b["close"].shift(1)
    tr = pd.concat([b["high"] - b["low"], (b["high"] - prev).abs(), (b["low"] - prev).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean().to_numpy()


def fractal_events(bars: pd.DataFrame) -> pd.DataFrame:
    """All M5 bars where M5 and M1 show the same consistent reversal AMD (any correlation)."""
    key = (id(bars), len(bars), bars.index[0], bars.index[-1])
    if key in _cache:
        return _cache[key]
    b5 = resample_bars(bars, "5min")
    atr5 = _atr(b5)
    sma1 = bars["close"].rolling(5).mean().to_numpy()
    sma5 = b5["close"].rolling(5).mean().to_numpy()
    ny = b5.index.tz_convert(NY).strftime("%H:%M")
    cand = np.flatnonzero((ny >= "10:30") & (ny <= "15:00"))
    cand = cand[cand >= WINDOW + WARM]
    m1_idx = bars.index
    rows = []
    for i in cand:
        s5 = fit_amd(b5.iloc[i - WINDOW - WARM + 1:i + 1], window=WINDOW)[0]
        if not (s5.consistent and s5.dist in OPP and s5.manip == OPP[s5.dist]):
            continue
        t_last = b5.index[i] + pd.Timedelta(minutes=4)          # last M1 bar inside M5 bar i
        j = m1_idx.searchsorted(t_last, side="right") - 1        # last M1 bar starting <= t_last
        if j < WINDOW + WARM or m1_idx[j] < b5.index[i]:
            continue
        # M1 window must be contiguous (no session break inside the last hour)
        if m1_idx[j] - m1_idx[j - WINDOW + 1] != pd.Timedelta(minutes=WINDOW - 1):
            continue
        s1 = fit_amd(bars.iloc[j - WINDOW - WARM + 1:j + 1], window=WINDOW)[0]
        if not (s1.consistent and (s1.manip, s1.dist) == (s5.manip, s5.dist)):
            continue
        p1, p5 = sma1[j - WINDOW + 1:j + 1], sma5[i - WINDOW + 1:i + 1]
        rho = float(np.corrcoef(p1, p5)[0, 1])
        rows.append((m1_idx[j], 1 if s5.dist == "U" else -1, rho, atr5[i], b5.index[i]))
    ev = pd.DataFrame(rows, columns=["time", "side", "rho", "atr5", "m5_bar"])
    _cache.clear()
    _cache[key] = ev
    return ev


def signals(bars: pd.DataFrame, symbol: str = "", rho: float = 0.8, exit: str = "2R") -> pd.DataFrame:
    ev = fractal_events(bars)
    if ev.empty:
        return pd.DataFrame({k: pd.Series(dtype=object) for k in COLUMNS})
    ev = ev[(ev["rho"] >= rho) & np.isfinite(ev["atr5"]) & (ev["atr5"] > 0)]
    if ev.empty:
        return pd.DataFrame({k: pd.Series(dtype=object) for k in COLUMNS})
    close_t = ev["m5_bar"] + pd.Timedelta(minutes=5)
    dates = close_t.dt.tz_convert(NY).dt.tz_localize(None).dt.normalize()
    eod = pd.Series(local_times(dates, "15:55", NY), index=ev.index)
    exit_time = np.minimum(close_t + HOLD, eod)
    stop = STOP_ATR * ev["atr5"].to_numpy()
    sig = pd.DataFrame({
        "time": ev["time"].to_numpy(),
        "side": ev["side"].to_numpy(),
        "order": "market",
        "stop_dist": stop,
        "target_dist": 2.0 * stop if exit == "2R" else np.nan,
        "exit_time": exit_time.to_numpy(),
    })
    if exit not in ("2R", "time"):
        raise ValueError(exit)
    return sig.reset_index(drop=True)
