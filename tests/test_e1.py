"""Tests for the E1 (VIX term structure / spike) signal generator and the CBOE loader (synthetic data only)."""
import numpy as np
import pandas as pd
import pytest

from pfbot.backtest.engine import run_backtest
from pfbot.data import cboe
from pfbot.data.synthetic import make_bars
from pfbot.research import harness
from pfbot.research.harness import local_times, price_at
from pfbot.strategies import daily_common as dc
from pfbot.strategies import e1_vix as e1

NY = "America/New_York"
START, DAYS = "2023-06-01", 330  # HAR warm-up ends ~Nov 2023
PRICE = ["open", "high", "low", "close"]
MIN = pd.Timedelta(minutes=1)
TS = dict(variant="ts", th=0.95)
SPIKE = dict(variant="spike", jump=0.10)
ALWAYS = dict(variant="always")


@pytest.fixture(scope="module")
def bars():
    # shift by 2h so the synthetic daily break sits after the NY close (as in tests/test_b_daily.py)
    b = make_bars(START, DAYS, seed=3)
    b.index = b.index + pd.Timedelta(hours=2)
    return b


@pytest.fixture(scope="module")
def dates(bars):
    return dc.ny_trading_dates(bars)


@pytest.fixture(scope="module")
def vols(dates):
    rng = np.random.default_rng(11)
    vix = pd.Series(18 * np.exp(0.12 * rng.standard_normal(len(dates))), index=dates)
    vix3m = pd.Series(18 * np.exp(0.03 * rng.standard_normal(len(dates))), index=dates)
    return vix, vix3m


@pytest.fixture(scope="module")
def sigs(bars, vols):
    cache = {}

    def get(**cfg):
        key = tuple(sorted(cfg.items()))
        if key not in cache:
            cache[key] = e1.signals(bars, symbol="US100", vix=vols[0], vix3m=vols[1], **cfg)
        return cache[key]

    return get


def ny(ts):
    return pd.DatetimeIndex(ts).tz_convert(NY)


def prev_day(dates, d):
    return dates[dates.get_loc(d) - 1]


# ---------------------------------------------------------------------------------------------
def test_configs_grid():
    assert len(e1.CONFIGS) == 5
    assert [c for c in e1.CONFIGS if c["variant"] == "ts"] == [dict(variant="ts", th=t) for t in (0.90, 0.95, 1.00)]
    assert [c for c in e1.CONFIGS if c["variant"] == "spike"] == [dict(variant="spike", jump=j) for j in (0.10, 0.20)]
    assert e1.BENCHMARK == dict(variant="always") and e1.BENCHMARK not in e1.CONFIGS


def test_unknown_variant_and_missing_params(bars, vols):
    with pytest.raises(ValueError):
        e1.signals(bars, symbol="US100", variant="nope", vix=vols[0], vix3m=vols[1])
    with pytest.raises(ValueError):
        e1.signals(bars, symbol="US100", variant="ts", vix=vols[0], vix3m=vols[1])  # no th
    with pytest.raises(ValueError):
        e1.signals(bars, symbol="US100", variant="spike", vix=vols[0])  # no jump


# ---------------------------------------------------------------------------------------------
# calendar / mapping
# ---------------------------------------------------------------------------------------------
@pytest.mark.parametrize("cfg", [TS, SPIKE, ALWAYS])
def test_entry_exit_instants_and_mapping(sigs, dates, cfg):
    s = sigs(**cfg)
    assert len(s) > 40
    assert set(s["side"]) == {1} and (s["order"] == "market").all() and (s["stop_dist"] > 0).all()
    ent, ex = ny(s["time"] + MIN), ny(s["exit_time"])
    assert (ent.hour == 9).all() and (ent.minute == 35).all()
    assert (ex.hour == 9).all() and (ex.minute == 30).all()
    assert (ent.tz_localize(None).normalize() == pd.DatetimeIndex(s["date"])).all()
    assert (ex.tz_localize(None).normalize() == pd.DatetimeIndex(s["exit_date"])).all()
    for _, r in s.iterrows():  # VIX day = previous trading day, exit day = next trading day
        i = dates.get_loc(r["date"])
        assert r["vix_date"] == dates[i - 1] and r["exit_date"] == dates[i + 1]
        assert r["vix_date"] < r["date"] < r["exit_date"]
    # information day is strictly before the entry day, and covers Fri -> Mon and Mon -> Tue
    dow = pd.DatetimeIndex(s["date"]).dayofweek
    assert {0, 1, 2, 3, 4} <= set(dow)
    assert (pd.DatetimeIndex(s.loc[dow == 0, "vix_date"]).dayofweek == 4).all()
    assert ((pd.DatetimeIndex(s.loc[dow == 0, "date"]) - pd.DatetimeIndex(s.loc[dow == 0, "vix_date"])).days == 3).all()
    assert ((pd.DatetimeIndex(s.loc[dow == 4, "exit_date"]) - pd.DatetimeIndex(s.loc[dow == 4, "date"])).days == 3).all()


