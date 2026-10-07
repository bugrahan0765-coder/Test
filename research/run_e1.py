"""Run the pre-registered in-sample grid for E1 (VIX term structure / spikes) -> research/reports/E1_IS.{md,csv}

Usage: python -m research.run_e1

The 5 configurations are logged to the trial registry (hypothesis id "E1") at base costs; the
"always" benchmark is run against a temporary registry and is NOT logged.
"""
from __future__ import annotations

import tempfile
import time
from pathlib import Path

import pandas as pd

import pfbot.strategies.e1_vix as e1
from pfbot.data import cboe
from pfbot.research.harness import load_period, run_grid
from pfbot.stats.performance import TrialRegistry

REPORTS = Path(__file__).parent / "reports"
SYMBOLS = ["US100", "US500"]
COLS = ["config", "spread_mult", "n", "win_rate", "avg_R", "t_stat", "profit_factor", "total_R", "worst_mae_R"]

# spec: research/hypotheses/E1_vix_term_structure.md (IS pass criteria)
MIN_N = {"ts": 200, "spike": 40}
MIN_T = {"ts": 2.0, "spike": 1.5}
BENCH_KEY = ",".join(f"{k}={v}" for k, v in e1.BENCHMARK.items())


def verdicts(df: pd.DataFrame, cfgs: list[dict]) -> pd.DataFrame:
    base = df[df.spread_mult == 1.0].set_index(["config", "symbol"])
    stress = df[df.spread_mult == 1.5].set_index(["config", "symbol"])
    rows = []
    for cfg in cfgs:
        key = ",".join(f"{k}={v}" for k, v in cfg.items())
        v = cfg["variant"]
        row = {"config": key}
        ok_all = True
        for s in SYMBOLS:
            r = base.loc[(key, s)]
            bench = base.loc[(BENCH_KEY, s)]
            n_ok = r["n"] >= MIN_N[v]
            mean_ok = r["avg_R"] > 0
            t_ok = r["t_stat"] > MIN_T[v]
            beat = (r["avg_R"] > bench["avg_R"]) if v == "ts" else True
            row[f"{s}_n"] = int(r["n"])
            row[f"{s}_avg_R"] = round(float(r["avg_R"]), 4)
            row[f"{s}_t"] = round(float(r["t_stat"]), 2)
            row[f"{s}_bench_avg_R"] = round(float(bench["avg_R"]), 4)
            row[f"{s}_n_ok"] = n_ok
            row[f"{s}_t_ok"] = bool(mean_ok and t_ok)
            row[f"{s}_beats_bench"] = bool(beat) if v == "ts" else "n/a"
            row[f"{s}_x1.5_avg_R"] = round(float(stress.loc[(key, s)]["avg_R"]), 4)
            ok_all &= bool(n_ok and mean_ok and t_ok and beat)
        row["verdict"] = "PASS" if ok_all else "FAIL"
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    vix, vix3m = cboe.load_vix("VIX"), cboe.load_vix("VIX3M")
    fn = lambda bars, symbol, **cfg: e1.signals(bars, symbol=symbol, vix=vix, vix3m=vix3m, **cfg)  # noqa: E731
    parts = ["# E1 in-sample results (2015-2020, excluded months removed, cost model v3)", "",
             f"VIX data: {vix.index.min().date()} .. {vix.index.max().date()}; "
             f"VIX3M: {vix3m.index.min().date()} .. {vix3m.index.max().date()}. "
             "Information of day d is used from 09:35 ET on the next trading day.", ""]
    allres = []
    with tempfile.TemporaryDirectory() as tmp:
        scratch = TrialRegistry(Path(tmp) / "benchmark_not_logged.jsonl")
        for s in SYMBOLS:
            t0 = time.time()
            bars = load_period(s, "IS")
            res, _ = run_grid("E1", s, "IS", bars, fn, e1.CONFIGS, spread_mults=(1.0, 1.5))
            bres, _ = run_grid("E1_benchmark", s, "IS", bars, fn, [e1.BENCHMARK], spread_mults=(1.0, 1.5),
                               registry=scratch)
            res = pd.concat([res, bres], ignore_index=True)
            res.insert(0, "symbol", s)
            allres.append(res)
            parts += [f"## {s} ({time.time() - t0:.0f}s)", "",
                      res[COLS].round(3).to_markdown(index=False), ""]
    df = pd.concat(allres, ignore_index=True)
    ver = verdicts(df, e1.CONFIGS)
    parts += ["## Pass/fail against the pre-registered IS criteria (base costs)", "",
              "Criteria per instrument: n >= 200 (ts) / 40 (spike); mean R > 0 with t > 2.0 (ts) / 1.5 (spike); "
              "ts configs must beat the benchmark mean R (on each instrument). A config passes only if it "
              "meets all of them on both US100 and US500. `x1.5_avg_R` is informational.", "",
              ver.to_markdown(index=False), ""]
    for _, r in ver.iterrows():
        parts.append(f"- `{r['config']}`: **{r['verdict']}**")
    parts.append("")
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "E1_IS.md").write_text("\n".join(parts))
    df.to_csv(REPORTS / "E1_IS.csv", index=False)
    ver.to_csv(REPORTS / "E1_IS_verdicts.csv", index=False)
    print("\n".join(parts))


if __name__ == "__main__":
    main()
