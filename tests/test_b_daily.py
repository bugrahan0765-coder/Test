"""Tests for the B1 / B2 / B3 signal generators and daily_common (synthetic data only)."""
import numpy as np
import pandas as pd
import pytest

from pfbot.backtest.engine import run_backtest
from pfbot.data.synthetic import make_bars
from pfbot.features.volatility import daily_realized_vol, har_rv_forecast, intraday_returns
from pfbot.research import harness
from pfbot.research.harness import SESSIONS, local_times, price_at
from pfbot.strategies import b1_turn_of_month as b1
from pfbot.strategies import b2_overnight_drift as b2
from pfbot.strategies import b3_tsmom as b3
from pfbot.strategies import daily_common as dc

NY = "America/New_York"
START, DAYS = "2023-06-01", 330  # HAR warm-up ends ~Nov 2023; covers Jan and Jul 2024
PRICE = ["open", "high", "low", "close"]
MIN = pd.Timedelta(minutes=1)


@pytest.fixture(scope="module")
def bars():
    # make_bars has its daily break at 21:00-22:00 UTC (16:00-17:00 New York in winter); shift by 2h so
    # the break sits at 18:00-19:00 ET (winter) / 19:00-20:00 ET (summer), as in tests/test_a1.py.
    b = make_bars(START, DAYS, seed=3)
    b.index = b.index + pd.Timedelta(hours=2)
    return b


@pytest.fixture(scope="module")
def sigs(bars):
    cache = {}

    def get(mod, symbol="US100", **cfg):
        key = (mod.__name__, symbol, tuple(sorted(cfg.items())))
        if key not in cache:
            cache[key] = mod.signals(bars, symbol=symbol, **cfg)
        return cache[key]

    return get


def ny(ts):
    return pd.DatetimeIndex(ts).tz_convert(NY)


def corrupt(bars, cutoff):
    """Copy of bars with prices from `cutoff` (UTC) on scaled by 1.5 (keeps OHLC valid)."""
    bad = bars.copy()
    bad.loc[bad.index >= cutoff, PRICE] *= 1.5
    return bad


B1_BASE = dict(d_in=-1, d_out=2, k=2)
B2_BASE = dict(t_in="15:55", t_out="09:31", fri=True)
B3_BASE = dict(L=20, k=2, long_only=False)


# ---------------------------------------------------------------------------------------------
# grids
# ---------------------------------------------------------------------------------------------
def test_configs_grid():
    assert len(b1.CONFIGS) == 8
    assert {c["d_in"] for c in b1.CONFIGS} == {-2, -1} and {c["d_out"] for c in b1.CONFIGS} == {2, 3}
    assert {c["k"] for c in b1.CONFIGS} == {2, 3}
    assert len(b2.CONFIGS) == 8
    assert {c["t_in"] for c in b2.CONFIGS} == {"15:55", "16:10"}
    assert {c["t_out"] for c in b2.CONFIGS} == {"09:31", "09:45"}
    assert {c["fri"] for c in b2.CONFIGS} == {False, True}
    assert len(b3.CONFIGS) == 12
    assert {c["L"] for c in b3.CONFIGS} == {20, 60, 120} and {c["k"] for c in b3.CONFIGS} == {2, 3}
    assert {c["long_only"] for c in b3.CONFIGS} == {False, True}


# ---------------------------------------------------------------------------------------------
# daily_common
# ---------------------------------------------------------------------------------------------
def test_trading_dates_and_closes_dst(bars):
    dates = dc.ny_trading_dates(bars)
    assert dates.is_monotonic_increasing and dates.is_unique
    assert (dates.dayofweek < 5).all() and len(dates) > 300
    t = local_times(dates, dc.DECISION_TIME, NY)
    for month in (1, 7):
        sel = t[dates.month == month]
        assert len(sel) > 15
        assert (ny(sel).hour == 15).all() and (ny(sel).minute == 55).all()
    # 15:55 ET is 20:55 UTC in winter and 19:55 UTC in summer
    assert t[dates.month == 1][0].hour == 20 and t[dates.month == 7][0].hour == 19
    closes = dc.daily_closes(bars, dates)
    assert np.isfinite(closes).all()
    np.testing.assert_array_equal(closes, price_at(bars, t))


