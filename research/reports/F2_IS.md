# F2 in-sample result: fractal AMD maze, M1 + M5 (US100 only, 2015-2020)

Hypothesis: `research/hypotheses/F2_fractal_maze.md`. Cost model v3. The run was stopped after US100 on the
user's request (US500 skipped). The pre-registered pass criterion needs BOTH instruments, so a fail on US100
is already a rejection.

Numbers from the run log (stdout table) and `research/trials.jsonl`; the trade lists were not saved.

| config | spread_mult | n trades | per-trade Sharpe | t (= SR x sqrt n) | avg win R | avg loss R |
|---|---|---|---|---|---|---|
| rho=0.8, 2R | 1.0 | 9 | -0.671 | -2.01 | 0.300 | -0.780 |
| rho=0.8, time | 1.0 | 9 | -0.671 | -2.01 | 0.300 | -0.780 |
| rho=0.9, 2R | 1.0 | 1 | n/a | n/a | 0.192 | - |
| rho=0.9, time | 1.0 | 1 | n/a | n/a | 0.192 | - |

(2R and time exits gave identical trades: no trade reached the 2R target within the hold.)

Pass: >= 200 trades and mean R > 0 with t > 2.0 on both instruments.

**F2 is REJECTED in-sample.** The joint condition (same consistent reversal AMD on M1 and M5, correlation
>= 0.8) occurred 9 times in six years of US100 (once at >= 0.9), and those 9 trades lost on average.
