"""D2 out-of-sample evaluation per research/hypotheses/D2_OOS_plan.md -> research/reports/D2_OOS.md

Bars from 2020-06 onward are loaded so the volatility model is warmed up at the start of 2021; only
trades whose signal falls in 2021-01-01 .. 2023-12-31 are evaluated.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import pfbot.strategies.d2_fx_month_end_fix as d2
from pfbot.backtest.engine import run_backtest
from pfbot.research.harness import cost_model, load_period
from pfbot.stats.performance import TrialRegistry, deflated_sharpe_ratio, sharpe_moments

PAIRS = ["EURUSD", "GBPUSD", "AUDUSD", "USDJPY", "USDCAD", "USDCHF"]
OOS_START, OOS_END = pd.Timestamp("2021-01-01", tz="UTC"), pd.Timestamp("2024-01-01", tz="UTC")
REPORTS = Path(__file__).parent / "reports"


def load(symbol: str) -> pd.DataFrame:
    is_tail = load_period(symbol, "IS")
    is_tail = is_tail[is_tail.index >= "2020-06-01"]
    return pd.concat([is_tail, load_period(symbol, "OOS")])


def trades_for(t_in: str, bars: dict, us500: pd.DataFrame, period: tuple) -> pd.DataFrame:
    out = []
    for p in PAIRS:
        sig = d2.signals(bars[p], p, t_in, us500)
        sig = sig[(sig["time"] >= period[0]) & (sig["time"] < period[1])]
        t = run_backtest(bars[p], sig, cost_model(p), symbol=p)
        out.append(t)
    return pd.concat(out, ignore_index=True)


def main() -> None:
    us500 = load("US500")
    bars = {p: load(p) for p in PAIRS}
    is_trades = pd.read_csv(REPORTS / "D2_IS_v3.csv")  # for the IS Sharpe reference
    lines = ["# D2 out-of-sample results (2021-2023, cost model v3)", "",
             "Plan: research/hypotheses/D2_OOS_plan.md. Verdict uses t_in = 10:00 only.", ""]
    verdict_rows = {}
    for t_in in ["10:00", "12:00", "14:00"]:
        tr = trades_for(t_in, bars, us500, (OOS_START, OOS_END))
        r = tr["R"].to_numpy()
        month = pd.DatetimeIndex(tr["entry_time"]).tz_convert(None).to_period("M")
        mavg = pd.Series(r).groupby(month).mean()
        per_pair = tr.groupby("symbol")["R"].agg(["count", "mean"])
        sr = r.mean() / r.std(ddof=1)
        verdict_rows[t_in] = (tr, sr)
        lines += [f"## t_in = {t_in}", "",
                  f"- trades {len(r)}, months {len(mavg)}, pooled mean R {r.mean():+.4f}, "
                  f"pooled t {sr * np.sqrt(len(r)):+.2f}, month-avg t {mavg.mean() / mavg.std(ddof=1) * np.sqrt(len(mavg)):+.2f}, "
                  f"per-trade Sharpe {sr:.3f}", "",
                  per_pair.round(4).to_markdown(), ""]

    # verdict for 10:00
    tr, sr_oos = verdict_rows["10:00"]
    is_rows = is_trades[(is_trades["config"].str.contains("t_in=10:00")) & (is_trades["spread_mult"] == 1.0)]
    # IS per-trade Sharpe from the IS trade list: recompute by re-running IS for 10:00
    is_bars = {p: load_period(p, "IS") for p in PAIRS}
    is_us500 = load_period("US500", "IS")
    is_tr = trades_for("10:00", is_bars, is_us500, (pd.Timestamp("2015-01-01", tz="UTC"), OOS_START))
    sr_is = is_tr["R"].mean() / is_tr["R"].std(ddof=1)
    pos_pairs = int((tr.groupby("symbol")["R"].mean() > 0).sum())
    combined = np.concatenate([is_tr["R"].to_numpy(), tr["R"].to_numpy()])
    sr_c, sk, ku, n = sharpe_moments(combined)
    reg = TrialRegistry()
    trial_srs = [s for s in reg.sharpes() if np.isfinite(s)]
    dsr = deflated_sharpe_ratio(sr_c, sr_trials=trial_srs, n_trials=len(trial_srs), n_obs=int(n), skew=sk, kurt=ku)
    checks = {
        "pooled mean R > 0": tr["R"].mean() > 0,
        f"OOS Sharpe {sr_oos:.3f} >= 0.5 x IS {sr_is:.3f}": sr_oos >= 0.5 * sr_is,
        f"pairs positive {pos_pairs}/6 >= 4": pos_pairs >= 4,
        f"DSR {dsr:.3f} > 0.90 (trials {len(trial_srs)}, combined n {int(n)}, SR {sr_c:.3f})": dsr > 0.90,
    }
    lines += ["## Verdict (t_in = 10:00)", ""] + [f"- {'PASS' if ok else 'FAIL'}: {k}" for k, ok in checks.items()]
    overall = all(checks.values())
    lines += ["", f"**D2 OOS OVERALL: {'PASS' if overall else 'FAIL'}**", ""]
    (REPORTS / "D2_OOS.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
