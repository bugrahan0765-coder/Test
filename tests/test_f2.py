import numpy as np
import pandas as pd

from pfbot.strategies import f2_fractal_maze as f2


def _amd(n_a, n_m, n_d, slope_m, slope_d, start=100.0):
    a = np.full(n_a, start)
    m = start + slope_m * np.arange(1, n_m + 1)
    d = m[-1] + slope_d * np.arange(1, n_d + 1)
    return np.r_[a, m, d]


def _m1_bars():
    # 9.5 hours of M1 ending at 15:00 New York (19:00 UTC in March 2019 after DST), big AMD on M5 scale:
    # flat 390 min, down 60 min (manipulation), up 120 min (distribution); the last 60 min repeat the
    # same shape on M1 scale (flat 25, down 15, up 20).
    big = _amd(390, 60, 120, -0.08, 0.12)
    small = _amd(25, 15, 20, -0.15, 0.40, start=big[-61])
    path = np.r_[big[:-60], small]
    rng = np.random.default_rng(0)
    path = path + rng.normal(0, 0.01, len(path))
    idx = pd.date_range(end="2019-03-12 19:04", periods=len(path), freq="1min", tz="UTC")
    return pd.DataFrame({"open": path, "high": path + 0.05, "low": path - 0.05, "close": path}, index=idx)


def test_same_amd_on_m1_and_m5_gives_long_signal():
    bars = _m1_bars()
    ev = f2.fractal_events(bars)
    assert not ev.empty
    last = ev.iloc[-1]
    assert last["side"] == 1
    assert last["time"] == bars.index[-1]          # decided on the last M1 bar inside the M5 bar
    assert last["m5_bar"] == pd.Timestamp("2019-03-12 19:00", tz="UTC")
    sig = f2.signals(bars, rho=-1.0, exit="2R")
    s = sig.iloc[-1]
    assert np.isclose(s["target_dist"], 2 * s["stop_dist"])
    # M5 close 15:05 NY + 60 min would be 16:05, capped at 15:55 NY (19:55 UTC)
    assert s["exit_time"] == pd.Timestamp("2019-03-12 19:55", tz="UTC")


def test_rho_filter_and_time_exit():
    bars = _m1_bars()
    assert f2.signals(bars, rho=1.01).empty
    sig = f2.signals(bars, rho=-1.0, exit="time")
    assert sig["target_dist"].isna().all()
