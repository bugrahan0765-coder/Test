# G1 in-sample result: Wyckoff spring / upthrust (2015-2020)

Hypothesis: `research/hypotheses/G1_wyckoff_spring_upthrust.md`. Cost model v3; spread_mult 1.5 = stress run (not a pass criterion).

## US100

| config | spread_mult | n | win_rate | avg_R | t_stat | profit_factor | avg_win_R | avg_loss_R |
|---|---|---|---|---|---|---|---|---|
| L=48,target=range | 1.000 | 2922 | 0.211 | -0.047 | -1.127 | 0.941 | 3.561 | -1.011 |
| L=48,target=range | 1.500 | 2956 | 0.207 | -0.081 | -1.990 | 0.899 | 3.484 | -1.011 |
| L=48,target=2R | 1.000 | 3109 | 0.335 | -0.064 | -2.611 | 0.905 | 1.826 | -1.017 |
| L=48,target=2R | 1.500 | 3138 | 0.331 | -0.087 | -3.647 | 0.871 | 1.790 | -1.017 |
| L=96,target=range | 1.000 | 3155 | 0.197 | -0.070 | -1.671 | 0.914 | 3.783 | -1.013 |
| L=96,target=range | 1.500 | 3181 | 0.193 | -0.094 | -2.307 | 0.884 | 3.734 | -1.012 |
| L=96,target=2R | 1.000 | 3257 | 0.327 | -0.081 | -3.402 | 0.881 | 1.843 | -1.017 |
| L=96,target=2R | 1.500 | 3276 | 0.324 | -0.099 | -4.201 | 0.856 | 1.812 | -1.016 |

## US500

| config | spread_mult | n | win_rate | avg_R | t_stat | profit_factor | avg_win_R | avg_loss_R |
|---|---|---|---|---|---|---|---|---|
| L=48,target=range | 1.000 | 2565 | 0.202 | -0.086 | -1.937 | 0.894 | 3.563 | -1.011 |
| L=48,target=range | 1.500 | 2602 | 0.196 | -0.123 | -2.880 | 0.848 | 3.510 | -1.009 |
| L=48,target=2R | 1.000 | 2686 | 0.327 | -0.072 | -2.717 | 0.893 | 1.830 | -0.997 |
| L=48,target=2R | 1.500 | 2721 | 0.316 | -0.118 | -4.602 | 0.827 | 1.782 | -0.995 |
| L=96,target=range | 1.000 | 2609 | 0.196 | -0.062 | -1.286 | 0.924 | 3.819 | -1.009 |
| L=96,target=range | 1.500 | 2647 | 0.190 | -0.101 | -2.178 | 0.877 | 3.756 | -1.007 |
| L=96,target=2R | 1.000 | 2691 | 0.327 | -0.076 | -2.927 | 0.887 | 1.823 | -0.997 |
| L=96,target=2R | 1.500 | 2727 | 0.318 | -0.115 | -4.592 | 0.831 | 1.774 | -0.996 |

## By side (spread_mult 1.0, reported only)

| symbol | config | side | n | avg_R | t_stat |
|---|---|---|---|---|---|
| US100 | L=48,target=range | long (spring) | 1234 | -0.031 | -0.529 |
| US100 | L=48,target=range | short (upthrust) | 1688 | -0.059 | -1.008 |
| US100 | L=48,target=2R | long (spring) | 1326 | -0.001 | -0.021 |
| US100 | L=48,target=2R | short (upthrust) | 1783 | -0.111 | -3.488 |
| US100 | L=96,target=range | long (spring) | 1376 | -0.087 | -1.577 |
| US100 | L=96,target=range | short (upthrust) | 1779 | -0.057 | -0.936 |
| US100 | L=96,target=2R | long (spring) | 1425 | -0.017 | -0.469 |
| US100 | L=96,target=2R | short (upthrust) | 1832 | -0.131 | -4.192 |
| US500 | L=48,target=range | long (spring) | 1206 | -0.046 | -0.719 |
| US500 | L=48,target=range | short (upthrust) | 1359 | -0.121 | -1.976 |
| US500 | L=48,target=2R | long (spring) | 1264 | -0.013 | -0.326 |
| US500 | L=48,target=2R | short (upthrust) | 1422 | -0.125 | -3.417 |
| US500 | L=96,target=range | long (spring) | 1246 | -0.085 | -1.349 |
| US500 | L=96,target=range | short (upthrust) | 1363 | -0.041 | -0.566 |
| US500 | L=96,target=2R | long (spring) | 1300 | -0.004 | -0.118 |
| US500 | L=96,target=2R | short (upthrust) | 1391 | -0.142 | -4.045 |

## Verdict

Pass: on BOTH instruments >= 200 trades, mean R > 0, t > 2.0.

- L=48,target=range: fail
- L=48,target=2R: fail
- L=96,target=range: fail
- L=96,target=2R: fail

Best single (symbol, config) by mean R: ('US100', 'L=48,target=range'), per-trade SR -0.021, DSR over 4380 logged trials = 0.000.

**G1 is REJECTED in-sample.**
