"""Tests for the C1 intraday scan (synthetic data only)."""
import numpy as np
import pandas as pd
import pytest

from pfbot.data.histdata import SPREAD
from pfbot.data.synthetic import make_bars
from pfbot.research.harness import SLIPPAGE
from research import c1_scan as c1

NY = "America/New_York"
START, DAYS = "2023-06-01", 330  # vol model warm-up ~6 months, then ~200 usable dates
SLOT, H = 10 * 60, 60            # 10:00 ET, 60 minutes
FAR_SLOT = 14 * 60
SLOTS = (SLOT, FAR_SLOT, 12 * 60)
HS = (60, 120)


def _shift(b):
    # make_bars' daily break is 21:00-22:00 UTC; shift +2h so it sits at 18:00-19:00 ET (as in test_a1)
    b = b.copy()
    b.index = b.index + pd.Timedelta(hours=2)
    return b


def _drift(index, sigma):
    """Positive drift (0.15 per-minute sigma) in 10:00-11:00 ET, defined on the shifted clock."""
    et = (index + pd.Timedelta(hours=2)).tz_convert(NY)
    mins = et.hour * 60 + et.minute
    return np.where((mins >= 10 * 60) & (mins < 11 * 60), 0.15 * sigma, 0.0)


@pytest.fixture(scope="module")
def bars():
    return _shift(make_bars(START, DAYS, seed=3))


@pytest.fixture(scope="module")
def base(bars):
    return c1.scan_bars(bars, "US100", SLOTS, HS)


@pytest.fixture(scope="module")
def edge():
    return c1.scan_bars(_shift(make_bars(START, DAYS, seed=3, drift_fn=_drift)), "US100", SLOTS, HS)


def _corrupt_after(bars, cutoff_utc, seed=0):
    """Scale every bar starting at/after cutoff by a random factor (keeps OHLC consistent)."""
    b = bars.copy()
    rng = np.random.default_rng(seed)
    m = b.index >= cutoff_utc
    f = np.exp(rng.normal(0, 0.05, m.sum()).cumsum() * 0.1 + 0.2)
    for col in ("open", "high", "low", "close"):
        b.loc[m, col] = b.loc[m, col].to_numpy() * f
    return b


