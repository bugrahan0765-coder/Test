"""F1 in-sample run: analog pattern memory on US100 M5 (research/hypotheses/F1_analog_patterns.md).

Library 2015-2019, queries 2020 every 30 min between 10:30 and 15:00 New York time.
Usage: python -m research.run_f1
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from pfbot.data.schema import resample_bars
from pfbot.data.store import load_bars
from pfbot.features.analog import AnalogLibrary, shape_table
from pfbot.stats.performance import TrialRegistry

COST_BP = 0.7      # cost model v3, US100 round trip incl. slippage
K = 20
P_LONG, P_SHORT = 0.65, 0.35
OUT = Path("research/reports/F1_IS.md")


def evaluate(lib: AnalogLibrary, qmeta: pd.DataFrame, QX: np.ndarray) -> dict:
    matches = lib.query(QX, k=K)
    p = np.array([AnalogLibrary.p_up(m) for m in matches])
    fwd_bp = qmeta["fwd"].to_numpy() * 1e4
    side = np.where(p >= P_LONG, 1, np.where(p <= P_SHORT, -1, 0))
    tr = side != 0
    net = side[tr] * fwd_bp[tr] - COST_BP
    hit = float((np.sign(fwd_bp[tr]) == side[tr]).mean()) if tr.any() else np.nan
    t = float(net.mean() / (net.std(ddof=1) / np.sqrt(len(net)))) if len(net) > 2 else np.nan
    rho = stats.spearmanr(p, fwd_bp).statistic
    return {"n_queries": len(p), "n_trades": int(tr.sum()), "n_long": int((side == 1).sum()),
            "n_short": int((side == -1).sum()), "mean_net_bp": float(net.mean()) if len(net) else np.nan,
            "t": t, "hit": hit, "spearman": float(rho), "sharpe_per_trade": float(net.mean() / net.std(ddof=1))
            if len(net) > 2 else np.nan, "mean_dist": float(np.mean([m["dist"].mean() for m in matches]))}


def main() -> None:
    bars = resample_bars(load_bars("US100", start="2015-01-01", end="2020-12-31 23:59"), "5min")
    meta, X = shape_table(bars)
    years = meta.index.year
    lib_mask = years <= 2019
    q_mask = (years == 2020) & np.isfinite(meta["fwd"].to_numpy())
    ny = meta.index.tz_convert("America/New_York")
    q_mask &= (ny.minute % 30 == 0)
    qmeta, QX = meta[q_mask], X[q_mask]

    lib_days = pd.Index(sorted(set(meta["day"][lib_mask])))
    last100 = set(lib_days[-100:])
    configs = {
        "lib100": lib_mask & meta["day"].isin(last100).to_numpy(),
        "libfull": lib_mask,
    }
    reg = TrialRegistry()
    rows = []
    for name, mask in configs.items():
        lib = AnalogLibrary(meta[mask], X[mask])
        r = evaluate(lib, qmeta, QX)
        r.update(config=name, lib_days=lib.n_days, lib_windows=len(lib))
        passed = r["n_trades"] >= 200 and r["mean_net_bp"] > 0 and r["t"] > 2.0 and r["hit"] > 0.52
        r["passed"] = bool(passed)
        reg.log("F1", {"config": name, "k": K, "p_long": P_LONG, "p_short": P_SHORT, "cost": "v3"},
                r["n_trades"], r["sharpe_per_trade"], period="IS-2020", **{k: v for k, v in r.items()
                                                                          if k not in ("config",)})
        rows.append(r)
        print(r)

    write_report(rows)


def _md_table(df: pd.DataFrame) -> str:
    cols = ["config"] + list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for name, r in df.iterrows():
        cells = [name] + [f"{v:.3f}" if isinstance(v, float) else str(v) for v in r]
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def write_report(rows: list[dict]) -> None:
    keep = ["lib_days", "lib_windows", "n_queries", "n_trades", "n_long", "n_short", "mean_net_bp", "t",
            "hit", "spearman", "mean_dist", "passed"]
    df = pd.DataFrame(rows).set_index("config")[keep]
    lines = [
        "# F1 in-sample result: analog pattern memory (US100 M5)",
        "",
        "Hypothesis: `research/hypotheses/F1_analog_patterns.md`. Library 2015-2019 (or its last 100 days),",
        f"queries 2020 every 30 min 10:30-15:00 NY, k = {K}, long if P(up) >= {P_LONG}, short if <= {P_SHORT},",
        f"exit after 12 bars (1 h), cost v3 = {COST_BP} bp round trip.",
        "",
        _md_table(df),
        "",
        "Pass: >= 200 trades, mean net > 0 with t > 2.0, hit rate > 52%.",
        "",
        "**Verdict:** " + ("PASSED (" + ", ".join(df.index[df["passed"]]) + ")" if df["passed"].any()
                           else "REJECTED - no configuration passes."),
    ]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT.read_text())


def report_from_registry() -> None:
    """Rebuild the report from the logged trials (no re-run, no duplicate trials)."""
    recs = TrialRegistry().load("F1")
    last = {}
    for r in recs:
        last[r["params"]["config"]] = {**r, "config": r["params"]["config"]}
    write_report(list(last.values()))


if __name__ == "__main__":
    import sys
    report_from_registry() if "--report-only" in sys.argv else main()
