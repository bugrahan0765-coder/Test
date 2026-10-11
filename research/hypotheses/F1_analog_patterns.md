# F1 - Analog (nearest-neighbour) pattern matching on the 5-SMA path ("pattern memory")

**Status:** pre-registered 2026-10-11, before any result was seen.

## Why
User request: instead of resolving the AMD model's ambiguity by rules (two neighbouring phases with the
same direction, see `pfbot/features/amd_maze.py`), store many historical chart shapes of NQ (US100) M5 as a
pattern memory, find the past shapes most similar to the current one and read the most likely outcome
from what followed them. Doing this "by eye" over screenshots is not reproducible; the equivalent done
properly is a numeric analog / k-nearest-neighbour search over the same shapes.

## Data
US100 M5 (HistData M1 resampled), in-sample only: library 2015-2019, evaluation queries 2020.
2021-2023 (OOS) and 2024+ (locked) are not touched.

## Method (`pfbot/features/analog.py`)
- Shape at bar t: 5-SMA of close over the last 60 M5 bars, minus its value at t, divided by ATR(14, M5)
  at t (keeps the size of moves relative to volatility; "flat then down" differs from "down all along").
- Library: every bar t whose New York time is 10:30-15:00 (window may start before the cash open).
  Label = forward return over the next 12 bars (1 h), close(t+12)/close(t) - 1.
- Query: same shape at t; Euclidean distance; at most one match per library day (the closest window that
  day); k = 20 nearest.
- Prediction: P(up) = share of the 20 analogs with positive forward return.
- AMD use: for an AMD window whose phases are ambiguous, the analogs' outcome says whether the last move
  continued (distribution) or reversed (manipulation).

## Trading rule evaluated
Queries in 2020 every 6 bars (30 min) between 10:30 and 15:00 NY. Long if P(up) >= 0.65, short if
P(up) <= 0.35, else no trade. Exit at t+12 bars. Cost v3 (US100: 0.5 bp round trip + 0.1 bp slippage per
side = 0.7 bp). Return per trade in bp, net.

## Grid (2 configurations)
- `lib100`: library = last 100 trading days of 2019 (the user's "100 days").
- `libfull`: library = all of 2015-2019.

## Pass criteria (IS)
Per configuration: >= 200 trades, mean net return > 0 with t > 2.0, and directional hit rate > 52%.
Also reported (not a criterion): Spearman correlation between P(up) and the realised forward return on all
queries. If neither configuration passes, F1 is rejected and the AMD ambiguity stays documented as is.
