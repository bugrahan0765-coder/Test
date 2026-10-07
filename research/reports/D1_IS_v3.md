# D1 in-sample results: FX time-of-day (2015-2020, excluded months removed, cost model v2)

Spec: research/hypotheses/D1_fx_time_of_day.md. Trades enter at the window start and exit after H hours (stop 3 x ex-ante expected std of the window). Costs: FX cost model v2 (spread 0.6 bp + 0.1 bp slippage/side + 5% p.a. financing), stress x1.5 spread.

## EURUSD (25s)

| config          |   spread_mult |    n |   win_rate |   avg_R |   t_stat |   profit_factor |   total_R |   worst_mae_R |
|:----------------|--------------:|-----:|-----------:|--------:|---------:|----------------:|----------:|--------------:|
| window=US,H=2   |           1   | 1433 |      0.477 |  -0.005 |   -0.527 |           0.962 |    -6.632 |        -1.012 |
| window=US,H=2   |           1.5 | 1433 |      0.466 |  -0.011 |   -1.26  |           0.912 |   -15.864 |        -1.012 |
| window=US,H=4   |           1   | 1433 |      0.495 |  -0.005 |   -0.588 |           0.958 |    -7.252 |        -1.004 |
| window=US,H=4   |           1.5 | 1433 |      0.488 |  -0.01  |   -1.138 |           0.921 |   -14.033 |        -1.004 |
| window=home,H=2 |           1   | 1431 |      0.468 |  -0.016 |   -1.916 |           0.875 |   -23.301 |        -1.009 |
| window=home,H=2 |           1.5 | 1431 |      0.46  |  -0.025 |   -2.903 |           0.817 |   -35.327 |        -1.009 |
| window=home,H=4 |           1   | 1431 |      0.486 |  -0.003 |   -0.385 |           0.973 |    -4.555 |        -1.008 |
| window=home,H=4 |           1.5 | 1431 |      0.477 |  -0.009 |   -1.127 |           0.924 |   -13.338 |        -1.008 |

## GBPUSD (24s)

| config          |   spread_mult |    n |   win_rate |   avg_R |   t_stat |   profit_factor |   total_R |   worst_mae_R |
|:----------------|--------------:|-----:|-----------:|--------:|---------:|----------------:|----------:|--------------:|
| window=US,H=2   |           1   | 1432 |      0.467 |  -0.012 |   -1.409 |           0.906 |   -17.786 |        -1.018 |
| window=US,H=2   |           1.5 | 1432 |      0.461 |  -0.019 |   -2.102 |           0.863 |   -26.514 |        -1.018 |
| window=US,H=4   |           1   | 1432 |      0.484 |  -0.007 |   -0.74  |           0.95  |    -9.336 |        -1.013 |
| window=US,H=4   |           1.5 | 1432 |      0.478 |  -0.011 |   -1.228 |           0.918 |   -15.486 |        -1.013 |
| window=home,H=2 |           1   | 1431 |      0.495 |  -0.012 |   -1.368 |           0.909 |   -17.822 |        -1.016 |
| window=home,H=2 |           1.5 | 1431 |      0.484 |  -0.019 |   -2.041 |           0.867 |   -26.57  |        -1.016 |
| window=home,H=4 |           1   | 1431 |      0.487 |  -0.01  |   -1.088 |           0.928 |   -14.19  |        -1.011 |
| window=home,H=4 |           1.5 | 1431 |      0.482 |  -0.015 |   -1.63  |           0.894 |   -21.291 |        -1.011 |

## AUDUSD (24s)

| config          |   spread_mult |    n |   win_rate |   avg_R |   t_stat |   profit_factor |   total_R |   worst_mae_R |
|:----------------|--------------:|-----:|-----------:|--------:|---------:|----------------:|----------:|--------------:|
| window=US,H=2   |           1   | 1433 |      0.458 |  -0.027 |   -3.236 |           0.795 |   -38.565 |        -1.015 |
| window=US,H=2   |           1.5 | 1433 |      0.449 |  -0.033 |   -3.964 |           0.756 |   -47.223 |        -1.015 |
| window=US,H=4   |           1   | 1433 |      0.47  |  -0.021 |   -2.56  |           0.838 |   -30.383 |        -1.01  |
| window=US,H=4   |           1.5 | 1433 |      0.461 |  -0.026 |   -3.104 |           0.807 |   -36.918 |        -1.01  |
| window=home,H=2 |           1   | 1327 |      0.42  |  -0.037 |   -4.553 |           0.716 |   -48.622 |        -1.016 |
| window=home,H=2 |           1.5 | 1327 |      0.413 |  -0.045 |   -5.63  |           0.662 |   -60.111 |        -1.016 |
| window=home,H=4 |           1   | 1327 |      0.444 |  -0.021 |   -2.509 |           0.827 |   -28.404 |        -1.026 |
| window=home,H=4 |           1.5 | 1327 |      0.437 |  -0.026 |   -3.06  |           0.793 |   -34.63  |        -1.026 |

