"""Dukascopy daily M1 candle files -> canonical M1 bars (24x fewer requests than ticks).

Feed URL: {BASE_URL}/{CODE}/{YYYY}/{MM0}/{DD}/{BID|ASK}_candles_min_1.bi5
Each file is LZMA compressed and holds 24-byte big-endian records:
uint32 seconds-from-day-start (UTC), uint32 open, close, low, high, float32 volume.
Minutes with zero volume are Dukascopy's flat fill for a closed market and are dropped.

The feed rate-limits hard (HTTP 429), so we download BID candles for every day and
ASK candles only for a sample of days. The spread is estimated per month and
30-minute UTC bucket from the sampled days (median ask-bid), and mid = bid + spread/2.
The spread is therefore an estimate, not the exact per-minute spread.

CLI: python -m pfbot.data.dukascopy_candles US100:2018-2025 US500:2018-2025 ...
"""
from __future__ import annotations

import argparse
import logging
import lzma
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from pfbot.data.dukascopy import BASE_URL, SYMBOLS, sanity_check_price_level
from pfbot.data.schema import validate_bars
from pfbot.data.store import save_bars

log = logging.getLogger(__name__)

_CANDLE_DTYPE = np.dtype([("sec", ">u4"), ("open", ">u4"), ("close", ">u4"),
                          ("low", ">u4"), ("high", ">u4"), ("volume", ">f4")])


def decode_candles(payload: bytes, day: pd.Timestamp, point: float) -> pd.DataFrame:
    """Decode one day file into OHLCV (UTC index), dropping zero-volume filler minutes."""
    cols = ["open", "high", "low", "close", "volume"]
    if not payload:
        return pd.DataFrame(columns=cols, dtype=float, index=pd.DatetimeIndex([], tz="UTC", name="time"))
    try:
        raw = lzma.decompress(payload, format=lzma.FORMAT_ALONE)
    except lzma.LZMAError:
        raw = lzma.decompress(payload, format=lzma.FORMAT_AUTO)
    rec = np.frombuffer(raw, dtype=_CANDLE_DTYPE)
    rec = rec[rec["volume"] > 0]
    idx = pd.DatetimeIndex(pd.Timestamp(day, tz="UTC") + pd.to_timedelta(rec["sec"].astype("int64"), unit="s"),
                           name="time")
    df = pd.DataFrame({c: rec[c].astype(float) / point for c in ("open", "high", "low", "close")}, index=idx)
    df["volume"] = rec["volume"].astype(float)
    return df[cols]


class PacedFetcher:
    """Single-threaded fetcher that backs off on 429s and survives dropped tunnels."""

    def __init__(self, raw_root: Path, max_attempts: int = 12):
        self.raw_root = Path(raw_root)
        self.max_attempts = max_attempts
        self.session = requests.Session()
        self.stats = {"ok": 0, "cached": 0, "empty": 0, "429": 0, "errors": 0}

    def path(self, code: str, side: str, day: pd.Timestamp) -> Path:
        return self.raw_root / code / side / f"{day.year}" / f"{day.month - 1:02d}" / f"{day.day:02d}.bi5"

    def get(self, code: str, side: str, day: pd.Timestamp) -> bytes:
        p = self.path(code, side, day)
        if p.exists():
            self.stats["cached"] += 1
            return p.read_bytes()
        url = f"{BASE_URL}/{code}/{day.year}/{day.month - 1:02d}/{day.day:02d}/{side}_candles_min_1.bi5"
        wait = 1.0
        for _ in range(self.max_attempts):
            try:
                r = self.session.get(url, timeout=30)
            except requests.RequestException:
                self.stats["errors"] += 1
                self.session = requests.Session()
                time.sleep(wait)
                wait = min(wait * 2, 60)
                continue
            if r.status_code == 200:
                data = r.content
                self.stats["ok"] += 1
            elif r.status_code == 404:
                data = b""
                self.stats["empty"] += 1
            elif r.status_code in (403, 407):
                raise RuntimeError(f"HTTP {r.status_code} for {url}: blocked by network policy")
            else:  # 429 / 5xx
                self.stats["429"] += 1
                time.sleep(wait)
                wait = min(wait * 2, 60)
                continue
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
            return data
        raise RuntimeError(f"giving up on {url}")


