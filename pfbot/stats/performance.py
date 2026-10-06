"""Performance statistics and backtest-overfitting diagnostics (PLAN.md section 3).

Units: unless stated otherwise every Sharpe ratio here is *per period* (mean / std of
the per-period returns, no annualization). PSR / DSR formulas of Bailey & Lopez de
Prado are only valid in per-period units together with the per-period skewness,
kurtosis and number of observations; annualize only for reporting
(``annualize_sharpe``). Kurtosis is always *Pearson* kurtosis (normal = 3), not excess.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import NamedTuple

import numpy as np
from scipy import stats

__all__ = [
    "sharpe", "annualize_sharpe", "deannualize_sharpe", "annualize_return", "annualize_vol",
    "sharpe_moments", "drawdown", "max_drawdown",
    "SharpeCI", "bootstrap_sharpe_ci",
    "probabilistic_sharpe_ratio", "expected_max_sharpe", "deflated_sharpe_ratio",
    "PBOResult", "pbo_cscv", "TrialRegistry",
]

EULER_GAMMA = 0.5772156649015329


# ---------------------------------------------------------------------------
# basic
# ---------------------------------------------------------------------------
def _clean(x) -> np.ndarray:
    a = np.asarray(x, dtype=float)
    return a[~np.isnan(a)]


def sharpe(returns, periods_per_year: float | None = None) -> float:
    """Sharpe ratio mean / std (ddof=1) of ``returns`` (zero risk-free rate).

    Per period if ``periods_per_year`` is None, else annualized by sqrt(periods_per_year).
    """
    r = _clean(returns)
    sd = r.std(ddof=1)
    sr = r.mean() / sd if sd > 0 else np.nan
    return float(sr if periods_per_year is None else annualize_sharpe(sr, periods_per_year))


def annualize_sharpe(sr: float, periods_per_year: float) -> float:
    """Per-period Sharpe -> annual (iid scaling, sqrt(periods_per_year))."""
    return sr * np.sqrt(periods_per_year)


def deannualize_sharpe(sr_annual: float, periods_per_year: float) -> float:
    """Annual Sharpe -> per-period Sharpe."""
    return sr_annual / np.sqrt(periods_per_year)


def annualize_return(mean_return: float, periods_per_year: float, compound: bool = False) -> float:
    """Annualize a mean per-period simple return (arithmetic by default, or compounded)."""
    return (1 + mean_return) ** periods_per_year - 1 if compound else mean_return * periods_per_year


def annualize_vol(std: float, periods_per_year: float) -> float:
    """Per-period volatility -> annual volatility (sqrt-time)."""
    return std * np.sqrt(periods_per_year)


def sharpe_moments(returns) -> tuple[float, float, float, int]:
    """(per-period Sharpe, skewness, Pearson kurtosis, n) in the units PSR/DSR expect."""
    r = _clean(returns)
    return (sharpe(r), float(stats.skew(r)), float(stats.kurtosis(r, fisher=False)), len(r))


def drawdown(equity) -> np.ndarray:
    """Drawdown series as a fraction of the running peak (<= 0). Equity must be > 0."""
    e = np.asarray(equity, dtype=float)
    return e / np.maximum.accumulate(e) - 1.0


def max_drawdown(equity) -> float:
    """Maximum peak-to-trough drawdown as a positive fraction (0.12 = -12%)."""
    return float(-drawdown(equity).min())


# ---------------------------------------------------------------------------
# bootstrap
# ---------------------------------------------------------------------------
class SharpeCI(NamedTuple):
    sharpe: float
    lo: float
    hi: float
    samples: np.ndarray


def _block_bootstrap_indices(T: int, n: int, block: float, method: str,
                             rng: np.random.Generator) -> np.ndarray:
    """(n, T) resampling indices; stationary (geometric block lengths, mean ``block``,
    Politis-Romano 1994) or circular (fixed block length, wrap-around)."""
    if method == "stationary":
        idx = np.empty((n, T), dtype=np.int64)
        idx[:, 0] = rng.integers(0, T, n)
        new_block = rng.random((n, T)) < 1.0 / block
        starts = rng.integers(0, T, (n, T))
        for t in range(1, T):
            idx[:, t] = np.where(new_block[:, t], starts[:, t], (idx[:, t - 1] + 1) % T)
        return idx
    if method == "circular":
        b = max(int(block), 1)
        nb = -(-T // b)
        starts = rng.integers(0, T, (n, nb))
        idx = (starts[:, :, None] + np.arange(b)[None, None, :]) % T
        return idx.reshape(n, nb * b)[:, :T]
    raise ValueError("method must be 'stationary' or 'circular'")


def bootstrap_sharpe_ci(returns, n: int = 2000, block: float = 10, alpha: float = 0.05,
                        seed: int | None = None, method: str = "stationary",
                        periods_per_year: float | None = None) -> SharpeCI:
    """Percentile confidence interval of the Sharpe ratio by block bootstrap.

    Blocks preserve short-range autocorrelation / vol clustering; ``block`` is the mean
    (stationary) or fixed (circular) block length in periods; ``block=1`` is the iid
    bootstrap. Returns per-period values unless ``periods_per_year`` is given.
    """
    r = _clean(returns)
    rng = np.random.default_rng(seed)
    idx = _block_bootstrap_indices(len(r), n, block, method, rng)
    s = r[idx]
    sd = s.std(axis=1, ddof=1)
    srs = np.where(sd > 0, s.mean(axis=1) / np.where(sd > 0, sd, 1.0), np.nan)
    point = sharpe(r)
    if periods_per_year is not None:
        srs = annualize_sharpe(srs, periods_per_year)
        point = annualize_sharpe(point, periods_per_year)
    lo, hi = np.nanquantile(srs, [alpha / 2, 1 - alpha / 2])
    return SharpeCI(float(point), float(lo), float(hi), srs)


# ---------------------------------------------------------------------------
# PSR / DSR  (Bailey & Lopez de Prado 2012, 2014)
# ---------------------------------------------------------------------------
def probabilistic_sharpe_ratio(sr: float, sr_benchmark: float, n: int, skew: float = 0.0,
                               kurt: float = 3.0) -> float:
    """P(true SR > sr_benchmark) given an observed per-period ``sr`` over ``n`` returns.

        PSR = Phi( (sr - sr*) sqrt(n - 1) / sqrt(1 - skew sr + (kurt - 1)/4 sr^2) )

    All inputs per period; ``kurt`` is Pearson kurtosis (3 for normal returns).
    """
    var = 1.0 - skew * sr + (kurt - 1.0) / 4.0 * sr ** 2
    return float(stats.norm.cdf((sr - sr_benchmark) * np.sqrt(n - 1) / np.sqrt(var)))


def expected_max_sharpe(sr_variance: float, n_trials: int) -> float:
    """Expected maximum of ``n_trials`` per-period Sharpe estimates under the null of
    zero true Sharpe (False Strategy Theorem):

        SR0 = sqrt(V[SR]) ((1 - g) Phi^-1(1 - 1/N) + g Phi^-1(1 - 1/(N e))),  g = Euler

    ``sr_variance`` is the cross-sectional variance of the trials' per-period SRs.
    """
    if n_trials <= 1:
        return 0.0
    z1 = stats.norm.ppf(1.0 - 1.0 / n_trials)
    z2 = stats.norm.ppf(1.0 - 1.0 / (n_trials * np.e))
    return float(np.sqrt(sr_variance) * ((1 - EULER_GAMMA) * z1 + EULER_GAMMA * z2))


def deflated_sharpe_ratio(observed_sr: float, sr_trials=None, n_trials: int | None = None,
                          n_obs: int | None = None, skew: float = 0.0, kurt: float = 3.0,
                          sr_variance: float | None = None) -> float:
    """Deflated Sharpe Ratio = PSR(observed_sr, benchmark = expected_max_sharpe).

    Pass either ``sr_trials`` (per-period SRs of *all* trials, incl. the selected one;
    their variance is used and ``n_trials`` defaults to their count) or ``sr_variance``
    and ``n_trials``. ``observed_sr``, ``skew``, ``kurt`` (Pearson) and ``n_obs`` refer
    to the selected strategy's per-period returns. Returns a probability; DSR > 0.95 is
    the usual bar.
    """
    if sr_trials is not None:
        trials = _clean(sr_trials)
        sr_variance = float(np.var(trials, ddof=1)) if len(trials) > 1 else 0.0
        n_trials = len(trials) if n_trials is None else n_trials
    if sr_variance is None or n_trials is None or n_obs is None:
        raise ValueError("need (sr_trials or sr_variance + n_trials) and n_obs")
    sr0 = expected_max_sharpe(sr_variance, n_trials)
    return probabilistic_sharpe_ratio(observed_sr, sr0, n_obs, skew, kurt)


# ---------------------------------------------------------------------------
# PBO via CSCV  (Bailey, Borwein, Lopez de Prado, Zhu 2016)
# ---------------------------------------------------------------------------
class PBOResult(NamedTuple):
    pbo: float            # fraction of splits whose IS-best config ranks <= median OOS
    logits: np.ndarray    # lambda_c = log(w / (1 - w)), w = OOS relative rank of IS-best
    n_combinations: int


def pbo_cscv(perf_matrix, n_splits: int = 16) -> PBOResult:
    """Probability of Backtest Overfitting by Combinatorially Symmetric CV.

    ``perf_matrix``: T x N per-period returns of N configurations (columns) on the same
    T periods. Rows are cut into ``n_splits`` (even) contiguous blocks (remainder rows
    dropped from the end); for each of the C(S, S/2) choices of S/2 blocks as in-sample
    (rest out-of-sample) the configuration with the best IS Sharpe is selected and its
    OOS Sharpe rank among all N is recorded as w = rank / (N + 1) (ranks 1..N, average
    ranks for ties). PBO = share of combinations with logit(w) <= 0, i.e. the IS winner
    is at or below the OOS median. ~0.5 means selection is pure noise.
    """
    M = np.asarray(perf_matrix, dtype=float)
    T, N = M.shape
    S = int(n_splits)
    if S % 2 or S < 2:
        raise ValueError("n_splits must be even and >= 2")
    L = T // S
    if L < 2:
        raise ValueError("too few rows for n_splits")
    blocks = M[: L * S].reshape(S, L, N)
    # per-block sufficient statistics, so each combination is a matrix product
    s1, s2 = blocks.sum(axis=1), (blocks ** 2).sum(axis=1)  # (S, N)
    combos = np.array(list(combinations(range(S), S // 2)))
    ind = np.zeros((len(combos), S))
    ind[np.arange(len(combos))[:, None], combos] = 1.0
    nobs = L * S // 2

    def _sr(a1, a2):
        mean = a1 / nobs
        var = (a2 - nobs * mean ** 2) / (nobs - 1)
        return mean / np.sqrt(np.maximum(var, 1e-300))

    sr_is = _sr(ind @ s1, ind @ s2)
    sr_oos = _sr((1 - ind) @ s1, (1 - ind) @ s2)
    best = np.argmax(sr_is, axis=1)
    ranks = stats.rankdata(sr_oos, axis=1)  # 1 = worst, N = best
    w = ranks[np.arange(len(combos)), best] / (N + 1)
    logits = np.log(w / (1 - w))
    return PBOResult(float(np.mean(logits <= 0)), logits, len(combos))


# ---------------------------------------------------------------------------
# trial registry
# ---------------------------------------------------------------------------
_DEFAULT_REGISTRY = Path(__file__).resolve().parents[2] / "research" / "trials.jsonl"


class TrialRegistry:
    """Append-only JSONL log of every backtest trial, so DSR can count them all.

    One line per trial: {"timestamp", "hypothesis_id", "params", "n_obs", "sharpe", ...}
    with ``sharpe`` per period. Never edit or delete lines; failed ideas count too.
    """

    def __init__(self, path: str | Path = _DEFAULT_REGISTRY):
        self.path = Path(path)

    def log(self, hypothesis_id: str, params: dict, n_obs: int, sharpe: float, **extra) -> dict:
        rec = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hypothesis_id": hypothesis_id,
            "params": params,
            "n_obs": int(n_obs),
            "sharpe": float(sharpe),
            **extra,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, default=str) + "\n")
        return rec

    def load(self, hypothesis_id: str | None = None) -> list[dict]:
        if not self.path.exists():
            return []
        with self.path.open(encoding="utf-8") as f:
            recs = [json.loads(line) for line in f if line.strip()]
        return [r for r in recs if hypothesis_id is None or r["hypothesis_id"] == hypothesis_id]

    def sharpes(self, hypothesis_id: str | None = None) -> np.ndarray:
        """Per-period Sharpe ratios of the logged trials (feed to ``deflated_sharpe_ratio``)."""
        return np.array([r["sharpe"] for r in self.load(hypothesis_id)], dtype=float)

    def n_trials(self, hypothesis_id: str | None = None) -> int:
        return len(self.load(hypothesis_id))
