# D1 in-sample results: FX time-of-day (2015-2020, excluded months removed, cost model v2)

Spec: research/hypotheses/D1_fx_time_of_day.md. Trades enter at the window start and exit after H hours (stop 3 x ex-ante expected std of the window). Costs: FX cost model v2 (spread 0.6 bp + 0.1 bp slippage/side + 5% p.a. financing), stress x1.5 spread.

## EURUSD (24s)

| config          |   spread_mult |    n |   win_rate |   avg_R |   t_stat |   profit_factor |   total_R |   worst_mae_R |
|:----------------|--------------:|-----:|-----------:|--------:|---------:|----------------:|----------:|--------------:|
| window=US,H=2   |           1   | 1445 |      0.481 |  -0.009 |   -1.278 |           0.91  |   -12.437 |        -1.007 |
| window=US,H=2   |           1.5 | 1445 |      0.473 |  -0.013 |   -1.886 |           0.87  |   -18.355 |        -1.007 |
| window=US,H=4   |           1   | 1445 |      0.477 |  -0.01  |   -1.404 |           0.905 |   -13.759 |        -1.005 |
| window=US,H=4   |           1.5 | 1445 |      0.472 |  -0.012 |   -1.826 |           0.879 |   -17.885 |        -1.005 |
| window=home,H=2 |           1   | 1443 |      0.479 |  -0.012 |   -1.63  |           0.888 |   -16.717 |        -1.007 |
| window=home,H=2 |           1.5 | 1443 |      0.465 |  -0.018 |   -2.472 |           0.835 |   -25.342 |        -1.007 |
| window=home,H=4 |           1   | 1443 |      0.488 |  -0     |   -0.059 |           0.996 |    -0.574 |        -1.004 |
| window=home,H=4 |           1.5 | 1443 |      0.482 |  -0.004 |   -0.631 |           0.957 |    -6.115 |        -1.004 |

## GBPUSD (24s)

| config          |   spread_mult |    n |   win_rate |   avg_R |   t_stat |   profit_factor |   total_R |   worst_mae_R |
|:----------------|--------------:|-----:|-----------:|--------:|---------:|----------------:|----------:|--------------:|
| window=US,H=2   |           1   | 1444 |      0.481 |  -0.012 |   -1.567 |           0.893 |   -16.692 |        -1.379 |
| window=US,H=2   |           1.5 | 1444 |      0.476 |  -0.015 |   -2.083 |           0.861 |   -22.187 |        -1.379 |
| window=US,H=4   |           1   | 1444 |      0.495 |  -0.005 |   -0.638 |           0.957 |    -7.072 |        -1.249 |
| window=US,H=4   |           1.5 | 1444 |      0.493 |  -0.008 |   -0.981 |           0.935 |   -10.871 |        -1.249 |
| window=home,H=2 |           1   | 1443 |      0.517 |   0.007 |    0.995 |           1.071 |    10.373 |        -1.003 |
| window=home,H=2 |           1.5 | 1443 |      0.511 |   0.003 |    0.418 |           1.029 |     4.353 |        -1.003 |
| window=home,H=4 |           1   | 1443 |      0.501 |   0.001 |    0.188 |           1.013 |     1.987 |        -1.003 |
| window=home,H=4 |           1.5 | 1443 |      0.498 |  -0.001 |   -0.205 |           0.986 |    -2.163 |        -1.003 |

## AUDUSD (23s)

| config          |   spread_mult |    n |   win_rate |   avg_R |   t_stat |   profit_factor |   total_R |   worst_mae_R |
|:----------------|--------------:|-----:|-----------:|--------:|---------:|----------------:|----------:|--------------:|
| window=US,H=2   |           1   | 1445 |      0.468 |  -0.017 |   -2.47  |           0.839 |   -24.426 |        -1.006 |
| window=US,H=2   |           1.5 | 1445 |      0.461 |  -0.021 |   -3.075 |           0.803 |   -30.499 |        -1.013 |
| window=US,H=4   |           1   | 1445 |      0.482 |  -0.014 |   -1.994 |           0.868 |   -20.136 |        -1.004 |
| window=US,H=4   |           1.5 | 1445 |      0.478 |  -0.017 |   -2.369 |           0.846 |   -23.919 |        -1.004 |
| window=home,H=2 |           1   | 1301 |      0.417 |  -0.028 |   -4.275 |           0.71  |   -37.073 |        -1.014 |
| window=home,H=2 |           1.5 | 1301 |      0.404 |  -0.035 |   -5.178 |           0.661 |   -44.897 |        -1.014 |
| window=home,H=4 |           1   | 1301 |      0.45  |  -0.017 |   -2.44  |           0.828 |   -22.238 |        -1.022 |
| window=home,H=4 |           1.5 | 1301 |      0.446 |  -0.02  |   -2.867 |           0.801 |   -26.125 |        -1.022 |

