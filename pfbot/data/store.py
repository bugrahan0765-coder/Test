"""Parquet persistence for canonical bar frames.

Layout: {root}/{symbol}/{timeframe}/{YYYY-MM}.parquet, one file per calendar month (UTC).
Saving merges with any existing month file (new rows win on duplicate timestamps),
so incremental updates are safe.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from pfbot.data.schema import validate_bars


def _month_dir(symbol: str, timeframe: str, root: str | Path) -> Path:
    return Path(root) / symbol / timeframe


def _to_utc(ts) -> pd.Timestamp | None:
    if ts is None:
        return None
    ts = pd.Timestamp(ts)
    return ts.tz_localize("UTC") if ts.tz is None else ts.tz_convert("UTC")


def save_bars(df: pd.DataFrame, symbol: str, timeframe: str = "1min",
              root: str | Path = "data/bars") -> list[Path]:
    """Write bars to monthly parquet files, merging with existing data. Returns written paths."""
    validate_bars(df)
    if df.empty:
        return []
    d = _month_dir(symbol, timeframe, root)
    d.mkdir(parents=True, exist_ok=True)
    written = []
    months = df.index.tz_convert(None).to_period("M")
    for period, part in df.groupby(months):
        path = d / f"{period.strftime('%Y-%m')}.parquet"
        if path.exists():
            old = pd.read_parquet(path)
            part = pd.concat([old[~old.index.isin(part.index)], part]).sort_index()
        part = part.astype("float64")
        part.index.name = "time"
        validate_bars(part)
        tmp = path.with_suffix(".parquet.tmp")
        # float32 + zstd halves the size; rounding is monotonic so OHLC stays consistent.
        part.astype("float32").to_parquet(tmp, engine="pyarrow", compression="zstd")
        tmp.replace(path)  # atomic-ish: never leave a half-written month file
        written.append(path)
    return written


def load_bars(symbol: str, timeframe: str = "1min", start=None, end=None,
              root: str | Path = "data/bars") -> pd.DataFrame:
    """Load bars in [start, end] (inclusive; naive timestamps are treated as UTC)."""
    d = _month_dir(symbol, timeframe, root)
    start, end = _to_utc(start), _to_utc(end)
    files = sorted(d.glob("*.parquet")) if d.exists() else []
    if not files:
        raise FileNotFoundError(f"no bars stored for {symbol}/{timeframe} under {d}")
    lo = start.strftime("%Y-%m") if start is not None else None
    hi = end.strftime("%Y-%m") if end is not None else None
    files = [f for f in files if (lo is None or f.stem >= lo) and (hi is None or f.stem <= hi)]
    if not files:
        cols = ["open", "high", "low", "close"]
        empty = pd.DataFrame(columns=cols, dtype="float64",
                             index=pd.DatetimeIndex([], tz="UTC", name="time"))
        return empty
    df = pd.concat([pd.read_parquet(f) for f in files]).sort_index().astype("float64")
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    else:
        df.index = df.index.tz_convert("UTC")
    df.index.name = "time"
    if start is not None:
        df = df[df.index >= start]
    if end is not None:
        df = df[df.index <= end]
    return validate_bars(df)
