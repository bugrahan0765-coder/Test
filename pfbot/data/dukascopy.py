"""Dukascopy free tick feed -> canonical M1 bars.

Feed URL: https://datafeed.dukascopy.com/datafeed/{CODE}/{YYYY}/{MM0}/{DD}/{HH}h_ticks.bi5
(MM0 = zero-based month). Each file is LZMA ("alone" format) compressed and holds
20-byte big-endian records: uint32 ms-from-hour-start, uint32 ask, uint32 bid,
float32 ask volume, float32 bid volume. Prices are integers / point factor.
A 0-byte file means no ticks in that hour (market closed) and is normal.

Raw .bi5 files are cached under {out_dir}/raw/dukascopy/... so reruns only fetch
what is missing; M1 bars are written month by month via pfbot.data.store.

CLI: python -m pfbot.data.dukascopy --symbol US100 --start 2015-01-01 --end 2025-12-31
"""
from __future__ import annotations

import argparse
import datetime as dt
import logging
import lzma
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from pfbot.data.schema import validate_bars
from pfbot.data.store import save_bars

log = logging.getLogger(__name__)

BASE_URL = "https://datafeed.dukascopy.com/datafeed"

# our name -> (Dukascopy instrument code, point factor: price = raw_int / factor)
#
# !!! The FX factors are well known (1e5 for EURUSD/GBPUSD, 1e3 for JPY pairs).
# !!! The XAUUSD and index-CFD factors (1e3) follow dukascopy-node's instrument
# !!! metadata but MUST be verified against the first real download:
# !!! sanity_check_price_level() is run on every month and raises if the median
# !!! close is off (a wrong factor shows up as a 10x/100x price error).
SYMBOLS: dict[str, tuple[str, float]] = {
    "US100": ("USATECHIDXUSD", 1e3),
    "US500": ("USA500IDXUSD", 1e3),
    "GER40": ("DEUIDXEUR", 1e3),
    "XAUUSD": ("XAUUSD", 1e3),
    "EURUSD": ("EURUSD", 1e5),
    "GBPUSD": ("GBPUSD", 1e5),
    "USDJPY": ("USDJPY", 1e3),
}

# Plausible median-close ranges over 2003..~2026 (deliberately wide; they only
# need to catch point-factor errors, which are powers of ten).
PRICE_RANGES: dict[str, tuple[float, float]] = {
    "US100": (1_000, 50_000),
    "US500": (500, 12_000),
    "GER40": (3_000, 40_000),
    "XAUUSD": (250, 8_000),
    "EURUSD": (0.7, 1.7),
    "GBPUSD": (1.0, 2.2),
    "USDJPY": (70, 200),
    "AUDUSD": (0.5, 1.2),
    "USDCAD": (0.9, 1.6),
    "USDCHF": (0.7, 1.2),
}

_TICK_DTYPE = np.dtype([("ms", ">u4"), ("ask", ">u4"), ("bid", ">u4"),
                        ("ask_vol", ">f4"), ("bid_vol", ">f4")])

NETWORK_HINT = (
    "Cannot reach datafeed.dukascopy.com. If you are in a sandbox/cloud environment, "
    "add 'datafeed.dukascopy.com' to the network allow-list (Network access -> Custom -> "
    "Allowed domains), or download data on your own machine (e.g. `npx dukascopy-node ... -f csv`) "
    "and import it with `python -m pfbot.data.csv_import`."
)


class DukascopyNetworkError(RuntimeError):
    pass


# --------------------------------------------------------------------------- decoding

def decode_bi5(payload: bytes, hour_start: pd.Timestamp, point: float) -> pd.DataFrame:
    """Decode one .bi5 payload into a tick frame (index time UTC; ask, bid, volume)."""
    if not payload:
        return _empty_ticks()
    try:
        raw = lzma.decompress(payload, format=lzma.FORMAT_ALONE)
    except lzma.LZMAError:
        raw = lzma.decompress(payload, format=lzma.FORMAT_AUTO)
    if len(raw) % _TICK_DTYPE.itemsize:
        raise ValueError(f"corrupt bi5 for {hour_start}: {len(raw)} bytes not a multiple of 20")
    rec = np.frombuffer(raw, dtype=_TICK_DTYPE)
    if rec.size == 0:
        return _empty_ticks()
    hour_start = pd.Timestamp(hour_start)
    hour_start = hour_start.tz_localize("UTC") if hour_start.tz is None else hour_start.tz_convert("UTC")
    idx = hour_start + pd.to_timedelta(rec["ms"].astype("int64"), unit="ms")
    return pd.DataFrame(
        {
            "ask": rec["ask"].astype("float64") / point,
            "bid": rec["bid"].astype("float64") / point,
            "volume": rec["ask_vol"].astype("float64") + rec["bid_vol"].astype("float64"),
        },
        index=pd.DatetimeIndex(idx, name="time"),
    )


