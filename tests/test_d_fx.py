"""Tests for the D1 (FX time of day) and D2 (month-end 4pm fix) signal generators (synthetic data only)."""
import numpy as np
import pandas as pd
import pytest

from pfbot.backtest.engine import run_backtest
from pfbot.data.synthetic import make_bars
from pfbot.research.harness import cost_model, local_times, price_at
from pfbot.strategies import d1_fx_time_of_day as d1
from pfbot.strategies import d2_fx_month_end_fix as d2

START, DAYS = "2023-06-01", 330  # HAR warm-up ends ~Oct 2023; covers Jan and Jul 2024
NY, LON = "America/New_York", "Europe/London"
SCALE = {"EURUSD": 1.0, "GBPUSD": 1.2, "AUDUSD": 0.7, "USDJPY": 110.0, "USDCAD": 1.3, "USDCHF": 0.95}
ALL_CONFIGS = [(s, c) for s, cs in d1.CONFIGS_BY_SYMBOL.items() for c in cs]


def _scaled(base: pd.DataFrame, k: float) -> pd.DataFrame:
    b = base.copy()
    b[["open", "high", "low", "close", "spread"]] *= k
    return b


def _shifted(b: pd.DataFrame) -> pd.DataFrame:
    """make_bars has its daily break at 21:00-22:00 UTC, which would sit on the Sydney window start. Move it
    to 18:00-19:00 UTC, where no tested window or decision bar lives (real FX has no such daily break)."""
    b = b.copy()
    b.index = b.index - pd.Timedelta(hours=3)
    return b


@pytest.fixture(scope="module")
def base():
    return _shifted(make_bars(START, DAYS, seed=3, price0=1.1, daily_vol=0.006, spread=0.00006))


@pytest.fixture(scope="module")
def us500():
    return _shifted(make_bars(START, DAYS, seed=11, price0=3000.0, daily_vol=0.01, spread=0.3))


@pytest.fixture(scope="module")
def fx(base):
    return {s: _scaled(base, k) for s, k in SCALE.items()}


@pytest.fixture(scope="module")
def sig1(fx):
    cache = {}

    def get(symbol, window, H):
        key = (symbol, window, H)
        if key not in cache:
            cache[key] = d1.signals(fx[symbol], symbol=symbol, window=window, H=H)
        return cache[key]

    return get


@pytest.fixture(scope="module")
def sig2(fx, us500):
    cache = {}

    def get(symbol, t_in):
        key = (symbol, t_in)
        if key not in cache:
            cache[key] = d2.signals(fx[symbol], symbol, t_in, us500)
        return cache[key]

    return get


# ------------------------------------------------------------------------------------------ grid
def test_d1_grid():
    assert sum(len(v) for v in d1.CONFIGS_BY_SYMBOL.values()) == 22
    assert set(d1.CONFIGS_BY_SYMBOL) == set(SCALE)
    for s, cs in d1.CONFIGS_BY_SYMBOL.items():
        windows = {c["window"] for c in cs}
        assert windows == ({"US"} if s == "USDCAD" else {"US", "home"})
        assert {c["H"] for c in cs} == {2, 4}
        assert len(cs) == (2 if s == "USDCAD" else 4)
    with pytest.raises(ValueError):
        d1.window_spec("USDCAD", "home")


def test_d2_grid():
    assert [c["t_in"] for c in d2.CONFIGS] == ["10:00", "12:00", "14:00"]
    assert len(d2.CONFIGS) * 6 == 18


# ------------------------------------------------------------------------------------------ D1 timing / DST
EXPECTED_WINDOW = {  # (symbol, window) -> (tz, local start)
    ("EURUSD", "US"): (NY, "08:00"), ("USDJPY", "US"): (NY, "08:00"),
    ("EURUSD", "home"): ("Europe/Berlin", "08:00"), ("USDCHF", "home"): ("Europe/Berlin", "08:00"),
    ("GBPUSD", "home"): ("Europe/London", "08:00"), ("USDJPY", "home"): ("Asia/Tokyo", "09:00"),
    ("AUDUSD", "home"): ("Australia/Sydney", "09:00"),
}


