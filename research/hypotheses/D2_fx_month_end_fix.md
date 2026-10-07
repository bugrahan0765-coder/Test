# D2 - Month-end USD flows into the London 4pm fix

**Status:** pre-registered, not yet tested.

**Definitive IS result (true-UTC data, cost model v3, 2026-10-07):** D2: PASS in all 3 groups; 10:00 London pooled +0.079 R (t 3.54, month-avg t 2.05), 12:00 +0.069 R (t 3.06/1.81), 14:00 +0.067 R (t 2.76/1.81); 5/6 pairs positive (USDJPY negative). Earlier results above used
mis-stamped data (1h off in US DST) and are superseded.

## Mechanism
Foreign investors holding US equities hedge the currency exposure and rebalance those hedges at
month-end, typically executing at the WM/Reuters 4pm London fix. When US equities have risen over the
month, the hedge must be increased, i.e. USD sold; when they fell, USD bought (Melvin & Prins 2015,
"Equity hedging and exchange rates at the London 4p.m. fix"; also Evans 2018 on fix flows).
A predictable, price-insensitive flow on a known day and time.

## Rules
Pairs: EURUSD, GBPUSD, AUDUSD, USDJPY, USDCAD, USDCHF.
- Day: last trading day of the month (calendar known in advance).
- Signal: sign of the US500 log return from the last close of the previous month (16:00 New York of the
  previous month's last trading day) to the entry instant. Positive -> sell USD; negative -> buy USD.
- Entry: market at `t_in` London time on that day; exit: time exit at 16:01 London (just after the fix).
- Stop: 3 x expected std of the holding window.
- Pooled evaluation across pairs (6 pairs x ~70 months).

## Grid
`t_in` in {"10:00", "12:00", "14:00"} London: 3 configurations per pair, 18 in total.

## Pass criteria (low frequency)
Pooled across pairs per `t_in`: mean R > 0 with pooled t > 2.0 (clustering: also report the t-stat on the
per-month average across pairs, which must exceed 1.5), at least 4 of 6 pairs positive, positive with spread
x1.5.
