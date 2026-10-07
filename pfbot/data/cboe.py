"""CBOE index history (VIX, VIX3M, ...) for the E1 hypothesis.

Files live in ``data/external/{NAME}_History.csv`` (columns DATE MM/DD/YYYY, OPEN, HIGH, LOW, CLOSE).
The close is the official 16:15 ET value, published after the cash close: a value for date d is only
usable from the next trading day on (handled in ``pfbot.strategies.e1_vix``).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

EXTERNAL_ROOT = Path(__file__).resolve().parents[2] / "data" / "external"
URL = "https://cdn.cboe.com/api/global/us_indices/daily_prices/{name}_History.csv"
NAMES = ("VIX", "VIX3M")


def csv_path(name: str, root: Path = EXTERNAL_ROOT) -> Path:
    return Path(root) / f"{name}_History.csv"


def load_vix(name: str = "VIX", root: Path = EXTERNAL_ROOT) -> pd.Series:
    """Daily closes of CBOE index ``name`` ("VIX", "VIX3M", ...) indexed by naive, sorted, unique dates."""
    df = pd.read_csv(csv_path(name, root))
    df.columns = [c.strip().upper() for c in df.columns]
    idx = pd.DatetimeIndex(pd.to_datetime(df["DATE"], format="%m/%d/%Y")).normalize()
    s = pd.Series(pd.to_numeric(df["CLOSE"], errors="coerce").to_numpy(float), index=idx, name=name)
    s = s[~s.index.duplicated(keep="last")].sort_index().dropna()
    return s[s > 0]


def download(names=NAMES, root: Path = EXTERNAL_ROOT, timeout: float = 60.0) -> list[Path]:
    """Refresh ``{NAME}_History.csv`` from CBOE (redirects followed). Returns the written paths.

    A download is validated (parsable, has DATE/CLOSE, > 100 rows) before it replaces the old file."""
    import io

    import requests

    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    out = []
    for name in names:
        r = requests.get(URL.format(name=name), allow_redirects=True, timeout=timeout)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        cols = {c.strip().upper() for c in df.columns}
        if not {"DATE", "CLOSE"} <= cols or len(df) < 100:
            raise ValueError(f"unexpected CBOE payload for {name}: columns={list(df.columns)}, rows={len(df)}")
        p = csv_path(name, root)
        tmp = p.with_suffix(".csv.tmp")
        tmp.write_text(r.text, encoding="utf-8")
        tmp.replace(p)
        out.append(p)
    return out


if __name__ == "__main__":
    for p in download():
        print(p)
