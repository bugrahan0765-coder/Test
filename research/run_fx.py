"""Run the pre-registered in-sample grids for D1 (FX time of day) and D2 (month-end 4pm fix)
-> research/reports/<hyp>_IS.md (+ .csv, + _pooled.csv)

Usage: python -m research.run_fx D1 D2 [--no-log]

``--no-log`` writes the trial registry to a throw-away file (dry runs); a real run appends every
configuration to research/trials.jsonl under hypothesis ids "D1" / "D2".
"""
from __future__ import annotations

import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd

import pfbot.strategies.d1_fx_time_of_day as d1
import pfbot.strategies.d2_fx_month_end_fix as d2
from pfbot.features import volatility
from pfbot.research.harness import load_period, run_grid
from pfbot.stats.performance import TrialRegistry

REPORTS = Path(__file__).parent / "reports"
PAIRS = d1.PAIRS
COLS = ["config", "spread_mult", "n", "win_rate", "avg_R", "t_stat", "profit_factor", "total_R", "worst_mae_R"]
MULTS = (1.0, 1.5)

# D1 per-configuration criteria and pooled criteria (spec)
D1_MIN_TRADES, D1_T, D1_POOL_T, D1_POOL_PAIRS = 200, 2.0, 2.5, 4
# D2 pooled criteria (spec)
D2_POOL_T, D2_MONTH_T, D2_POOL_PAIRS = 2.0, 1.5, 4


def _cached_vol():
    """Memoise expected_bar_vol per (bars object, tz): it is the slow part of each signal call."""
    orig = volatility.expected_bar_vol
    cache = {}

    def wrapped(bars, *args, **kw):
        key = (id(bars), args, tuple(sorted(kw.items())))
        if key not in cache:
            cache[key] = orig(bars, *args, **kw)
        return cache[key]

    d1.expected_bar_vol = wrapped
    d2.expected_bar_vol = wrapped


def histdata_to_true_utc(bars: pd.DataFrame) -> pd.DataFrame:
    """Convert HistData stamps to true UTC.

    ``pfbot.data.histdata`` assumes the files are fixed EST (UTC-5, no DST) and adds 5 hours. Checked
    against Dukascopy M1 candles (EURUSD, USDJPY, US500 on 2016-2019 summer and winter days, and
    independently by the 08:30 ET data-release spike and the Sunday market open), the stamps are in fact
    New York wall-clock time *with* US daylight saving: stored stamp = NY wall clock + 5h. During US DST
    the stored "UTC" index is therefore 1 hour later than true UTC (corr 0.99+ at lag -60 min in summer,
    lag 0 in winter). Time-of-day hypotheses need true UTC, so the index is rebuilt from the NY wall
    clock. The weekend hole covers the DST switch hours, so nothing is lost there.
    """
    wall = bars.index.tz_convert(None) - pd.Timedelta(hours=5)
    true = wall.tz_localize("America/New_York", ambiguous="NaT", nonexistent="NaT").tz_convert("UTC")
    ok = ~pd.isna(true)
    out = bars[ok].copy()
    out.index = pd.DatetimeIndex(true[ok], name="time")
    return out


def load_true(symbol: str) -> pd.DataFrame:
    return histdata_to_true_utc(load_period(symbol, "IS"))


def tstat(x) -> float:
    x = np.asarray(x, float)
    if len(x) < 2 or x.std(ddof=1) == 0:
        return float("nan")
    return float(x.mean() / x.std(ddof=1) * np.sqrt(len(x)))


def _pass(b: bool) -> str:
    return "PASS" if b else "FAIL"


def _fmt(df: pd.DataFrame, nd: int = 3) -> str:
    return df.round(nd).to_markdown(index=False)


