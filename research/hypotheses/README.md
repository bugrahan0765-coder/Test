# Hypothesis pre-registration

Every hypothesis is written down here **before** its first backtest: mechanism, exact rules,
the full parameter grid and the pass/fail criteria. Changing a spec after seeing results means
a new hypothesis id (e.g. A1b), and every configuration ever run is logged to
`research/trials.jsonl` so the deflated Sharpe counts all of them.

## Common protocol (PLAN.md section 3)

| Item | Value |
|---|---|
| In-sample (IS) | 2015-01-01 .. 2020-12-31 (exploration may start on 2018-2020 while older data downloads) |
| Out-of-sample (OOS) | 2021-01-01 .. 2023-12-31, opened once per hypothesis after the IS grid is frozen |
| Locked test | 2024-01-01 .. latest. Opened once, for the final portfolio only |
| Data | Dukascopy M1 candles; mid = bid + estimated spread/2; spread estimated per month and 30-min bucket |
| Costs (base) | estimated spread from the data, slippage 0.5 index point (0.10 for XAUUSD) on market/stop fills, no commission (FTMO indices/metals CFDs) |
| Costs (stress) | spread x1.5 and x2.0 |
| Fills | `pfbot.backtest.engine` on M1 bars, signals decided on M5/M15 bars at bar close |
| Sessions | New York cash session 09:30-16:00 America/New_York; Xetra 09:00-17:30 Europe/Berlin |

## Pass criteria
**IS** (per configuration, base costs):
1. at least 200 trades;
2. mean R > 0 with t-stat > 2.0;
3. same sign of mean R on the sister instrument (US100 <-> US500, GER40 where applicable);
4. plateau: the neighbouring grid points are also positive;
5. still positive with spread x1.5.

**OOS** (only the configurations chosen from IS, chosen before looking):
1. mean R > 0, and OOS per-trade Sharpe at least half of IS;
2. deflated Sharpe over all logged trials for the hypothesis > 0.90 on the combined IS+OOS sample.

Survivors move to the portfolio and FTMO Monte Carlo stage.
