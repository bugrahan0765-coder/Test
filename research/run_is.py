"""Run the pre-registered in-sample grids for A1 and A2 -> research/reports/<hyp>_IS.md

Usage: python -m research.run_is A1 A2
"""
from __future__ import annotations

import sys
import time
from functools import lru_cache
from pathlib import Path

import pandas as pd

import pfbot.strategies.a1_intraday_momentum as a1
import pfbot.strategies.a2_opening_range as a2
import pfbot.strategies.b1_turn_of_month as b1
import pfbot.strategies.b2_overnight_drift as b2
import pfbot.strategies.b3_tsmom as b3
from pfbot.features import volatility
from pfbot.research.harness import SESSIONS, load_period, run_grid

REPORTS = Path(__file__).parent / "reports"
SYMBOLS = ["US100", "US500"]


def _cached_vol():
    """Memoise expected_bar_vol per (bars object, tz): it is the slow part of each signal call."""
    orig = volatility.expected_bar_vol
    cache = {}

    def wrapped(bars, *args, **kw):
        key = (id(bars), args, tuple(sorted(kw.items())))
        if key not in cache:
            cache[key] = orig(bars, *args, **kw)
        return cache[key]

    a1.expected_bar_vol = wrapped
    a2.expected_bar_vol = wrapped


HYPS = {
    "A1": (a1.signals, a1.CONFIGS),
    "A2": (a2.signals, a2.CONFIGS),
    "B1": (b1.signals, b1.CONFIGS),
    "B2": (b2.signals, b2.CONFIGS),
    "B3": (b3.signals, b3.CONFIGS),
}
HYP_SYMBOLS = {"B3": ["US100", "US500", "XAUUSD"]}

COLS = ["config", "spread_mult", "n", "win_rate", "avg_R", "t_stat", "profit_factor", "total_R", "worst_mae_R"]


def main(hyps: list[str]) -> None:
    _cached_vol()
    bars = {s: load_period(s, "IS") for s in SYMBOLS + ["XAUUSD"]}
    for h in hyps:
        fn, configs = HYPS[h]
        parts = [f"# {h} in-sample results (2015-2020, excluded months removed, cost model v2)", ""]
        allres = []
        for s in HYP_SYMBOLS.get(h, SYMBOLS):
            t0 = time.time()
            res, _ = run_grid(h + "_v2", s, "IS", bars[s], fn, configs, spread_mults=(1.0, 1.5))
            res.insert(0, "symbol", s)
            allres.append(res)
            parts += [f"## {s} ({time.time() - t0:.0f}s)", "", res[COLS].round(3).to_markdown(index=False), ""]
        df = pd.concat(allres)
        base = df[df.spread_mult == 1.0].pivot(index="config", columns="symbol", values=["avg_R", "t_stat", "n"])
        parts += ["## Cross-instrument summary (base costs)", "", base.round(3).to_markdown(), ""]
        REPORTS.mkdir(exist_ok=True)
        (REPORTS / f"{h}_IS_v2.md").write_text("\n".join(parts))
        df.to_csv(REPORTS / f"{h}_IS_v2.csv", index=False)
        print("\n".join(parts))


if __name__ == "__main__":
    main(sys.argv[1:] or list(HYPS))
