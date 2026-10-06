"""Shared machinery for testing pre-registered hypotheses.

- Period guard: the locked test period can only be loaded with ``unlock=True``.
- Per-symbol cost models and session definitions.
- ``run_grid`` runs a signal function over a parameter grid (and cost stress
  levels), logs every configuration to the trial registry, and returns a
  results table plus the trade lists.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

from pfbot.backtest.engine import CostModel, run_backtest, summarize
from pfbot.data.store import load_bars
from pfbot.stats.performance import TrialRegistry

DATA_ROOT = Path(__file__).resolve().parents[2] / "data" / "bars"

PERIODS = {
    "IS": ("2015-01-01", "2020-12-31 23:59"),
    "OOS": ("2021-01-01", "2023-12-31 23:59"),
    "LOCKED": ("2024-01-01", "2100-01-01"),
}


@dataclass(frozen=True)
class Session:
    tz: str
    open: str  # local "HH:MM"
    close: str


SESSIONS = {
    "US100": Session("America/New_York", "09:30", "16:00"),
    "US500": Session("America/New_York", "09:30", "16:00"),
    "GER40": Session("Europe/Berlin", "09:00", "17:30"),
    "XAUUSD": Session("America/New_York", "08:20", "13:30"),  # COMEX gold pit hours
}

# Months dropped from research because the HistData source is incomplete or wrong
# (see research/reports/data_quality.md). GER40 2021-2023 is not even the DAX.
_BAD_2023 = ["2023-03", "2023-04", "2023-05", "2023-06", "2023-07"]
EXCLUDED_MONTHS = {
    "US100": _BAD_2023,
    "US500": ["2016-08", "2017-05", "2017-07", "2017-09", "2017-10", "2017-11"] + _BAD_2023,
    "XAUUSD": _BAD_2023,
    "GER40": [f"{y}-{m:02d}" for y in range(2015, 2019) for m in range(1, 13)]
    + ["2020-12"] + [f"{y}-{m:02d}" for y in (2021, 2022, 2023) for m in range(1, 13)],
}

SLIPPAGE = {"US100": 0.5, "US500": 0.25, "GER40": 0.5, "XAUUSD": 0.10}


# Assumed CFD overnight financing (FTMO swap), fraction of notional per year, both directions.
# Conservative placeholder until calibrated against FTMO's published swap table.
FINANCING_ANNUAL = 0.05


def cost_model(symbol: str, spread_mult: float = 1.0, financing: float = FINANCING_ANNUAL) -> CostModel:
    return CostModel(spread_mult=spread_mult, slippage=SLIPPAGE.get(symbol, 0.0), financing_annual=financing)


def load_period(symbol: str, period: str, unlock: bool = False, root: Path = DATA_ROOT) -> pd.DataFrame:
    """M1 bars for a named period. The locked period requires unlock=True."""
    if period == "LOCKED" and not unlock:
        raise PermissionError("the locked test period is opened only once, for the final portfolio")
    start, end = PERIODS[period]
    bars = load_bars(symbol, "1min", start=start, end=end, root=root)
    bad = EXCLUDED_MONTHS.get(symbol, [])
    if bad:
        month = bars.index.tz_convert(None).strftime("%Y-%m")
        bars = bars[~month.isin(bad)]
    return bars


def local_times(dates, hhmm: str, tz: str) -> pd.DatetimeIndex:
    """UTC timestamps for local wall-clock time hhmm on each date (DST aware)."""
    d = pd.DatetimeIndex(pd.to_datetime(dates)).tz_localize(None).normalize()
    local = d + pd.Timedelta(hours=int(hhmm[:2]), minutes=int(hhmm[3:]))
    return local.tz_localize(tz, ambiguous="NaT", nonexistent="NaT").tz_convert("UTC")


def session_dates(bars: pd.DataFrame, session: Session) -> pd.DatetimeIndex:
    """Local dates on which the session had a bar at its open minute."""
    local = bars.index.tz_convert(session.tz)
    open_min = int(session.open[:2]) * 60 + int(session.open[3:])
    at_open = (local.hour * 60 + local.minute) == open_min
    return pd.DatetimeIndex(local[at_open].normalize().tz_localize(None)).unique()


def price_at(bars: pd.DataFrame, times: pd.DatetimeIndex, field: str = "close") -> np.ndarray:
    """Value of `field` of the last bar starting strictly before each time
    (i.e. the latest price known at that instant). NaN if none within 30 minutes."""
    idx = bars.index
    pos = idx.searchsorted(times, side="left") - 1
    out = np.full(len(times), np.nan)
    ok = (pos >= 0) & ~pd.isna(times)
    vals = bars[field].to_numpy()
    out[ok] = vals[pos[ok]]
    stale = np.zeros(len(times), bool)
    stale[ok] = (times[ok] - idx[pos[ok]]) > pd.Timedelta(minutes=30)
    out[stale] = np.nan
    return out


def window_stats(bars: pd.DataFrame, starts: pd.DatetimeIndex, ends: pd.DatetimeIndex) -> pd.DataFrame:
    """Open/high/low/close of M1 bars in [start, end) per window (NaN if empty)."""
    idx = bars.index
    a = idx.searchsorted(starts, side="left")
    b = idx.searchsorted(ends, side="left")
    o, h, l, c = (bars[k].to_numpy() for k in ("open", "high", "low", "close"))
    rows = []
    for i, j in zip(a, b):
        if j > i:
            rows.append((o[i], h[i:j].max(), l[i:j].min(), c[j - 1], j - i))
        else:
            rows.append((np.nan,) * 4 + (0,))
    return pd.DataFrame(rows, columns=["open", "high", "low", "close", "n"])


def grid(**axes) -> list[dict]:
    keys = list(axes)
    return [dict(zip(keys, vals)) for vals in itertools.product(*(axes[k] for k in keys))]


def run_grid(
    hyp_id: str,
    symbol: str,
    period: str,
    bars: pd.DataFrame,
    signal_fn: Callable[..., pd.DataFrame],
    configs: list[dict],
    spread_mults=(1.0, 1.5),
    registry: TrialRegistry | None = None,
) -> tuple[pd.DataFrame, dict]:
    """Backtest every config; returns (results table, {(config_key, mult): trades})."""
    registry = registry or TrialRegistry()
    rows, trades_out = [], {}
    for cfg in configs:
        sig = signal_fn(bars, symbol=symbol, **cfg)
        key = ",".join(f"{k}={v}" for k, v in cfg.items())
        for m in spread_mults:
            t = run_backtest(bars, sig, cost_model(symbol, m), symbol=symbol)
            s = summarize(t)
            trades_out[(key, m)] = t
            row = {"config": key, "spread_mult": m, **s}
            rows.append(row)
            if m == 1.0 and s.get("n", 0) > 1:
                r = t["R"].to_numpy()
                registry.log(hyp_id, {"symbol": symbol, "period": period, **cfg},
                             n_obs=len(r), sharpe=float(r.mean() / r.std(ddof=1)))
    return pd.DataFrame(rows), trades_out
