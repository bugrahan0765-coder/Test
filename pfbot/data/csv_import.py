"""Import user-supplied bar CSVs into the canonical format / parquet store.

Supported formats:
- "dukascopy-node": output of `npx dukascopy-node -i <instr> -from .. -to .. -t m1 -f csv`,
  columns timestamp,open,high,low,close[,volume]; timestamp is epoch ms (UTC) or an
  ISO date string (with -df/date-format options).
- "mt5": MetaTrader 5 history export, tab- or comma-separated, header
  <DATE> <TIME> <OPEN> <HIGH> <LOW> <CLOSE> <TICKVOL> <VOL> <SPREAD>, timestamps in the
  broker's server time zone (`source_tz`). Most MT5 brokers run GMT+2 / GMT+3 with DST,
  approximated here by "Europe/Athens". NOTE: brokers often switch DST on the *US*
  schedule, so for a few weeks per year the offset may be off by one hour -- verify
  against a known session open if it matters. MT5 SPREAD is in points; pass `point`
  (price per point) to convert it, otherwise spread is dropped.

CLI: python -m pfbot.data.csv_import path.csv --symbol US100 --format dukascopy-node
"""
from __future__ import annotations

import argparse
import logging

import pandas as pd

from pfbot.data.schema import validate_bars
from pfbot.data.store import save_bars

log = logging.getLogger(__name__)

FORMATS = ("dukascopy-node", "mt5")


def _finish(df: pd.DataFrame) -> pd.DataFrame:
    df.index.name = "time"
    df = df.astype("float64")
    df = df.dropna(subset=["open", "high", "low", "close"])
    df = df[~df.index.duplicated(keep="last")].sort_index()
    return validate_bars(df)


def read_dukascopy_node(src) -> pd.DataFrame:
    raw = pd.read_csv(src)
    raw.columns = [c.strip().lower() for c in raw.columns]
    ts = raw["timestamp"]
    if pd.api.types.is_numeric_dtype(ts):
        idx = pd.to_datetime(ts.astype("int64"), unit="ms", utc=True)
    else:
        idx = pd.to_datetime(ts, utc=True)
    cols = [c for c in ["open", "high", "low", "close", "volume"] if c in raw.columns]
    df = raw[cols].set_axis(pd.DatetimeIndex(idx), axis=0)
    return _finish(df)


def read_mt5(src, source_tz: str = "Europe/Athens", point: float | None = None) -> pd.DataFrame:
    raw = pd.read_csv(src, sep=None, engine="python")  # sniff tab vs comma
    raw.columns = [c.strip().strip("<>").lower() for c in raw.columns]
    local = pd.to_datetime(raw["date"].astype(str) + " " + raw["time"].astype(str),
                           format="%Y.%m.%d %H:%M:%S")
    try:
        idx = pd.DatetimeIndex(local).tz_localize(source_tz, ambiguous="infer", nonexistent="NaT")
    except Exception:  # cannot infer the repeated DST hour -> drop it
        idx = pd.DatetimeIndex(local).tz_localize(source_tz, ambiguous="NaT", nonexistent="NaT")
    df = pd.DataFrame({c: raw[c].to_numpy() for c in ["open", "high", "low", "close"]},
                      index=idx.tz_convert("UTC"))
    vol = raw["tickvol"] if "tickvol" in raw.columns else raw.get("vol")
    if vol is not None:
        df["volume"] = vol.to_numpy()
    if point is not None and "spread" in raw.columns:
        df["spread"] = raw["spread"].to_numpy() * point
    bad = df.index.isna()
    if bad.any():
        log.warning("dropping %d rows with ambiguous/nonexistent local times", int(bad.sum()))
        df = df[~bad]
    return _finish(df)


def import_csv(path, fmt: str, source_tz: str = "Europe/Athens",
               point: float | None = None) -> pd.DataFrame:
    """Read a CSV (path or text buffer) in one of FORMATS and return validated bars."""
    if fmt == "dukascopy-node":
        return read_dukascopy_node(path)
    if fmt == "mt5":
        return read_mt5(path, source_tz=source_tz, point=point)
    raise ValueError(f"unknown format {fmt!r}; expected one of {FORMATS}")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Import a bar CSV into the parquet store.")
    ap.add_argument("path")
    ap.add_argument("--symbol", required=True)
    ap.add_argument("--format", required=True, choices=FORMATS)
    ap.add_argument("--timeframe", default="1min")
    ap.add_argument("--source-tz", default="Europe/Athens", help="MT5 server time zone")
    ap.add_argument("--point", type=float, default=None, help="MT5: price per spread point")
    ap.add_argument("--root", default="data/bars")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    df = import_csv(args.path, args.format, source_tz=args.source_tz, point=args.point)
    files = save_bars(df, args.symbol, args.timeframe, root=args.root)
    print(f"{args.symbol}: imported {len(df)} bars into {len(files)} monthly files under {args.root}")


if __name__ == "__main__":
    main()