@pytest.mark.parametrize("key", list(EXPECTED_WINDOW))
@pytest.mark.parametrize("H", [2, 4])
def test_d1_window_instants_are_local_wall_clock(sig1, key, H):
    symbol, window = key
    tz, start = EXPECTED_WINDOW[key]
    s = sig1(symbol, window, H)
    assert len(s) > 150
    entry = s["time"] + pd.Timedelta(minutes=1)  # decision bar closes at the entry instant
    loc_in, loc_out = entry.dt.tz_convert(tz), s["exit_time"].dt.tz_convert(tz)
    h0, m0 = int(start[:2]), int(start[3:])
    assert ((loc_in.dt.hour == h0) & (loc_in.dt.minute == m0)).all()
    assert ((loc_out.dt.hour == h0 + H) & (loc_out.dt.minute == m0)).all()
    assert (loc_in.dt.dayofweek < 5).all()  # weekdays only (local date)
    assert (loc_in.dt.normalize() == loc_out.dt.normalize()).all()
    # DST: the UTC hour of the entry moves between January and July by the zone's shift
    jan = entry[(entry.dt.year == 2024) & (entry.dt.month == 1)]
    jul = entry[(entry.dt.year == 2024) & (entry.dt.month == 7)]
    assert len(jan) > 10 and len(jul) > 10
    uh = lambda x: set(x.dt.hour)
    assert len(uh(jan)) == 1 and len(uh(jul)) == 1
    shift = {NY: -1, "Europe/Berlin": -1, "Europe/London": -1, "Asia/Tokyo": 0, "Australia/Sydney": 1}[tz]
    assert (uh(jul).pop() - uh(jan).pop()) % 24 == shift % 24


def test_d1_dst_utc_values(sig1):
    """Explicit UTC instants: NY 08:00 is 13:00 UTC in January (EST) and 12:00 UTC in July (EDT);
    Sydney 09:00 is 22:00 UTC the evening before in January (AEDT) and 23:00 UTC in July (AEST)."""
    s = sig1("EURUSD", "US", 2)
    e = s["time"] + pd.Timedelta(minutes=1)
    assert set(e[(e.dt.month == 1) & (e.dt.year == 2024)].dt.hour) == {13}
    assert set(e[(e.dt.month == 7) & (e.dt.year == 2024)].dt.hour) == {12}
    s = sig1("AUDUSD", "home", 2)
    e = s["time"] + pd.Timedelta(minutes=1)
    assert set(e[(e.dt.month == 1) & (e.dt.year == 2024)].dt.hour) == {22}
    assert set(e[(e.dt.month == 7) & (e.dt.year == 2024)].dt.hour) == {23}
    # the helper agrees with a hand-computed instant: Sydney Tuesday 2024-01-16 09:00 AEDT = Mon 22:00 UTC
    assert local_times(["2024-01-16"], "09:00", "Australia/Sydney")[0] == pd.Timestamp("2024-01-15 22:00", tz="UTC")


def test_d1_window_between_dst_switches():
    """US and EU DST switch on different dates: on 2024-03-20 NY is EDT, Berlin still CET."""
    ny = local_times(["2024-03-20"], "08:00", NY)[0]
    be = local_times(["2024-03-20"], "08:00", "Europe/Berlin")[0]
    assert (ny.hour, be.hour) == (12, 7)


# ------------------------------------------------------------------------------------------ D1 sides
SIDES = {  # (symbol, window) -> side; +1 long
    ("EURUSD", "US"): 1, ("GBPUSD", "US"): 1, ("AUDUSD", "US"): 1,
    ("USDJPY", "US"): -1, ("USDCAD", "US"): -1, ("USDCHF", "US"): -1,
    ("EURUSD", "home"): -1, ("GBPUSD", "home"): -1, ("AUDUSD", "home"): -1,
    ("USDJPY", "home"): 1, ("USDCHF", "home"): 1,
}


@pytest.mark.parametrize("key", list(SIDES))
def test_d1_side_mapping(sig1, key):
    symbol, window = key
    s = sig1(symbol, window, 2)
    assert len(s) > 150
    assert set(s["side"]) == {SIDES[key]}
    assert d1.side_for(symbol, window) == SIDES[key]
    assert (s["order"] == "market").all() and (s["stop_dist"] > 0).all()


