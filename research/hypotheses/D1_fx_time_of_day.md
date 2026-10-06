# D1 - FX time-of-day effect: currencies weaken during their home trading hours

**Status:** pre-registered, not yet tested.

## Mechanism
Ranaldo (2009, "Segmentation and time-of-day patterns in foreign exchange markets") and Breedon &
Ranaldo (2013, "Intraday patterns in FX returns and order flow") find that a currency tends to
depreciate during its own country's working hours and appreciate during foreign hours, linked to
domestic investors being net buyers of foreign currency (and of foreign assets) when they are active.
Daily frequency, many trades, and FX majors have the lowest CFD costs.

## Rules
Pairs: EURUSD, GBPUSD, AUDUSD (quote USD) and USDJPY, USDCAD, USDCHF (base USD).
Windows (local wall-clock, DST aware):
- `US`: 08:00-12:00 New York (USD home hours): sell USD (long EURUSD/GBPUSD/AUDUSD, short USDJPY/USDCAD/USDCHF).
- `home`: the non-USD currency's home hours: EUR, CHF 08:00-12:00 Europe/Berlin; GBP 08:00-12:00 Europe/London;
  JPY 09:00-13:00 Asia/Tokyo; AUD 09:00-13:00 Australia/Sydney; CAD is excluded from `home` (its hours overlap the US window).
  Sell the home currency (short EURUSD/GBPUSD/AUDUSD, long USDJPY/USDCHF).
- `H` = hold the first 2 hours or the full 4 hours of the window (entry at window start, time exit).
- Stop: 3 x ex-ante expected std of the holding window (`expected_bar_vol`), market entry at the window start.
- Weekdays only; skip if a bar is missing within 5 minutes of entry or exit.

## Grid
`window` in {US, home} x `H` in {2h, 4h}: 4 configurations per pair (US-window configs for all six pairs,
home-window configs for five), 22 configurations in total.

## Pass criteria
Per configuration: >= 200 trades, mean R > 0 with t > 2.0 in IS, positive with spread x1.5. Because the
mechanism is cross-sectional, also report the equal-weight pooled result per (window, H) across pairs; the
pooled t-stat must exceed 2.5 and at least 4 of the pairs must have a positive mean.
