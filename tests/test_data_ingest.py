import io
import lzma
import struct

import numpy as np
import pandas as pd
import pytest

from pfbot.data import dukascopy as dk
from pfbot.data.csv_import import import_csv
from pfbot.data.schema import validate_bars
from pfbot.data.store import load_bars, save_bars

HOUR = pd.Timestamp("2024-03-05 14:00", tz="UTC")


def make_bi5(records, fmt=lzma.FORMAT_ALONE):
    raw = b"".join(struct.pack(">IIIff", *r) for r in records)
    return lzma.compress(raw, format=fmt)


# (ms, ask, bid, ask_vol, bid_vol) with point factor 1e3 -> e.g. 18001.000
RECORDS = [
    (1_000, 18_001_000, 17_999_000, 1.0, 2.0),    # 14:00 mid 18000.0 spread 2.0
    (30_000, 18_005_000, 18_001_000, 0.5, 0.5),   # 14:00 mid 18003.0 spread 4.0
    (59_999, 17_999_000, 17_997_000, 1.0, 1.0),   # 14:00 mid 17998.0 spread 2.0
    (61_000, 18_010_000, 18_008_000, 3.0, 0.0),   # 14:01 mid 18009.0 spread 2.0
    (3_599_000, 18_020_000, 18_016_000, 1.0, 1.0),  # 14:59 mid 18018.0 spread 4.0
]


def test_decode_and_aggregate():
    ticks = dk.decode_bi5(make_bi5(RECORDS), HOUR, 1e3)
    assert len(ticks) == 5
    assert ticks.index[0] == HOUR + pd.Timedelta(seconds=1)
    assert ticks["ask"].iloc[0] == pytest.approx(18001.0)

    bars = dk.ticks_to_m1(ticks)
    validate_bars(bars)
    assert list(bars.index) == [HOUR, HOUR + pd.Timedelta(minutes=1), HOUR + pd.Timedelta(minutes=59)]
    b0 = bars.iloc[0]
    assert (b0.open, b0.high, b0.low, b0.close) == pytest.approx((18000.0, 18003.0, 17998.0, 17998.0))
    assert b0.spread == pytest.approx((2 + 4 + 2) / 3)
    assert b0.volume == pytest.approx(6.0)
    assert bars.iloc[1].open == bars.iloc[1].close == pytest.approx(18009.0)
    assert bars.iloc[2].spread == pytest.approx(4.0)
    dk.sanity_check_price_level("US100", bars)


def test_decode_auto_fallback_and_empty():
    ticks = dk.decode_bi5(make_bi5(RECORDS, fmt=lzma.FORMAT_XZ), HOUR, 1e3)
    assert len(ticks) == 5
    assert dk.decode_bi5(b"", HOUR, 1e3).empty
    assert dk.ticks_to_m1(dk.decode_bi5(b"", HOUR, 1e3)).empty


def test_sanity_check_catches_wrong_factor():
    bars = dk.ticks_to_m1(dk.decode_bi5(make_bi5(RECORDS), HOUR, 1e5))  # 100x too small
    with pytest.raises(ValueError, match="point factor"):
        dk.sanity_check_price_level("US100", bars)


def test_url_and_symbols():
    assert dk._hour_url("EURUSD", pd.Timestamp("2024-01-09 07:00", tz="UTC")).endswith(
        "/EURUSD/2024/00/09/07h_ticks.bi5")
    assert set(dk.SYMBOLS) == set(dk.PRICE_RANGES)


def test_download_m1_from_cache(tmp_path, monkeypatch):
    """download_m1 works offline when the raw cache is already populated."""
    code, _ = dk.SYMBOLS["US100"]
    day = pd.Timestamp("2024-03-05", tz="UTC")
    for h in range(24):
        hs = day + pd.Timedelta(hours=h)
        p = dk._cache_path(tmp_path / "raw" / "dukascopy", code, hs)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(make_bi5(RECORDS) if h == 14 else b"")
    monkeypatch.setattr(dk._Fetcher, "_session", lambda self: pytest.fail("network used"))
    df = dk.download_m1("US100", "2024-03-05", "2024-03-05", out_dir=tmp_path)
    assert len(df) == 3
    stored = load_bars("US100", root=tmp_path / "bars")
    pd.testing.assert_frame_equal(stored, df, check_freq=False)


def _bars(start, n):
    idx = pd.date_range(start, periods=n, freq="1min", tz="UTC", name="time")
    close = 100 + np.cumsum(np.random.default_rng(0).normal(size=n))
    df = pd.DataFrame({"open": close, "close": close, "spread": 0.1, "volume": 1.0}, index=idx)
    df["high"] = close + 0.5
    df["low"] = close - 0.5
    return df[["open", "high", "low", "close", "spread", "volume"]]


def test_store_roundtrip(tmp_path):
    df = _bars("2024-01-31 23:50", 30)  # spans Jan/Feb
    files = save_bars(df, "US100", "1min", root=tmp_path)
    assert sorted(f.name for f in files) == ["2024-01.parquet", "2024-02.parquet"]
    out = load_bars("US100", root=tmp_path)
    pd.testing.assert_frame_equal(out, df, check_freq=False)
    part = load_bars("US100", start="2024-02-01", end="2024-02-01 00:05", root=tmp_path)
    assert len(part) == 6 and part.index[0] == pd.Timestamp("2024-02-01", tz="UTC")
    # merge: overlapping save replaces rows, keeps others
    upd = df.iloc[5:10].copy()
    upd[["open", "high", "low", "close"]] += 1
    save_bars(upd, "US100", "1min", root=tmp_path)
    out2 = load_bars("US100", root=tmp_path)
    assert len(out2) == 30
    assert out2["close"].iloc[7] == pytest.approx(df["close"].iloc[7] + 1)


def test_csv_dukascopy_node():
    text = ("timestamp,open,high,low,close,volume\n"
            "1704189600000,16800.5,16802.0,16799.0,16801.0,12.5\n"
            "1704189660000,16801.0,16803.0,16800.0,16802.5,8\n")
    df = import_csv(io.StringIO(text), "dukascopy-node")
    assert df.index[0] == pd.Timestamp("2024-01-02 10:00", tz="UTC")
    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    assert df["close"].iloc[1] == 16802.5


def test_csv_mt5_timezone():
    text = ("<DATE>\t<TIME>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\t<TICKVOL>\t<VOL>\t<SPREAD>\n"
            "2024.01.02\t12:00:00\t16800.5\t16802.0\t16799.0\t16801.0\t40\t0\t15\n"   # winter GMT+2
            "2024.07.02\t12:00:00\t20000.0\t20001.0\t19999.0\t20000.5\t30\t0\t10\n")  # summer GMT+3
    df = import_csv(io.StringIO(text), "mt5", point=0.1)
    assert df.index[0] == pd.Timestamp("2024-01-02 10:00", tz="UTC")
    assert df.index[1] == pd.Timestamp("2024-07-02 09:00", tz="UTC")
    assert df["spread"].iloc[0] == pytest.approx(1.5)
    assert df["volume"].iloc[1] == 30
    # comma separated, no point -> spread dropped
    df2 = import_csv(io.StringIO(text.replace("\t", ",")), "mt5")
    assert "spread" not in df2.columns and len(df2) == 2
