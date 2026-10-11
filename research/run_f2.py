"""F2 in-sample run (research/hypotheses/F2_fractal_maze.md) -> research/reports/F2_IS.md

Usage: python -m research.run_f2
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from pfbot.research.harness import load_period, run_grid
from pfbot.stats.performance import TrialRegistry, deflated_sharpe_ratio, sharpe_moments
from pfbot.strategies import f2_fractal_maze as f2

OUT = Path(__file__).parent / "reports" / "F2_IS.md"
SYMBOLS = ["US100", "US500"]
COLS = ["n", "win_rate", "avg_R", "t_stat", "profit_factor", "avg_win_R", "avg_loss_R"]


def _fmt(v) -> str:
    return f"{v:.3f}" if isinstance(v, (float, np.floating)) else str(v)


def _md(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(_fmt(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(out)


def main() -> None:
    lines = ["# F2 in-sample result: fractal AMD maze, M1 + M5 (2015-2020)", "",
             "Hypothesis: `research/hypotheses/F2_fractal_maze.md`. Cost model v3; "
             "spread_mult 1.5 = stress run (not a pass criterion).", ""]
    base = {}
    sides = []
    for sym in SYMBOLS:
        bars = load_period(sym, "IS")
        res, trades = run_grid(f2.HYPOTHESIS, sym, "IS", bars, f2.signals, f2.CONFIGS)
        lines += [f"## {sym}", "", _md(res.reindex(columns=["config", "spread_mult"] + COLS)), ""]
        for (key, m), t in trades.items():
            if m == 1.0:
                base[(sym, key)] = t
                for s, name in ((1, "long"), (-1, "short")):
                    r = t.loc[t["side"] == s, "R"]
                    sides.append({"symbol": sym, "config": key, "side": name, "n": len(r),
                                  "avg_R": r.mean() if len(r) else np.nan,
                                  "t_stat": r.mean() / r.std(ddof=1) * np.sqrt(len(r)) if len(r) > 2 else np.nan})
        print(res.reindex(columns=["config", "spread_mult"] + COLS))

    lines += ["## By side (spread_mult 1.0, reported only)", "", _md(pd.DataFrame(sides)), ""]

    verdict = []
    for cfg in f2.CONFIGS:
        key = ",".join(f"{k}={v}" for k, v in cfg.items())
        ok = True
        for sym in SYMBOLS:
            r = base[(sym, key)]["R"].to_numpy()
            t = r.mean() / r.std(ddof=1) * np.sqrt(len(r)) if len(r) > 2 else np.nan
            ok &= bool(len(r) >= 200 and r.mean() > 0 and t > 2.0)
        verdict.append((key, ok))

    trial_srs = np.array([t["sharpe"] for t in TrialRegistry().load() if np.isfinite(t.get("sharpe", np.nan))])
    nonempty = [k for k in base if len(base[k]) > 2]
    if nonempty:
        best_key = max(nonempty, key=lambda k: base[k]["R"].mean())
        sr, sk, ku, n = sharpe_moments(base[best_key]["R"].to_numpy())
        dsr = deflated_sharpe_ratio(sr, sr_trials=trial_srs, n_trials=len(trial_srs), n_obs=int(n), skew=sk,
                                    kurt=ku)
    else:
        best_key, sr, dsr = "none (fewer than 3 trades everywhere)", float("nan"), float("nan")
    lines += ["## Verdict", "",
              "Pass: on BOTH instruments >= 200 trades, mean R > 0, t > 2.0.", ""]
    lines += [f"- {k}: {'PASS' if ok else 'fail'}" for k, ok in verdict]
    lines += ["", f"Best single (symbol, config) by mean R: {best_key}, per-trade SR {sr:.3f}, "
                  f"DSR over {len(trial_srs)} logged trials = {dsr:.3f}.", "",
              "**F2 " + ("PASSES in-sample: " + ", ".join(k for k, ok in verdict if ok) + "**"
                         if any(ok for _, ok in verdict) else "is REJECTED in-sample.**")]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT.read_text())


if __name__ == "__main__":
    main()