## USDJPY (25s)

| config          |   spread_mult |    n |   win_rate |   avg_R |   t_stat |   profit_factor |   total_R |   worst_mae_R |
|:----------------|--------------:|-----:|-----------:|--------:|---------:|----------------:|----------:|--------------:|
| window=US,H=2   |           1   | 1432 |      0.466 |  -0.012 |   -1.329 |           0.905 |   -17.865 |        -1.011 |
| window=US,H=2   |           1.5 | 1432 |      0.455 |  -0.02  |   -2.128 |           0.853 |   -28.57  |        -1.011 |
| window=US,H=4   |           1   | 1433 |      0.485 |  -0.003 |   -0.319 |           0.977 |    -4.143 |        -1.007 |
| window=US,H=4   |           1.5 | 1433 |      0.478 |  -0.008 |   -0.909 |           0.937 |   -11.793 |        -1.007 |
| window=home,H=2 |           1   | 1434 |      0.453 |  -0.045 |   -5.041 |           0.698 |   -63.866 |        -1.022 |
| window=home,H=2 |           1.5 | 1434 |      0.446 |  -0.053 |   -6.035 |           0.651 |   -76.34  |        -1.022 |
| window=home,H=4 |           1   | 1434 |      0.444 |  -0.046 |   -5.482 |           0.673 |   -65.806 |        -1.012 |
| window=home,H=4 |           1.5 | 1434 |      0.43  |  -0.053 |   -6.362 |           0.631 |   -76.605 |        -1.012 |

## USDCAD (13s)

| config        |   spread_mult |    n |   win_rate |   avg_R |   t_stat |   profit_factor |   total_R |   worst_mae_R |
|:--------------|--------------:|-----:|-----------:|--------:|---------:|----------------:|----------:|--------------:|
| window=US,H=2 |           1   | 1432 |      0.468 |  -0.024 |   -2.847 |           0.813 |   -34.172 |        -1.351 |
| window=US,H=2 |           1.5 | 1432 |      0.458 |  -0.03  |   -3.571 |           0.771 |   -42.837 |        -1.355 |
| window=US,H=4 |           1   | 1432 |      0.476 |  -0.017 |   -2.065 |           0.865 |   -24.567 |        -1.037 |
| window=US,H=4 |           1.5 | 1432 |      0.467 |  -0.021 |   -2.581 |           0.834 |   -30.688 |        -1.041 |

## USDCHF (25s)

| config          |   spread_mult |    n |   win_rate |   avg_R |   t_stat |   profit_factor |   total_R |   worst_mae_R |
|:----------------|--------------:|-----:|-----------:|--------:|---------:|----------------:|----------:|--------------:|
| window=US,H=2   |           1   | 1432 |      0.478 |   0.005 |    0.555 |           1.041 |     6.713 |        -1.008 |
| window=US,H=2   |           1.5 | 1432 |      0.474 |  -0.002 |   -0.236 |           0.983 |    -2.849 |        -1.008 |
| window=US,H=4   |           1   | 1432 |      0.508 |   0.004 |    0.55  |           1.039 |     6.371 |        -1.005 |
| window=US,H=4   |           1.5 | 1432 |      0.497 |  -0     |   -0.034 |           0.998 |    -0.395 |        -1.005 |
| window=home,H=2 |           1   | 1430 |      0.468 |  -0.035 |   -4.267 |           0.747 |   -49.804 |        -1.012 |
| window=home,H=2 |           1.5 | 1430 |      0.457 |  -0.043 |   -5.283 |           0.696 |   -61.65  |        -1.012 |
| window=home,H=4 |           1   | 1430 |      0.479 |  -0.018 |   -2.118 |           0.865 |   -25.074 |        -1.009 |
| window=home,H=4 |           1.5 | 1430 |      0.47  |  -0.024 |   -2.846 |           0.822 |   -33.684 |        -1.009 |

