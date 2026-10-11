# F2 - Fractal AMD maze: the same AMD structure on M1 and M5 at the same time

**Status:** pre-registered 2026-10-11, before any result was seen.

## Why
User's idea: the maze / AMD model works through self-similarity between the 1-minute and the 5-minute chart
(the market is fractal: the last hour on M1 repeats the shape of the last five hours on M5). F1 compared the
current M5 shape with past days and found nothing; F2 compares the two timeframes with each other, now.
The "meeting point" of the maze is where both timeframes independently reach the same AMD decomposition.

## Data
US100 and US500, HistData M1, M5 resampled from it. In-sample 2015-2020 (excluded months per harness).
OOS 2021-2023 only if IS passes; 2024+ locked.

## Rules (decided at the close of M5 bar t)
- M5 window: the 60 M5 bars ending with t (5 h). M1 window: the 60 M1 bars ending with the last M1 bar
  inside t (1 h). Both use `pfbot.features.amd_maze.fit_amd` with its defaults (5-SMA, min phase 5 bars,
  flat threshold 0.05 ATR/bar, ATR 14 of the same timeframe).
- Same structure: the best scenario on M5 and on M1 is the same A(F) -> M(x) -> D(y), both `consistent`,
  with y in {U, D} and x the opposite of y (classic AMD: manipulation against the real move).
- Self-similarity: Pearson correlation between the two 60-point 5-SMA paths >= rho.
- Trade in the distribution direction y: market entry on the next M1 bar. Stop = 1.5 x ATR(14, M5).
- Exit config `2R`: target 2 x stop distance, plus time exit; config `time`: time exit only.
  Time exit = 60 min after the M5 close of t, or 15:55 New York, whichever is earlier.
- Signal bars with New York start time 10:30-15:00; one position at a time; cost model v3 (+1.5x stress).

## Grid (4 configurations per instrument)
rho in {0.8, 0.9} x exit in {2R, time}.

## Pass criteria (IS)
A configuration passes if on BOTH US100 and US500: >= 200 trades, mean R > 0 with t > 2.0. DSR over all
logged trials is reported. If nothing passes, F2 is rejected.
