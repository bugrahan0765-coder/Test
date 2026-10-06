# B3 - Time-series momentum (trend following), weekly rebalanced

**Status:** REJECTED in-sample (2026-10-06). No configuration has t > 1.5 on two instruments; best
L=20 long-only on US100 (+0.05 R, t 1.55) but ~0 on US500 and negative on XAUUSD. See research/reports/B3_IS.md.

## Mechanism
An asset's own past 1-12 month return predicts its next-month return, across equity indices,
bonds, currencies and commodities (Moskowitz, Ooi & Pedersen 2012; Hurst, Ooi & Pedersen 2017
over 1880-2016). Explanations: initial under-reaction and later over-reaction to news,
hedging/flow pressure, and risk premia in crisis periods. Scaling positions by ex-ante volatility
is integral to the documented results; here each trade risks the same R at a stop of k x expected
weekly std, which is a volatility-targeted position by construction.

## Rules
Instruments: US100, US500, XAUUSD.
- Decision time: Friday 15:55 ET (or the last trading day of the week), daily closes taken at
  15:55 ET.
- Signal: sign of the log return over the previous `L` trading days (close to close, up to the
  decision time). `long_only` variant takes only positive signals.
- Entry: market at the decision time; exit: time exit at the next week's decision time, then
  re-enter if the new signal is non-zero (each week is one trade).
- Stop: `k` x ex-ante expected std of the week (daily HAR-RV forecast x 5, square-rooted) in price terms.
- Financing at 5%/yr per night.

## Grid (12 configurations per instrument)
- `L` in {20, 60, 120}; `k` in {2, 3}; `long_only` in {False, True}

## Pass criteria (low-frequency variant)
About 300 weekly trades per instrument in-sample. IS: mean R > 0 with t > 1.5 on at least two of the
three instruments for the same configuration, neighbouring L values positive, still positive with
spread x1.5. OOS: mean R > 0 on the same instruments.
