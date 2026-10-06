import numpy as np
import pandas as pd
import pytest

from pfbot.propsim.rules import FTMO_PHASE1, PhaseRules, RiskPolicy
from pfbot.propsim.sim import build_day_book, monte_carlo, run_phase

DAYS = pd.bdate_range("2024-01-01", periods=300)
NO_THROTTLE = RiskPolicy(risk_per_trade=0.01, daily_soft_stop=1.0, dd_reduce_at=1.0, dd_halt_at=1.0)


def trades(spec):
    """spec: list of (day_i, entry 'HH:MM', exit 'HH:MM', R, mae_R); times are Prague local."""
    rows = []
    for d, a, b, r, m in spec:
        day = DAYS[d]
        rows.append(dict(
            entry_time=pd.Timestamp(f"{day.date()} {a}", tz="Europe/Prague").tz_convert("UTC"),
            exit_time=pd.Timestamp(f"{day.date()} {b}", tz="Europe/Prague").tz_convert("UTC"),
            R=r, mae_R=m,
        ))
    return pd.DataFrame(rows)


def run(spec, policy=NO_THROTTLE, rules=FTMO_PHASE1):
    book = build_day_book(trades(spec), DAYS)
    return run_phase(book, np.arange(len(DAYS)), rules, policy)


def test_steady_winner_passes_after_ten_days():
    r = run([(d, "15:00", "16:00", 1.0, -0.2) for d in range(30)])
    assert r["status"] == "pass" and r["days"] == 10 and r["balance"] == pytest.approx(1.10)


def test_min_trading_days_enforced():
    two_days = run([(0, "15:00", "16:00", 11.0, 0.0), (5, "15:00", "16:00", 0.1, 0.0)])
    assert two_days["status"] == "timeout" and two_days["balance"] > 1.10
    four_days = run([(0, "15:00", "16:00", 11.0, 0.0)] + [(d, "15:00", "16:00", 0.1, 0.0) for d in (3, 5, 9)])
    assert four_days["status"] == "pass" and four_days["days"] == 10 and four_days["trading_days"] == 4


def test_floating_loss_breaches_daily_limit_even_if_trade_recovers():
    r = run([(0, "15:00", "16:00", 1.0, -5.5)])
    assert r["status"] == "fail_daily"


def test_overlapping_trades_count_together():
    overlap = [(0, "15:00", "17:00", -1.0, -3.0), (0, "16:00", "18:00", -1.0, -3.0)]
    sequential = [(0, "15:00", "16:00", -1.0, -1.0), (0, "16:30", "18:00", -1.0, -1.0)]
    assert run(overlap)["status"] == "fail_daily"
    assert run(sequential)["status"] != "fail_daily"


def test_total_loss_limit():
    r = run([(d, "15:00", "16:00", -1.0, -1.0) for d in range(20)])
    assert r["status"] == "fail_total" and r["days"] == 10


def test_soft_stop_skips_trades_after_daily_loss():
    pol = RiskPolicy(risk_per_trade=0.01, daily_soft_stop=0.02, dd_reduce_at=1.0, dd_halt_at=1.0)
    spec = [(0, f"{h}:00", f"{h}:30", -1.0, -1.0) for h in range(10, 16)]
    r = run(spec, policy=pol, rules=PhaseRules("t", 0.10, max_days=5))
    assert r["balance"] == pytest.approx(0.98)


def test_monte_carlo_edge_beats_coin_flip():
    rng = np.random.default_rng(0)
    n = len(DAYS)
    coin = trades([(d, "15:00", "16:00", r, min(r, 0)) for d, r in enumerate(rng.choice([-1.0, 1.0], n))])
    edge = trades([(d, "15:00", "16:00", r, min(r, 0)) for d, r in enumerate(rng.choice([-1.0, 1.5], n, p=[0.55, 0.45]))])
    pol = RiskPolicy(risk_per_trade=0.01)
    mc_coin = monte_carlo(build_day_book(coin, DAYS), pol, n_paths=800, seed=1)
    mc_edge = monte_carlo(build_day_book(edge, DAYS), pol, n_paths=800, seed=1)
    assert mc_edge["p_funded"] > mc_coin["p_funded"] + 0.1
    assert mc_coin["expected_payout_per_attempt"] < mc_edge["expected_payout_per_attempt"]
