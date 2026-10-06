# D1 in-sample results: FX time-of-day (2015-2020, excluded months removed, cost model v2)

Spec: research/hypotheses/D1_fx_time_of_day.md. Trades enter at the window start and exit after H hours (stop 3 x ex-ante expected std of the window). Costs: FX cost model v2 (spread 0.6 bp + 0.1 bp slippage/side + 5% p.a. financing), stress x1.5 spread.

## EURUSD (24s)

| config          |   spread_mult |    n |   win_rate |   avg_R |   t_stat |   profit_factor |   total_R |   worst_mae_R |
|:----------------|--------------:|-----:|-----------:|--------:|---------:|----------------:|----------:|--------------:|
| window=US,H=2   |           1   | 1433 |      0.482 |  -0.001 |   -0.14  |           0.99  |    -1.765 |        -1.012 |
| window=US,H=2   |           1.5 | 1433 |      0.475 |  -0.006 |   -0.71  |           0.949 |    -8.94  |        -1.012 |
| window=US,H=4   |           1   | 1433 |      0.497 |  -0.003 |   -0.313 |           0.978 |    -3.861 |        -1.004 |
| window=US,H=4   |           1.5 | 1433 |      0.493 |  -0.006 |   -0.725 |           0.949 |    -8.947 |        -1.004 |
| window=home,H=2 |           1   | 1431 |      0.477 |  -0.012 |   -1.4   |           0.907 |   -16.994 |        -1.009 |
| window=home,H=2 |           1.5 | 1431 |      0.467 |  -0.018 |   -2.173 |           0.86  |   -26.454 |        -1.009 |
| window=home,H=4 |           1   | 1431 |      0.491 |  -0     |   -0.014 |           0.999 |    -0.164 |        -1.008 |
| window=home,H=4 |           1.5 | 1431 |      0.484 |  -0.005 |   -0.57  |           0.961 |    -6.751 |        -1.008 |

## GBPUSD (24s)

| config          |   spread_mult |    n |   win_rate |   avg_R |   t_stat |   profit_factor |   total_R |   worst_mae_R |
|:----------------|--------------:|-----:|-----------:|--------:|---------:|----------------:|----------:|--------------:|
| window=US,H=2   |           1   | 1432 |      0.472 |  -0.009 |   -1.063 |           0.928 |   -13.422 |        -1.018 |
| window=US,H=2   |           1.5 | 1432 |      0.466 |  -0.014 |   -1.583 |           0.895 |   -19.968 |        -1.018 |
| window=US,H=4   |           1   | 1432 |      0.488 |  -0.004 |   -0.496 |           0.966 |    -6.26  |        -1.013 |
| window=US,H=4   |           1.5 | 1432 |      0.483 |  -0.008 |   -0.862 |           0.942 |   -10.873 |        -1.013 |
| window=home,H=2 |           1   | 1431 |      0.502 |  -0.009 |   -1.03  |           0.93  |   -13.425 |        -1.016 |
| window=home,H=2 |           1.5 | 1431 |      0.494 |  -0.014 |   -1.536 |           0.898 |   -20.009 |        -1.016 |
| window=home,H=4 |           1   | 1431 |      0.49  |  -0.008 |   -0.824 |           0.945 |   -10.739 |        -1.011 |
| window=home,H=4 |           1.5 | 1431 |      0.486 |  -0.011 |   -1.252 |           0.917 |   -16.355 |        -1.011 |

## AUDUSD (23s)

| config          |   spread_mult |    n |   win_rate |   avg_R |   t_stat |   profit_factor |   total_R |   worst_mae_R |
|:----------------|--------------:|-----:|-----------:|--------:|---------:|----------------:|----------:|--------------:|
| window=US,H=2   |           1   | 1433 |      0.461 |  -0.022 |   -2.62  |           0.83  |   -31.471 |        -1.015 |
| window=US,H=2   |           1.5 | 1433 |      0.453 |  -0.028 |   -3.418 |           0.785 |   -40.73  |        -1.015 |
| window=US,H=4   |           1   | 1433 |      0.473 |  -0.019 |   -2.3   |           0.853 |   -27.304 |        -1.01  |
| window=US,H=4   |           1.5 | 1433 |      0.467 |  -0.022 |   -2.69  |           0.831 |   -31.922 |        -1.01  |
| window=home,H=2 |           1   | 1327 |      0.425 |  -0.032 |   -4.014 |           0.744 |   -42.878 |        -1.016 |
| window=home,H=2 |           1.5 | 1327 |      0.416 |  -0.039 |   -4.822 |           0.702 |   -51.495 |        -1.016 |
| window=home,H=4 |           1   | 1327 |      0.448 |  -0.019 |   -2.233 |           0.844 |   -25.291 |        -1.026 |
| window=home,H=4 |           1.5 | 1327 |      0.443 |  -0.023 |   -2.646 |           0.818 |   -29.961 |        -1.026 |

