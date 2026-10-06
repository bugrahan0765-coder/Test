"""Canonical bar format shared by every module.

A bar frame is a pandas DataFrame with:
- a tz-aware UTC DatetimeIndex named "time", strictly increasing, one row per bar
  (bar open time; missing bars are simply absent, never forward-filled),
- float columns: open, high, low, close (mid prices),
- optional float columns: spread (average ask-bid in price units), volume.
"""
from __future__ import annotations

import pandas as pd

PRICE_COLS = ["open", "high", "low", "close"]
OPTIONAL_COLS = ["spread", "volume"]


def validate_bars(df: pd.DataFrame) -> pd.DataFrame:
    """Raise ValueError if df violates the canonical bar format; return df."""
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("index must be a DatetimeIndex")
    if df.index.tz is None or str(df.index.tz) != "UTC":
        raise ValueError("index must be tz-aware UTC")
    if not df.index.is_monotonic_increasing or df.index.has_duplicates:
        raise ValueError("index must be strictly increasing")
    missing = [c for c in PRICE_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"missing columns: {missing}")
    p = df[PRICE_COLS]
    if p.isna().any().any():
        raise ValueError("NaN prices")
    if (df["high"] < p.max(axis=1) - 1e-12).any() or (df["low"] > p.min(axis=1) + 1e-12).any():
        raise ValueError("high/low inconsistent with open/close")
    return df


def resample_bars(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    """Aggregate bars to a coarser timeframe (e.g. "5min", "1h"), dropping empty bins."""
    agg = {"open": "first", "high": "max", "low": "min", "close": "last"}
    if "spread" in df.columns:
        agg["spread"] = "mean"
    if "volume" in df.columns:
        agg["volume"] = "sum"
    out = df.resample(rule, label="left", closed="left").agg(agg)
    out = out.dropna(subset=["open"])
    out.index.name = "time"
    return out
