# E1 - VIX term structure and VIX spikes as conditioning information for index exposure

**Status:** pre-registered, not yet tested.

## Why
Every earlier family used only the traded instrument's own prices and failed. E1 adds information from the
options market. The slope of the VIX term structure (VIX / VIX3M) measures how much near-term crash
protection costs relative to 3-month protection. In backwardation (ratio > 1) markets are in stress and
subsequent equity returns are volatile and poor on a risk-adjusted basis; in contango the variance risk
premium is being earned and equities tend to drift up (Johnson 2017, "Risk Premia and the VIX Term
Structure", JFQA; Simon & Campasano 2014; practitioner evidence). Separately, sharp VIX spikes tend to be
followed by short-term equity rebounds as forced de-risking and hedging demand reverse.

## Data
CBOE daily VIX and VIX3M closes (16:15 ET official close), `data/external/` (source:
https://cdn.cboe.com/api/global/us_indices/daily_prices/). A value for date d is used only from 09:35 ET of
the next trading day on (no look-ahead: the close is published after the cash close).

## Rules
Instruments: US100, US500. One position per day at most; holding = one trading day.
- Entry: market at 09:35 ET on trading day d+1 using information up to the close of day d.
- Exit: time exit at 09:30 ET on day d+2 (next morning). Stop: 3 x expected std of the holding period.
- Variant `ts` (term structure): long when VIX/VIX3M on day d < `th`; flat otherwise.
- Variant `spike`: long when VIX(d) / VIX(d-1) - 1 >= `jump`; flat otherwise.
- Benchmark (reported, not a hypothesis): long every day (unconditional equity drift after costs).

## Grid
- `ts`: `th` in {0.90, 0.95, 1.00}  (3 configs)
- `spike`: `jump` in {0.10, 0.20} (2 configs)
5 configurations per instrument, 10 in total.

## Pass criteria
IS (2015-2020): per config >= 200 trades for `ts` (>= 40 for `spike`), mean R > 0 with t > 2.0 on both
instruments (t > 1.5 for `spike`), and the `ts` configs must beat the unconditional benchmark's mean R.
OOS (2021-2023): chosen config(s) fixed before opening; mean R > 0 on both instruments and DSR > 0.90 over all
logged trials.
