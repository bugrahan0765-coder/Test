# A2 - Opening range momentum (first N minutes of the cash session)

**Status:** pre-registered, not yet tested.

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
