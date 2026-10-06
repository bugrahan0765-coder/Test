# Project context (read first)

The user writes in Turkish; answer in Turkish. They have ~5 years of unsuccessful manual trading
(ICT/SMC/indicators/orderflow, many blown prop challenges) and asked Claude to lead this project
end to end: a systematic intraday bot that passes prop firm challenges and earns payouts.
They have some programming knowledge. Be honest about odds; never promise profits.

**The full plan is in `PLAN.md` (Turkish). Read it before doing anything.**

## Decisions already made (don't re-litigate)
- Prop firm: FTMO 2-Step (EAs allowed on MT5, static 10% max loss, 5% daily incl. floating,
  targets 10% / 5%, min 4 trading days, day boundary = midnight Europe/Prague).
- Instruments: US100, US500, GER40 CFDs + XAUUSD; FX majors later.
- Timeframe: intraday, M5/M15 signals, holds minutes to hours, flat before the weekend.
- No classic indicators (RSI, MACD...), no martingale/grid, no news trading.
- Edge sources, in research order: intraday structural effects (intraday momentum, opening-range
  breakout, overextension mean reversion, session transitions, month-end/OPEX flows); volatility
  forecasting (HAR-RV) for sizing and filtering; regime filters (variance ratio, Hurst); later
  stat-arb and ML meta-labeling as a filter only.
- Every hypothesis follows the protocol in PLAN.md section 3: pre-registered in
  `research/hypotheses/`, in-sample ~2015-2020, out-of-sample ~2021-2023, **2024+ locked**
  until the final one-shot test, realistic + stressed costs, deflated Sharpe / PBO, every
  trial logged via `pfbot.stats.performance.TrialRegistry`.

## Code (package `pfbot`, all tests: `python -m pytest -q`)
- `pfbot/data/schema.py`: canonical bar format contract (UTC index "time", open/high/low/close mid, optional spread/volume).
- `pfbot/data/dukascopy.py`: free tick feed downloader -> M1 parquet
  (`python -m pfbot.data.dukascopy --symbol US100 --start 2015-01-01 --end 2025-12-31`).
  Index/XAUUSD point factors (1e3) are UNVERIFIED: eyeball the first download.
- `pfbot/data/store.py` (parquet under `data/bars`, gitignored), `csv_import.py` (dukascopy-node, MT5 exports), `synthetic.py`.
- `pfbot/backtest/engine.py`: conservative bar simulator (bid/ask aware, gap fills, stop-first intrabar, R and MAE per trade).
- `pfbot/propsim/`: FTMO rules, RiskPolicy, day-level account simulator, block-bootstrap Monte Carlo, `risk_sweep`, `expected_value`.
- `pfbot/features/volatility.py` (realized vol, walk-forward HAR-RV, intraday profile, expected_bar_vol), `regime.py` (variance ratio, Hurst).
- `pfbot/stats/performance.py`: Sharpe, bootstrap CI, PSR/DSR, PBO (CSCV), TrialRegistry.
- Dependencies: numpy, pandas>=3, pyarrow, scipy, statsmodels, numba, requests, pytest
  (`pip install numpy pandas pyarrow scipy statsmodels numba requests pytest`).

## Status / next steps
1. DONE: plan, data layer, backtest engine, prop simulator, volatility/regime/stats modules (tested on synthetic data only).
2. NEXT: download 2015-2025 M1 for US100, US500, GER40, XAUUSD from Dukascopy (needs network access to
   datafeed.dukascopy.com); verify price levels and spreads; write a data-quality report.
3. Then: hypotheses A1 (intraday momentum) and A2 (opening range breakout) on US100/US500 per the protocol,
   then the rest of section 2.2-A, then the FTMO Monte Carlo on the survivors.
4. Later: calibrate costs against FTMO MT5 data (user will provide exports from an FTMO Free Trial account).

Work on branch `ccr-93d9848a-98ftn2` unless told otherwise. Using subagents to test hypotheses in parallel is approved by the user.
