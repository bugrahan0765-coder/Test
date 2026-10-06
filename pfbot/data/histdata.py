"""HistData.com free M1 bars -> canonical bars (one request per symbol-year).

HistData's documentation says "EST without daylight saving", but the timestamps are New York wall-clock
time WITH daylight saving (verified 2026-10-07: the 09:30 ET cash-open volatility spike and the 08:30 ET
data-release spike sit at the same stamped minute in winter and summer; Dukascopy cross-checks match only
under this reading). We therefore localise to America/New_York and convert to UTC; the repeated hour at the
autumn transition is dropped.
There is no spread information, so a conservative constant spread per symbol is
assumed (SPREAD below; calibrate against FTMO MT5 data later) and
mid = bid + spread / 2.

CLI: python -m pfbot.data.histdata US100:2015-2025 US500:2015-2025 GER40:2015-2025 XAUUSD:2015-2025
"""
from __future__ import annotations

import argparse
import io
import logging
import re
import time
import zipfile
from pathlib import Path

import pandas as pd
import requests

from pfbot.data.dukascopy import sanity_check_price_level
from pfbot.data.schema import validate_bars
from pfbot.data.store import save_bars

log = logging.getLogger(__name__)

PAIRS = {"US100": "NSXUSD", "US500": "SPXUSD", "GER40": "GRXEUR", "XAUUSD": "XAUUSD",
         "EURUSD": "EURUSD", "GBPUSD": "GBPUSD", "USDJPY": "USDJPY", "AUDUSD": "AUDUSD",
         "USDCAD": "USDCAD", "USDCHF": "USDCHF"}

# Assumed full spread in price units (conservative vs. typical FTMO quotes; Dukascopy
# US100 samples showed medians of 1.2-2.9 points).
SPREAD = {"US100": 2.0, "US500": 0.6, "GER40": 1.5, "XAUUSD": 0.30,
          "EURUSD": 0.00006, "GBPUSD": 0.00009, "USDJPY": 0.008, "AUDUSD": 0.00007,
          "USDCAD": 0.00009, "USDCHF": 0.00009}

PAGE = "https://www.histdata.com/download-free-forex-historical-data/?/ascii/1-minute-bar-quotes/{pair}/{year}"
GET = "https://www.histdata.com/get.php"


def fetch_year_zip(pair: str, year: int, month: int | None = None, retries: int = 5) -> bytes:
    """Download the yearly (or, for the current year, monthly) ASCII M1 zip."""
    page = PAGE.format(pair=pair.lower(), year=year) + (f"/{month}" if month else "")
    for attempt in range(retries):
        try:
            s = requests.Session()
            html = s.get(page, timeout=60).text
            tk = re.search(r'id="tk" value="([^"]+)"', html).group(1)
            datemonth = f"{year}{month:02d}" if month else str(year)
            r = s.post(GET, timeout=300, headers={"Referer": page}, data={
                "tk": tk, "date": str(year), "datemonth": datemonth,
                "platform": "ASCII", "timeframe": "M1", "fxpair": pair})
            if r.status_code == 200 and r.content[:2] == b"PK":
                return r.content
            log.warning("%s %s: HTTP %s (%d bytes)", pair, datemonth, r.status_code, len(r.content))
        except (requests.RequestException, AttributeError) as e:
            log.warning("%s %s: %s", pair, year, e)
        time.sleep(5 * 2 ** attempt)
    raise RuntimeError(f"could not download {pair} {year} {month or ''}")


def parse_zip(payload: bytes, symbol: str) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        name = next(n for n in z.namelist() if n.endswith(".csv"))
        raw = pd.read_csv(z.open(name), sep=";", header=None,
                          names=["dt", "open", "high", "low", "close", "volume"])
    local = pd.to_datetime(raw["dt"], format="%Y%m%d %H%M%S")
    t = pd.DatetimeIndex(local).tz_localize("America/New_York", ambiguous="NaT", nonexistent="NaT")
    keep = ~t.isna()
    raw, t = raw[keep], t[keep].tz_convert("UTC").tz_localize(None)
    spread = SPREAD[symbol]
    df = pd.DataFrame({c: raw[c].to_numpy(float) + spread / 2 for c in ("open", "high", "low", "close")},
                      index=pd.DatetimeIndex(t, name="time").tz_localize("UTC"))
    df["spread"] = spread
    df = df[~df.index.duplicated(keep="last")].sort_index()
    # repair rare inconsistent rows rather than dropping the minute
    df["high"] = df[["open", "high", "low", "close"]].max(axis=1)
    df["low"] = df[["open", "high", "low", "close"]].min(axis=1)
    return validate_bars(df)


def download(symbol: str, first_year: int, last_year: int, root: str | Path = "data") -> None:
    pair = PAIRS[symbol]
    out = Path(root) / "bars" / symbol / "1min"
    now = pd.Timestamp.now()
    for year in range(first_year, last_year + 1):
        if year < now.year:
            if out.exists() and len(list(out.glob(f"{year}-*.parquet"))) >= 12:
                continue
            chunks = [fetch_year_zip(pair, year)]
        else:  # current year is published month by month
            chunks = [fetch_year_zip(pair, year, m) for m in range(1, now.month)]
        for payload in chunks:
            bars = parse_zip(payload, symbol)
            sanity_check_price_level(symbol, bars)
            save_bars(bars, symbol, "1min", root=Path(root) / "bars")
            log.info("%s %d: %d bars %s -> %s", symbol, year, len(bars), bars.index[0], bars.index[-1])


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("jobs", nargs="+", help="SYMBOL:FIRST-LAST")
    ap.add_argument("--root", default="data")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    for job in args.jobs:
        sym, years = job.split(":")
        a, b = (int(x) for x in years.split("-"))
        download(sym, a, b, root=args.root)


if __name__ == "__main__":
    main()