def _pooled_stats(trades: pd.DataFrame, cluster: pd.Series) -> dict:
    """Pooled stats over all trades; ``cluster`` labels trades by calendar period (day / month)."""
    r = trades["R"].to_numpy(float)
    by = trades.assign(_c=cluster.to_numpy()).groupby("_c")["R"].mean()
    return {"n": len(r), "mean_R": r.mean() if len(r) else np.nan, "t": tstat(r),
            "n_clusters": len(by), "mean_R_cluster": by.mean() if len(by) else np.nan, "t_cluster": tstat(by.to_numpy())}


# --------------------------------------------------------------------------------------------------
def run_d1(bars: dict, registry) -> tuple[str, pd.DataFrame, pd.DataFrame]:
    parts = ["# D1 in-sample results: FX time-of-day (2015-2020, excluded months removed, cost model v2)", "",
             "Spec: research/hypotheses/D1_fx_time_of_day.md. Trades enter at the window start and exit after H hours "
             "(stop 3 x ex-ante expected std of the window). Costs: FX cost model v2 (spread 0.6 bp + 0.1 bp "
             "slippage/side + 5% p.a. financing), stress x1.5 spread.", ""]
    allres, trades = [], {}
    for s in PAIRS:
        t0 = time.time()
        res, tr = run_grid("D1", s, "IS", bars[s], d1.signals, d1.CONFIGS_BY_SYMBOL[s], spread_mults=MULTS,
                           registry=registry)
        res.insert(0, "symbol", s)
        allres.append(res)
        for (key, m), t in tr.items():
            trades[(s, key, m)] = t
        parts += [f"## {s} ({time.time() - t0:.0f}s)", "", _fmt(res[COLS]), ""]
    df = pd.concat(allres, ignore_index=True)

    base = df[df.spread_mult == 1.0].pivot(index="config", columns="symbol", values=["avg_R", "t_stat", "n"])
    parts += ["## Cross-pair summary (base costs)", "", base.round(3).to_markdown(), ""]

    # ---- per-configuration verdicts ----
    rows = []
    for s in PAIRS:
        for cfg in d1.CONFIGS_BY_SYMBOL[s]:
            key = ",".join(f"{k}={v}" for k, v in cfg.items())
            a = df[(df.symbol == s) & (df.config == key)].set_index("spread_mult")
            n, avg, t = a.loc[1.0, "n"], a.loc[1.0, "avg_R"], a.loc[1.0, "t_stat"]
            avg15 = a.loc[1.5, "avg_R"]
            ok = bool(n >= D1_MIN_TRADES and avg > 0 and t > D1_T and avg15 > 0)
            rows.append({"symbol": s, "config": key, "n": n, "avg_R": avg, "t": t, "avg_R_x1.5": avg15, "verdict": _pass(ok)})
    pc = pd.DataFrame(rows)

    # ---- pooled per (window, H) ----
    prow = []
    for window in ("US", "home"):
        for H in (2, 4):
            key = f"window={window},H={H}"
            pairs = [s for s in PAIRS if any(c == dict(window=window, H=H) for c in d1.CONFIGS_BY_SYMBOL[s])]
            tr1 = pd.concat([trades[(s, key, 1.0)].assign(symbol=s) for s in pairs], ignore_index=True)
            tr15 = pd.concat([trades[(s, key, 1.5)] for s in pairs], ignore_index=True)
            day = (tr1["entry_time"] + pd.Timedelta(hours=2)).dt.tz_convert("UTC").dt.normalize()
            st = _pooled_stats(tr1, day)
            per_pair = tr1.groupby("symbol")["R"].mean().reindex(pairs)
            pos = int((per_pair > 0).sum())
            prow.append({
                "window": window, "H": H, "pairs": len(pairs), "n_trades": st["n"], "pooled_mean_R": st["mean_R"],
                "pooled_t": st["t"], "eqwt_mean_R": per_pair.mean(), "pairs_positive": pos,
                "t_day_clustered": st["t_cluster"], "pooled_mean_R_x1.5": tr15["R"].mean(),
                "verdict": _pass(st["t"] > D1_POOL_T and pos >= D1_POOL_PAIRS),
            })
    pool = pd.DataFrame(prow)

    parts += ["## Pooled evaluation per (window, H), base costs", "",
              "pooled mean R / t over all trades of all pairs; eqwt = mean of the per-pair mean R; "
              "t_day_clustered = t-stat of the per-day average R across pairs (informational, not a spec criterion); "
              "x1.5 = pooled mean R with spread x1.5 (informational for D1).", "", _fmt(pool), "",
              "Per-pair mean R by group (base costs):", "", _pair_means(trades, PAIRS), ""]

    parts += ["## Verdicts", "",
              f"Per-pair configuration criteria: n >= {D1_MIN_TRADES}, mean R > 0, t > {D1_T}, mean R > 0 with spread x1.5.", "",
              _fmt(pc), ""]
    parts += [f"Pooled group criteria: pooled t > {D1_POOL_T} and >= {D1_POOL_PAIRS} pairs with positive mean R.", ""]
    for _, r in pool.iterrows():
        parts.append(f"- **{r.verdict}** D1 window={r.window}, H={r.H}h: pooled mean R {r.pooled_mean_R:+.4f}, "
                     f"pooled t {r.pooled_t:+.2f} (need > {D1_POOL_T}), pairs positive {r.pairs_positive}/{r.pairs} "
                     f"(need >= {D1_POOL_PAIRS}); x1.5 spread pooled mean R {r['pooled_mean_R_x1.5']:+.4f}")
    npass_cfg, npass_grp = int((pc.verdict == "PASS").sum()), int((pool.verdict == "PASS").sum())
    parts += ["", f"Per-pair configurations passing: {npass_cfg} of {len(pc)}. Pooled groups passing: {npass_grp} of {len(pool)}.",
              "", f"**D1 OVERALL: {_pass(npass_grp > 0)}** ({'at least one pooled group passes' if npass_grp else 'no pooled group passes'}).", ""]
    return "\n".join(parts), df, pool.assign(hyp="D1")