## USDJPY (24s)

| config          |   spread_mult |    n |   win_rate |   avg_R |   t_stat |   profit_factor |   total_R |   worst_mae_R |
|:----------------|--------------:|-----:|-----------:|--------:|---------:|----------------:|----------:|--------------:|
| window=US,H=2   |           1   | 1432 |      0.469 |  -0.009 |   -0.932 |           0.932 |   -12.533 |        -1.011 |
| window=US,H=2   |           1.5 | 1432 |      0.461 |  -0.014 |   -1.528 |           0.892 |   -20.531 |        -1.011 |
| window=US,H=4   |           1   | 1433 |      0.492 |   0     |    0.005 |           1     |     0.063 |        -1.007 |
| window=US,H=4   |           1.5 | 1433 |      0.482 |  -0.004 |   -0.466 |           0.967 |    -6.055 |        -1.007 |
| window=home,H=2 |           1   | 1434 |      0.462 |  -0.04  |   -4.545 |           0.723 |   -57.629 |        -1.022 |
| window=home,H=2 |           1.5 | 1434 |      0.453 |  -0.047 |   -5.289 |           0.686 |   -66.984 |        -1.022 |
| window=home,H=4 |           1   | 1434 |      0.449 |  -0.042 |   -5.065 |           0.694 |   -60.838 |        -1.012 |
| window=home,H=4 |           1.5 | 1434 |      0.439 |  -0.048 |   -5.691 |           0.663 |   -68.293 |        -1.012 |

## USDCAD (12s)

| config        |   spread_mult |    n |   win_rate |   avg_R |   t_stat |   profit_factor |   total_R |   worst_mae_R |
|:--------------|--------------:|-----:|-----------:|--------:|---------:|----------------:|----------:|--------------:|
| window=US,H=2 |           1   | 1432 |      0.475 |  -0.021 |   -2.485 |           0.834 |   -29.84  |        -1.348 |
| window=US,H=2 |           1.5 | 1432 |      0.464 |  -0.025 |   -3.028 |           0.802 |   -36.338 |        -1.352 |
| window=US,H=4 |           1   | 1432 |      0.48  |  -0.015 |   -1.808 |           0.88  |   -21.506 |        -1.036 |
| window=US,H=4 |           1.5 | 1432 |      0.472 |  -0.018 |   -2.194 |           0.857 |   -26.097 |        -1.038 |

## USDCHF (24s)

| config          |   spread_mult |    n |   win_rate |   avg_R |   t_stat |   profit_factor |   total_R |   worst_mae_R |
|:----------------|--------------:|-----:|-----------:|--------:|---------:|----------------:|----------:|--------------:|
| window=US,H=2   |           1   | 1432 |      0.483 |   0.008 |    0.95  |           1.071 |    11.494 |        -1.008 |
| window=US,H=2   |           1.5 | 1432 |      0.478 |   0.003 |    0.357 |           1.026 |     4.323 |        -1.008 |
| window=US,H=4   |           1   | 1432 |      0.513 |   0.007 |    0.842 |           1.061 |     9.753 |        -1.005 |
| window=US,H=4   |           1.5 | 1432 |      0.506 |   0.003 |    0.404 |           1.029 |     4.679 |        -1.005 |
| window=home,H=2 |           1   | 1430 |      0.471 |  -0.031 |   -3.759 |           0.773 |   -43.882 |        -1.012 |
| window=home,H=2 |           1.5 | 1430 |      0.466 |  -0.037 |   -4.521 |           0.734 |   -52.766 |        -1.012 |
| window=home,H=4 |           1   | 1430 |      0.483 |  -0.015 |   -1.754 |           0.886 |   -20.77  |        -1.009 |
| window=home,H=4 |           1.5 | 1430 |      0.477 |  -0.019 |   -2.3   |           0.854 |   -27.227 |        -1.009 |

