"""Illustration for F1: one ambiguous AMD window in 2020 and its 20 analogs from 2015-2019.

Usage: python -m research.plot_f1_example   -> research/reports/F1_example.png
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pfbot.data.schema import resample_bars
from pfbot.data.store import load_bars
from pfbot.features.amd_maze import fit_amd
from pfbot.features.analog import AnalogLibrary, shape_table

H = 12
UP, DOWN, INK, MUTED, SURFACE = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#fcfcfb"


def path(bars, sma, atr, t, window=60):
    i = bars.index.get_loc(t)
    seg = sma[i - window + 1:i + H + 1]
    return (seg - sma[i]) / atr[i]


def main() -> None:
    bars = resample_bars(load_bars("US100", start="2015-01-01", end="2020-12-31 23:59"), "5min")
    meta, X = shape_table(bars)
    sma = bars["close"].rolling(5).mean().to_numpy()
    yrs = meta.index.year
    lib = AnalogLibrary(meta[yrs <= 2019], X[yrs <= 2019])

    # first 2020 query (13:00 NY) whose AMD fit is the ambiguous "same direction M and D" case
    q = meta[(yrs == 2020) & meta["fwd"].notna().to_numpy()]
    q = q[q.index.tz_convert("America/New_York").strftime("%H:%M") == "13:00"]
    for t in q.index:
        i = bars.index.get_loc(t)
        best = fit_amd(bars.iloc[i - 80:i + 1], window=60)[0]
        if best.manip == best.dist and best.dist != "F" and best.consistent:
            break
    m = lib.query(X[meta.index.get_loc(t)], k=20)[0]
    x = np.arange(-59, H + 1)
    fig, ax = plt.subplots(figsize=(10, 5.5), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    atr = _atr(bars)
    for tt, f in zip(m.index, m["fwd"]):
        ax.plot(x, path(bars, sma, atr, tt), color=UP if f > 0 else DOWN, lw=1, alpha=0.55)
    qp = path(bars, sma, atr, t)
    ax.plot(x[:60], qp[:60], color=INK, lw=2.5, label="Şu anki pencere (sorgu)")
    ax.plot(x[59:], qp[59:], color=INK, lw=2, ls="--", label="Sorgunun gerçek devamı")
    ax.plot([], [], color=UP, lw=1.5, label=f"Benzer geçmiş gün, sonra yükseldi ({(m['fwd'] > 0).sum()})")
    ax.plot([], [], color=DOWN, lw=1.5, label=f"Benzer geçmiş gün, sonra düştü ({(m['fwd'] <= 0).sum()})")
    ax.axvline(0, color=MUTED, lw=1)
    ax.text(0.5, ax.get_ylim()[1], " şimdi", color=MUTED, va="top", fontsize=9)
    ax.set_xlabel("M5 mum (0 = şimdi)", color=MUTED)
    ax.set_ylabel("5-SMA, şimdiki değere göre (ATR)", color=MUTED)
    ny = t.tz_convert("America/New_York")
    ax.set_title(f"US100 M5 {ny:%Y-%m-%d %H:%M} NY: AMD {best.name} (belirsiz) ve en benzer 20 geçmiş gün",
                 color=INK, fontsize=11, loc="left")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED)
    ax.grid(axis="y", color="#e6e5e1", lw=0.8)
    ax.legend(frameon=False, loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig("research/reports/F1_example.png", dpi=130, facecolor=SURFACE)
    print(t, best.name, AnalogLibrary.p_up(m), meta.loc[t, "fwd"])


def _atr(bars):
    prev = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - prev).abs(), (bars["low"] - prev).abs()],
                   axis=1).max(axis=1)
    return tr.rolling(14).mean().to_numpy()


if __name__ == "__main__":
    main()
