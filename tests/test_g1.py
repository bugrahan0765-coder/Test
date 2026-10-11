import numpy as np
import pandas as pd

from pfbot.strategies import g1_wyckoff as g1


def _m5(close_path, start="2019-03-04 13:00"):
    idx = pd.date_range(start, periods=len(close_path), freq="5min", tz="UTC")
    c = np.asarray(close_path, float)
    return pd.DataFrame({"open": c, "high": c + 0.5, "low": c - 0.5, "close": c}, index=idx)


def _range_then(last_bar):
    # 60 bars oscillating between ~98 and ~102 (a clean trading range), then one event bar
    t = np.arange(60)
    path = 100 + 2 * np.sin(t / 3.0)
    b = _m5(np.r_[path, 100.0])
    b.iloc[-1] = last_bar
    return b


def test_spring_detected_and_uses_only_past_range():
    b = _range_then({"open": 99.0, "high": 99.6, "low": 97.0, "close": 98.5})
    ev = g1.wyckoff_events(b, L=48)
    assert len(ev) == 1 and ev["side"].iloc[0] == 1
    assert ev.index[0] == b.index[-1]
    # range comes from bars before t only
    assert np.isclose(ev["range_lo"].iloc[0], b["low"].iloc[-49:-1].min())


def test_upthrust_detected():
    b = _range_then({"open": 101.0, "high": 103.0, "low": 100.8, "close": 101.4})
    ev = g1.wyckoff_events(b, L=48)
    assert len(ev) == 1 and ev["side"].iloc[0] == -1


def test_breakdown_is_not_a_spring():
    # closes below support -> breakdown, not a spring
    b = _range_then({"open": 99.0, "high": 99.2, "low": 97.0, "close": 97.2})
    assert g1.wyckoff_events(b, L=48).empty
    # pierces too far (> 1 ATR) -> not a shakeout
    b = _range_then({"open": 99.0, "high": 99.2, "low": 90.0, "close": 98.5})
    assert g1.wyckoff_events(b, L=48).empty


def test_trend_is_not_a_range():
    b = _m5(np.r_[100 + 0.3 * np.arange(60), 117.0])
    b.iloc[-1] = {"open": 117.0, "high": 117.4, "low": 100.0, "close": 117.0}
    assert g1.wyckoff_events(b, L=48).empty