## Cross-pair summary (base costs)

| config          |   ('avg_R', 'AUDUSD') |   ('avg_R', 'EURUSD') |   ('avg_R', 'GBPUSD') |   ('avg_R', 'USDCAD') |   ('avg_R', 'USDCHF') |   ('avg_R', 'USDJPY') |   ('t_stat', 'AUDUSD') |   ('t_stat', 'EURUSD') |   ('t_stat', 'GBPUSD') |   ('t_stat', 'USDCAD') |   ('t_stat', 'USDCHF') |   ('t_stat', 'USDJPY') |   ('n', 'AUDUSD') |   ('n', 'EURUSD') |   ('n', 'GBPUSD') |   ('n', 'USDCAD') |   ('n', 'USDCHF') |   ('n', 'USDJPY') |
|:----------------|----------------------:|----------------------:|----------------------:|----------------------:|----------------------:|----------------------:|-----------------------:|-----------------------:|-----------------------:|-----------------------:|-----------------------:|-----------------------:|------------------:|------------------:|------------------:|------------------:|------------------:|------------------:|
| window=US,H=2   |                -0.022 |                -0.001 |                -0.009 |                -0.021 |                 0.008 |                -0.009 |                 -2.62  |                 -0.14  |                 -1.063 |                 -2.485 |                  0.95  |                 -0.932 |              1433 |              1433 |              1432 |              1432 |              1432 |              1432 |
| window=US,H=4   |                -0.019 |                -0.003 |                -0.004 |                -0.015 |                 0.007 |                 0     |                 -2.3   |                 -0.313 |                 -0.496 |                 -1.808 |                  0.842 |                  0.005 |              1433 |              1433 |              1432 |              1432 |              1432 |              1433 |
| window=home,H=2 |                -0.032 |                -0.012 |                -0.009 |               nan     |                -0.031 |                -0.04  |                 -4.014 |                 -1.4   |                 -1.03  |                nan     |                 -3.759 |                 -4.545 |              1327 |              1431 |              1431 |               nan |              1430 |              1434 |
| window=home,H=4 |                -0.019 |                -0     |                -0.008 |               nan     |                -0.015 |                -0.042 |                 -2.233 |                 -0.014 |                 -0.824 |                nan     |                 -1.754 |                 -5.065 |              1327 |              1431 |              1431 |               nan |              1430 |              1434 |

## Pooled evaluation per (window, H), base costs

pooled mean R / t over all trades of all pairs; eqwt = mean of the per-pair mean R; t_day_clustered = t-stat of the per-day average R across pairs (informational, not a spec criterion); x1.5 = pooled mean R with spread x1.5 (informational for D1).

| window   |   H |   pairs |   n_trades |   pooled_mean_R |   pooled_t |   eqwt_mean_R |   pairs_positive |   t_day_clustered |   pooled_mean_R_x1.5 | verdict   |
|:---------|----:|--------:|-----------:|----------------:|-----------:|--------------:|-----------------:|------------------:|---------------------:|:----------|
| US       |   2 |       6 |       8594 |          -0.009 |     -2.537 |        -0.009 |                1 |            -1.391 |               -0.014 | FAIL      |
| US       |   4 |       6 |       8595 |          -0.006 |     -1.641 |        -0.006 |                2 |            -0.917 |               -0.009 | FAIL      |
| home     |   2 |       5 |       7053 |          -0.025 |     -6.475 |        -0.025 |                0 |            -5.474 |               -0.031 | FAIL      |
| home     |   4 |       5 |       7053 |          -0.017 |     -4.378 |        -0.017 |                0 |            -3.56  |               -0.021 | FAIL      |

Per-pair mean R by group (base costs):

| symbol   |   US 2h |   US 4h |   home 2h |   home 4h |
|:---------|--------:|--------:|----------:|----------:|
| EURUSD   | -0.0012 | -0.0027 |   -0.0119 |   -0.0001 |
| GBPUSD   | -0.0094 | -0.0044 |   -0.0094 |   -0.0075 |
| AUDUSD   | -0.022  | -0.0191 |   -0.0323 |   -0.0191 |
| USDJPY   | -0.0088 |  0      |   -0.0402 |   -0.0424 |
| USDCAD   | -0.0208 | -0.015  |  nan      |  nan      |
| USDCHF   |  0.008  |  0.0068 |   -0.0307 |   -0.0145 |

