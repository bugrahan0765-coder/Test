# D2 out-of-sample results (2021-2023, cost model v3)

Plan: research/hypotheses/D2_OOS_plan.md. Verdict uses t_in = 10:00 only.

## t_in = 10:00

- trades 174, months 29, pooled mean R -0.0700, pooled t -2.38, month-avg t -1.15, per-trade Sharpe -0.180

| symbol   |   count |    mean |
|:---------|--------:|--------:|
| AUDUSD   |      29 | -0.0587 |
| EURUSD   |      29 | -0.1684 |
| GBPUSD   |      29 | -0.1023 |
| USDCAD   |      29 |  0.0342 |
| USDCHF   |      29 |  0.0273 |
| USDJPY   |      29 | -0.1522 |

## t_in = 12:00

- trades 174, months 29, pooled mean R -0.0653, pooled t -2.12, month-avg t -1.03, per-trade Sharpe -0.161

| symbol   |   count |    mean |
|:---------|--------:|--------:|
| AUDUSD   |      29 | -0.0097 |
| EURUSD   |      29 | -0.1712 |
| GBPUSD   |      29 | -0.1013 |
| USDCAD   |      29 |  0.086  |
| USDCHF   |      29 | -0.0409 |
| USDJPY   |      29 | -0.1546 |

## t_in = 14:00

- trades 174, months 29, pooled mean R -0.0288, pooled t -0.84, month-avg t -0.42, per-trade Sharpe -0.063

| symbol   |   count |    mean |
|:---------|--------:|--------:|
| AUDUSD   |      29 |  0.0595 |
| EURUSD   |      29 | -0.1819 |
| GBPUSD   |      29 | -0.0628 |
| USDCAD   |      29 |  0.0458 |
| USDCHF   |      29 |  0.0526 |
| USDJPY   |      29 | -0.0862 |

## Verdict (t_in = 10:00)

- FAIL: pooled mean R > 0
- FAIL: OOS Sharpe -0.180 >= 0.5 x IS 0.199
- FAIL: pairs positive 2/6 >= 4
- FAIL: DSR 0.000 > 0.90 (trials 4370, combined n 492, SR 0.065)

**D2 OOS OVERALL: FAIL**