## Cross-pair summary (base costs)

| config          |   ('avg_R', 'AUDUSD') |   ('avg_R', 'EURUSD') |   ('avg_R', 'GBPUSD') |   ('avg_R', 'USDCAD') |   ('avg_R', 'USDCHF') |   ('avg_R', 'USDJPY') |   ('t_stat', 'AUDUSD') |   ('t_stat', 'EURUSD') |   ('t_stat', 'GBPUSD') |   ('t_stat', 'USDCAD') |   ('t_stat', 'USDCHF') |   ('t_stat', 'USDJPY') |   ('n', 'AUDUSD') |   ('n', 'EURUSD') |   ('n', 'GBPUSD') |   ('n', 'USDCAD') |   ('n', 'USDCHF') |   ('n', 'USDJPY') |
|:----------------|----------------------:|----------------------:|----------------------:|----------------------:|----------------------:|----------------------:|-----------------------:|-----------------------:|-----------------------:|-----------------------:|-----------------------:|-----------------------:|------------------:|------------------:|------------------:|------------------:|------------------:|------------------:|
| window=US,H=2   |                -0.027 |                -0.005 |                -0.012 |                -0.024 |                 0.005 |                -0.012 |                 -3.236 |                 -0.527 |                 -1.409 |                 -2.847 |                  0.555 |                 -1.329 |              1433 |              1433 |              1432 |              1432 |              1432 |              1432 |
| window=US,H=4   |                -0.021 |                -0.005 |                -0.007 |                -0.017 |                 0.004 |                -0.003 |                 -2.56  |                 -0.588 |                 -0.74  |                 -2.065 |                  0.55  |                 -0.319 |              1433 |              1433 |              1432 |              1432 |              1432 |              1433 |
| window=home,H=2 |                -0.037 |                -0.016 |                -0.012 |               nan     |                -0.035 |                -0.045 |                 -4.553 |                 -1.916 |                 -1.368 |                nan     |                 -4.267 |                 -5.041 |              1327 |              1431 |              1431 |               nan |              1430 |              1434 |
| window=home,H=4 |                -0.021 |                -0.003 |                -0.01  |               nan     |                -0.018 |                -0.046 |                 -2.509 |                 -0.385 |                 -1.088 |                nan     |                 -2.118 |                 -5.482 |              1327 |              1431 |              1431 |               nan |              1430 |              1434 |

## Pooled evaluation per (window, H), base costs

pooled mean R / t over all trades of all pairs; eqwt = mean of the per-pair mean R; t_day_clustered = t-stat of the per-day average R across pairs (informational, not a spec criterion); x1.5 = pooled mean R with spread x1.5 (informational for D1).

| window   |   H |   pairs |   n_trades |   pooled_mean_R |   pooled_t |   eqwt_mean_R |   pairs_positive |   t_day_clustered |   pooled_mean_R_x1.5 | verdict   |
|:---------|----:|--------:|-----------:|----------------:|-----------:|--------------:|-----------------:|------------------:|---------------------:|:----------|
| US       |   2 |       6 |       8594 |          -0.013 |     -3.549 |        -0.013 |                1 |            -1.947 |               -0.019 | FAIL      |
| US       |   4 |       6 |       8595 |          -0.008 |     -2.315 |        -0.008 |                1 |            -1.295 |               -0.013 | FAIL      |
| home     |   2 |       5 |       7053 |          -0.029 |     -7.534 |        -0.029 |                0 |            -6.364 |               -0.037 | FAIL      |
| home     |   4 |       5 |       7053 |          -0.02  |     -5.131 |        -0.02  |                0 |            -4.179 |               -0.025 | FAIL      |

Per-pair mean R by group (base costs):

| symbol   |   US 2h |   US 4h |   home 2h |   home 4h |
|:---------|--------:|--------:|----------:|----------:|
| EURUSD   | -0.0046 | -0.0051 |   -0.0163 |   -0.0032 |
| GBPUSD   | -0.0124 | -0.0065 |   -0.0125 |   -0.0099 |
| AUDUSD   | -0.0269 | -0.0212 |   -0.0366 |   -0.0214 |
| USDJPY   | -0.0125 | -0.0029 |   -0.0445 |   -0.0459 |
| USDCAD   | -0.0239 | -0.0172 |  nan      |  nan      |
| USDCHF   |  0.0047 |  0.0044 |   -0.0348 |   -0.0175 |

