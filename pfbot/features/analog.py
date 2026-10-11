"""Analog (nearest-neighbour) pattern memory on the 5-SMA path. Hypothesis F1.

A "shape" at bar t is the 5-SMA of close over the last ``window`` bars, minus
its value at t, divided by ATR at t. The library stores the shapes of many
past bars together with what followed them (forward return over ``horizon``
bars). A query shape is compared with every library shape (Euclidean
distance); the closest window of each library day is kept and the k nearest
days are the analogs. P(up) = share of analogs whose forward return was > 0.

All features at t use bars up to and including t only; the label uses bars
t+1..t+horizon and is only ever read from the library (past data).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

__all__ = ["shape_table", "AnalogLibrary"]

NY = "America/New_York"


def shape_table(
    bars: pd.DataFrame,
    window: int = 60,
    horizon: int = 12,
    sma_len: int = 5,
    atr_len: int = 14,
    ny_start: str = "10:30",
    ny_end: str = "15:00",
    bar: str = "5min",
) -> tuple[pd.DataFrame, np.ndarray]:
    """Shapes and labels for every bar whose New York time is in [ny_start, ny_end].

    Returns (meta, X): meta has index time (UTC) and columns day (NY date), close,
    atr, fwd (forward return, NaN if the next ``horizon`` bars are not contiguous);
    X is float32 (n, window).
    """
    close = bars["close"].astype(float)
    sma = close.rolling(sma_len).mean().to_numpy()
    prev = close.shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - prev).abs(),
                    (bars["low"] - prev).abs()], axis=1).max(axis=1)
    atr = tr.rolling(atr_len).mean().to_numpy()
    n = len(bars)
    first = window - 1 + sma_len - 1
    if n <= first:
        raise ValueError("not enough bars")

    idx = np.arange(first, n)
    ny = bars.index[idx].tz_convert(NY)
    hhmm = ny.strftime("%H:%M")
    keep = (hhmm >= ny_start) & (hhmm <= ny_end) & np.isfinite(atr[idx]) & (atr[idx] > 0)
    idx = idx[keep]

    win = sliding_window_view(sma, window)  # win[j] = sma[j : j + window]
    X = (win[idx - window + 1] - sma[idx, None]) / atr[idx, None]

    fwd = np.full(len(idx), np.nan)
    ok = idx + horizon < n
    j = idx[ok]
    gap_ok = (bars.index[j + horizon] - bars.index[j]) == pd.Timedelta(bar) * horizon
    f = close.to_numpy()[j + horizon] / close.to_numpy()[j] - 1.0
    fwd[np.flatnonzero(ok)] = np.where(gap_ok, f, np.nan)

    meta = pd.DataFrame(
        {"day": ny[keep].date, "close": close.to_numpy()[idx], "atr": atr[idx], "fwd": fwd},
        index=bars.index[idx],
    )
    good = np.isfinite(X).all(axis=1)
    return meta[good], X[good].astype(np.float32)


@dataclass
class AnalogLibrary:
    meta: pd.DataFrame
    X: np.ndarray

    def __post_init__(self):
        lab = np.isfinite(self.meta["fwd"].to_numpy())
        self.meta, self.X = self.meta[lab], self.X[lab]
        self._sq = (self.X.astype(np.float64) ** 2).sum(axis=1)
        self._day = pd.factorize(self.meta["day"])[0]

    def __len__(self) -> int:
        return len(self.X)

    @property
    def n_days(self) -> int:
        return int(self._day.max()) + 1 if len(self._day) else 0

    def query(self, Q: np.ndarray, k: int = 20, pool: int = 3000) -> list[pd.DataFrame]:
        """k nearest analogs (at most one per library day) for each row of Q."""
        Q = np.atleast_2d(Q).astype(np.float64)
        out = []
        for s in range(0, len(Q), 256):
            q = Q[s:s + 256]
            d2 = (q ** 2).sum(1)[:, None] + self._sq[None, :] - 2.0 * q @ self.X.T.astype(np.float64)
            m = min(pool, d2.shape[1] - 1)
            cand = np.argpartition(d2, m, axis=1)[:, :m + 1]
            for r in range(len(q)):
                c = cand[r][np.argsort(d2[r, cand[r]])]
                _, first = np.unique(self._day[c], return_index=True)
                c = c[np.sort(first)][:k]
                res = self.meta.iloc[c].copy()
                res["dist"] = np.sqrt(np.maximum(d2[r, c], 0.0))
                out.append(res)
        return out

    @staticmethod
    def p_up(matches: pd.DataFrame) -> float:
        return float((matches["fwd"] > 0).mean())
