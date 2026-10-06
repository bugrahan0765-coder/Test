"""How much edge does an FTMO challenge actually need? -> research/reports/prop_economics.md

Synthetic trade streams (one trade per trading day, win +1.5R / loss -1R) with a chosen
expectancy are run through the FTMO 2-step Monte Carlo (phase 1 -> phase 2 -> 250-day funded
account with payouts every 10 trading days at an 80% split). EV is per challenge purchase on a
100k account with a 540 EUR (~600 USD) fee refunded with the first payout.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from pfbot.propsim.rules import RiskPolicy
from pfbot.propsim.sim import build_day_book, expected_value, monte_carlo

OUT = Path(__file__).parent / "reports" / "prop_economics.md"
ACCOUNT, FEE = 100_000, 600.0
WIN_R = 1.5


def synthetic_trades(expectancy: float, n_days: int = 1500, seed: int = 0) -> tuple[pd.DataFrame, pd.DatetimeIndex]:
    rng = np.random.default_rng(seed)
    p = (expectancy + 1) / (WIN_R + 1)
    days = pd.bdate_range("2015-01-01", periods=n_days)
    win = rng.random(n_days) < p
    R = np.where(win, WIN_R, -1.0)
    mae = np.where(win, -rng.uniform(0, 0.9, n_days), -1.0)
    entry = (days + pd.Timedelta(hours=15)).tz_localize("Europe/Prague").tz_convert("UTC")
    t = pd.DataFrame({"entry_time": entry, "exit_time": entry + pd.Timedelta(hours=2), "R": R, "mae_R": mae})
    return t, days


def main() -> None:
    rows = []
    for e in (-0.10, -0.05, 0.0, 0.05, 0.10, 0.15):
        trades, days = synthetic_trades(e)
        book = build_day_book(trades, days)
        for risk in (0.0025, 0.005, 0.0075, 0.01):
            mc = monte_carlo(book, RiskPolicy(risk_per_trade=risk), n_paths=4000, seed=1)
            rows.append({
                "expectancy_R": e, "risk_%": risk * 100,
                "P(pass ph1)": mc["p_phase1"], "P(funded)": mc["p_funded"],
                "payout|funded_%": 100 * mc["mean_payout_if_funded"],
                "EV_per_attempt_$": expected_value(mc, ACCOUNT, FEE),
            })
    df = pd.DataFrame(rows)
    lines = [
        "# Prop firm economics: how much edge is needed?", "",
        __doc__.strip(), "",
        "Challenge phases capped at 120 trading days each (a timeout counts as a failure). "
        "Risk policy: daily soft stop 3%, risk halved below -6%, trading halted below -8%.", "",
        df.round(3).to_markdown(index=False), "",
    ]
    OUT.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