def spread_profile(samples: pd.Series) -> pd.Series:
    """Median spread per 30-minute UTC bucket (minutes since midnight)."""
    bucket = samples.index.hour * 60 + (samples.index.minute // 30) * 30
    return samples.groupby(bucket).median()


def build_month(fetcher: PacedFetcher, symbol: str, month: pd.Timestamp, ask_every: int = 5) -> pd.DataFrame:
    code, point = SYMBOLS[symbol]
    days = pd.date_range(month, month + pd.offsets.MonthEnd(0), freq="D")
    days = [d for d in days if d.dayofweek != 5 and d < pd.Timestamp.now().normalize()]
    bids, spreads = [], []
    for i, d in enumerate(days):
        bid = decode_candles(fetcher.get(code, "BID", d), d, point)
        if bid.empty:
            continue
        bids.append(bid)
        if d.dayofyear % ask_every == 0 or i == len(days) - 1 and not spreads:
            ask = decode_candles(fetcher.get(code, "ASK", d), d, point)
            both = bid["close"].to_frame("bid").join(ask["close"].rename("ask"), how="inner")
            s = (both["ask"] - both["bid"])
            spreads.append(s[s >= 0])
    if not bids:
        return pd.DataFrame()
    bars = pd.concat(bids).sort_index()
    samples = pd.concat(spreads) if spreads else pd.Series(dtype=float)
    if samples.empty:
        raise RuntimeError(f"{symbol} {month:%Y-%m}: no spread samples")
    prof = spread_profile(samples)
    bucket = bars.index.hour * 60 + (bars.index.minute // 30) * 30
    spr = pd.Series(bucket, index=bars.index).map(prof).fillna(samples.median()).to_numpy()
    for c in ("open", "high", "low", "close"):
        bars[c] = bars[c] + spr / 2
    bars["spread"] = spr
    bars = validate_bars(bars[["open", "high", "low", "close", "spread", "volume"]])
    sanity_check_price_level(symbol, bars)
    return bars


def download(symbol: str, first_year: int, last_year: int, root: str | Path = "marketdata",
             raw_root: str | Path = "data/raw/dukascopy_candles", newest_first: bool = True) -> None:
    fetcher = PacedFetcher(Path(raw_root))
    months = list(pd.date_range(f"{first_year}-01-01", f"{last_year}-12-01", freq="MS"))
    months = [m for m in months if m < pd.Timestamp.now()]
    done_dir = Path(root) / "bars" / symbol / "1min"
    for m in (reversed(months) if newest_first else months):
        target = done_dir / f"{m:%Y-%m}.parquet"
        if target.exists() and m + pd.offsets.MonthEnd(0) < pd.Timestamp.now() - pd.Timedelta(days=2):
            continue
        t0 = time.time()
        bars = build_month(fetcher, symbol, m)
        if bars.empty:
            log.info("%s %s: no data", symbol, f"{m:%Y-%m}")
            continue
        save_bars(bars, symbol, "1min", root=Path(root) / "bars")
        log.info("%s %s: %d bars, median spread %.3g, %.0fs, %s", symbol, f"{m:%Y-%m}", len(bars),
                 bars["spread"].median(), time.time() - t0, fetcher.stats)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("jobs", nargs="+", help="SYMBOL:FIRST-LAST, e.g. US100:2018-2025")
    ap.add_argument("--root", default="marketdata")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    for job in args.jobs:
        sym, years = job.split(":")
        a, b = (int(x) for x in years.split("-"))
        download(sym, a, b, root=args.root)


if __name__ == "__main__":
    main()
