# E1 in-sample results (2015-2020, excluded months removed, cost model v3)

VIX data: 1990-01-02 .. 2026-10-09; VIX3M: 2009-09-18 .. 2026-10-09. Information of day d is used from 09:35 ET on the next trading day.

## US100 (78s)

| config                 |   spread_mult |    n |   win_rate |   avg_R |   t_stat |   profit_factor |   total_R |   worst_mae_R |
|:-----------------------|--------------:|-----:|-----------:|--------:|---------:|----------------:|----------:|--------------:|
| variant=ts,th=0.9      |           1   |  830 |      0.581 |   0.024 |    2.073 |           1.21  |    19.964 |        -1.02  |
| variant=ts,th=0.9      |           1.5 |  830 |      0.578 |   0.023 |    1.978 |           1.199 |    19.048 |        -1.02  |
| variant=ts,th=0.95     |           1   | 1069 |      0.572 |   0.019 |    1.775 |           1.153 |    19.854 |        -1.115 |
| variant=ts,th=0.95     |           1.5 | 1069 |      0.571 |   0.018 |    1.677 |           1.144 |    18.756 |        -1.117 |
| variant=ts,th=1.0      |           1   | 1215 |      0.569 |   0.019 |    1.979 |           1.16  |    23.52  |        -1.115 |
| variant=ts,th=1.0      |           1.5 | 1215 |      0.567 |   0.018 |    1.878 |           1.151 |    22.323 |        -1.117 |
| variant=spike,jump=0.1 |           1   |  114 |      0.526 |   0.001 |    0.034 |           1.008 |     0.134 |        -1.007 |
| variant=spike,jump=0.1 |           1.5 |  114 |      0.526 |   0     |    0.013 |           1.003 |     0.053 |        -1.008 |
| variant=spike,jump=0.2 |           1   |   36 |      0.472 |  -0.003 |   -0.053 |           0.979 |    -0.122 |        -1.007 |
| variant=spike,jump=0.2 |           1.5 |   36 |      0.472 |  -0.004 |   -0.062 |           0.975 |    -0.144 |        -1.008 |
| variant=always         |           1   | 1411 |      0.567 |   0.018 |    1.876 |           1.139 |    24.698 |        -1.115 |
| variant=always         |           1.5 | 1411 |      0.566 |   0.017 |    1.777 |           1.132 |    23.379 |        -1.117 |

## US500 (58s)

| config                 |   spread_mult |    n |   win_rate |   avg_R |   t_stat |   profit_factor |   total_R |   worst_mae_R |
|:-----------------------|--------------:|-----:|-----------:|--------:|---------:|----------------:|----------:|--------------:|
| variant=ts,th=0.9      |           1   |  696 |      0.55  |   0.012 |    1.002 |           1.103 |     8.125 |        -1.046 |
| variant=ts,th=0.9      |           1.5 |  696 |      0.55  |   0.01  |    0.841 |           1.086 |     6.825 |        -1.048 |
| variant=ts,th=0.95     |           1   |  935 |      0.544 |   0.008 |    0.767 |           1.068 |     7.548 |        -1.046 |
| variant=ts,th=0.95     |           1.5 |  935 |      0.544 |   0.006 |    0.604 |           1.053 |     5.944 |        -1.048 |
| variant=ts,th=1.0      |           1   | 1079 |      0.549 |   0.008 |    0.811 |           1.066 |     8.634 |        -1.046 |
| variant=ts,th=1.0      |           1.5 | 1079 |      0.549 |   0.006 |    0.645 |           1.052 |     6.867 |        -1.048 |
| variant=spike,jump=0.1 |           1   |  111 |      0.495 |  -0.043 |   -1.204 |           0.748 |    -4.81  |        -1.013 |
| variant=spike,jump=0.1 |           1.5 |  111 |      0.495 |  -0.045 |   -1.237 |           0.742 |    -4.94  |        -1.013 |
| variant=spike,jump=0.2 |           1   |   37 |      0.405 |  -0.096 |   -1.469 |           0.521 |    -3.548 |        -1.013 |
| variant=spike,jump=0.2 |           1.5 |   37 |      0.405 |  -0.097 |   -1.485 |           0.517 |    -3.583 |        -1.013 |
| variant=always         |           1   | 1271 |      0.544 |   0.004 |    0.432 |           1.032 |     5.19  |        -1.046 |
| variant=always         |           1.5 | 1271 |      0.544 |   0.003 |    0.27  |           1.02  |     3.239 |        -1.048 |

## Pass/fail against the pre-registered IS criteria (base costs)

Criteria per instrument: n >= 200 (ts) / 40 (spike); mean R > 0 with t > 2.0 (ts) / 1.5 (spike); ts configs must beat the benchmark mean R (on each instrument). A config passes only if it meets all of them on both US100 and US500. `x1.5_avg_R` is informational.

| config                 |   US100_n |   US100_avg_R |   US100_t |   US100_bench_avg_R | US100_n_ok   | US100_t_ok   | US100_beats_bench   |   US100_x1.5_avg_R |   US500_n |   US500_avg_R |   US500_t |   US500_bench_avg_R | US500_n_ok   | US500_t_ok   | US500_beats_bench   |   US500_x1.5_avg_R | verdict   |
|:-----------------------|----------:|--------------:|----------:|--------------------:|:-------------|:-------------|:--------------------|-------------------:|----------:|--------------:|----------:|--------------------:|:-------------|:-------------|:--------------------|-------------------:|:----------|
| variant=ts,th=0.9      |       830 |        0.0241 |      2.07 |              0.0175 | True         | True         | True                |             0.0229 |       696 |        0.0117 |      1    |              0.0041 | True         | False        | True                |             0.0098 | FAIL      |
| variant=ts,th=0.95     |      1069 |        0.0186 |      1.77 |              0.0175 | True         | False        | True                |             0.0175 |       935 |        0.0081 |      0.77 |              0.0041 | True         | False        | True                |             0.0064 | FAIL      |
| variant=ts,th=1.0      |      1215 |        0.0194 |      1.98 |              0.0175 | True         | False        | True                |             0.0184 |      1079 |        0.008  |      0.81 |              0.0041 | True         | False        | True                |             0.0064 | FAIL      |
| variant=spike,jump=0.1 |       114 |        0.0012 |      0.03 |              0.0175 | True         | False        | n/a                 |             0.0005 |       111 |       -0.0433 |     -1.2  |              0.0041 | True         | False        | n/a                 |            -0.0445 | FAIL      |
| variant=spike,jump=0.2 |        36 |       -0.0034 |     -0.05 |              0.0175 | False        | False        | n/a                 |            -0.004  |        37 |       -0.0959 |     -1.47 |              0.0041 | False        | False        | n/a                 |            -0.0968 | FAIL      |

- `variant=ts,th=0.9`: **FAIL**
- `variant=ts,th=0.95`: **FAIL**
- `variant=ts,th=1.0`: **FAIL**
- `variant=spike,jump=0.1`: **FAIL**
- `variant=spike,jump=0.2`: **FAIL**