def test_d1_signal_table_and_stop(fx, sig1):
    s = sig1("EURUSD", "US", 4)
    assert s["time"].is_monotonic_increasing and s["time"].is_unique
    p = price_at(fx["EURUSD"], s["time"] + pd.Timedelta(minutes=1))
    # stop = 3 x std of the window in log units x price: a 4h window of 5-min vol of ~0.6% daily vol => a few tenths of %
    rel = s["stop_dist"].to_numpy() / p
    assert 0.0005 < np.median(rel) < 0.02
    s2 = sig1("EURUSD", "US", 2)
    j = s.merge(s2, on="time", suffixes=("4", "2"))
    assert (j["stop_dist4"] > j["stop_dist2"]).all()  # longer window, wider stop
    np.testing.assert_allclose((j["stop_dist4"] / j["stop_dist2"]).median(), np.sqrt(2), rtol=0.3)


def test_d1_skips_days_without_bars(fx):
    b = fx["EURUSD"]
    full = d1.signals(b, symbol="EURUSD", window="US", H=2)
    day = full["time"].iloc[len(full) // 2]
    t0 = local_times([day.tz_convert(NY).tz_localize(None).normalize()], "07:50", NY)[0]
    t1 = local_times([day.tz_convert(NY).tz_localize(None).normalize()], "08:20", NY)[0]
    holed = b[(b.index < t0) | (b.index >= t1)]  # no bars within 5 min of the entry
    s = d1.signals(holed, symbol="EURUSD", window="US", H=2)
    assert day not in set(s["time"])
    assert len(s) == len(full) - 1


# ------------------------------------------------------------------------------------------ D1 no look-ahead
@pytest.mark.parametrize("symbol,window", [("EURUSD", "US"), ("USDJPY", "home"), ("AUDUSD", "home")])
def test_d1_no_lookahead(fx, sig1, symbol, window):
    base_sig = sig1(symbol, window, 4)
    tz, start = EXPECTED_WINDOW[(symbol, window)]
    day = base_sig["time"].iloc[len(base_sig) // 2]
    cutoff = day + pd.Timedelta(minutes=1)  # the entry instant of that day
    bad = fx[symbol].copy()
    m = bad.index >= cutoff
    bad.loc[m, ["open", "high", "low", "close"]] *= 1.5
    sig = d1.signals(bad, symbol=symbol, window=window, H=4)
    a = base_sig[base_sig["time"] < cutoff].reset_index(drop=True)
    b = sig[sig["time"] < cutoff].reset_index(drop=True)
    assert len(a) > 100
    pd.testing.assert_frame_equal(a, b)
    # the corrupted day's own decision is unaffected as well (decision bar closed at the cutoff)
    own = sig[sig["time"] == day]
    pd.testing.assert_frame_equal(own.reset_index(drop=True), base_sig[base_sig["time"] == day].reset_index(drop=True))


# ------------------------------------------------------------------------------------------ D2
@pytest.mark.parametrize("t_in", ["10:00", "12:00", "14:00"])
def test_d2_timing_and_last_day(sig2, t_in):
    s = sig2("EURUSD", t_in)
    assert len(s) >= 8
    entry = s["time"] + pd.Timedelta(minutes=1)
    loc = entry.dt.tz_convert(LON)
    h0 = int(t_in[:2])
    assert ((loc.dt.hour == h0) & (loc.dt.minute == 0)).all()
    ex = s["exit_time"].dt.tz_convert(LON)
    assert ((ex.dt.hour == 16) & (ex.dt.minute == 1)).all()
    # last weekday of its month (synthetic data has every weekday)
    d = loc.dt.tz_localize(None).dt.normalize()
    eom = d.dt.to_period("M").dt.to_timestamp(how="end").dt.normalize()
    last_wd = eom - pd.to_timedelta(np.maximum(eom.dt.dayofweek - 4, 0), unit="D")
    assert (d == last_wd).all()
    assert s["time"].is_monotonic_increasing and s["time"].is_unique
    # DST: London-time entry in January is the same UTC hour, in July one hour earlier in UTC
    jan, jul = s[loc.dt.month == 1], s[loc.dt.month == 7]
    assert len(jan) and len(jul)
    assert set((jan["time"] + pd.Timedelta(minutes=1)).dt.hour) == {h0}
    assert set((jul["time"] + pd.Timedelta(minutes=1)).dt.hour) == {h0 - 1}
    assert set(jan["exit_time"].dt.hour) == {16} and set(jul["exit_time"].dt.hour) == {15}


def test_d2_side_and_return(fx, us500, sig2):
    for symbol in SCALE:
        s = sig2(symbol, "12:00")
        assert len(s) >= 8
        usd_sell = 1 if symbol in ("EURUSD", "GBPUSD", "AUDUSD") else -1
        assert (s["side"].to_numpy() == usd_sell * np.sign(s["us500_ret"].to_numpy())).all()
        assert d2.USD_SELL_SIDE[symbol] == usd_sell
    s = sig2("EURUSD", "12:00")
    assert set(s["side"]) == {-1, 1}  # both directions occur
    # independent recomputation of the month-to-date return
    entry = s["time"] + pd.Timedelta(minutes=1)
    d = entry.dt.tz_convert(LON).dt.tz_localize(None).dt.normalize()
    prev_eom = d.dt.to_period("M").dt.to_timestamp() - pd.Timedelta(days=1)
    prev_wd = prev_eom - pd.to_timedelta(np.maximum(prev_eom.dt.dayofweek - 4, 0), unit="D")
    base_px = price_at(us500, local_times(prev_wd, "16:00", NY))
    now_px = price_at(us500, pd.DatetimeIndex(entry))
    np.testing.assert_allclose(np.log(now_px / base_px), s["us500_ret"].to_numpy(), rtol=1e-12)
    # a signal never uses a US500 return of exactly zero
    assert (s["us500_ret"] != 0).all()


def test_d2_stop_scales_with_entry(sig2):
    # earlier entry -> longer holding window -> wider stop (same month-end days, same price level)
    m = sig2("EURUSD", "10:00").merge(sig2("EURUSD", "14:00"), on="exit_time", suffixes=("10", "14"))
    assert len(m) > 8
    assert (m["stop_dist10"] > m["stop_dist14"]).all()


def test_d2_holiday_fallbacks(fx, us500, sig2):
    s = sig2("EURUSD", "12:00")
    i = len(s) // 2
    entry = s["time"].iloc[i] + pd.Timedelta(minutes=1)
    day = entry.tz_convert(LON).tz_localize(None).normalize()
    # (a) FX holiday on the last day: the trade moves to the previous weekday
    lo = local_times([day], "00:00", LON)[0]
    holed = fx["EURUSD"][(fx["EURUSD"].index < lo) | (fx["EURUSD"].index >= lo + pd.Timedelta(days=1))]
    s2 = d2.signals(holed, "EURUSD", "12:00", us500)
    prev_entry = local_times([day - pd.offsets.BDay(1)], "12:00", LON)[0]
    assert (s2["time"] + pd.Timedelta(minutes=1) == prev_entry).any()
    assert not (s2["time"] + pd.Timedelta(minutes=1) == entry).any()
    # (b) US500 closed at the base instant of the previous month-end: base falls back one weekday
    prev_eom = day.to_period("M").to_timestamp() - pd.Timedelta(days=1)
    prev_wd = prev_eom - pd.Timedelta(days=max(prev_eom.dayofweek - 4, 0))
    tb = local_times([prev_wd], "16:00", NY)[0]
    cut = us500[(us500.index < tb - pd.Timedelta(minutes=30)) | (us500.index >= tb + pd.Timedelta(hours=6))]
    s3 = d2.signals(fx["EURUSD"], "EURUSD", "12:00", cut)
    row = s3[s3["time"] == s["time"].iloc[i]]
    assert len(row) == 1
    prev_wd2 = prev_wd - pd.offsets.BDay(1)
    exp = np.log(price_at(us500, pd.DatetimeIndex([entry]))[0] / price_at(us500, local_times([prev_wd2], "16:00", NY))[0])
    assert row["us500_ret"].iloc[0] == pytest.approx(exp)


def test_d2_skip_without_us500_price(fx, us500, sig2):
    s = sig2("GBPUSD", "12:00")
    i = len(s) // 2
    entry = s["time"].iloc[i] + pd.Timedelta(minutes=1)
    holed = us500[(us500.index < entry - pd.Timedelta(hours=2)) | (us500.index >= entry)]  # stale by > 30 min
    s2 = d2.signals(fx["GBPUSD"], "GBPUSD", "12:00", holed)
    assert s["time"].iloc[i] not in set(s2["time"])
    assert len(s2) == len(s) - 1


def test_d2_no_lookahead_us500(fx, us500, sig2):
    s = sig2("EURUSD", "12:00")
    i = len(s) // 2
    cutoff = s["time"].iloc[i] + pd.Timedelta(minutes=1)  # the entry instant
    bad = us500.copy()
    bad.loc[bad.index >= cutoff, ["open", "high", "low", "close"]] *= 1.5
    s2 = d2.signals(fx["EURUSD"], "EURUSD", "12:00", bad)
    a, b = s[s["time"] <= s["time"].iloc[i]], s2[s2["time"] <= s["time"].iloc[i]]
    assert len(a) == i + 1
    pd.testing.assert_frame_equal(a.reset_index(drop=True), b.reset_index(drop=True))
    # non-vacuous: corrupting the bar that closes at the instant does change the signal's return
    bad = us500.copy()
    k = bad.index < cutoff
    bad.loc[bad.index == bad.index[k][-1], ["open", "high", "low", "close"]] *= 1.01
    s3 = d2.signals(fx["EURUSD"], "EURUSD", "12:00", bad)
    assert s3["us500_ret"].iloc[i] != s["us500_ret"].iloc[i]


def test_d2_no_lookahead_fx(fx, us500, sig2):
    s = sig2("USDJPY", "10:00")
    i = len(s) // 2
    cutoff = s["time"].iloc[i] + pd.Timedelta(minutes=1)
    bad = fx["USDJPY"].copy()
    bad.loc[bad.index >= cutoff, ["open", "high", "low", "close"]] *= 1.5
    s2 = d2.signals(bad, "USDJPY", "10:00", us500)
    a, b = s[s["time"] <= s["time"].iloc[i]], s2[s2["time"] <= s["time"].iloc[i]]
    pd.testing.assert_frame_equal(a.reset_index(drop=True), b.reset_index(drop=True))


# ------------------------------------------------------------------------------------------ engine integration
@pytest.mark.parametrize("symbol,cfg", ALL_CONFIGS, ids=[f"{s}-{c['window']}-{c['H']}h" for s, c in ALL_CONFIGS])
def test_d1_engine_integration(fx, sig1, symbol, cfg):
    s = sig1(symbol, cfg["window"], cfg["H"])
    t = run_backtest(fx[symbol], s, cost_model(symbol), symbol=symbol)
    assert len(t) > 0.9 * len(s)
    assert np.isfinite(t["R"]).all() and (t["risk"] > 0).all()
    assert (t["side"] == s["side"].iloc[0]).all()
    entry = pd.DatetimeIndex(t["signal_time"]) + pd.Timedelta(minutes=1)
    assert ((t["entry_time"] - entry) < pd.Timedelta(minutes=5)).all() and (t["entry_time"] >= entry).all()
    assert (t["exit_reason"].isin(["time", "stop"])).all()
    assert (t["exit_reason"] == "time").mean() > 0.7
    timed = t[t["exit_reason"] == "time"]
    ex = s.set_index("time").loc[timed["signal_time"], "exit_time"].to_numpy()
    assert ((timed["exit_time"].to_numpy() - ex) < np.timedelta64(5, "m")).all()
    assert (timed["exit_time"].to_numpy() >= ex).all()


@pytest.mark.parametrize("symbol", list(SCALE))
@pytest.mark.parametrize("t_in", ["10:00", "12:00", "14:00"])
def test_d2_engine_integration(fx, sig2, symbol, t_in):
    s = sig2(symbol, t_in)
    t = run_backtest(fx[symbol], s, cost_model(symbol), symbol=symbol)
    assert len(t) >= len(s) - 1 and len(t) >= 8
    assert np.isfinite(t["R"]).all() and (t["risk"] > 0).all()
    assert (t["side"].to_numpy() == s["side"].to_numpy()[: len(t)]).all() or len(t) < len(s)
    assert (t["exit_reason"].isin(["time", "stop"])).all()
    timed = t[t["exit_reason"] == "time"]
    assert len(timed) > 0
    loc = timed["exit_time"].dt.tz_convert(LON)
    assert ((loc.dt.hour == 16) & (loc.dt.minute == 1)).all()


def test_engine_has_no_free_lunch(fx, sig1):
    """Random-walk data: the mean R of an unconditional fixed-direction window trade is ~0 minus costs."""
    t = run_backtest(fx["EURUSD"], sig1("EURUSD", "US", 4), cost_model("EURUSD"), symbol="EURUSD")
    assert abs(t["R"].mean()) < 4 * t["R"].std() / np.sqrt(len(t))