def _pick_date(sd):
    """A date in the middle of the sample with a valid trade and valid signals."""
    good = np.flatnonzero(sd.ok & np.isfinite(sd.x_day) & np.isfinite(sd.x_recent))
    assert len(good) > 20
    return int(good[len(good) // 2])


def test_grid_size():
    assert len(c1.SLOT_MINUTES) == 28
    assert len(c1.SLOT_MINUTES) * len(c1.HS) * len(c1.KINDS) * len(c1.RULES) == c1.N_CONFIGS_PER_SYMBOL == 504
    assert c1.hhmm(c1.SLOT_MINUTES[0]) == "02:00" and c1.hhmm(c1.SLOT_MINUTES[-1]) == "15:30"


# (a) no look-ahead ---------------------------------------------------------------------------
def test_no_lookahead_after_exit(bars, base):
    sd = base[(c1.hhmm(SLOT), H)]
    i = _pick_date(sd)
    d = sd.dates[i]
    t_exit = pd.Timestamp(d + pd.Timedelta(hours=SLOT // 60, minutes=SLOT % 60 + H)).tz_localize(NY).tz_convert("UTC")
    bad = c1.scan_bars(_corrupt_after(bars, t_exit), "US100", SLOTS, HS)[(c1.hhmm(SLOT), H)]
    assert bad.dates[i] == d
    for kind in c1.KINDS:
        for rule in c1.RULES:
            a, b = c1.config_values(sd, kind, rule)[i], c1.config_values(bad, kind, rule)[i]
            assert np.isfinite(a) or kind != "none"
            assert (np.isnan(a) and np.isnan(b)) or a == pytest.approx(b, rel=0, abs=1e-12)
    assert sd.entry[i] == bad.entry[i] and sd.exit[i] == bad.exit[i] and sd.sigma[i] == bad.sigma[i]
    # sanity: the corruption does change later dates, so the test is not vacuous
    assert not np.allclose(np.nan_to_num(sd.exit[i + 5:]), np.nan_to_num(bad.exit[i + 5:]))


def test_signal_ignores_prices_after_entry(bars, base):
    sd = base[(c1.hhmm(SLOT), H)]
    i = _pick_date(sd)
    d = sd.dates[i]
    t_entry = pd.Timestamp(d + pd.Timedelta(hours=SLOT // 60)).tz_localize(NY).tz_convert("UTC")
    bad = c1.scan_bars(_corrupt_after(bars, t_entry, seed=1), "US100", SLOTS, HS)[(c1.hhmm(SLOT), H)]
    assert sd.x_day[i] == bad.x_day[i] and sd.x_recent[i] == bad.x_recent[i]
    assert sd.entry[i] == bad.entry[i] and sd.sigma[i] == bad.sigma[i]  # entry price and ex-ante sigma too
    assert sd.exit[i] != bad.exit[i]  # the outcome does change


# (b) injected edge ---------------------------------------------------------------------------
def test_injected_edge_detected(edge):
    near = c1.config_values(edge[(c1.hhmm(SLOT), 60)], "none", "follow")
    near = near[~np.isnan(near)]
    far = c1.config_values(edge[(c1.hhmm(FAR_SLOT), 60)], "none", "follow")
    far = far[~np.isnan(far)]
    assert len(near) > 150 and len(far) > 150
    s_near, s_far = c1.trade_stats(near), c1.trade_stats(far)
    assert s_near["mean"] > 0.4 and s_near["t"] > 6, s_near
    assert abs(s_far["t"]) < 3 and s_far["mean"] < 0.25, s_far
    # fading the edge loses
    fade = c1.trade_stats(c1.config_values(edge[(c1.hhmm(SLOT), 60)], "none", "fade"))
    assert fade["mean"] < -0.4


def test_no_edge_without_injection(base):
    s = c1.trade_stats(c1.config_values(base[(c1.hhmm(SLOT), 60)], "none", "follow"))
    assert abs(s["t"]) < 3.5 and s["mean"] < 0.25


# (c) cost exactly once ------------------------------------------------------------------------
def test_cost_subtracted_once(base):
    sd = base[(c1.hhmm(SLOT), 120)]
    cost = SPREAD["US100"] + 2 * SLIPPAGE["US100"]
    assert sd.cost == cost
    f = c1.config_values(sd, "none", "follow")
    s = c1.config_values(sd, "none", "fade")
    ok = sd.ok
    assert ok.sum() > 150 and np.array_equal(~np.isnan(f), ok)
    expect_f = (np.log(sd.exit / sd.entry) - cost / sd.entry) / sd.sigma
    expect_s = (-np.log(sd.exit / sd.entry) - cost / sd.entry) / sd.sigma
    np.testing.assert_allclose(f[ok], expect_f[ok], rtol=1e-12)
    np.testing.assert_allclose(s[ok], expect_s[ok], rtol=1e-12)
    # long + short value sums to exactly -2 x cost in sigma units (gross return cancels)
    np.testing.assert_allclose((f + s)[ok] / 2 * sd.sigma[ok] * sd.entry[ok], -cost, rtol=1e-9)


def test_values_match_independent_oracle(bars, base):
    """Recompute entry/exit/sigma for a few dates straight from the 5-min bars and the vol series."""
    sd = base[(c1.hhmm(SLOT), 120)]
    bars5, ev = c1.prepare_bars(bars)
    for i in np.flatnonzero(sd.ok)[[5, 60, 120]]:
        d = sd.dates[i]
        t = pd.Timestamp(d + pd.Timedelta(hours=10)).tz_localize(NY).tz_convert("UTC")
        te = t + pd.Timedelta(minutes=120)
        before = bars5[bars5.index < t]
        assert sd.entry[i] == before["close"].iloc[-1]
        assert sd.exit[i] == bars5[bars5.index < te]["close"].iloc[-1]
        w = ev[(ev.index >= t) & (ev.index < te)]
        assert len(w) == 24
        assert sd.sigma[i] == pytest.approx(np.sqrt((w ** 2).sum()), rel=1e-12)
        # day signal: previous weekday 16:00 close over summed variance of the bins in between
        prev = bars5[bars5.index < pd.Timestamp(d - pd.tseries.offsets.BDay(1) + pd.Timedelta(hours=16))
                     .tz_localize(NY).tz_convert("UTC")]["close"].iloc[-1]
        t_prev = pd.Timestamp(d - pd.tseries.offsets.BDay(1) + pd.Timedelta(hours=16)).tz_localize(NY).tz_convert("UTC")
        v = ev[(ev.index >= t_prev) & (ev.index < t)].dropna()
        assert sd.x_day[i] == pytest.approx(np.log(sd.entry[i] / prev) / np.sqrt((v ** 2).sum()), rel=1e-9)


def test_skips_exit_after_close(bars):
    late = c1.scan_bars(bars, "US100", (15 * 60, 15 * 60 + 30), (60, 120))
    assert late[("15:00", 60)].ok.sum() > 150      # exits exactly at 16:00: allowed
    assert late[("15:00", 120)].ok.sum() == 0      # exit 17:00: skipped
    assert late[("15:30", 60)].ok.sum() == 0
    assert late[("15:30", 120)].ok.sum() == 0


def test_threshold_and_sides(base):
    sd = base[(c1.hhmm(SLOT), 60)]
    f = c1.config_values(sd, "day", "follow")
    s = c1.config_values(sd, "day", "fade")
    trade = ~np.isnan(f)
    assert np.array_equal(trade, ~np.isnan(s))
    assert np.all(np.abs(sd.x_day[trade]) >= 0.5)
    assert trade.sum() < sd.ok.sum()  # the threshold filters something
    side = np.sign(sd.x_day[trade])
    np.testing.assert_allclose(f[trade], (side * sd.logret[trade] - sd.cost_log[trade]) / sd.sigma[trade], rtol=1e-12)


def test_selection_rule():
    base_row = dict(slot="10:00", H=60, x="none", rule="follow", d_n=400, d_mean=0.1, d_t=3.5, c_n=200, c_mean=0.1, c_t=2.5)
    rows = [
        dict(symbol="US100", **base_row),
        dict(symbol="US500", **{**base_row, "d_mean": 0.05, "d_t": 1.0}),            # sister positive -> US100 passes; US500 fails t
        dict(symbol="XAUUSD", **{**base_row, "d_t": 3.2}),                              # XAU needs 3.4
        dict(symbol="XAUUSD", **{**base_row, "slot": "11:00", "d_t": 3.5}),            # passes
        dict(symbol="US100", **{**base_row, "slot": "12:00", "d_n": 250}),             # too few trades
        dict(symbol="US100", **{**base_row, "slot": "13:00", "c_t": 1.5}),             # confirmation fails
        dict(symbol="US100", **{**base_row, "slot": "14:00"}),
        dict(symbol="US500", **{**base_row, "slot": "14:00", "d_mean": -0.01}),        # sister negative -> fails
    ]
    t = c1.select_candidates(pd.DataFrame(rows))
    assert list(t["candidate"]) == [True, False, False, True, False, False, False, False]
