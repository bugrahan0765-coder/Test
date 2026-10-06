"""Synthetic M1 bars for testing the research stack before real data is available.

Prices follow a random walk whose volatility has the two stylised facts the
strategies care about: clustering across days (GARCH-like) and a U-shaped
intraday profile with spikes at the London and New York opens. With
``drift_fn=None`` the series has no directional edge, which is what the
"random strategy must not make money" engine tests rely on.
"""
from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd

from .schema import validate_bars

# UTC minute-of-day centres of activity spikes (London 07:00, NY cash open 13:30).
_SPIKES = ((7 * 60, 1.8, 45.0), (13 * 60 + 30, 2.5, 40.0))


def intraday_profile(minutes: np.ndarray) -> np.ndarray:
    """Relative volatility multiplier per UTC minute-of-day (mean ~1)."""
    base = 0.6 + 0.4 * np.cos(2 * np.pi * (minutes - 14 * 60) / 1440) ** 2
    for centre, height, width in _SPIKES:
        base = base + height * np.exp(-0.5 * ((minutes - centre) / width) ** 2)
    return base / base.mean()


def make_bars(
    start: str = "2020-01-01",
    days: int = 250,
    price0: float = 15000.0,
    daily_vol: float = 0.012,
    spread: float = 1.0,
    seed: int = 0,
    drift_fn: Callable[[pd.DatetimeIndex, np.ndarray], np.ndarray] | None = None,
    substeps: int = 6,
) -> pd.DataFrame:
    """Generate weekday M1 bars (21:00-22:00 UTC daily break removed).

    drift_fn(index, sigma) may return a per-minute log-return drift array to
    inject a known edge; sigma is the per-minute volatility used for the bar.
    """
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(start, periods=days, tz="UTC")
    minutes = np.array([m for m in range(1440) if not (21 * 60 <= m < 22 * 60)])

    # GARCH(1,1)-style daily variance multiplier.
    omega, alpha, beta = 0.05, 0.10, 0.85
    var = np.empty(days)
    v = 1.0
    for d in range(days):
        var[d] = v
        shock = rng.standard_normal()
        v = omega + alpha * v * shock**2 + beta * v
    day_mult = np.sqrt(var)

    prof = intraday_profile(minutes)
    per_min = daily_vol / np.sqrt(len(minutes))
    sigma = (day_mult[:, None] * prof[None, :] * per_min).ravel()

    stamps = dates.asi8[:, None] + pd.to_timedelta(minutes, unit="min").as_unit(dates.unit).asi8[None, :]
    index = pd.DatetimeIndex(pd.to_datetime(stamps.ravel(), unit=dates.unit, utc=True), name="time")

    drift = np.zeros_like(sigma) if drift_fn is None else np.asarray(drift_fn(index, sigma), float)
    steps = rng.standard_normal((len(sigma), substeps)) * (sigma / np.sqrt(substeps))[:, None]
    steps += (drift / substeps)[:, None]
    path = np.cumsum(steps.ravel()).reshape(len(sigma), substeps)
    prev_close = np.concatenate([[0.0], path[:-1, -1]])
    logp = np.column_stack([prev_close, path])  # open = previous close

    px = price0 * np.exp(logp)
    df = pd.DataFrame(
        {
            "open": px[:, 0],
            "high": px.max(axis=1),
            "low": px.min(axis=1),
            "close": px[:, -1],
            "spread": spread,
        },
        index=index,
    )
    return validate_bars(df)
