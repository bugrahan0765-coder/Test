# F1 in-sample result: analog pattern memory (US100 M5)

Hypothesis: `research/hypotheses/F1_analog_patterns.md`. Library 2015-2019 (or its last 100 days),
queries 2020 every 30 min 10:30-15:00 NY, k = 20, long if P(up) >= 0.65, short if <= 0.35,
exit after 12 bars (1 h), cost v3 = 0.7 bp round trip.

| config | lib_days | lib_windows | n_queries | n_trades | n_long | n_short | mean_net_bp | t | hit | spearman | mean_dist | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lib100 | 100 | 5311 | 2483 | 716 | 425 | 291 | -0.831 | -0.467 | 0.524 | -0.006 | 9.077 | False |
| libfull | 1283 | 68876 | 2483 | 712 | 524 | 188 | -1.855 | -0.982 | 0.501 | -0.015 | 5.860 | False |

Pass: >= 200 trades, mean net > 0 with t > 2.0, hit rate > 52%.

**Verdict:** REJECTED - no configuration passes.
