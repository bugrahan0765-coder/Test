import numpy as np
import pandas as pd
import pytest

from pfbot.backtest.engine import CostModel, run_backtest, summarize
from pfbot.data.synthetic import make_bars


def bars_from(rows, spread=0.0):
    """rows: list of (open, high, low, close) on consecutive minutes."""
    idx = pd.date_range("2024-01-02 14:00", periods=len(rows), freq="1min", tz="UTC", name="time")
    df = pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=idx)
    df["spread"] = spread
    return df


def sig(bars, i, **kw):
    return pd.DataFrame([dict(time=bars.index[i], **kw)])


FLAT = (100, 100.5, 99.5, 100)


def test_market_long_hits_target():
    b = bars_from([FLAT, FLAT, (100, 101, 99.8, 100.9), (101, 103, 100.5, 102)])
    t = run_backtest(b, sig(b, 0, side=1, stop_dist=1.0, target_dist=2.0))
    assert len(t) == 1
    r = t.iloc[0]
    assert r.entry_time == b.index[1] and r.entry_price == 100
    assert r.exit_reason == "target" and r.exit_price == 102
    assert r.R == pytest.approx(2.0)


def test_stop_wins_when_both_touched_in_one_bar():
    b = bars_from([FLAT, FLAT, (100, 103, 98, 100)])
    t = run_backtest(b, sig(b, 0, side=1, stop_dist=1.0, target_dist=2.0))
    assert t.iloc[0].exit_reason == "stop" and t.iloc[0].R == pytest.approx(-1.0)


def test_gap_through_stop_loses_more_than_1R():
    b = bars_from([FLAT, FLAT, (97, 97.5, 96, 97)])
    t = run_backtest(b, sig(b, 0, side=1, stop_dist=1.0))
    assert t.iloc[0].exit_price == 97 and t.iloc[0].R == pytest.approx(-3.0)
    assert t.iloc[0].mae_R == pytest.approx(-3.0)


def test_short_and_spread_costs():
    b = bars_from([FLAT, FLAT, FLAT, FLAT], spread=0.2)
    t = run_backtest(b, sig(b, 0, side=-1, stop_dist=2.0, exit_time=b.index[3]))
    r = t.iloc[0]
    # sell at bid 99.9, buy back at ask 100.1 -> lose the full spread
    assert r.exit_reason == "time" and r.pnl == pytest.approx(-0.2)
    assert r.R == pytest.approx(-0.2 / 2.0)  # risk is the 2.0 stop distance from intended entry


def test_stop_entry_triggers_and_entry_bar_checks_stop_only():
    b = bars_from([FLAT, (100.7, 101.2, 100.6, 101), (101, 101.5, 100.6, 101.4)])
    t = run_backtest(b, sig(b, 0, side=1, order="stop", price=101.0, stop_price=100.5, target_price=101.1))
    r = t.iloc[0]
    assert r.entry_time == b.index[1] and r.entry_price == 101.0
    # target 101.1 was touched on the entry bar but is ignored there; filled on the next bar
    assert r.exit_time == b.index[2] and r.exit_reason == "target"


def test_limit_requires_trade_through_and_expiry_cancels():
    b = bars_from([FLAT, (100, 100.5, 99.0, 99.5), FLAT, (100, 100.5, 98.5, 99)])
    # low touches 99.0 exactly -> no fill (strict); expires before bar 3
    t = run_backtest(b, sig(b, 0, side=1, order="limit", price=99.0, stop_dist=1.0, expiry=b.index[3]))
    assert len(t) == 0
    t = run_backtest(b, sig(b, 0, side=1, order="limit", price=99.0, stop_dist=1.0))
    assert t.iloc[0].entry_time == b.index[3] and t.iloc[0].entry_price == 99.0


def test_signals_ignored_while_in_position():
    b = bars_from([FLAT] * 6)
    s = pd.DataFrame(dict(time=b.index[[0, 1, 4]], side=1, stop_dist=5.0, exit_time=b.index[3]))
    s.loc[2, "exit_time"] = pd.NaT
    t = run_backtest(b, s)
    assert list(t.signal_time) == [b.index[0], b.index[4]]
    assert t.iloc[1].exit_reason == "end_of_data"


def test_wrong_side_stop_rejected():
    b = bars_from([FLAT, FLAT])
    with pytest.raises(ValueError):
        run_backtest(b, sig(b, 0, side=1, stop_price=101.0))


def _random_signals(bars, n, seed, hold=60):
    rng = np.random.default_rng(seed)
    pick = np.sort(rng.choice(len(bars) - hold - 1, n, replace=False))
    return pd.DataFrame(dict(
        time=bars.index[pick],
        side=rng.choice([-1, 1], n),
        stop_dist=bars["close"].to_numpy()[pick] * 0.003,
        target_dist=bars["close"].to_numpy()[pick] * 0.003,
        exit_time=bars.index[pick + hold],
    ))


def test_random_entries_have_no_edge_without_costs():
    bars = make_bars(days=120, spread=0.0, seed=1)
    t = run_backtest(bars, _random_signals(bars, 3000, seed=2))
    s = summarize(t)
    assert s["n"] > 1000
    assert abs(s["t_stat"]) < 3.0


def test_random_entries_lose_the_spread():
    bars = make_bars(days=120, spread=2.0, seed=1)
    t = run_backtest(bars, _random_signals(bars, 3000, seed=2))
    assert summarize(t)["t_stat"] < -3.0


def test_injected_edge_is_recovered():
    # Positive drift every day 14:00-16:00 UTC; a long held through that window must profit.
    def drift(index, sigma):
        h = index.hour
        return np.where((h >= 14) & (h < 16), 0.25 * sigma, 0.0)

    bars = make_bars(days=200, spread=0.5, seed=3, drift_fn=drift)
    days = bars.index.normalize().unique()
    s = pd.DataFrame(dict(
        time=days + pd.Timedelta("13:59:00"),
        side=1,
        stop_dist=bars["close"].iloc[0] * 0.02,
        exit_time=days + pd.Timedelta("16:00:00"),
    ))
    st = summarize(run_backtest(bars, s, CostModel()))
    assert st["n"] == 200 and st["t_stat"] > 3.0


def test_financing_charged_per_night():
    idx = pd.DatetimeIndex(["2024-01-05 20:00", "2024-01-05 20:01", "2024-01-08 15:00", "2024-01-08 15:01"],
                           tz="UTC", name="time")  # Friday 15:00 ET -> Monday 10:00 ET: 3 nights
    b = pd.DataFrame({"open": 100.0, "high": 100.5, "low": 99.5, "close": 100.0}, index=idx)
    s = pd.DataFrame([dict(time=idx[0], side=1, stop_dist=5.0, exit_time=idx[2])])
    t = run_backtest(b, s, CostModel(financing_annual=0.036))
    assert t.iloc[0].pnl == pytest.approx(-100 * 0.036 / 360 * 3)
