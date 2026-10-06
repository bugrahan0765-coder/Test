# B2 - Overnight drift (close-to-open) in equity indices

**Status:** REJECTED in-sample (2026-10-06). All configs slightly negative after spread + 5% financing
(US100 -0.006..-0.013 R, US500 -0.017..-0.025 R). See research/reports/B2_IS.md.

## Mechanism
A large share of the US equity premium has historically been earned outside cash-session hours
(Cliff, Cooper & Gulen 2008; Kelly & Clark 2011; Lou, Polk & Skouras 2019 "A tug of war"):
institutions trade intraday, retail and overseas flows and the absorption of overnight news at the
open push prices up overnight. Holding overnight costs one spread plus CFD financing per night,
which may consume most of the effect; this test answers that directly.

## Rules
Instruments: US100, US500.
- Entry: long at market at `t_in` ET on each trading day (Mon-Thu, plus Friday when `fri` is True).
- Exit: time exit at `t_out` ET on the next trading day.
- Stop: 3 x expected std of the overnight window (HAR-RV daily forecast x share of daily variance
  that falls in the overnight window, estimated from the previous 60 days only).
- Financing charged per night (weekend = 3 nights) at the harness default 5%/yr; sensitivity at 2.5% and 0%
  reported for information but the decision uses 5%.

## Grid (8 configurations per instrument)
- `t_in` in {"15:55", "16:10"}; `t_out` in {"09:31", "09:45"}; `fri` in {False, True}

## Pass criteria
Common protocol (>= 200 trades, t > 2, both instruments, plateau, spread x1.5).
