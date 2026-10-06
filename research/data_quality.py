"""Data quality report for the M1 bar store -> research/reports/data_quality.md"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from pfbot.data.store import load_bars
from pfbot.research.harness import DATA_ROOT, SESSIONS, local_times, session_dates

OUT = Path(__file__).parent / "reports" / "data_quality.md"
SYMBOLS = ["US100", "US500", "GER40", "XAUUSD"]


def session_coverage(bars: pd.DataFrame, symbol: str) -> pd.DataFrame:
    sess = SESSIONS[symbol]
    local = bars.index.tz_convert(sess.tz)
    mins = local.hour * 60 + local.minute
    o = int(sess.open[:2]) * 60 + int(sess.open[3:])
    c = int(sess.close[:2]) * 60 + int(sess.close[3:])
    inside = (mins >= o) & (mins < c) & (local.dayofweek < 5)
    day = local[inside].normalize()
    per_day = pd.Series(1, index=day).groupby(level=0).size()
    full = c - o
    return pd.DataFrame({"minutes": per_day, "coverage": per_day / full})


def alignment_check(symbol: str) -> str:
    """Compare against Dukascopy bars (if any) to verify the timezone conversion."""
    d = DATA_ROOT.parent / "bars_dukascopy"
    try:
        ref = load_bars(symbol, root=d)
    except FileNotFoundError:
        return "no Dukascopy reference"
    hd = load_bars(symbol, start=ref.index[0], end=ref.index[-1])
    r1 = np.log(hd["close"]).diff()
    r2 = np.log(ref["close"]).diff()
    best = []
    for lag in range(-90, 91, 30):
        x = r1.shift(lag, freq="1min")
        j = pd.concat([x, r2], axis=1, join="inner").dropna()
        best.append((lag, j.corr().iloc[0, 1], len(j)))
    lag, corr, n = max(best, key=lambda t: t[1])
    j = pd.concat([hd["close"], ref["close"]], axis=1, join="inner").dropna()
    diff = (j.iloc[:, 0] - j.iloc[:, 1]).median()
    return (f"best lag {lag} min (corr of 1-min returns {corr:.3f}, n={n}); "
            f"median HistData - Dukascopy mid = {diff:.2f}")


def main() -> None:
    lines = ["# Data quality report", "", f"Source: HistData M1 (bid + assumed spread/2), store `{DATA_ROOT}`.", ""]
    for sym in SYMBOLS:
        bars = load_bars(sym, root=DATA_ROOT)
        lines += [f"## {sym}", ""]
        cov = session_coverage(bars, sym)
        open_days = session_dates(bars, SESSIONS[sym])
        yr = pd.DataFrame({
            "bars": bars.groupby(bars.index.year).size(),
            "median_close": bars["close"].groupby(bars.index.year).median().round(1),
        })
        cy = cov.groupby(cov.index.year)
        yr["session_days"] = cy.size()
        yr["median_session_coverage"] = cy["coverage"].median().round(3)
        yr["days_cov<90%"] = cy["coverage"].apply(lambda s: int((s < 0.9).sum()))
        yr["days_with_open_bar"] = pd.Series(1, index=open_days).groupby(open_days.year).size()
        lines += [yr.to_markdown(), ""]
        # largest intra-session gaps
        sess = SESSIONS[sym]
        local = bars.index.tz_convert(sess.tz)
        gaps = pd.Series(bars.index[1:] - bars.index[:-1], index=bars.index[1:])
        mins = local[1:].hour * 60 + local[1:].minute
        o = int(sess.open[:2]) * 60 + int(sess.open[3:])
        c = int(sess.close[:2]) * 60 + int(sess.close[3:])
        g = gaps[(mins > o) & (mins < c) & (gaps > pd.Timedelta("5min")) & (gaps < pd.Timedelta("12h"))]
        lines += [f"Intra-session gaps > 5 min: {len(g)} (largest: "
                  + ", ".join(f"{t:%Y-%m-%d %H:%M} {v}" for t, v in g.nlargest(3).items()) + ")", ""]
        r = np.log(bars["close"]).diff().abs()
        lines += [f"1-min |return| > 2%: {int((r > 0.02).sum())} bars", ""]
        lines += [f"Timezone check vs Dukascopy: {alignment_check(sym)}", ""]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