## Verdicts

Per-pair configuration criteria: n >= 200, mean R > 0, t > 2.0, mean R > 0 with spread x1.5.

| symbol   | config          |    n |   avg_R |      t |   avg_R_x1.5 | verdict   |
|:---------|:----------------|-----:|--------:|-------:|-------------:|:----------|
| EURUSD   | window=US,H=2   | 1433 |  -0.005 | -0.527 |       -0.011 | FAIL      |
| EURUSD   | window=US,H=4   | 1433 |  -0.005 | -0.588 |       -0.01  | FAIL      |
| EURUSD   | window=home,H=2 | 1431 |  -0.016 | -1.916 |       -0.025 | FAIL      |
| EURUSD   | window=home,H=4 | 1431 |  -0.003 | -0.385 |       -0.009 | FAIL      |
| GBPUSD   | window=US,H=2   | 1432 |  -0.012 | -1.409 |       -0.019 | FAIL      |
| GBPUSD   | window=US,H=4   | 1432 |  -0.007 | -0.74  |       -0.011 | FAIL      |
| GBPUSD   | window=home,H=2 | 1431 |  -0.012 | -1.368 |       -0.019 | FAIL      |
| GBPUSD   | window=home,H=4 | 1431 |  -0.01  | -1.088 |       -0.015 | FAIL      |
| AUDUSD   | window=US,H=2   | 1433 |  -0.027 | -3.236 |       -0.033 | FAIL      |
| AUDUSD   | window=US,H=4   | 1433 |  -0.021 | -2.56  |       -0.026 | FAIL      |
| AUDUSD   | window=home,H=2 | 1327 |  -0.037 | -4.553 |       -0.045 | FAIL      |
| AUDUSD   | window=home,H=4 | 1327 |  -0.021 | -2.509 |       -0.026 | FAIL      |
| USDJPY   | window=US,H=2   | 1432 |  -0.012 | -1.329 |       -0.02  | FAIL      |
| USDJPY   | window=US,H=4   | 1433 |  -0.003 | -0.319 |       -0.008 | FAIL      |
| USDJPY   | window=home,H=2 | 1434 |  -0.045 | -5.041 |       -0.053 | FAIL      |
| USDJPY   | window=home,H=4 | 1434 |  -0.046 | -5.482 |       -0.053 | FAIL      |
| USDCAD   | window=US,H=2   | 1432 |  -0.024 | -2.847 |       -0.03  | FAIL      |
| USDCAD   | window=US,H=4   | 1432 |  -0.017 | -2.065 |       -0.021 | FAIL      |
| USDCHF   | window=US,H=2   | 1432 |   0.005 |  0.555 |       -0.002 | FAIL      |
| USDCHF   | window=US,H=4   | 1432 |   0.004 |  0.55  |       -0     | FAIL      |
| USDCHF   | window=home,H=2 | 1430 |  -0.035 | -4.267 |       -0.043 | FAIL      |
| USDCHF   | window=home,H=4 | 1430 |  -0.018 | -2.118 |       -0.024 | FAIL      |

Pooled group criteria: pooled t > 2.5 and >= 4 pairs with positive mean R.

- **FAIL** D1 window=US, H=2h: pooled mean R -0.0126, pooled t -3.55 (need > 2.5), pairs positive 1/6 (need >= 4); x1.5 spread pooled mean R -0.0191
- **FAIL** D1 window=US, H=4h: pooled mean R -0.0081, pooled t -2.31 (need > 2.5), pairs positive 1/6 (need >= 4); x1.5 spread pooled mean R -0.0127
- **FAIL** D1 window=home, H=2h: pooled mean R -0.0288, pooled t -7.53 (need > 2.5), pairs positive 0/5 (need >= 4); x1.5 spread pooled mean R -0.0369
- **FAIL** D1 window=home, H=4h: pooled mean R -0.0196, pooled t -5.13 (need > 2.5), pairs positive 0/5 (need >= 4); x1.5 spread pooled mean R -0.0255

Per-pair configurations passing: 0 of 22. Pooled groups passing: 0 of 4.

**D1 OVERALL: FAIL** (no pooled group passes).
