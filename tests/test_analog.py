import numpy as np
import pandas as pd

from pfbot.features.analog import AnalogLibrary, shape_table


def _bars(close):
    idx = pd.date_range("2019-01-02 14:00", periods=len(close), freq="5min", tz="UTC")
    close = np.asarray(close, float)
    return pd.DataFrame({"open": close, "high": close + 0.5, "low": close - 0.5, "close": close}, index=idx)


def test_shape_is_relative_to_last_value_and_atr():
    rng = np.random.default_rng(0)
    b = _bars(100 + np.cumsum(rng.normal(0, 1, 400)))
    meta, X = shape_table(b, ny_start="00:00", ny_end="23:59")
    assert X.shape[1] == 60
    assert np.allclose(X[:, -1], 0.0)
    # label is the forward return over 12 bars
    t = meta.index[10]
    i = b.index.get_loc(t)
    assert np.isclose(meta["fwd"].iloc[10], b["close"].iloc[i + 12] / b["close"].iloc[i] - 1)


def test_planted_pattern_is_recovered_one_match_per_day():
    # library: shape "V" always followed by up, shape "A" always by down
    rng = np.random.default_rng(1)
    v = np.abs(np.linspace(-1, 1, 60)) * 5
    a = -v
    X = np.vstack([v + rng.normal(0, 0.2, 60) for _ in range(30)] + [a + rng.normal(0, 0.2, 60) for _ in range(30)])
    X = (X - X[:, -1:]).astype(np.float32)
    days = [f"d{i}" for i in range(60)]
    meta = pd.DataFrame({"day": days, "close": 1.0, "atr": 1.0, "fwd": [0.01] * 30 + [-0.01] * 30},
                        index=pd.date_range("2019-01-01", periods=60, freq="D", tz="UTC"))
    lib = AnalogLibrary(meta, X)
    mv, ma = lib.query(np.vstack([v - v[-1], a - a[-1]]), k=10)
    assert AnalogLibrary.p_up(mv) == 1.0 and AnalogLibrary.p_up(ma) == 0.0
    assert mv["day"].is_unique and (mv["dist"].diff().dropna() >= 0).all()
