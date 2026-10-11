# G1 - Wyckoff spring / upthrust at the edge of an intraday trading range

**Status:** pre-registered 2026-10-11, before any result was seen.

## Why
The user's own discretionary setup is the Wyckoff method. Its core tradable event: price builds a trading
range (TR, accumulation or distribution), then briefly pierces the range edge to shake out weak holders
(spring below support / upthrust above resistance, the "manipulation" phase of the AMD model in
`pfbot/features/amd_maze.py`) and closes back inside. The entry is taken on the reclaim, the stop under
(over) the spring (upthrust) extreme, the target is the opposite side of the range (start of markup /
markdown). This hypothesis tests the mechanical core of that setup.

## Data
US100 and US500 M5 signals (HistData M1 resampled), fills simulated on M1. In-sample 2015-2020
(excluded months per `pfbot/research/harness.py`). OOS 2021-2023 only if IS passes; 2024+ locked.

**Limitation:** the data has no volume. Wyckoff's volume confirmation (spring on low volume, sign of
strength on high volume) is NOT tested here; it can only be checked in the forward test on a platform with
volume. G1 tests the price structure alone.

## Rules (decided at the close of M5 bar t; ATR = 14-bar SMA of true range on M5, at t-1)
Trading range = the L bars t-L .. t-1 (bar t excluded). H = max high, Lo = min low, W = H - Lo.
- Sideways: efficiency ratio |close(t-1) - close(t-L)| / sum |close changes| over the window <= 0.30.
- Width: 3 x ATR <= W <= 15 x ATR.
- Tested edges: at least 3 bars with low <= Lo + 0.2 W and at least 3 bars with high >= H - 0.2 W.
- **Spring (long):** low(t) < Lo, low(t) >= Lo - 1.0 x ATR (a shakeout, not a breakdown) and close(t) > Lo.
- **Upthrust (short):** high(t) > H, high(t) <= H + 1.0 x ATR and close(t) < H.
- Entry: market at the next M1 bar after the M5 close. Stop: spring low - 0.25 ATR (upthrust high + 0.25 ATR).
- Target: config `range` = opposite edge of the TR (H for longs, Lo for shorts); skip the signal if that is
  less than 1R away. Config `2R` = 2 x the stop distance.
- Signal bars whose New York start time is 10:00-15:00 only; time exit 15:55 New York. One position at a time.
- Costs: cost model v3 (frozen), plus a 1.5x spread stress run.

## Grid (4 configurations per instrument)
L in {48, 96} M5 bars (4 h, 8 h) x target in {range, 2R}.

## Pass criteria (IS)
A configuration passes if on BOTH US100 and US500: >= 200 trades, mean R > 0 with t > 2.0. The DSR over all
logged trials is reported. If nothing passes, G1 is rejected; the volume-based part of the user's Wyckoff
reading can then only be judged in the pre-registered forward demo test.