def test_dst_entry_times(sigs):
    s = sigs(**ALWAYS)
    ent = ny(s["time"] + MIN)
    for month in (1, 7):
        sel = ent.month == month
        assert sel.sum() > 10
        assert (ent[sel].hour == 9).all() and (ent[sel].minute == 35).all()
    # 09:35 ET is 14:35 UTC in winter and 13:35 UTC in summer
    assert (s["time"] + MIN)[ent.month == 1].iloc[0].hour == 14
    assert (s["time"] + MIN)[ent.month == 7].iloc[0].hour == 13


def test_holiday_and_weekend_mapping(bars, vols):
    """A holiday (no bars, no VIX) is bridged: Friday's VIX is used on Tuesday after a Monday holiday."""
    vix, vix3m = vols
    dates = dc.ny_trading_dates(bars)
    base = e1.signals(bars, "US100", **ALWAYS)
    # pick a Monday late in the sample and remove it from bars and from both VIX series
    mondays = [d for d in pd.DatetimeIndex(base["date"]) if d.dayofweek == 0]
    mon = mondays[len(mondays) // 2]
    fri = mon - pd.Timedelta(days=3)
    m = ny(bars.index)
    nomon = bars[~(m.tz_localize(None).normalize() == mon)]
    s = e1.signals(nomon, "US100", vix=vix.drop(mon), vix3m=vix3m.drop(mon), **TS | dict(th=1e9))
    tue = mon + pd.Timedelta(days=1)
    r = s[s["date"] == tue]
    assert len(r) == 1 and r.iloc[0]["vix_date"] == fri
    assert mon not in set(s["date"]) and mon not in set(s["exit_date"]) and mon not in set(s["vix_date"])
    # Friday's trade exits Tuesday (4 calendar days over the holiday weekend), allowed
    r = s[s["date"] == fri]
    assert len(r) == 1 and r.iloc[0]["exit_date"] == tue
    # the same holiday where the VIX series still has a value for that date (data hole in the bars only):
    # the preceding trading day is then missing in the bars -> Tuesday is skipped, nothing is carried forward
    s2 = e1.signals(nomon, "US100", vix=vix, vix3m=vix3m, **TS | dict(th=1e9))
    # (Friday's own trade is skipped as well: its exit day Tuesday is not the next trading day of the VIX calendar)
    assert tue not in set(s2["date"]) and fri not in set(s2["date"])


# ---------------------------------------------------------------------------------------------
# variant logic
# ---------------------------------------------------------------------------------------------
def _expected_dates(dates, go_fn):
    """Entry dates e (all trading dates but the first and last) with go_fn(prev trading day d, e)."""
    out = []
    for i in range(1, len(dates) - 1):
        if go_fn(dates[i - 1], dates[i], i):
            out.append(dates[i])
    return out


@pytest.mark.parametrize("th", [0.90, 0.95, 1.00])
def test_ts_logic(sigs, dates, vols, th):
    vix, vix3m = vols
    s = sigs(variant="ts", th=th)
    ratio = (vix / vix3m)
    exp = set(_expected_dates(dates, lambda d, e, i: ratio[d] < th)) & set(sigs(**ALWAYS)["date"])
    assert set(s["date"]) == exp and 0 < len(s) < len(sigs(**ALWAYS))
    np.testing.assert_allclose(s["metric"].to_numpy(), ratio.loc[s["vix_date"]].to_numpy())
    assert (s["metric"] < th).all()
    # monotone in th: neighbouring grid points nest
    assert set(sigs(variant="ts", th=0.90)["date"]) <= set(sigs(variant="ts", th=0.95)["date"]) <= set(
        sigs(variant="ts", th=1.00)["date"])


def test_ts_threshold_is_strict(bars, dates):
    vix = pd.Series(20.0, index=dates)
    vix3m = pd.Series(20.0, index=dates)  # ratio exactly 1.0 everywhere
    assert len(e1.signals(bars, "US100", variant="ts", th=1.0, vix=vix, vix3m=vix3m)) == 0
    assert len(e1.signals(bars, "US100", variant="ts", th=1.0 + 1e-9, vix=vix, vix3m=vix3m)) > 40
    assert len(e1.signals(bars, "US100", variant="ts", th=0.95, vix=vix * 0.94, vix3m=vix3m)) > 40


@pytest.mark.parametrize("jump", [0.10, 0.20])
def test_spike_logic(sigs, dates, vols, jump):
    vix = vols[0]
    s = sigs(variant="spike", jump=jump)
    chg = vix / vix.shift(1) - 1
    exp = set(_expected_dates(dates, lambda d, e, i: chg[d] >= jump)) & set(sigs(**ALWAYS)["date"])
    assert set(s["date"]) == exp and len(s) >= 5
    np.testing.assert_allclose(s["metric"].to_numpy(), chg.loc[s["vix_date"]].to_numpy())
    assert set(sigs(variant="spike", jump=0.20)["date"]) <= set(sigs(variant="spike", jump=0.10)["date"])


def test_spike_boundary_inclusive(bars, dates):
    vix = pd.Series(20.0, index=dates)
    d = dates[300]
    vix[d] = 22.0  # exactly +10% (floating point: 22/20 - 1 = 0.10000000000000009 or 0.0999..)
    s = e1.signals(bars, "US100", variant="spike", jump=0.10, vix=vix)
    assert list(s["date"]) == [dates[301]] and s.iloc[0]["vix_date"] == d
    vix[d] = 21.99
    assert len(e1.signals(bars, "US100", variant="spike", jump=0.10, vix=vix)) == 0
    # jump 0.1 computed through a awkward float pair
    vix[d] = 1.1 * 17.3
    vix[dates[299]] = 17.3
    assert len(e1.signals(bars, "US100", variant="spike", jump=0.10, vix=vix)) == 1


def test_always_is_superset_and_needs_no_vix(bars, sigs):
    a = sigs(**ALWAYS)
    for cfg in (TS, SPIKE):
        assert set(sigs(**cfg)["date"]) <= set(a["date"])
    nov = e1.signals(bars, "US100", variant="always")  # no VIX passed, none loaded
    pd.testing.assert_frame_equal(nov, a)
    # stop distances of a given day are identical across variants (same stop machinery)
    ts = sigs(**TS)
    np.testing.assert_allclose(a.set_index("date").loc[ts["date"], "stop_dist"].to_numpy(), ts["stop_dist"].to_numpy())


def test_missing_vix_skips_day(bars, dates, vols, sigs):
    vix, vix3m = vols
    base_ts = e1.signals(bars, "US100", variant="ts", th=1e9, vix=vix, vix3m=vix3m)
    d = dates[300]
    e = dates[301]
    assert e in set(base_ts["date"])
    # VIX missing on d -> entry on d+1 skipped (nothing carried forward), d+2 unaffected for ts
    s = e1.signals(bars, "US100", variant="ts", th=1e9, vix=vix.drop(d), vix3m=vix3m)
    assert set(base_ts["date"]) - set(s["date"]) == {e}
    s = e1.signals(bars, "US100", variant="ts", th=1e9, vix=vix, vix3m=vix3m.drop(d))
    assert set(base_ts["date"]) - set(s["date"]) == {e}
    # spike: VIX(d) missing kills entries d+1 (no value) and d+2 (no previous-day value)
    base_sp = e1.signals(bars, "US100", variant="spike", jump=-10, vix=vix)
    s = e1.signals(bars, "US100", variant="spike", jump=-10, vix=vix.drop(d))
    assert set(base_sp["date"]) - set(s["date"]) == {e, dates[302]}
    # always does not look at the VIX at all
    assert len(sigs(**ALWAYS)) > len(base_ts) * 0  # smoke


def test_missing_bars_skip(bars, dates, vols):
    vix, vix3m = vols
    kw = dict(variant="ts", th=1e9, vix=vix, vix3m=vix3m)
    base = e1.signals(bars, "US100", **kw)
    e = base["date"].iloc[40]
    # no bar within 5 minutes of the entry instant -> skipped
    t = local_times([e], "09:35", NY)[0]
    hole = bars[~((bars.index >= t - pd.Timedelta(minutes=4)) & (bars.index < t + pd.Timedelta(minutes=10)))]
    s = e1.signals(hole, "US100", **kw)
    assert e not in set(s["date"]) and len(s) == len(base) - 1
    # a missing 09:30 bar removes the date from the calendar (the 09:30 bar defines trading dates): the
    # entry on that date, the entry on the day before (its exit day is gone and a VIX print lies between
    # the dates) and the entry on the day after (its VIX day is missing) are all skipped, nothing else
    m = ny(bars.index).tz_localize(None).normalize()
    nodays = bars[~(m == e)]
    s2 = e1.signals(nodays, "US100", **kw)
    i = dates.get_loc(e)
    assert set(base["date"]) - set(s2["date"]) == {dates[i - 1], e, dates[i + 1]}
    # with no 09:30 bar the exit date cannot be mapped even if other bars of the day remain
    t1 = local_times([e], "09:30", NY)[0]
    s3 = e1.signals(bars[bars.index != t1], "US100", **kw)
    assert set(base["date"]) - set(s3["date"]) == {dates[i - 1], e, dates[i + 1]}


def test_stop_formula(bars, sigs):
    s = sigs(**TS)
    fc = dc.daily_variance_forecast(bars, pd.DatetimeIndex(s["date"]))
    px = price_at(bars, local_times(s["date"], "09:35", NY))
    np.testing.assert_allclose(s["stop_dist"], 3 * np.sqrt(fc * 1.0) * px)
    assert (s["stop_dist"] / px).between(0.005, 0.2).all()


# ---------------------------------------------------------------------------------------------
# no look-ahead
# ---------------------------------------------------------------------------------------------
@pytest.mark.parametrize("cfg", [TS, SPIKE, ALWAYS])
def test_no_lookahead_vix(bars, dates, vols, sigs, cfg):
    vix, vix3m = vols
    base = sigs(**cfg) if cfg is not ALWAYS else sigs(**TS)
    cfg2 = cfg if cfg is not ALWAYS else TS
    d = base["vix_date"].iloc[len(base) // 2]  # VIX day whose value is changed
    e = dates[dates.get_loc(d) + 1]
    cutoff = local_times([e], "09:35", NY)[0]  # first instant at which d's close may be used
    bad_vix, bad_vix3m = vix.copy(), vix3m.copy()
    bad_vix[d] *= 0.3
    bad_vix3m[d] *= 3.0
    bad = e1.signals(bars, "US100", vix=bad_vix, vix3m=bad_vix3m, **cfg2)
    # signal `time` is the decision bar, decided at its close (time + 1 min): compare decisions before 09:35
    ok = base[base["time"] + MIN < cutoff].reset_index(drop=True)
    ok2 = bad[bad["time"] + MIN < cutoff].reset_index(drop=True)
    assert len(ok) > 10
    pd.testing.assert_frame_equal(ok, ok2)
    # the benchmark never changes; the conditioned variants react on day e (sanity check of the test)
    if cfg2 is not ALWAYS:
        assert not base[base["date"] == e].equals(bad[bad["date"] == e])
    # values of d+1 and later never influence the decision for e: change them, signals up to and
    # including e's decision are identical
    bad_vix2, bad_vix3m2 = vix.copy(), vix3m.copy()
    later = vix.index > d
    bad_vix2[later] *= 0.2
    bad_vix3m2[later] *= 4.0
    bad2 = e1.signals(bars, "US100", vix=bad_vix2, vix3m=bad_vix3m2, **cfg2)
    pd.testing.assert_frame_equal(base[base["time"] < cutoff].reset_index(drop=True),  # incl. e's own decision
                                  bad2[bad2["time"] < cutoff].reset_index(drop=True))


def test_no_lookahead_vix_all_dates_exhaustive(bars, dates, vols):
    """For many d: changing VIX(d) changes nothing decided before 09:35 ET of the next trading day."""
    vix, vix3m = vols
    base = e1.signals(bars, "US100", **TS, vix=vix, vix3m=vix3m)
    for d in dates[200:320:7]:
        e = dates[dates.get_loc(d) + 1]
        cutoff = local_times([e], "09:35", NY)[0]
        v2 = vix.copy()
        v2[d] = v2[d] * 1.7
        bad = e1.signals(bars, "US100", **TS, vix=v2, vix3m=vix3m)
        pd.testing.assert_frame_equal(base[base["time"] + MIN < cutoff].reset_index(drop=True),
                                      bad[bad["time"] + MIN < cutoff].reset_index(drop=True))


@pytest.mark.parametrize("cfg", [TS, SPIKE, ALWAYS])
def test_no_lookahead_prices(bars, vols, sigs, cfg):
    vix, vix3m = vols
    base = sigs(**cfg)
    e = base["date"].iloc[len(base) // 2]
    cutoff = local_times([e], "09:35", NY)[0]  # entry instant of day e
    bad = bars.copy()
    bad.loc[bad.index >= cutoff, ["open", "high", "low", "close"]] *= 1.5
    bad_sigs = e1.signals(bad, "US100", vix=vix, vix3m=vix3m, **cfg)
    a = base[base["time"] < cutoff].reset_index(drop=True)
    b = bad_sigs[bad_sigs["time"] < cutoff].reset_index(drop=True)
    assert len(a) > 5 and a["date"].iloc[-1] == e  # e's own decision (bar 09:34) is compared
    pd.testing.assert_frame_equal(a, b)
    # corrupting the decision bar (09:34) itself does change that day's stop (it is the entry price)
    bad2 = bars.copy()
    bad2.loc[bad2.index >= cutoff - MIN, ["open", "high", "low", "close"]] *= 1.5
    s2 = e1.signals(bad2, "US100", vix=vix, vix3m=vix3m, **cfg)
    assert base[base["date"] == e].iloc[0]["stop_dist"] != s2[s2["date"] == e].iloc[0]["stop_dist"]


# ---------------------------------------------------------------------------------------------
# engine integration
# ---------------------------------------------------------------------------------------------
@pytest.mark.parametrize("cfg", [*e1.CONFIGS, e1.BENCHMARK])
@pytest.mark.parametrize("symbol", ["US100", "US500"])
def test_engine_integration(bars, vols, cfg, symbol):
    s = e1.signals(bars, symbol, vix=vols[0], vix3m=vols[1], **cfg)
    assert len(s) >= 5, cfg
    t = run_backtest(bars, s, harness.cost_model(symbol), symbol=symbol)
    assert len(t) == len(s)  # 09:30 exit then 09:35 entry: the engine never drops a signal
    assert (t["side"] == 1).all() and (t["risk"] > 0).all() and np.isfinite(t["R"]).all()
    assert set(t["exit_reason"]) <= {"stop", "time"}
    assert ((t["entry_time"] - t["signal_time"]) == MIN).all()
    e = ny(t["entry_time"])
    assert (e.hour == 9).all() and (e.minute == 35).all()
    te = t[t["exit_reason"] == "time"]
    assert len(te) > 3
    x = ny(te["exit_time"])
    assert (x.hour == 9).all() and (x.minute == 30).all()
    assert (te["exit_time"].to_numpy() == s.set_index("time").loc[te["signal_time"], "exit_time"].to_numpy()).all()
    assert (t["entry_time"].iloc[1:].to_numpy() > t["exit_time"].iloc[:-1].to_numpy()).all()  # no overlap


def test_engine_run_grid_logs_only_given_registry(bars, vols, tmp_path):
    from pfbot.stats.performance import TrialRegistry

    reg = TrialRegistry(tmp_path / "t.jsonl")
    fn = lambda b, symbol, **cfg: e1.signals(b, symbol, vix=vols[0], vix3m=vols[1], **cfg)  # noqa: E731
    res, trades = harness.run_grid("E1", "US100", "IS", bars, fn, e1.CONFIGS, spread_mults=(1.0, 1.5), registry=reg)
    assert len(res) == 10 and len(reg.load("E1")) == 5
    assert {r["params"]["variant"] for r in reg.load("E1")} == {"ts", "spike"}


# ---------------------------------------------------------------------------------------------
# CBOE loader
# ---------------------------------------------------------------------------------------------
def test_load_vix_tmp_csv(tmp_path):
    (tmp_path / "VIX_History.csv").write_text(
        "DATE,OPEN,HIGH,LOW,CLOSE\n01/05/2015,1,2,1,20.5\n01/02/2015,1,2,1,17.0\n01/06/2015,1,2,1,\n01/07/2015,1,2,1,0\n"
        "01/08/2015,1,2,1,19.0\n"
    )
    s = cboe.load_vix("VIX", root=tmp_path)
    assert s.index.tz is None and s.index.is_monotonic_increasing
    assert list(s.index) == [pd.Timestamp("2015-01-02"), pd.Timestamp("2015-01-05"), pd.Timestamp("2015-01-08")]
    assert list(s) == [17.0, 20.5, 19.0]


def test_load_vix_real_files():
    vix, vix3m = cboe.load_vix("VIX"), cboe.load_vix("VIX3M")
    for s in (vix, vix3m):
        assert s.index.tz is None and s.index.is_monotonic_increasing and s.index.is_unique
        assert (s > 0).all() and s.index.min() <= pd.Timestamp("2015-01-02") and s.index.max() >= pd.Timestamp("2020-12-31")
    assert 9 < vix["2017-06-01":"2017-06-30"].mean() < 20
    assert vix.loc["2020-03-16"] > 70
