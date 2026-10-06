"""Tests for the A1 intraday-momentum signal generator (synthetic data only)."""
import numpy as np
import pandas as pd
import pytest

from pfbot.backtest.engine import CostModel, run_backtest
from pfbot.data.synthetic import make_bars
from pfbot.research.harness import SESSIONS, local_times, price_at
from pfbot.strategies import a1_intraday_momentum as a1
from pfbot.strategies.a1_intraday_momentum import CONFIGS, signals

NY = "America/New_York"
START, DAYS = "2023-06-01", 330  # warm-up ends ~Nov 2023; covers Jan and Jul 2024
BASE = dict(symbol="US100", z=0.0, k=1.5, confirm=False)


@pytest.fixture(scope="module", autouse=True)
def _memo_expected_vol():
    """Memoise the (slow) vol forecast across tests; the key includes the price content so a
    corrupted copy of the bars is never served a cached forecast."""
    real, cache = a1.expected_bar_vol, {}

    def memo(b, **kw):
        key = (len(b), float(b["close"].to_numpy().sum()), float(b["open"].to_numpy()[-1]), tuple(sorted(kw.items())))
        if key not in cache:
            cache[key] = real(b, **kw)
        return cache[key]

    mp = pytest.MonkeyPatch()
    mp.setattr(a1, "expected_bar_vol", memo)
    yield
    mp.undo()


@pytest.fixture(scope="module")
def bars():
    # make_bars has its daily break at 21:00-22:00 UTC, i.e. 16:00-17:00 New York in winter, so
    # the 16:00 ET exit would have no bar. Shift the clock by 2h so the break sits at
    # 18:00-19:00 ET (winter) / 19:00-20:00 ET (summer), as in the real 17:00-18:00 ET break.
    b = make_bars(START, DAYS, seed=3)
    b.index = b.index + pd.Timedelta(hours=2)
    return b


@pytest.fixture(scope="module")
def sigs(bars):
    cache = {}

    def get(z=0.0, k=1.5, confirm=False, symbol="US100"):
        key = (symbol, z, k, confirm)
        if key not in cache:
            cache[key] = signals(bars, symbol=symbol, z=z, k=k, confirm=confirm)
        return cache[key]

    return get


def ny(ts):
    return pd.DatetimeIndex(ts).tz_convert(NY)


def test_configs_grid():
    assert len(CONFIGS) == 12
    assert {c["z"] for c in CONFIGS} == {0.0, 0.5, 1.0}
    assert {c["k"] for c in CONFIGS} == {1.5, 2.5}
    assert {c["confirm"] for c in CONFIGS} == {False, True}


def test_signal_table_basics(sigs):
    s = sigs(0.0, 1.5, False)
    assert len(s) > 80
    assert set(s["side"]) <= {-1, 1}
    assert (s["order"] == "market").all()
    assert (s["stop_dist"] > 0).all()
    assert s["time"].is_monotonic_increasing and s["time"].is_unique
    # decision bar is the one closing at the entry instant, exit is the session close
    local = ny(s["time"] + pd.Timedelta(minutes=1))
    assert (local.hour == 15).all() and (local.minute == 30).all()
    assert ((s["exit_time"] - s["time"]) == pd.Timedelta(minutes=31)).all()