def test_decision_bar(bars):
    dates = dc.ny_trading_dates(bars)[100:105]
    t = local_times(dates, "15:55", NY)
    dec, fill, ok = dc.decision_bar(bars, t)
    assert ok.all()
    assert ((t - dec) == MIN).all() and (fill == t).all()
    # a hole of 10 minutes around the instant: not ok
    hole = bars[~((bars.index >= t[0] - pd.Timedelta(minutes=10)) & (bars.index < t[0] + pd.Timedelta(minutes=10)))]
    _, _, ok2 = dc.decision_bar(hole, t)
    assert not ok2[0] and ok2[1:].all()


def test_forecast_alignment_and_no_lookahead(bars):
    dates = dc.ny_trading_dates(bars)
    fc = dc.daily_variance_forecast(bars, dates)
    rv = daily_realized_vol(bars)
    ref = har_rv_forecast(rv).reindex(dates).to_numpy()
    m = np.isfinite(fc) & np.isfinite(ref)
    assert m.sum() > 150
    np.testing.assert_allclose(fc[m], ref[m])
    # the forecast on date d does not change when every price from the START of trading day d
    # (17:00 ET on the previous calendar day) onwards is corrupted
    d = dates[250]
    cutoff = local_times([d - pd.Timedelta(days=1)], "17:00", NY)[0]
    bad = corrupt(bars, cutoff)
    fc_bad = dc.daily_variance_forecast(bad, dates)
    n = 251  # dates up to and including d
    np.testing.assert_array_equal(fc[:n], fc_bad[:n])
    assert np.isfinite(fc[250]) and np.isfinite(fc_bad[250])
    # ...while a later date does react (sanity check of the test itself)
    assert fc[256] != fc_bad[256]


def test_exit_instants_half_day_fallback(bars):
    dates = dc.ny_trading_dates(bars)
    d = dates[200]
    cut = local_times([d], "13:00", NY)[0]
    end = local_times([d + pd.Timedelta(days=1)], "00:00", NY)[0]
    half = bars[~((bars.index >= cut) & (bars.index < end))]
    # (the shifted synthetic data has bars after midnight ET too; only that calendar date is cut)
    ex, ok = dc.exit_instants(half, pd.DatetimeIndex([d, dates[201]]), "15:55")
    assert ok.all()
    assert ex[0] == cut - MIN  # last bar of the session of the half day starts at 12:59 ET
    assert ex[1] == local_times([dates[201]], "15:55", NY)[0]
    # no fallback for morning exits, and none when disabled
    _, ok_m = dc.exit_instants(half, pd.DatetimeIndex([d]), "15:55", early_close_fallback=False)
    assert not ok_m[0]


# ---------------------------------------------------------------------------------------------
# B1
# ---------------------------------------------------------------------------------------------
def _bday(d, n):
    return d + pd.offsets.BDay(n)


@pytest.mark.parametrize("d_in,d_out", [(-1, 2), (-2, 2), (-1, 3), (-2, 3)])
def test_b1_calendar(sigs, d_in, d_out):
    s = sigs(b1, d_in=d_in, d_out=d_out, k=2)
    assert len(s) >= 8
    assert set(s["side"]) == {1} and (s["order"] == "market").all() and (s["stop_dist"] > 0).all()
    for _, r in s.iterrows():
        d = r["date"]
        last_bd = d.to_period("M").end_time.normalize()
        last_bd = last_bd if last_bd.dayofweek < 5 else last_bd - pd.offsets.BDay(1)
        assert d == _bday(last_bd, d_in + 1), (d, d_in)  # -1 -> last trading day, -2 -> the one before
        first_bd = (d + pd.offsets.MonthBegin(1)).normalize()
        first_bd = first_bd if first_bd.dayofweek < 5 else first_bd + pd.offsets.BDay(1)
        assert r["exit_date"] == _bday(first_bd, d_out - 1)
        assert r["n_days"] == len(pd.bdate_range(d, r["exit_date"])) - 1
    # entries at 15:55 ET (decision bar 15:54), exits at 15:55 ET, DST-correct
    ent, ex = ny(s["time"] + MIN), ny(s["exit_time"])
    assert (ent.hour == 15).all() and (ent.minute == 55).all()
    assert (ex.hour == 15).all() and (ex.minute == 55).all()
    assert (ex.tz_localize(None).normalize() == pd.DatetimeIndex(s["exit_date"])).all()
    assert (ent.tz_localize(None).normalize() == pd.DatetimeIndex(s["date"])).all()


