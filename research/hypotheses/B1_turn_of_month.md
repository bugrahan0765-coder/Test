# B1 - Turn-of-the-month effect in equity indices

**Status:** NOT PASSED in-sample (2026-10-06), weak positive. 6 of 8 configs positive on both instruments;
best d_in=-1,d_out=3,k=2: US100 +0.096 R (t 1.55), US500 +0.096 R (t 1.26), ~60 trades each. The pre-registered
bar (t > 1.5 on both) is missed on US500. Kept on a watch list as a candidate portfolio component; any reuse
must count these 16 trials. See research/reports/B1_IS.md.

## Mechanism
Equity index returns concentrate in the window from the last trading day of a month to the first
few trading days of the next (Ariel 1987; Lakonishok & Smidt 1988; McConnell & Xu 2008 across 35
countries; Etula, Rinne, Suominen & Vaittinen 2020 link it to month-end payment/liquidity cycles:
institutions sell before month-end to meet cash needs and buy back after). Flow-driven, documented
for about a century, and needs only a handful of trades per month, so spread costs are small
relative to the multi-day move.

## Rules
Instruments: US100, US500.
- Trading days = New York cash-session dates present in the data (`session_dates`).
- Entry: long at market at 15:55 ET on trading day `d_in` relative to the month end
  (-1 = last trading day of the month, -2 = the one before).
- Exit: time exit at 15:55 ET on trading day `d_out` of the next month (+1 = first trading day).
- Stop: `k` x ex-ante expected std of the holding period in price terms
  (daily HAR-RV forecast available at entry x number of trading days held, square-rooted).
- Month-end calendar is known in advance (public trading calendar), so using the next trading
  day's date is not look-ahead; prices after the entry instant are never used.

## Grid (8 configurations per instrument)
- `d_in` in {-2, -1}; `d_out` in {+2, +3}; `k` in {2, 3}

## Pass criteria (low-frequency variant of the common protocol)
About 70 trades per instrument in-sample, so the 200-trade rule cannot apply.
IS: mean R > 0 with t > 1.5 on both US100 and US500, all `k` values positive for the chosen
(d_in, d_out), still positive with spread x1.5 and financing 5%. OOS: mean R > 0 on both.
