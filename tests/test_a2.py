"""Tests for the A2 opening-range signal generator (synthetic data)."""
import numpy as np
import pandas as pd
import pytest

from pfbot.backtest.engine import CostModel, run_backtest
from pfbot.data.synthetic import make_bars
from pfbot.features.volatility import expected_bar_vol
from pfbot.research.harness import SESSIONS, local_times
from pfbot.strategies.a2_opening_range import CONFIGS, signals

NY = "America/New_York"


@pytest.fixture(scope="module")
def bars():
    return make_bars(start="2020-01-01", days=160, seed=3)


@pytest.fixture(scope="module")
def long_bars():
    # ~14 months so that signals exist in both January and July after the vol warm-up
    return make_bars(start="2019-05-01", days=330, seed=5)


@pytest.fixture(scope="module")
def exp_us(bars):
    return expected_bar_vol(bars, tz=NY)


def _cfg(entry="candle", N=15, tR=3):
    return dict(symbol="US100", N=N, tR=tR, entry=entry)


def _local(ts, tz=NY):
    return pd.DatetimeIndex(ts).tz_convert(tz)


def test_config_grid():
    assert len(CONFIGS) == 12
    assert sum(c["entry"] == "candle" for c in CONFIGS) == 9
    assert {c["N"] for c in CONFIGS if c["entry"] == "breakout"} == {15}


