# Cost model versions

## v1 (2026-10-06, first runs)
Constant spread in price points (US100 2.0, US500 0.6, GER40 1.5, XAUUSD 0.30) plus constant slippage
in points. Because index levels rose ~5x between 2015 and 2025 while CFD spreads in points stayed
roughly constant, v1 charged 2015-2020 trades several times more (relative to price and volatility)
than the same trade costs today. That made the in-sample results unrepresentative of what the strategy
would pay when traded now.

## v2 (current)
Costs as a fraction of price: full spread 1.0 bp + slippage 0.2 bp per side (round trip 1.4 bp) for
US100, US500, GER40, XAUUSD (`harness.COST_BPS`), financing 5%/yr per night. Conservative against
typical FTMO quotes (e.g. US100 ~1.5-2 points at ~25,000 = 0.6-0.8 bp). To be replaced by measured FTMO
spreads, commissions and swaps from an MT5 export.

Hypothesis rules and pass criteria were not changed. All v2 runs are logged as separate trials
(`<id>_v2`, `C1v2`) so the deflated Sharpe counts both.

## v2 in-sample outcome (2015-2020)
| Hyp | Best config (both instruments) | Result |
|---|---|---|
| A1 | z=1,k=2.5,confirm: US100 +0.02 R (t 0.51), US500 -0.01 R | rejected |
| A2 | N=15 breakout: US100 +0.18 R (t 1.84), US500 -0.03 R | rejected (not on both) |
| B1 | d_in=-1,d_out=3,k=2: US100 +0.106 R (t 1.70), US500 +0.106 R (t 1.38) | not passed (t > 1.5 on both required), closest |
| B2 | US100 +0.012 R (t 1.33), US500 ~0 | rejected |
| B3 | L=120,k=3,long-only: US100 +0.03 R (t 1.48), US500 +0.015, XAUUSD +0.014 | rejected |
| C1 | 0 candidates of 1,512; 3 configs with discovery t > 2 vs ~30 expected under the null | rejected |
