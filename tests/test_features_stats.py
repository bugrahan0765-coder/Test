"""Tests for pfbot.features.{volatility,regime} and pfbot.stats.performance (synthetic data)."""
import numpy as np
import pandas as pd
import pytest

from pfbot.data.schema import validate_bars
from pfbot.features.regime import (hurst_exponent, rolling_hurst, rolling_variance_ratio,
                                   variance_ratio)
from pfbot.features.volatility import (daily_realized_vol, expected_bar_vol, har_rv_forecast,
                                       intraday_vol_profile, trading_date)
from pfbot.stats.performance import (TrialRegistry, bootstrap_sharpe_ci, deflated_sharpe_ratio,
                                     max_drawdown, pbo_cscv, probabilistic_sharpe_ratio, sharpe,
                                     sharpe_moments)

NY = "America/New_York"


# ---------------------------------------------------------------------------
# synthetic 5-min bars: daily GARCH(1,1) variance x U-shaped intraday profile
# ---------------------------------------------------------------------------
def _simulate_bars(n_days=420, seed=0):
    rng = np.random.default_rng(seed)
    # trading days run 17:00 NY -> 17:00 NY, Mon..Fri trading dates
    t = pd.date_range("2021-01-03 17:00", periods=(n_days * 7 // 5 + 7) * 288, freq="5min", tz=NY)
    t = t.tz_convert("UTC")
    td = trading_date(t, NY, 17)
    t = t[td.dayofweek < 5]
    td = trading_date(t, NY, 17)
    days = td.unique()[:n_days]
    keep = td.isin(days)
    t, td = t[keep], td[keep]

    # daily GARCH(1,1) on daily variance (in log-return units)
    omega, alpha, beta = 2e-6, 0.08, 0.90
    h = np.empty(n_days)
    h[0] = omega / (1 - alpha - beta)
    day_ret = 0.0
    for d in range(1, n_days):
        h[d] = omega + alpha * day_ret ** 2 + beta * h[d - 1]
        day_ret = np.sqrt(h[d]) * rng.standard_normal()
    # U-shaped intraday weights (NY local hour), normalized per day
    local = t.tz_convert(NY)
    hour = local.hour + local.minute / 60
    u = 1.0 + 3.0 * np.exp(-((hour - 9.5) ** 2) / 2) + 2.0 * np.exp(-((hour - 15.5) ** 2) / 2)
    day_idx = pd.Index(days).get_indexer(td)
    u = u / pd.Series(u).groupby(day_idx).transform("sum").to_numpy()
    r = np.sqrt(h[day_idx] * u) * rng.standard_normal(len(t))

    close = 100 * np.exp(np.cumsum(r))
    open_ = np.r_[100.0, close[:-1]]
    wig = np.abs(rng.standard_normal(len(t))) * np.sqrt(h[day_idx] * u) * 0.3
    bars = pd.DataFrame({
        "open": open_, "close": close,
        "high": np.maximum(open_, close) * np.exp(wig),
        "low": np.minimum(open_, close) * np.exp(-wig),
    }, index=pd.DatetimeIndex(t, name="time"))
    return validate_bars(bars), pd.Series(h, index=pd.DatetimeIndex(days, name="date"))


@pytest.fixture(scope="module")
def sim():
    return _simulate_bars()


def _assert_same(a, b):
    """Exact equality on the overlap (NaN == NaN)."""
    a, b = a.align(b, join="inner")
    np.testing.assert_array_equal(a.to_numpy(), b.to_numpy())


# ---------------------------------------------------------------------------
# volatility
# ---------------------------------------------------------------------------
def test_trading_date_boundary():
    t = pd.DatetimeIndex(["2024-03-04 21:55", "2024-03-04 22:00"], tz="UTC")  # 16:55/17:00 NY (EST)
    d = trading_date(t, NY, 17)
    assert list(d.strftime("%Y-%m-%d")) == ["2024-03-04", "2024-03-05"]


def test_realized_vol_matches_true_variance(sim):
    bars, h = sim
    rv = daily_realized_vol(bars)
    assert rv.index.equals(h.index)
    # RV of 288 returns is a precise estimate of the daily variance
    ratio = (rv / h).iloc[1:]
    assert abs(ratio.median() - 1) < 0.05


def test_har_forecast_predicts_and_no_lookahead(sim):
    bars, _ = sim
    rv = daily_realized_vol(bars)
    fc = har_rv_forecast(rv, refit_every=20, min_train=100)
    ok = fc.notna()
    assert ok.sum() > 250
    corr = np.corrcoef(np.log(fc[ok]), np.log(rv[ok]))[0, 1]
    assert corr > 0.3
    # forecasting log RV beats the unconditional mean of past values
    assert np.mean((np.log(fc[ok]) - np.log(rv[ok])) ** 2) < np.var(np.log(rv[ok]))

    # lookahead: truncating / altering the future never changes past forecasts
    _assert_same(fc, har_rv_forecast(rv.iloc[:300], refit_every=20, min_train=100))
    rv_mod = rv.copy()
    rv_mod.iloc[300:] *= 5.0
    _assert_same(fc.iloc[:301], har_rv_forecast(rv_mod, refit_every=20, min_train=100).iloc[:301])
    # rolling window variant also runs
    assert har_rv_forecast(rv, window=150).notna().sum() == ok.sum()


def test_intraday_profile_and_expected_vol(sim):
    bars, _ = sim
    prof = intraday_vol_profile(bars, lookback_days=60)
    last = prof.iloc[-1]
    # U shape: 09:30 NY bucket much more volatile than 03:00 NY
    assert last[9 * 60 + 30] > 1.5 * last[3 * 60]
    assert prof.iloc[0].isna().all()  # first day has no history

    ev = expected_bar_vol(bars)
    r = np.log(bars["close"]).diff()
    ok = ev.notna() & r.notna()
    assert ok.sum() > 50_000
    # calibration: E[r^2 / expected^2] ~ 1
    z2 = (r[ok] / ev[ok]) ** 2
    assert 0.8 < z2.mean() < 1.25

    # lookahead: cut bars mid-day, overlap must be identical (incl. the partial day)
    cut = bars.iloc[: len(bars) * 2 // 3 + 37]
    _assert_same(ev, expected_bar_vol(cut))
    _assert_same(prof, intraday_vol_profile(cut, lookback_days=60))
    # RV identical on all fully observed days
    rv_full, rv_cut = daily_realized_vol(bars), daily_realized_vol(cut)
    _assert_same(rv_full, rv_cut.iloc[:-1])


# ---------------------------------------------------------------------------
# regime
# ---------------------------------------------------------------------------
def _ar1(phi, n, rng):
    e = rng.standard_normal(n)
    x = np.empty(n)
    x[0] = e[0]
    for i in range(1, n):
        x[i] = phi * x[i - 1] + e[i]
    return x


def test_variance_ratio():
    rng = np.random.default_rng(1)
    iid = variance_ratio(rng.standard_normal(5000) * np.exp(rng.standard_normal(5000) * 0.3), 5)
    assert abs(iid.vr - 1) < 0.1 and abs(iid.z) < 3
    pos = variance_ratio(_ar1(0.3, 5000, rng), 5)
    neg = variance_ratio(_ar1(-0.3, 5000, rng), 5)
    assert pos.vr > 1.3 and pos.z > 5
    assert neg.vr < 0.8 and neg.z < -5


def test_rolling_variance_ratio_consistent_and_causal():
    rng = np.random.default_rng(2)
    close = pd.Series(100 * np.exp(np.cumsum(0.001 * rng.standard_normal(3000))))
    roll = rolling_variance_ratio(close, q=4, window=500)
    assert roll["vr"].iloc[:500].isna().all() and roll["vr"].iloc[500:].notna().all()
    direct = variance_ratio(np.log(close).diff().iloc[-500:], 4)
    assert roll["vr"].iloc[-1] == pytest.approx(direct.vr, rel=1e-12)
    assert roll["z"].iloc[-1] == pytest.approx(direct.z, rel=1e-12)
    _assert_same(roll["vr"].iloc[:2000], rolling_variance_ratio(close.iloc[:2000], 4, 500)["vr"])


def test_hurst():
    rng = np.random.default_rng(3)
    rw = np.cumsum(rng.standard_normal(5000))
    assert abs(hurst_exponent(rw) - 0.5) < 0.07
    assert hurst_exponent(_ar1(0.9, 5000, rng)) < 0.4  # mean-reverting levels
    # positively autocorrelated increments: H > 0.5 at short lags (short memory, so the
    # estimate drifts back to 0.5 at long lags)
    trend = np.cumsum(_ar1(0.5, 5000, rng))
    assert hurst_exponent(trend, lags=[1, 2, 4, 8]) > 0.6

    s = pd.Series(rw)
    roll = rolling_hurst(s, window=1000)
    assert roll.iloc[:999].isna().all()
    assert roll.iloc[-1] == pytest.approx(hurst_exponent(rw[-1000:]), abs=1e-9)
    _assert_same(roll.iloc[:3000], rolling_hurst(s.iloc[:3000], window=1000))


# ---------------------------------------------------------------------------
# performance
# ---------------------------------------------------------------------------
def test_sharpe_and_drawdown():
    r = np.array([0.01, -0.01, 0.02, 0.0])
    assert sharpe(r) == pytest.approx(r.mean() / r.std(ddof=1))
    assert sharpe(r, 252) == pytest.approx(sharpe(r) * np.sqrt(252))
    assert max_drawdown([100, 120, 90, 130, 117]) == pytest.approx(0.25)


def test_bootstrap_ci_covers_true_sharpe():
    rng = np.random.default_rng(4)
    true_sr = 0.05
    r = true_sr + rng.standard_normal(2000)
    for method in ("stationary", "circular"):
        ci = bootstrap_sharpe_ci(r, n=1000, block=10, seed=0, method=method)
        assert ci.lo < true_sr < ci.hi
        assert 0.06 < ci.hi - ci.lo < 0.12  # ~ 2 * 1.96 / sqrt(2000) = 0.088


def test_psr_and_dsr():
    assert probabilistic_sharpe_ratio(0.0, 0.0, 500) == pytest.approx(0.5)
    assert probabilistic_sharpe_ratio(0.1, 0.0, 1000) > 0.99
    # fatter tails / negative skew lower PSR
    assert probabilistic_sharpe_ratio(0.1, 0.0, 250, skew=-1, kurt=6) < \
        probabilistic_sharpe_ratio(0.1, 0.0, 250)

    dsr = [deflated_sharpe_ratio(0.1, n_trials=k, sr_variance=0.002, n_obs=1000)
           for k in (1, 2, 10, 100, 1000)]
    assert all(a > b for a, b in zip(dsr, dsr[1:]))
    assert dsr[0] == pytest.approx(probabilistic_sharpe_ratio(0.1, 0.0, 1000))

    rng = np.random.default_rng(5)
    trials = rng.normal(0, 0.03, 50)
    sr, sk, ku, n = sharpe_moments(rng.standard_normal(1000) + 0.05)
    assert deflated_sharpe_ratio(sr, trials, n_obs=n, skew=sk, kurt=ku) == pytest.approx(
        deflated_sharpe_ratio(sr, n_trials=50, sr_variance=np.var(trials, ddof=1), n_obs=n,
                              skew=sk, kurt=ku))


def test_pbo_noise_vs_edge():
    # pure noise: PBO of a single dataset is itself very noisy (often 0.15..0.85),
    # so check its average across independent datasets is ~0.5
    pbos = []
    for seed in range(12):
        noise = np.random.default_rng(seed).standard_normal((1000, 20))
        res = pbo_cscv(noise, n_splits=16)
        pbos.append(res.pbo)
    assert res.n_combinations == 12870 and len(res.logits) == 12870
    assert 0.35 < np.mean(pbos) < 0.65

    rng = np.random.default_rng(6)
    noise = rng.standard_normal((2000, 40))

    edge = noise.copy()
    edge[:, 7] += 0.2
    assert pbo_cscv(edge, n_splits=16).pbo < 0.05


def test_trial_registry(tmp_path):
    reg = TrialRegistry(tmp_path / "research" / "trials.jsonl")
    assert reg.n_trials() == 0
    reg.log("A1", {"lookback": 30}, 1200, 0.04)
    reg.log("A1", {"lookback": 60}, 1200, -0.01, note="x")
    reg.log("A2", {"n": 5}, 800, 0.02)
    assert reg.n_trials() == 3 and reg.n_trials("A1") == 2
    np.testing.assert_allclose(reg.sharpes("A1"), [0.04, -0.01])
    assert reg.load("A2")[0]["params"] == {"n": 5}
