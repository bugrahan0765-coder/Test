# D2 out-of-sample plan (fixed before opening 2021-2023)

Written 2026-10-07 after the in-sample run, before any OOS data was loaded for D2.

- **Configuration tested OOS:** `t_in = 10:00` London (highest IS pooled t), all six pre-registered pairs
  (EURUSD, GBPUSD, AUDUSD, USDJPY, USDCAD, USDCHF). USDJPY is kept even though it was negative IS: dropping it
  would be a selection on IS noise without a pre-registered reason. 12:00 and 14:00 are reported for
  information only and do not affect the verdict.
- **Data:** 2021-01-01 .. 2023-12-31 with the harness exclusions (FX 2023-02..07, US500 2023-03..07), cost
  model v3 (frozen), true-UTC store.
- **Pass criteria:**
  1. pooled mean R > 0;
  2. pooled per-trade Sharpe OOS >= 0.5 x IS (IS = 0.079 R / std of IS trades);
  3. at least 4 of 6 pairs with positive mean;
  4. deflated Sharpe ratio > 0.90 on the combined IS+OOS per-trade series, with the trial set = every trial
     logged in research/trials.jsonl (all hypotheses and versions).
- If it passes, D2 becomes the first portfolio component and goes to FTMO Monte Carlo and paper trading.
  If it fails, it is rejected; no re-specification on the same OOS data.