def _pair_means(trades: dict, pairs: list[str]) -> str:
    rows = []
    for s in pairs:
        row = {"symbol": s}
        for w in ("US", "home"):
            for h in (2, 4):
                k = (s, f"window={w},H={h}", 1.0)
                row[f"{w} {h}h"] = trades[k]["R"].mean() if k in trades else np.nan
        rows.append(row)
    return pd.DataFrame(rows).round(4).to_markdown(index=False)


# --------------------------------------------------------------------------------------------------
def run_d2(bars: dict, us500: pd.DataFrame, registry) -> tuple[str, pd.DataFrame, pd.DataFrame]:
    parts = ["# D2 in-sample results: month-end USD flows into the London 4pm fix (2015-2020, cost model v2)", "",
             "Spec: research/hypotheses/D2_fx_month_end_fix.md. Last trading day of the month, direction = sign of the "
             "US500 month-to-date return at entry (sell USD if up), exit 16:01 London, stop 3 x ex-ante expected std. "
             "Months lost: HAR warm-up (first ~5 months of 2015) and months where US500 prices are unavailable "
             "(excluded months and the month after them, since the base is the previous month-end close).", ""]
    configs = d2.CONFIGS
    allres, trades = [], {}
    for s in PAIRS:
        t0 = time.time()

        def fn(b, symbol, t_in, _us=us500):
            return d2.signals(b, symbol, t_in, _us)

        res, tr = run_grid("D2", s, "IS", bars[s], fn, configs, spread_mults=MULTS, registry=registry)
        res.insert(0, "symbol", s)
        allres.append(res)
        for (key, m), t in tr.items():
            trades[(s, key, m)] = t
        parts += [f"## {s} ({time.time() - t0:.0f}s)", "", _fmt(res[COLS]), ""]
    df = pd.concat(allres, ignore_index=True)
    base = df[df.spread_mult == 1.0].pivot(index="config", columns="symbol", values=["avg_R", "t_stat", "n"])
    parts += ["## Cross-pair summary (base costs)", "", base.round(3).to_markdown(), ""]

    prow = []
    for cfg in configs:
        key = ",".join(f"{k}={v}" for k, v in cfg.items())
        tr1 = pd.concat([trades[(s, key, 1.0)].assign(symbol=s) for s in PAIRS], ignore_index=True)
        tr15 = pd.concat([trades[(s, key, 1.5)] for s in PAIRS], ignore_index=True)
        month = tr1["entry_time"].dt.tz_convert("Europe/London").dt.tz_localize(None).dt.to_period("M")
        st = _pooled_stats(tr1, month)
        per_pair = tr1.groupby("symbol")["R"].mean().reindex(PAIRS)
        pos = int((per_pair > 0).sum())
        m15 = tr15["R"].mean()
        ok = bool(st["mean_R"] > 0 and st["t"] > D2_POOL_T and st["t_cluster"] > D2_MONTH_T
                  and pos >= D2_POOL_PAIRS and m15 > 0)
        prow.append({"t_in": cfg["t_in"], "n_trades": st["n"], "months": st["n_clusters"], "pooled_mean_R": st["mean_R"],
                     "pooled_t": st["t"], "month_avg_mean_R": st["mean_R_cluster"], "month_avg_t": st["t_cluster"],
                     "pairs_positive": pos, "pooled_mean_R_x1.5": m15, "verdict": _pass(ok)})
    pool = pd.DataFrame(prow)
    pp = pd.DataFrame({s: {cfg["t_in"]: trades[(s, ",".join(f"{k}={v}" for k, v in cfg.items()), 1.0)]["R"].mean()
                            for cfg in configs} for s in PAIRS})

    parts += ["## Pooled evaluation per t_in, base costs", "",
              "pooled mean R / t over all trades of all pairs; month_avg = per-month average R across pairs "
              "(t-stat over months, controls for cross-pair correlation within a month-end).", "", _fmt(pool), "",
              "Per-pair mean R (base costs):", "", pp.round(4).to_markdown(), ""]
    parts += ["## Verdicts", "",
              f"Criteria per t_in: pooled mean R > 0, pooled t > {D2_POOL_T}, month-average t > {D2_MONTH_T}, "
              f">= {D2_POOL_PAIRS} of 6 pairs positive, pooled mean R > 0 with spread x1.5.", ""]
    for _, r in pool.iterrows():
        parts.append(f"- **{r.verdict}** D2 t_in={r.t_in} London: pooled mean R {r.pooled_mean_R:+.4f}, pooled t {r.pooled_t:+.2f} "
                     f"(need > {D2_POOL_T}), month-avg t {r.month_avg_t:+.2f} (need > {D2_MONTH_T}), pairs positive "
                     f"{r.pairs_positive}/6 (need >= {D2_POOL_PAIRS}), x1.5 pooled mean R {r['pooled_mean_R_x1.5']:+.4f}")
    npass = int((pool.verdict == "PASS").sum())
    parts += ["", f"**D2 OVERALL: {_pass(npass > 0)}** ({npass} of {len(pool)} t_in groups pass).", ""]
    return "\n".join(parts), df, pool.assign(hyp="D2")


def main(hyps: list[str], log: bool = True) -> None:
    _cached_vol()
    registry = TrialRegistry() if log else TrialRegistry(Path(tempfile.mkdtemp()) / "trials_dry.jsonl")
    bars = {s: load_true(s) for s in PAIRS}
    REPORTS.mkdir(exist_ok=True)
    for h in hyps:
        if h == "D1":
            text, df, pool = run_d1(bars, registry)
        elif h == "D2":
            text, df, pool = run_d2(bars, load_true("US500"), registry)
        else:
            raise SystemExit(f"unknown hypothesis {h}")
        (REPORTS / f"{h}_IS.md").write_text(text)
        df.to_csv(REPORTS / f"{h}_IS.csv", index=False)
        pool.to_csv(REPORTS / f"{h}_IS_pooled.csv", index=False)
        print(text)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(args or ["D1", "D2"], log="--no-log" not in sys.argv)