## USDJPY (24s)

| config          |   spread_mult |    n |   win_rate |   avg_R |   t_stat |   profit_factor |   total_R |   worst_mae_R |
|:----------------|--------------:|-----:|-----------:|--------:|---------:|----------------:|----------:|--------------:|
| window=US,H=2   |           1   | 1444 |      0.46  |  -0.014 |   -1.836 |           0.871 |   -20.84  |        -1.011 |
| window=US,H=2   |           1.5 | 1444 |      0.449 |  -0.02  |   -2.503 |           0.829 |   -28.392 |        -1.011 |
| window=US,H=4   |           1   | 1445 |      0.486 |  -0.003 |   -0.322 |           0.977 |    -3.704 |        -1.006 |
| window=US,H=4   |           1.5 | 1445 |      0.476 |  -0.006 |   -0.754 |           0.947 |    -8.662 |        -1.007 |
| window=home,H=2 |           1   | 1445 |      0.475 |  -0.03  |   -3.951 |           0.756 |   -43.232 |        -1.01  |
| window=home,H=2 |           1.5 | 1445 |      0.464 |  -0.036 |   -4.758 |           0.714 |   -52.033 |        -1.01  |
| window=home,H=4 |           1   | 1445 |      0.469 |  -0.034 |   -4.449 |           0.717 |   -49.084 |        -2.857 |
| window=home,H=4 |           1.5 | 1445 |      0.462 |  -0.038 |   -5.031 |           0.686 |   -55.473 |        -2.86  |

## USDCAD (12s)

| config        |   spread_mult |    n |   win_rate |   avg_R |   t_stat |   profit_factor |   total_R |   worst_mae_R |
|:--------------|--------------:|-----:|-----------:|--------:|---------:|----------------:|----------:|--------------:|
| window=US,H=2 |           1   | 1444 |      0.458 |  -0.02  |   -2.685 |           0.823 |   -28.823 |        -1.006 |
| window=US,H=2 |           1.5 | 1444 |      0.448 |  -0.024 |   -3.265 |           0.79  |   -35.049 |        -1.006 |
| window=US,H=4 |           1   | 1444 |      0.467 |  -0.018 |   -2.363 |           0.845 |   -25.566 |        -1.035 |
| window=US,H=4 |           1.5 | 1444 |      0.461 |  -0.021 |   -2.747 |           0.823 |   -29.713 |        -1.038 |

## USDCHF (23s)

| config          |   spread_mult |    n |   win_rate |   avg_R |   t_stat |   profit_factor |   total_R |   worst_mae_R |
|:----------------|--------------:|-----:|-----------:|--------:|---------:|----------------:|----------:|--------------:|
| window=US,H=2   |           1   | 1444 |      0.475 |  -0.005 |   -0.735 |           0.948 |    -7.346 |        -1.007 |
| window=US,H=2   |           1.5 | 1444 |      0.465 |  -0.01  |   -1.376 |           0.905 |   -13.742 |        -1.007 |
| window=US,H=4   |           1   | 1444 |      0.497 |   0.002 |    0.259 |           1.018 |     2.488 |        -1.005 |
| window=US,H=4   |           1.5 | 1444 |      0.493 |  -0.001 |   -0.187 |           0.987 |    -1.799 |        -1.005 |
| window=home,H=2 |           1   | 1442 |      0.48  |  -0.014 |   -2.028 |           0.865 |   -20.069 |        -1.008 |
| window=home,H=2 |           1.5 | 1442 |      0.467 |  -0.02  |   -2.958 |           0.81  |   -29.262 |        -1.008 |
| window=home,H=4 |           1   | 1442 |      0.482 |  -0.012 |   -1.804 |           0.882 |   -17.733 |        -1.006 |
| window=home,H=4 |           1.5 | 1442 |      0.474 |  -0.016 |   -2.381 |           0.848 |   -23.407 |        -1.006 |