def test_b1_dst_and_stop(bars, sigs):
    s = sigs(b1, **B1_BASE)
    s3 = sigs(b1, d_in=-1, d_out=2, k=3)
    assert (s["time"] == s3["time"]).all()
    np.testing.assert_allclose(s3["stop_dist"] / s["stop_dist"], 1.5)
    # months of both DST regimes are present (Dec/Jan/Feb winter, Jun-Sep summer entries)
    off = {x.utcoffset() for x in ny(s["time"])}
    assert len(off) == 2
    # independent recomputation of the stop: k * sqrt(forecast(entry date) * days held) * price at 15:55
    fc = dc.daily_variance_forecast(bars, pd.DatetimeIndex(s["date"]))
    px = price_at(bars, local_times(s["date"], "15:55", NY))
    np.testing.assert_allclose(s["stop_dist"], 2 * np.sqrt(fc * s["n_days"]) * px)
    # d_out=3 holds one more day -> wider stop
    s_out3 = sigs(b1, d_in=-1, d_out=3, k=2)
    np.testing.assert_allclose((s_out3["stop_dist"] / s["stop_dist"]) ** 2, (s["n_days"] + 1) / s["n_days"])


def test_b1_no_lookahead(bars, sigs):
    base = sigs(b1, **B1_BASE)
    day = base["date"].iloc[len(base) // 2]
    cutoff = local_times([day], "15:55", NY)[0]
    bad_sigs = b1.signals(corrupt(bars, cutoff), symbol="US100", **B1_BASE)
    a = base[base["time"] < cutoff].reset_index(drop=True)
    b = bad_sigs[bad_sigs["time"] < cutoff].reset_index(drop=True)
    assert len(a) >= 3 and a["time"].max() == cutoff - MIN  # the cutoff day's own decision is compared
    pd.testing.assert_frame_equal(a, b)
    # corrupting one bar earlier (15:54, the decision bar) does change that day's stop
    bad2 = b1.signals(corrupt(bars, cutoff - MIN), symbol="US100", **B1_BASE)
    row_a = base[base["date"] == day].iloc[0]
    row_b = bad2[bad2["date"] == day].iloc[0]
    assert row_a["stop_dist"] != row_b["stop_dist"]


def test_b1_skips_missing_month_and_bars(bars, sigs):
    base = sigs(b1, **B1_BASE)
    # drop Jan 2024: Dec's trade (exit in Jan) and Jan's own trade vanish, others stay
    m = ny(bars.index)
    nojan = bars[~((m.year == 2024) & (m.month == 1))]
    s = b1.signals(nojan, symbol="US100", **B1_BASE)
    gone = {pd.Timestamp("2023-12-29"), pd.Timestamp("2024-01-31")}
    assert gone <= set(base["date"]) and not (gone & set(s["date"]))
    assert len(s) == len(base) - 2
    # no bar within 5 minutes of the entry instant -> that month is skipped
    day = base["date"].iloc[3]
    t = local_times([day], "15:55", NY)[0]
    hole = bars[~((bars.index >= t - pd.Timedelta(minutes=10)) & (bars.index < t + pd.Timedelta(minutes=10)))]
    s2 = b1.signals(hole, symbol="US100", **B1_BASE)
    assert day not in set(s2["date"]) and len(s2) == len(base) - 1


# ---------------------------------------------------------------------------------------------
# B2
# ---------------------------------------------------------------------------------------------
@pytest.mark.parametrize("t_in,t_out", [("15:55", "09:31"), ("16:10", "09:45")])
def test_b2_calendar_and_friday_filter(sigs, t_in, t_out):
    nf = sigs(b2, t_in=t_in, t_out=t_out, fri=False)
    wf = sigs(b2, t_in=t_in, t_out=t_out, fri=True)
    assert len(nf) > 100 and len(wf) > len(nf)
    assert (pd.DatetimeIndex(nf["date"]).dayofweek <= 3).all()
    assert (pd.DatetimeIndex(wf["date"]).dayofweek == 4).sum() > 20
    # fri=True adds exactly the Friday entries; everything else is identical
    fridays = wf[pd.DatetimeIndex(wf["date"]).dayofweek == 4]
    assert len(wf) == len(nf) + len(fridays)
    pd.testing.assert_frame_equal(wf[pd.DatetimeIndex(wf["date"]).dayofweek <= 3].reset_index(drop=True), nf)
    # entry instant (decision bar + 1 min) is t_in ET, exit is t_out ET on the next trading day
    h_in, m_in = int(t_in[:2]), int(t_in[3:])
    h_out, m_out = int(t_out[:2]), int(t_out[3:])
    ent, ex = ny(wf["time"] + MIN), ny(wf["exit_time"])
    assert (ent.hour == h_in).all() and (ent.minute == m_in).all()
    assert (ex.hour == h_out).all() and (ex.minute == m_out).all()
    nxt = pd.DatetimeIndex(wf["date"]).map(lambda d: d + pd.offsets.BDay(1))
    assert (ex.tz_localize(None).normalize() == nxt).all()
    assert (pd.DatetimeIndex(wf["exit_date"]) == nxt).all()
    # Friday trades span the weekend (3 calendar days)
    assert ((pd.DatetimeIndex(fridays["exit_date"]) - pd.DatetimeIndex(fridays["date"])).days == 3).all()
    assert (wf["share"] > 0).all() and (wf["share"] < 1.5).all()


def test_b2_dst(sigs):
    s = sigs(b2, **B2_BASE)
    ent, ex = ny(s["time"] + MIN), ny(s["exit_time"])
    for month in (1, 7):
        sel = ent.month == month
        assert sel.sum() > 10
        assert (ent[sel].hour == 15).all() and (ent[sel].minute == 55).all()
    sel = ex.month == 1
    assert (ex[sel].hour == 9).all() and (ex[sel].minute == 31).all()
    assert ent[ent.month == 1][0].utcoffset() != ent[ent.month == 7][0].utcoffset()


def test_b2_share_bruteforce(bars, sigs):
    s = sigs(b2, **B2_BASE)
    dates = dc.ny_trading_dates(bars)
    rv = daily_realized_vol(bars)
    ir = intraday_returns(bars, "5min")
    row = s.iloc[len(s) // 2]
    p = int(dates.get_loc(row["date"]))
    num = den = 0.0
    for q in range(p - 60, p):  # exit dates = the 60 session dates strictly before d
        t0 = local_times([dates[q - 1]], "15:55", NY)[0]
        t1 = local_times([dates[q]], "09:31", NY)[0]
        m = (ir.index >= t0) & (ir.index + pd.Timedelta(minutes=5) <= t1)
        num += (ir["r"][m] ** 2).sum()
        den += rv.loc[dates[q]]
    assert row["share"] == pytest.approx(num / den, rel=1e-9)
    fc = dc.daily_variance_forecast(bars, pd.DatetimeIndex([row["date"]]))[0]
    px = price_at(bars, local_times([row["date"]], "15:55", NY))[0]
    assert row["stop_dist"] == pytest.approx(3 * np.sqrt(fc * row["share"]) * px)


@pytest.mark.parametrize("cut,lag", [("15:55", 0), ("15:54", 1)])
def test_b2_no_lookahead(bars, sigs, cut, lag):
    base = sigs(b2, **B2_BASE)
    day = base["date"].iloc[len(base) // 2]
    cutoff = local_times([day], cut, NY)[0]
    bad_sigs = b2.signals(corrupt(bars, cutoff), symbol="US100", **B2_BASE)
    a = base[base["time"] < cutoff].reset_index(drop=True)
    b = bad_sigs[bad_sigs["time"] < cutoff].reset_index(drop=True)
    assert len(a) > 60
    assert (a["date"].iloc[-1] == day) == (lag == 0)  # lag 0: the cutoff day's own decision is compared
    pd.testing.assert_frame_equal(a, b)
    if lag:  # corrupting the decision bar itself changes that day's stop
        sa = base[base["date"] == day].iloc[0]["stop_dist"]
        sb = bad_sigs[bad_sigs["date"] == day].iloc[0]["stop_dist"]
        assert sa != sb


def test_b2_skips_missing_bars(bars, sigs):
    base = sigs(b2, **B2_BASE)
    day = base["date"].iloc[40]
    t = local_times([day], "15:55", NY)[0]
    hole = bars[~((bars.index >= t - pd.Timedelta(minutes=10)) & (bars.index < t + pd.Timedelta(minutes=10)))]
    s = b2.signals(hole, symbol="US100", **B2_BASE)
    assert day not in set(s["date"]) and len(s) == len(base) - 1
    # no bar within 5 minutes of the exit instant (09:31 .. 09:41 missing; the 09:30 bar keeps the
    # session date in the calendar) skips that entry
    t1 = local_times([base["exit_date"].iloc[41]], "09:31", NY)[0]
    hole2 = bars[~((bars.index >= t1) & (bars.index < t1 + pd.Timedelta(minutes=10)))]
    s2 = b2.signals(hole2, symbol="US100", **B2_BASE)
    assert base["date"].iloc[41] not in set(s2["date"])


# ---------------------------------------------------------------------------------------------
# B3
# ---------------------------------------------------------------------------------------------
@pytest.mark.parametrize("L", [20, 60, 120])
def test_b3_calendar_and_momentum(bars, sigs, L):
    s = sigs(b3, L=L, k=2, long_only=False)
    assert len(s) > 15
    d = pd.DatetimeIndex(s["date"])
    assert (d.dayofweek == 4).all()  # synthetic data has no holidays: last trading day = Friday
    assert (pd.DatetimeIndex(s["exit_date"]) == d + pd.Timedelta(days=7)).all()
    ent, ex = ny(s["time"]), ny(s["exit_time"])
    assert (ent.hour == 15).all() and (ent.minute == 55).all()  # signal bar = 15:55 bar, see module doc
    assert (ex.hour == 15).all() and (ex.minute == 55).all()
    assert (ex.tz_localize(None).normalize() == pd.DatetimeIndex(s["exit_date"])).all()
    # sign of the L-trading-day close-to-close log return (independent recomputation)
    dates = dc.ny_trading_dates(bars)
    pos = dates.get_indexer(d)
    p_now = price_at(bars, local_times(d, "15:55", NY))
    p_back = price_at(bars, local_times(dates[pos - L], "15:55", NY))
    mom = np.log(p_now / p_back)
    np.testing.assert_allclose(mom, s["mom"])
    assert (np.sign(mom) == s["side"]).all() and set(s["side"]) == {-1, 1}
    # every week (Friday) between the first and last signal is present: nothing is lost
    all_fri = pd.date_range(d.min(), d.max(), freq="W-FRI")
    assert set(all_fri) == set(d)


def test_b3_long_only_and_stop(bars, sigs):
    full = sigs(b3, **B3_BASE)
    lo = sigs(b3, L=20, k=2, long_only=True)
    assert 0 < len(lo) < len(full) and set(lo["side"]) == {1}
    assert set(lo["time"]) <= set(full["time"])
    assert set(full[full["side"] == 1]["time"]) == set(lo["time"])
    k3 = sigs(b3, L=20, k=3, long_only=False)
    np.testing.assert_allclose(k3["stop_dist"] / full["stop_dist"], 1.5)
    fc = dc.daily_variance_forecast(bars, pd.DatetimeIndex(full["date"]))
    px = price_at(bars, local_times(full["date"], "15:55", NY))
    np.testing.assert_allclose(full["stop_dist"], 2 * np.sqrt(5 * fc) * px)


def test_b3_dst(sigs):
    s = sigs(b3, **B3_BASE)
    ent = ny(s["time"])
    for month in (1, 7):
        sel = ent.month == month
        assert sel.sum() >= 3
        assert (ent[sel].hour == 15).all() and (ent[sel].minute == 55).all()
    assert ent[ent.month == 1][0].utcoffset() != ent[ent.month == 7][0].utcoffset()


@pytest.mark.parametrize("cut,lag", [("15:55", 0), ("15:54", 1)])
def test_b3_no_lookahead(bars, sigs, cut, lag):
    base = sigs(b3, **B3_BASE)
    day = base["date"].iloc[len(base) // 2]
    cutoff = local_times([day], cut, NY)[0]
    bad_sigs = b3.signals(corrupt(bars, cutoff), symbol="US100", **B3_BASE)
    # signal time is the 15:55 bar (one bar after the decision bar): compare strictly earlier decisions
    # plus the cutoff day's own decision, which only uses bars before 15:55
    lim = local_times([day], "15:55", NY)[0] + MIN
    a = base[base["time"] < lim].reset_index(drop=True)
    b = bad_sigs[bad_sigs["time"] < lim].reset_index(drop=True)
    assert len(a) >= 10 and a["date"].iloc[-1] == day
    if lag == 0:
        pd.testing.assert_frame_equal(a, b)
    else:  # the decision bar itself corrupted: earlier weeks unchanged, this week's stop/mom change
        pd.testing.assert_frame_equal(a.iloc[:-1], b.iloc[:-1])
        assert a.iloc[-1]["stop_dist"] != b.iloc[-1]["stop_dist"]


def test_b3_trade_count_equals_signals_and_exit_instants(bars, sigs):
    s = sigs(b3, **B3_BASE)
    t = run_backtest(bars, s, harness.cost_model("US100"), symbol="US100")
    assert len(t) == len(s) > 15  # no re-entry is dropped by the engine busy rule
    assert (t["side"] == s["side"].to_numpy()).all()
    # entries one bar after the signal bar (15:56 ET), time exits exactly at the 15:55 ET bar
    assert ((t["entry_time"] - t["signal_time"]) == MIN).all()
    time_exits = t[t["exit_reason"] == "time"]
    assert len(time_exits) > 10
    ex = ny(time_exits["exit_time"])
    assert (ex.hour == 15).all() and (ex.minute == 55).all()
    assert (time_exits["exit_time"].to_numpy() == s.loc[time_exits.index, "exit_time"].to_numpy()).all()
    # consecutive weekly trades are back to back: next entry is exit + 1 minute when the week ran to its end
    gaps = (t["entry_time"].shift(-1) - t["exit_time"]).iloc[:-1]
    full_week = (t["exit_reason"] == "time").iloc[:-1]
    assert (gaps[full_week] == MIN).all()


def test_b3_engine_busy_rule_would_drop_without_shift(bars, sigs):
    # documents why the signal is placed on the 15:55 bar: a signal on the 15:54 bar would activate on
    # the same bar the previous trade exits on, and the engine ignores it
    s = sigs(b3, **B3_BASE)
    early = s.copy()
    early["time"] = early["time"] - MIN
    t = run_backtest(bars, early, harness.cost_model("US100"), symbol="US100")
    assert len(t) < len(s)


def test_b3_half_day_exit_and_skipped_entry(bars, sigs):
    base = sigs(b3, **B3_BASE)
    i = len(base) // 2
    day = base["date"].iloc[i]  # a decision Friday; make it a half day (data stops at 13:00 ET)
    cut = local_times([day], "13:00", NY)[0]
    end = local_times([day + pd.Timedelta(days=1)], "00:00", NY)[0]
    half = bars[~((bars.index >= cut) & (bars.index < end))]
    s = b3.signals(half, symbol="US100", **B3_BASE)
    # that week has no decision price at 15:55 -> not entered (and, with L=20 = 4 weeks, it is also the
    # missing lookback close of the decision 4 weeks later); the previous week's trade exits at the
    # last bar of the half day (12:59 ET)
    assert set(base["date"]) - set(s["date"]) == {day, day + pd.Timedelta(days=28)}
    assert set(s["date"]) <= set(base["date"])
    prev = s[s["exit_date"] == day].iloc[0]
    assert prev["exit_time"] == cut - MIN
    t = run_backtest(half, s, harness.cost_model("US100"), symbol="US100")
    assert len(t) == len(s)
    held = t[t["signal_time"] == prev["time"]].iloc[0]
    assert held["exit_reason"] in ("time", "stop")
    if held["exit_reason"] == "time":
        assert held["exit_time"] == cut - MIN


# ---------------------------------------------------------------------------------------------
# engine integration (all configurations)
# ---------------------------------------------------------------------------------------------
@pytest.mark.parametrize("symbol", ["US100", "XAUUSD"])
def test_engine_integration_all_configs(bars, symbol):
    cm = harness.cost_model(symbol)
    for mod, configs in ((b1, b1.CONFIGS), (b2, b2.CONFIGS), (b3, b3.CONFIGS)):
        for cfg in configs:
            s = mod.signals(bars, symbol=symbol, **cfg)
            assert len(s) >= 1, (mod.__name__, cfg)
            t = run_backtest(bars, s, cm, symbol=symbol)
            assert len(t) > 0 and np.isfinite(t["R"]).all()
            assert (t["risk"] > 0).all()
            assert set(t["exit_reason"]) <= {"stop", "time"}
            assert len(t) == len(s), (mod.__name__, cfg)  # positions never overlap: nothing dropped
            if mod is not b3:
                assert (t["side"] == 1).all()  # B1 / B2 are long only
            # time exits happen at the intended exit instants
            te = t[t["exit_reason"] == "time"]
            exp = s.set_index("time").loc[te["signal_time"], "exit_time"]
            assert (te["exit_time"].to_numpy() == exp.to_numpy()).all()


def test_b3_trade_count_equals_signal_count_all_configs(bars):
    cm = harness.cost_model("US100")
    for cfg in b3.CONFIGS:
        s = b3.signals(bars, symbol="US100", **cfg)
        t = run_backtest(bars, s, cm, symbol="US100")
        assert len(t) == len(s), cfg