@pytest.mark.parametrize("cut_hhmm,lag", [("15:31", 1), ("15:30", 0)])
def test_no_lookahead(bars, sigs, cut_hhmm, lag):
    base = sigs(0.0, 1.5, True)
    # a mid-sample day that has a (confirmed) signal
    day = base["time"].dt.tz_convert(NY).iloc[len(base) // 2].tz_localize(None).normalize()
    cutoff = local_times([day], cut_hhmm, NY)[0]

    bad = bars.copy()
    m = bad.index >= cutoff
    bad.loc[m, ["open", "high", "low", "close"]] *= 1.5  # keeps OHLC valid
    assert (bad["high"] >= bad["low"]).all()
    bad_sigs = signals(bad, symbol="US100", z=0.0, k=1.5, confirm=True)

    lim = cutoff - pd.Timedelta(minutes=lag)
    a = base[base["time"] < lim].reset_index(drop=True)
    b = bad_sigs[bad_sigs["time"] < lim].reset_index(drop=True)
    assert len(a) > 20
    pd.testing.assert_frame_equal(a, b)
    # the cutoff day's own decision (bar 15:29) is among the compared signals
    assert a["time"].max() == local_times([day], "15:29", NY)[0]


def test_side_is_sign_of_opening_return(bars, sigs):
    s = sigs(0.0, 1.5, False)
    local = ny(s["time"])
    d = local.tz_localize(None).normalize()
    # independent recomputation of the raw opening return (previous weekday close -> 10:00)
    prev_d = pd.DatetimeIndex([x - pd.offsets.BDay(1) for x in d])
    raw = np.log(price_at(bars, local_times(d, "10:00", NY)) / price_at(bars, local_times(prev_d, "16:00", NY)))
    assert np.isfinite(raw).all()
    assert (np.sign(raw) == s["side"].to_numpy()).all()
    assert (np.sign(s["r_open"]) == s["side"]).all()


def test_z_filter(sigs):
    n0, n05, n1 = (len(sigs(z, 1.5, False)) for z in (0.0, 0.5, 1.0))
    assert n0 > n05 > n1 > 0
    s1 = sigs(1.0, 1.5, False)
    assert (s1["r_open"].abs() >= 1.0).all()
    # z only filters: the z=1 signals are a subset of the z=0 signals
    s0 = sigs(0.0, 1.5, False)
    assert set(s1["time"]) <= set(s0["time"])


@pytest.mark.parametrize("z", [0.0, 0.5, 1.0])
def test_confirm_is_subset(sigs, z):
    plain = sigs(z, 1.5, False).set_index("time")
    conf = sigs(z, 1.5, True).set_index("time")
    assert 0 < len(conf) < len(plain)
    assert conf.index.isin(plain.index).all()
    assert (conf["side"] == plain.loc[conf.index, "side"]).all()
    assert (np.sign(conf["r_late"]) == conf["side"]).all()


def test_stop_scales_with_k(sigs):
    a, b = sigs(0.0, 1.5, False), sigs(0.0, 2.5, False)
    assert (a["time"] == b["time"]).all()
    np.testing.assert_allclose(b["stop_dist"] / a["stop_dist"], 2.5 / 1.5)


def test_dst_entry_at_1530_new_york(sigs):
    s = sigs(0.0, 1.5, False)
    entry = ny(s["time"] + pd.Timedelta(minutes=1))
    exit_ = ny(s["exit_time"])
    for month in (1, 7):
        sel = entry.month == month
        assert sel.sum() > 5, f"no signals in month {month}"
        assert (entry[sel].hour == 15).all() and (entry[sel].minute == 30).all()
        assert (exit_[sel].hour == 16).all() and (exit_[sel].minute == 0).all()
    # UTC offset really differs between the two seasons
    assert entry[entry.month == 1][0].utcoffset() != entry[entry.month == 7][0].utcoffset()


def test_ger40_analogue(bars):
    s = signals(bars, symbol="GER40", z=0.0, k=1.5, confirm=False)
    assert len(s) > 80
    entry = (s["time"] + pd.Timedelta(minutes=1)).dt.tz_convert("Europe/Berlin")
    assert (entry.dt.hour == 17).all() and (entry.dt.minute == 0).all()
    ex = s["exit_time"].dt.tz_convert("Europe/Berlin")
    assert (ex.dt.hour == 17).all() and (ex.dt.minute == 30).all()
    # confirmation window 16:30-17:00 Berlin
    sc = signals(bars, symbol="GER40", z=0.0, k=1.5, confirm=True)
    assert 0 < len(sc) < len(s)


def test_engine_integration(bars, sigs):
    s = sigs(0.5, 2.5, True)
    t = run_backtest(bars, s, CostModel(slippage=0.5), symbol="US100")
    assert len(t) > 10
    assert len(t) == len(s)
    et, xt = ny(t["entry_time"]), ny(t["exit_time"])
    assert (et.hour == 15).all() and (et.minute == 30).all()
    close = pd.DatetimeIndex([x.normalize() + pd.Timedelta(hours=16) for x in xt.tz_localize(None)]).tz_localize(NY)
    assert (xt <= close).all()
    assert set(t["exit_reason"]) <= {"stop", "time"}
    assert (t["side"] == s["side"].to_numpy()).all()
    assert np.isfinite(t["R"]).all()


def test_skips_when_exit_bar_missing():
    # unshifted make_bars: in winter the 21:00 UTC break starts exactly at the 16:00 ET exit, so
    # there is no bar within 5 minutes of the exit instant -> those days are skipped; summer is kept.
    b = make_bars(START, DAYS, seed=3)
    s = signals(b, symbol="US100", z=0.0, k=1.5, confirm=False)
    months = ny(s["time"]).month
    assert (months == 7).sum() > 5
    assert (months == 1).sum() == 0