def _empty_ticks() -> pd.DataFrame:
    return pd.DataFrame({"ask": [], "bid": [], "volume": []}, dtype="float64",
                        index=pd.DatetimeIndex([], tz="UTC", name="time"))


def ticks_to_m1(ticks: pd.DataFrame) -> pd.DataFrame:
    """Aggregate ticks to 1-minute mid bars (+ mean spread, summed volume)."""
    cols = ["open", "high", "low", "close", "spread", "volume"]
    if ticks.empty:
        return pd.DataFrame(columns=cols, dtype="float64",
                            index=pd.DatetimeIndex([], tz="UTC", name="time"))
    ticks = ticks.sort_index(kind="stable")
    mid = (ticks["ask"] + ticks["bid"]) / 2
    key = ticks.index.floor("1min")
    g = pd.DataFrame({"mid": mid, "spread": ticks["ask"] - ticks["bid"],
                      "volume": ticks["volume"]}).groupby(key)
    out = pd.DataFrame({
        "open": g["mid"].first(),
        "high": g["mid"].max(),
        "low": g["mid"].min(),
        "close": g["mid"].last(),
        "spread": g["spread"].mean(),
        "volume": g["volume"].sum(),
    })
    out.index = pd.DatetimeIndex(out.index, name="time").tz_convert("UTC")
    return validate_bars(out.astype("float64"))


def sanity_check_price_level(symbol: str, df: pd.DataFrame) -> None:
    """Raise if the median close is implausible for symbol (catches wrong point factors)."""
    if df.empty:
        return
    lo, hi = PRICE_RANGES[symbol]
    med = float(df["close"].median())
    if not lo <= med <= hi:
        raise ValueError(
            f"{symbol}: median close {med:g} outside plausible range [{lo:g}, {hi:g}] -- "
            f"the point factor in SYMBOLS is probably wrong (currently {SYMBOLS[symbol][1]:g})"
        )


# --------------------------------------------------------------------------- downloading

def _hour_url(code: str, h: pd.Timestamp) -> str:
    return f"{BASE_URL}/{code}/{h.year:04d}/{h.month - 1:02d}/{h.day:02d}/{h.hour:02d}h_ticks.bi5"


def _cache_path(raw_root: Path, code: str, h: pd.Timestamp) -> Path:
    return raw_root / code / f"{h.year:04d}" / f"{h.month - 1:02d}" / f"{h.day:02d}" / f"{h.hour:02d}h_ticks.bi5"


class _Fetcher:
    """Thread-safe HTTP fetcher with retries, exponential backoff and a raw-file cache."""

    def __init__(self, raw_root: Path, retries: int = 5, backoff: float = 1.0, timeout: float = 30.0):
        self.raw_root = raw_root
        self.retries = retries
        self.backoff = backoff
        self.timeout = timeout
        self._local = threading.local()
        # requests honours HTTPS_PROXY and REQUESTS_CA_BUNDLE itself; SSL_CERT_FILE is not,
        # so pass it explicitly when it is the only CA override.
        self.verify: bool | str = os.environ.get("REQUESTS_CA_BUNDLE") or os.environ.get("SSL_CERT_FILE") or True

    def _session(self) -> requests.Session:
        s = getattr(self._local, "s", None)
        if s is None:
            s = requests.Session()
            s.headers["User-Agent"] = "pfbot-research/0.1"
            s.verify = self.verify
            self._local.s = s
        return s

    def get(self, code: str, h: pd.Timestamp, probe: bool = False) -> bytes:
        path = _cache_path(self.raw_root, code, h)
        if path.exists():
            return path.read_bytes()
        url = _hour_url(code, h)
        last_err: Exception | None = None
        for attempt in range(self.retries):
            try:
                r = self._session().get(url, timeout=self.timeout)
            except (requests.exceptions.ProxyError, requests.exceptions.SSLError,
                    requests.exceptions.ConnectionError) as e:
                if probe:
                    raise DukascopyNetworkError(f"{NETWORK_HINT}\n(underlying error: {e})") from e
                last_err = e
            except requests.RequestException as e:
                last_err = e
            else:
                if r.status_code == 200:
                    data = r.content
                    self._store(path, data)
                    return data
                if r.status_code == 404:
                    # No file for this hour: treat as empty. Only cache it for hours well in the
                    # past, since the feed publishes recent hours with some delay.
                    if h < pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=3):
                        self._store(path, b"")
                    return b""
                if r.status_code in (401, 403, 407) and probe:
                    raise DukascopyNetworkError(f"{NETWORK_HINT}\n(HTTP {r.status_code} for {url})")
                last_err = RuntimeError(f"HTTP {r.status_code} for {url}")
            time.sleep(self.backoff * 2 ** attempt)
        raise RuntimeError(f"giving up on {url} after {self.retries} attempts: {last_err}")

    @staticmethod
    def _store(path: Path, data: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + f".{threading.get_ident()}.tmp")
        tmp.write_bytes(data)
        tmp.replace(path)