## Cross-pair summary (base costs)

| config          |   ('avg_R', 'AUDUSD') |   ('avg_R', 'EURUSD') |   ('avg_R', 'GBPUSD') |   ('avg_R', 'USDCAD') |   ('avg_R', 'USDCHF') |   ('avg_R', 'USDJPY') |   ('t_stat', 'AUDUSD') |   ('t_stat', 'EURUSD') |   ('t_stat', 'GBPUSD') |   ('t_stat', 'USDCAD') |   ('t_stat', 'USDCHF') |   ('t_stat', 'USDJPY') |   ('n', 'AUDUSD') |   ('n', 'EURUSD') |   ('n', 'GBPUSD') |   ('n', 'USDCAD') |   ('n', 'USDCHF') |   ('n', 'USDJPY') |
|:----------------|----------------------:|----------------------:|----------------------:|----------------------:|----------------------:|----------------------:|-----------------------:|-----------------------:|-----------------------:|-----------------------:|-----------------------:|-----------------------:|------------------:|------------------:|------------------:|------------------:|------------------:|------------------:|
| window=US,H=2   |                -0.017 |                -0.009 |                -0.012 |                -0.02  |                -0.005 |                -0.014 |                 -2.47  |                 -1.278 |                 -1.567 |                 -2.685 |                 -0.735 |                 -1.836 |              1445 |              1445 |              1444 |              1444 |              1444 |              1444 |
| window=US,H=4   |                -0.014 |                -0.01  |                -0.005 |                -0.018 |                 0.002 |                -0.003 |                 -1.994 |                 -1.404 |                 -0.638 |                 -2.363 |                  0.259 |                 -0.322 |              1445 |              1445 |              1444 |              1444 |              1444 |              1445 |
| window=home,H=2 |                -0.028 |                -0.012 |                 0.007 |               nan     |                -0.014 |                -0.03  |                 -4.275 |                 -1.63  |                  0.995 |                nan     |                 -2.028 |                 -3.951 |              1301 |              1443 |              1443 |               nan |              1442 |              1445 |
| window=home,H=4 |                -0.017 |                -0     |                 0.001 |               nan     |                -0.012 |                -0.034 |                 -2.44  |                 -0.059 |                  0.188 |                nan     |                 -1.804 |                 -4.449 |              1301 |              1443 |              1443 |               nan |              1442 |              1445 |

## Pooled evaluation per (window, H), base costs

pooled mean R / t over all trades of all pairs; eqwt = mean of the per-pair mean R; t_day_clustered = t-stat of the per-day average R across pairs (informational, not a spec criterion); x1.5 = pooled mean R with spread x1.5 (informational for D1).

| window   |   H |   pairs |   n_trades |   pooled_mean_R |   pooled_t |   eqwt_mean_R |   pairs_positive |   t_day_clustered |   pooled_mean_R_x1.5 | verdict   |
|:---------|----:|--------:|-----------:|----------------:|-----------:|--------------:|-----------------:|------------------:|---------------------:|:----------|
| US       |   2 |       6 |       8666 |          -0.013 |     -4.338 |        -0.013 |                0 |            -2.412 |               -0.017 | FAIL      |
| US       |   4 |       6 |       8667 |          -0.008 |     -2.633 |        -0.008 |                1 |            -1.509 |               -0.011 | FAIL      |
| home     |   2 |       5 |       7074 |          -0.015 |     -4.736 |        -0.015 |                1 |            -3.979 |               -0.021 | FAIL      |
| home     |   4 |       5 |       7074 |          -0.012 |     -3.888 |        -0.012 |                1 |            -3.202 |               -0.016 | FAIL      |

Per-pair mean R by group (base costs):

| symbol   |   US 2h |   US 4h |   home 2h |   home 4h |
|:---------|--------:|--------:|----------:|----------:|
| EURUSD   | -0.0086 | -0.0095 |   -0.0116 |   -0.0004 |
| GBPUSD   | -0.0116 | -0.0049 |    0.0072 |    0.0014 |
| AUDUSD   | -0.0169 | -0.0139 |   -0.0285 |   -0.0171 |
| USDJPY   | -0.0144 | -0.0026 |   -0.0299 |   -0.034  |
| USDCAD   | -0.02   | -0.0177 |  nan      |  nan      |
| USDCHF   | -0.0051 |  0.0017 |   -0.0139 |   -0.0123 |

