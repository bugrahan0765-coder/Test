"""Regime statistics: Lo-MacKinlay variance ratio and Hurst exponent.

PLAN.md section 2.2-C. VR > 1 / H > 0.5 indicate trending (positively
autocorrelated) returns, VR < 1 / H < 0.5 mean reversion. Rolling versions are
strictly backward-looking: the value at time t uses only observations in the
``window`` ending at (and including) t.
"""
from __future__ import annotations

from typing import NamedTuple

import numba
import numpy as np
import pandas as pd
from scipy import stats

__all__ = [
    "VRResult",
    "variance_ratio",
    "rolling_variance_ratio",
    "hurst_exponent",
    "rolling_hurst",
]


class VRResult(NamedTuple):
    vr: float      # variance ratio VR(q)
    z: float       # heteroskedasticity-robust z statistic z*(q)
    pvalue: float  # two-sided p-value of z


@numba.njit(cache=False)
def _vr_core(r, q):
    """Lo & MacKinlay (1988) VR(q) with overlapping q-sums and robust z*(q).

    sigma_a^2 = sum (r_t - mu)^2 / (T - 1)
    sigma_c^2 = sum_{t>=q} (r_t + ... + r_{t-q+1} - q mu)^2 / m,
                m = q (T - q + 1) (1 - q / T)          (unbiased version)
    VR = sigma_c^2 / sigma_a^2
    delta_j = T * sum_{t>j} e_t^2 e_{t-j}^2 / (sum e_t^2)^2,   e = r - mu
    theta = sum_{j=1}^{q-1} (2 (q - j) / q)^2 delta_j,   z* = sqrt(T) (VR - 1) / sqrt(theta)
    (T here is the number of returns, Lo-MacKinlay's nq.)
    """
    T = r.shape[0]
    mu = r.mean()
    e = r - mu
    e2 = e * e
    den = e2.sum()
    sa = den / (T - 1)
    m = q * (T - q + 1) * (1.0 - q / T)
    s = 0.0
    for k in range(q):
        s += e[k]
    sc = s * s
    for t in range(q, T):
        s += e[t] - e[t - q]
        sc += s * s
    sc /= m
    vr = sc / sa
    theta = 0.0
    for j in range(1, q):
        acc = 0.0
        for t in range(j, T):
            acc += e2[t] * e2[t - j]
        delta = T * acc / (den * den)
        w = 2.0 * (q - j) / q
        theta += w * w * delta
    z = np.sqrt(T) * (vr - 1.0) / np.sqrt(theta) if theta > 0 else np.nan
    return vr, z


@numba.njit(cache=False)
def _rolling_vr(r, q, window):
    n = r.shape[0]
    vr = np.full(n, np.nan)
    z = np.full(n, np.nan)
    for t in range(window - 1, n):
        seg = r[t - window + 1:t + 1]
        ok = True
        for x in seg:
            if np.isnan(x):
                ok = False
                break
        if ok:
            vr[t], z[t] = _vr_core(seg, q)
    return vr, z


def variance_ratio(returns, q: int) -> VRResult:
    """Lo-MacKinlay variance ratio of (log) ``returns`` at horizon ``q`` (q >= 2).

    Uses overlapping q-period sums, bias-corrected variance estimators and the
    heteroskedasticity-consistent z*(q) statistic (asymptotically N(0, 1) under the
    martingale-difference null). NaNs are dropped.
    """
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if q < 2 or len(r) <= 2 * q:
        raise ValueError("need q >= 2 and more than 2q returns")
    vr, z = _vr_core(r, int(q))
    return VRResult(float(vr), float(z), float(2 * stats.norm.sf(abs(z))))


def rolling_variance_ratio(close: pd.Series, q: int, window: int) -> pd.DataFrame:
    """Rolling VR(q) and z*(q) on log returns of ``close``.

    Row t uses the ``window`` log returns ending at t (i.e. closes t-window..t), so it is
    known at bar t's close. Windows containing a NaN return give NaN. Returns a
    DataFrame with columns ``vr`` and ``z`` on ``close``'s index.
    """
    r = np.log(close.astype(float)).diff().to_numpy()
    vr, z = _rolling_vr(r, int(q), int(window))
    return pd.DataFrame({"vr": vr, "z": z}, index=close.index)


def _default_lags(n: int) -> np.ndarray:
    hi = max(4, n // 10)
    return np.unique(np.geomspace(2, hi, 10).astype(int))


def hurst_exponent(series, lags=None) -> float:
    """Hurst exponent of a *level* series (e.g. log price) by the aggregated-variance /
    variogram method: Var(X_{t+tau} - X_t) ~ tau^{2H}, so H = slope / 2 of
    log Var vs log tau over ``lags`` (default: ~10 geometric lags from 2 to n/10).

    Chosen over rescaled range (R/S) because R/S is noticeably biased upward in small
    samples (needs the Anis-Lloyd correction), while this estimator is ~unbiased for a
    random walk (H = 0.5). Pass cumulative levels, not returns.
    """
    x = np.asarray(series, dtype=float)
    x = x[~np.isnan(x)]
    lags = _default_lags(len(x)) if lags is None else np.asarray(lags, dtype=int)
    v = np.array([np.var(x[k:] - x[:-k], ddof=1) for k in lags])
    slope = np.polyfit(np.log(lags), np.log(v), 1)[0]
    return float(slope / 2.0)


def rolling_hurst(series: pd.Series, window: int, lags=None) -> pd.Series:
    """Rolling ``hurst_exponent`` over the ``window`` levels ending at t (no lookahead).

    For each lag tau, the variance of the window - tau differences whose both endpoints
    lie inside the window is computed with a rolling variance, then H is the per-row OLS
    slope / 2. Matches ``hurst_exponent(series[t-window+1 : t+1], lags)`` exactly up to
    floating point.
    """
    x = series.astype(float)
    lags = _default_lags(window) if lags is None else np.asarray(lags, dtype=int)
    logv = np.column_stack([
        np.log((x - x.shift(k)).rolling(window - k).var().to_numpy()) for k in lags
    ])
    lx = np.log(lags.astype(float))
    lxc = lx - lx.mean()
    slope = (logv - logv.mean(axis=1, keepdims=True)) @ lxc / (lxc @ lxc)
    return pd.Series(slope / 2.0, index=series.index, name="hurst")
