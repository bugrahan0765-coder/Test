# C1 - Systematic scan of conditional intraday return patterns

**Status:** pre-registered, not yet run.

## Why a scan
A1, A2, B1-B3 showed that individual textbook effects are too weak after CFD costs. The prop
economics study (research/reports/prop_economics.md) shows that a portfolio of components with
about +0.05 R after costs is enough. A scan looks for such components across many simple,
mechanism-plausible rules, and protects against data mining with a split-sample design and
an explicit count of every configuration tested.

## Rule family (all decided at the entry instant from closed M1 bars only)
- Instruments: US100, US500, XAUUSD.
- Entry slot `t`: every 30 minutes from 02:00 to 15:30 New York time (28 slots), weekdays.
- Holding period `H` in {60, 120, 240} minutes; trades whose exit would fall after 16:00 ET or into the
  daily break are not taken for that slot/H.
- Conditioning signal `x` (vol-normalised, ex-ante `expected_bar_vol`):
  - `none`: x = +1 (pure time-of-day drift, long);
  - `day`: return from the previous 16:00 ET close to t;
  - `recent`: return over the H minutes before t.
- Rule `follow` (side = sign(x)) or `fade` (side = -sign(x)); for `none` only follow/fade = long/short.
- Threshold: trade only when |x| >= 0.5 (for `day`/`recent`); `none` always trades.
- Configuration count: 28 x 3 x 3 x 2 = 504 per instrument, 1,512 in total.

## Measurement (fast, vectorised; no stops)
Per trade: R-like unit = (side x log return over the holding window - cost) / expected std of the
window, where cost = (assumed spread + 2 x slippage) / entry price, expected std = sqrt of summed
`expected_bar_vol` variances over the window. This is the trade return in units of a 1-sigma stop.

## Sample split (all inside IS)
- Discovery: 2015-01-01 .. 2018-12-31
- Confirmation: 2019-01-01 .. 2020-12-31
- OOS (2021-2023) is not touched by this scan.

## Selection rule (fixed in advance)
A configuration is a candidate if all hold:
1. discovery: mean > 0 after costs, t > 3.0 (about a Bonferroni-like bar for ~1,500 tests at one-sided 5% is
   t ~ 3.4; 3.0 plus the confirmation step is the agreed compromise);
2. confirmation: mean > 0, t > 2.0;
3. the same slot/H/x/rule has a positive discovery mean on the sister instrument (US100 <-> US500; XAUUSD has
   no sister and needs t > 3.4 in discovery);
4. at least 300 discovery trades.
Report also the deflated Sharpe of each candidate using all 1,512 configurations as the trial set.

## Next step for candidates
Candidates are re-implemented as engine strategies with a k-sigma stop (k in {1.5, 2.5}), checked with
realistic fills, then combined into a portfolio and evaluated once on OOS 2021-2023.
