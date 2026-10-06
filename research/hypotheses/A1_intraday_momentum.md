# A1 - Market intraday momentum (last half hour)

**Status:** pre-registered, not yet tested.

## Mechanism
Gao, Han, Li, Zhou (2018, JFE): the S&P 500 ETF return from the previous close to 10:00 ET
predicts the return of the last half hour (15:30-16:00 ET). Proposed drivers: dealers hedging
short gamma trade in the direction of the day's move into the close; institutions that
rebalance or execute late in the day; late-informed traders. Effect reported stronger on
high-volatility days and on news days.

## Rules
Instruments: US100, US500 (primary), GER40 (analogue on Xetra hours, reported separately).

- `r_open` = log return from the previous session's cash close (16:00 ET bar close, last M1 bar
  before 16:00) to the 10:00 ET price (close of the 09:55 M5 bar), in units of that day's
  ex-ante expected vol over the same window (`expected_bar_vol`, no look-ahead).
  GER40 analogue: previous 17:30 Berlin close to 09:30 Berlin; trade 17:00-17:30.
- Optional confirmation `r_late` = 15:00-15:30 ET return (variant flag).
- Signal: at the close of the 15:25 M5 bar (i.e. 15:30 ET) enter `sign(r_open)` at market when
  `|r_open| >= z`; with the confirmation variant also require `sign(r_late) == sign(r_open)`.
- Exit: market at 16:00 ET (time exit = first bar >= 16:00), or protective stop.
- Stop distance: `k` x expected vol of the 30-minute holding window.
- No target.

## Grid (12 configurations per instrument)
- `z` in {0.0, 0.5, 1.0}
- `k` in {1.5, 2.5}
- `confirm` in {False, True}

## Expected size of the effect
Paper: R^2 about 1.6% on half-hour returns, i.e. small per trade. Spread on US100 about 2-3 points
against a last-half-hour sigma of about 40-60 points, so costs consume a meaningful fraction.
Prior probability of surviving costs: moderate-low. Its value is that it is nearly
uncorrelated with the morning strategies (A2).