## Verdicts

Per-pair configuration criteria: n >= 200, mean R > 0, t > 2.0, mean R > 0 with spread x1.5.

| symbol   | config          |    n |   avg_R |      t |   avg_R_x1.5 | verdict   |
|:---------|:----------------|-----:|--------:|-------:|-------------:|:----------|
| EURUSD   | window=US,H=2   | 1433 |  -0.001 | -0.14  |       -0.006 | FAIL      |
| EURUSD   | window=US,H=4   | 1433 |  -0.003 | -0.313 |       -0.006 | FAIL      |
| EURUSD   | window=home,H=2 | 1431 |  -0.012 | -1.4   |       -0.018 | FAIL      |
| EURUSD   | window=home,H=4 | 1431 |  -0     | -0.014 |       -0.005 | FAIL      |
| GBPUSD   | window=US,H=2   | 1432 |  -0.009 | -1.063 |       -0.014 | FAIL      |
| GBPUSD   | window=US,H=4   | 1432 |  -0.004 | -0.496 |       -0.008 | FAIL      |
| GBPUSD   | window=home,H=2 | 1431 |  -0.009 | -1.03  |       -0.014 | FAIL      |
| GBPUSD   | window=home,H=4 | 1431 |  -0.008 | -0.824 |       -0.011 | FAIL      |
| AUDUSD   | window=US,H=2   | 1433 |  -0.022 | -2.62  |       -0.028 | FAIL      |
| AUDUSD   | window=US,H=4   | 1433 |  -0.019 | -2.3   |       -0.022 | FAIL      |
| AUDUSD   | window=home,H=2 | 1327 |  -0.032 | -4.014 |       -0.039 | FAIL      |
| AUDUSD   | window=home,H=4 | 1327 |  -0.019 | -2.233 |       -0.023 | FAIL      |
| USDJPY   | window=US,H=2   | 1432 |  -0.009 | -0.932 |       -0.014 | FAIL      |
| USDJPY   | window=US,H=4   | 1433 |   0     |  0.005 |       -0.004 | FAIL      |
| USDJPY   | window=home,H=2 | 1434 |  -0.04  | -4.545 |       -0.047 | FAIL      |
| USDJPY   | window=home,H=4 | 1434 |  -0.042 | -5.065 |       -0.048 | FAIL      |
| USDCAD   | window=US,H=2   | 1432 |  -0.021 | -2.485 |       -0.025 | FAIL      |
| USDCAD   | window=US,H=4   | 1432 |  -0.015 | -1.808 |       -0.018 | FAIL      |
| USDCHF   | window=US,H=2   | 1432 |   0.008 |  0.95  |        0.003 | FAIL      |
| USDCHF   | window=US,H=4   | 1432 |   0.007 |  0.842 |        0.003 | FAIL      |
| USDCHF   | window=home,H=2 | 1430 |  -0.031 | -3.759 |       -0.037 | FAIL      |
| USDCHF   | window=home,H=4 | 1430 |  -0.015 | -1.754 |       -0.019 | FAIL      |

Pooled group criteria: pooled t > 2.5 and >= 4 pairs with positive mean R.

- **FAIL** D1 window=US, H=2h: pooled mean R -0.0090, pooled t -2.54 (need > 2.5), pairs positive 1/6 (need >= 4); x1.5 spread pooled mean R -0.0142
- **FAIL** D1 window=US, H=4h: pooled mean R -0.0057, pooled t -1.64 (need > 2.5), pairs positive 2/6 (need >= 4); x1.5 spread pooled mean R -0.0092
- **FAIL** D1 window=home, H=2h: pooled mean R -0.0248, pooled t -6.48 (need > 2.5), pairs positive 0/5 (need >= 4); x1.5 spread pooled mean R -0.0309
- **FAIL** D1 window=home, H=4h: pooled mean R -0.0167, pooled t -4.38 (need > 2.5), pairs positive 0/5 (need >= 4); x1.5 spread pooled mean R -0.0211

Per-pair configurations passing: 0 of 22. Pooled groups passing: 0 of 4.

**D1 OVERALL: FAIL** (no pooled group passes).