def test_no_lookahead(bars):
    cfg = _cfg(N=15, tR=3)
    base = signals(bars, **cfg)
    assert len(base) > 20
    day = base["time"].iloc[len(base) // 2]
    open_utc = day + pd.Timedelta(minutes=1) - pd.Timedelta(minutes=15)
    cut = open_utc + pd.Timedelta(minutes=15)  # first bar after the range
    bad = bars.copy()
    sel = (bad.index >= cut) & (bad.index < cut + pd.Timedelta(hours=6))
    rng = np.random.default_rng(0)
    f = np.exp(rng.normal(0, 0.05, sel.sum()))
    for c in ("open", "high", "low", "close"):
        bad.loc[sel, c] = bad.loc[sel, c].to_numpy() * f
    bad["high"] = bad[["open", "high", "low", "close"]].max(axis=1)
    bad["low"] = bad[["open", "high", "low", "close"]].min(axis=1)
    new = signals(bad, **cfg)
    upto = base[base["time"] <= day].reset_index(drop=True)
    new_upto = new[new["time"] <= day].reset_index(drop=True)
    pd.testing.assert_frame_equal(upto, new_upto)  # that day and all earlier days unchanged
    assert len(new) > 0


def test_hand_checked_day():
    # Hand-built range: 09:30-09:34 NY on a flat tape, N=5. Bars for one session only
    # (vol model not warmed up), so supply a synthetic exp_vol via the argument.
    idx = pd.date_range("2024-01-09 14:25", "2024-01-09 21:00", freq="1min", tz="UTC", name="time")
    px = np.full(len(idx), 100.0)
    df = pd.DataFrame({"open": px, "high": px, "low": px, "close": px, "spread": 0.0}, index=idx)
    t0 = pd.Timestamp("2024-01-09 14:30", tz="UTC")
    rows = [(100.0, 100.5, 99.8, 100.2), (100.2, 101.0, 100.1, 100.8), (100.8, 101.2, 100.6, 101.0),
            (101.0, 101.1, 100.4, 100.6), (100.6, 101.0, 100.5, 100.9)]
    for i, r in enumerate(rows):
        df.loc[t0 + pd.Timedelta(minutes=i), ["open", "high", "low", "close"]] = r
    # O=100.0 H=101.2 L=99.8 C=100.9 -> long, stop 99.8, risk 1.1
    ev = pd.Series(0.0005, index=pd.date_range("2024-01-09 14:30", periods=2, freq="5min", tz="UTC"))
    s = signals(df, "US100", 5, 3, "candle", exp_vol=ev)
    assert len(s) == 1
    r = s.iloc[0]
    assert r.time == t0 + pd.Timedelta(minutes=4) and r.side == 1 and r.order == "market"
    assert r.stop_price == pytest.approx(99.8)
    assert r.target_price == pytest.approx(100.9 + 3 * 1.1)
    assert r.exit_time == pd.Timestamp("2024-01-09 20:55", tz="UTC")
    assert pd.isna(r.expiry)

    b = signals(df, "US100", 5, None, "breakout", exp_vol=ev).iloc[0]
    assert b.order == "stop" and b.price == pytest.approx(101.2) and b.stop_price == pytest.approx(99.8)
    assert pd.isna(b.target_price)
    assert b.expiry == pd.Timestamp("2024-01-09 17:00", tz="UTC")
    b3 = signals(df, "US100", 5, 3, "breakout", exp_vol=ev).iloc[0]
    assert b3.target_price == pytest.approx(101.2 + 3 * 1.4)

    # short: mirror the tape -> stop at H, target below
    m = df.copy()
    for c in ("open", "high", "low", "close"):
        m[c] = 200.0 - df[c]
    m["high"], m["low"] = m[["open", "high", "low", "close"]].max(axis=1), m[["open", "high", "low", "close"]].min(axis=1)
    ev2 = ev * 1.0
    sh = signals(m, "US100", 5, 3, "candle", exp_vol=ev2).iloc[0]
    assert sh.side == -1 and sh.stop_price == pytest.approx(200.0 - 99.8)
    assert sh.target_price == pytest.approx(200.0 - 100.9 - 3 * 1.1)

    # degenerate: huge expected vol -> skipped; close == extreme -> skipped
    assert len(signals(df, "US100", 5, 3, "candle", exp_vol=ev * 1000)) == 0
    assert len(signals(df, "US100", 5, 3, "candle", exp_vol=ev * np.nan)) == 0
    d = df.copy()
    d.loc[t0 + pd.Timedelta(minutes=4), ["high", "low", "close"]] = (101.5, 100.5, 101.5)
    d.loc[t0 + pd.Timedelta(minutes=2), ["high"]] = 101.5
    d.loc[t0 + pd.Timedelta(minutes=1), ["low"]] = 99.8
    d.loc[t0, ["low"]] = 99.8
    assert len(signals(d, "US100", 5, 3, "candle", exp_vol=ev)) == 1  # C == H is fine for a long
    # short whose close equals the range low is valid (stop is the high, far side)
    e = df.copy()
    e.loc[t0 : t0 + pd.Timedelta(minutes=4), ["open", "high", "low", "close"]] = 100.0
    e.loc[t0, ["high"]] = 100.4
    e.loc[t0 + pd.Timedelta(minutes=4), ["low", "close"]] = (99.0, 99.0)
    se = signals(e, "US100", 5, 3, "candle", exp_vol=ev).iloc[0]
    assert se.side == -1 and se.stop_price == pytest.approx(100.4)
    # missing first bar of the session -> skipped; <80% coverage -> skipped
    assert len(signals(df.drop(t0), "US100", 5, 3, "candle", exp_vol=ev)) == 0
    assert len(signals(df.drop([t0 + pd.Timedelta(minutes=2), t0 + pd.Timedelta(minutes=3)]), "US100", 5, 3, "candle", exp_vol=ev)) == 0
    # doji: C == O -> skipped
    z = df.copy()
    z.loc[t0 + pd.Timedelta(minutes=4), "close"] = 100.0
    assert len(signals(z, "US100", 5, 3, "candle", exp_vol=ev)) == 0


@pytest.mark.parametrize("symbol,tz,hhmm", [("US100", NY, "09:30"), ("GER40", "Europe/Berlin", "09:00")])
def test_dst_local_times(long_bars, symbol, tz, hhmm):
    N = 15
    s = signals(long_bars, symbol=symbol, N=N, tR=None, entry="candle")
    loc = _local(s["time"], tz) + pd.Timedelta(minutes=1)  # end of the last range bar
    h, m = int(hhmm[:2]), int(hhmm[3:])
    expected = h * 60 + m + N
    assert ((loc.hour * 60 + loc.minute) == expected).all()
    months = set(loc.month)
    assert 1 in months and 7 in months
    # UTC offset differs between January and July
    jan = s["time"][loc.month == 1].iloc[0]
    jul = s["time"][loc.month == 7].iloc[0]
    assert (jan.hour, jan.minute) != (jul.hour, jul.minute)
    ex = _local(s["exit_time"], tz)
    assert set(zip(ex.hour, ex.minute)) == ({(15, 55)} if symbol == "US100" else {(17, 25)})


@pytest.mark.parametrize("cfg", CONFIGS, ids=lambda c: f"{c['entry']}-N{c['N']}-t{c['tR']}")
def test_engine_integration(bars, exp_us, cfg):
    s = signals(bars, symbol="US100", exp_vol=exp_us, **cfg)
    assert len(s) > 20
    t = run_backtest(bars, s, CostModel(slippage=0.5), symbol="US100")
    assert len(t) > 10
    ent = _local(t["entry_time"])
    ext = _local(t["exit_time"])
    # entries at or after open + N (local), same day; exits by 15:55 local
    mins_e = ent.hour * 60 + ent.minute
    assert (mins_e >= 9 * 60 + 30 + cfg["N"]).all()
    assert (ext.hour * 60 + ext.minute <= 15 * 60 + 55).all()
    assert (ent.normalize() == ext.normalize()).all()
    if cfg["entry"] == "breakout":
        assert (mins_e < 12 * 60).all()  # never after the 12:00 expiry
        assert (t["order"] == "stop").all()
    else:
        assert (t["order"] == "market").all()
        assert (mins_e == 9 * 60 + 30 + cfg["N"]).all()
    assert (t["risk"] > 0).all()