def _hours(start: pd.Timestamp, end_excl: pd.Timestamp) -> list[pd.Timestamp]:
    hrs = pd.date_range(start, end_excl, freq="1h", inclusive="left")
    # Saturdays (UTC) never have data for these instruments; skip to save requests.
    return [h for h in hrs if h.dayofweek != 5]


def download_m1(symbol: str, start_date, end_date, out_dir: str | Path = "data",
                workers: int = 6) -> pd.DataFrame:
    """Download ticks for [start_date, end_date] (inclusive days, UTC), build M1 bars,
    persist them month by month to {out_dir}/bars and return the combined frame."""
    if symbol not in SYMBOLS:
        raise KeyError(f"unknown symbol {symbol}; known: {sorted(SYMBOLS)}")
    code, point = SYMBOLS[symbol]
    out_dir = Path(out_dir)
    fetcher = _Fetcher(out_dir / "raw" / "dukascopy")

    start = pd.Timestamp(start_date).tz_localize(None).normalize().tz_localize("UTC")
    end_excl = pd.Timestamp(end_date).tz_localize(None).normalize().tz_localize("UTC") + pd.Timedelta(days=1)
    end_excl = min(end_excl, pd.Timestamp.now(tz="UTC").floor("1h"))
    if end_excl <= start:
        raise ValueError("empty date range")

    hours = _hours(start, end_excl)
    if not hours:
        raise ValueError("no trading hours in range")
    # Probe a single uncached hour first so a blocked network fails fast with a clear message.
    uncached = [h for h in hours if not _cache_path(fetcher.raw_root, code, h).exists()]
    if uncached:
        fetcher.get(code, uncached[0], probe=True)

    month_starts = pd.date_range(start.replace(day=1), end_excl, freq="MS")
    frames = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for ms in month_starts:
            me = ms + pd.offsets.MonthBegin(1)
            mh = [h for h in hours if ms <= h < me]
            if not mh:
                continue
            payloads = list(pool.map(lambda h: fetcher.get(code, h), mh))
            ticks = [decode_bi5(p, h, point) for p, h in zip(payloads, mh) if p]
            ticks = [t for t in ticks if not t.empty]
            if not ticks:
                log.info("%s %s: no ticks", symbol, ms.strftime("%Y-%m"))
                continue
            bars = ticks_to_m1(pd.concat(ticks))
            sanity_check_price_level(symbol, bars)
            save_bars(bars, symbol, "1min", root=out_dir / "bars")
            log.info("%s %s: %d bars", symbol, ms.strftime("%Y-%m"), len(bars))
            frames.append(bars)
    if not frames:
        return ticks_to_m1(_empty_ticks())
    return validate_bars(pd.concat(frames).sort_index())


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Download Dukascopy ticks and build M1 parquet bars.")
    ap.add_argument("--symbol", required=True, choices=sorted(SYMBOLS))
    ap.add_argument("--start", required=True, help="YYYY-MM-DD (UTC, inclusive)")
    ap.add_argument("--end", required=True, help="YYYY-MM-DD (UTC, inclusive)")
    ap.add_argument("--out-dir", default="data")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        df = download_m1(args.symbol, args.start, args.end, args.out_dir, workers=args.workers)
    except DukascopyNetworkError as e:
        raise SystemExit(str(e))
    if df.empty:
        print(f"{args.symbol}: no bars")
    else:
        print(f"{args.symbol}: {len(df)} M1 bars {df.index[0]} -> {df.index[-1]}, "
              f"median close {df['close'].median():g}")


if __name__ == "__main__":
    main()