## Verdicts

Per-pair configuration criteria: n >= 200, mean R > 0, t > 2.0, mean R > 0 with spread x1.5.

| symbol   | config          |    n |   avg_R |      t |   avg_R_x1.5 | verdict   |
|:---------|:----------------|-----:|--------:|-------:|-------------:|:----------|
| EURUSD   | window=US,H=2   | 1445 |  -0.009 | -1.278 |       -0.013 | FAIL      |
| EURUSD   | window=US,H=4   | 1445 |  -0.01  | -1.404 |       -0.012 | FAIL      |
| EURUSD   | window=home,H=2 | 1443 |  -0.012 | -1.63  |       -0.018 | FAIL      |
| EURUSD   | window=home,H=4 | 1443 |  -0     | -0.059 |       -0.004 | FAIL      |
| GBPUSD   | window=US,H=2   | 1444 |  -0.012 | -1.567 |       -0.015 | FAIL      |
| GBPUSD   | window=US,H=4   | 1444 |  -0.005 | -0.638 |       -0.008 | FAIL      |
| GBPUSD   | window=home,H=2 | 1443 |   0.007 |  0.995 |        0.003 | FAIL      |
| GBPUSD   | window=home,H=4 | 1443 |   0.001 |  0.188 |       -0.001 | FAIL      |
| AUDUSD   | window=US,H=2   | 1445 |  -0.017 | -2.47  |       -0.021 | FAIL      |
| AUDUSD   | window=US,H=4   | 1445 |  -0.014 | -1.994 |       -0.017 | FAIL      |
| AUDUSD   | window=home,H=2 | 1301 |  -0.028 | -4.275 |       -0.035 | FAIL      |
| AUDUSD   | window=home,H=4 | 1301 |  -0.017 | -2.44  |       -0.02  | FAIL      |
| USDJPY   | window=US,H=2   | 1444 |  -0.014 | -1.836 |       -0.02  | FAIL      |
| USDJPY   | window=US,H=4   | 1445 |  -0.003 | -0.322 |       -0.006 | FAIL      |
| USDJPY   | window=home,H=2 | 1445 |  -0.03  | -3.951 |       -0.036 | FAIL      |
| USDJPY   | window=home,H=4 | 1445 |  -0.034 | -4.449 |       -0.038 | FAIL      |
| USDCAD   | window=US,H=2   | 1444 |  -0.02  | -2.685 |       -0.024 | FAIL      |
| USDCAD   | window=US,H=4   | 1444 |  -0.018 | -2.363 |       -0.021 | FAIL      |
| USDCHF   | window=US,H=2   | 1444 |  -0.005 | -0.735 |       -0.01  | FAIL      |
| USDCHF   | window=US,H=4   | 1444 |   0.002 |  0.259 |       -0.001 | FAIL      |
| USDCHF   | window=home,H=2 | 1442 |  -0.014 | -2.028 |       -0.02  | FAIL      |
| USDCHF   | window=home,H=4 | 1442 |  -0.012 | -1.804 |       -0.016 | FAIL      |

Pooled group criteria: pooled t > 2.5 and >= 4 pairs with positive mean R.

- **FAIL** D1 window=US, H=2h: pooled mean R -0.0128, pooled t -4.34 (need > 2.5), pairs positive 0/6 (need >= 4); x1.5 spread pooled mean R -0.0171
- **FAIL** D1 window=US, H=4h: pooled mean R -0.0078, pooled t -2.63 (need > 2.5), pairs positive 1/6 (need >= 4); x1.5 spread pooled mean R -0.0107
- **FAIL** D1 window=home, H=2h: pooled mean R -0.0151, pooled t -4.74 (need > 2.5), pairs positive 1/5 (need >= 4); x1.5 spread pooled mean R -0.0208
- **FAIL** D1 window=home, H=4h: pooled mean R -0.0124, pooled t -3.89 (need > 2.5), pairs positive 1/5 (need >= 4); x1.5 spread pooled mean R -0.0160

Per-pair configurations passing: 0 of 22. Pooled groups passing: 0 of 4.

**D1 OVERALL: FAIL** (no pooled group passes).
