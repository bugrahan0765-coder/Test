# A2 - Opening range momentum (first N minutes of the cash session)

**Status:** REJECTED in-sample (2026-10-06). All 12 configs negative on US100 and US500 after costs
(mean R -0.17 to -0.58). Zero-cost check (US100, N=15, no target, 2019-2020): +0.10 R, t = 0.6, not significant.
Opening ranges are narrow (stop ~8 US100 points) so spread + slippage cost 25-40% of the risk.
See research/reports/A2_IS.md.

**Definitive IS result (true-UTC data, cost model v3, 2026-10-07):** A2: N=5,tR=10 candle US100 +0.17 R (t 2.34) but US500 +0.03 R (t 0.43); fails sister check. Earlier results above used
mis-stamped data (1h off in US DST) and are superseded.

## Mechanism
Orders that accumulate overnight are executed at the cash open; the direction of the opening
imbalance tends to persist for the session (Zarattini & Aziz 2023 on QQQ with 5-minute opening
range: long if the first 5-minute candle closes up, short if down, stop at the opposite end of the
range, 10R target or end-of-day exit; reported a large edge in 2016-2023, especially "in play"
days with high relative volume). Mechanism and literature are intraday-specific and suit an
FTMO daily-loss constraint (one trade per day, defined risk).

## Rules
Instruments: US100, US500 (primary), GER40 on Xetra open (09:00 Berlin, reported separately).

- Opening range: the first `N` minutes of the cash session (09:30 ET + N).
  Range high H, low L, open O, close C of that window (from M1 bars).
- Skip the day if the range is degenerate (H - L < 0.25 x expected vol of the window) or the
  first bar of the session is missing.
- Variant `entry`:
  - `candle`: at the end of the range enter at market in direction sign(C - O); skip if C == O.
  - `breakout`: in direction sign(C - O), place a stop order at H (long) / L (short), valid until
    12:00 ET.
- Stop: opposite end of the range (L for longs, H for shorts).
- Target: `tR` x initial risk, or none.
- Exit: end of session (15:55 ET time exit) if neither stop nor target hit.

## Grid (12 configurations per instrument)
- `N` in {5, 15, 30} minutes
- `tR` in {none, 3, 10}
- `entry` in {candle, breakout}: only `candle` with all `N`/`tR` (9) + `breakout` with N=15, all tR (3)

## Notes
The original paper adds a "stocks in play" relative-volume filter that does not exist for an
index CFD; the analogous conditioning (relative opening-range size vs expected vol) is a later
variant A2b, not part of this grid.
