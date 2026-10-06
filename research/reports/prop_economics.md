# Prop firm economics: how much edge is needed?

How much edge does an FTMO challenge actually need? -> research/reports/prop_economics.md

Synthetic trade streams (one trade per trading day, win +1.5R / loss -1R) with a chosen
expectancy are run through the FTMO 2-step Monte Carlo (phase 1 -> phase 2 -> 250-day funded
account with payouts every 10 trading days at an 80% split). EV is per challenge purchase on a
100k account with a 540 EUR (~600 USD) fee refunded with the first payout.

Challenge phases capped at 120 trading days each (a timeout counts as a failure). Risk policy: daily soft stop 3%, risk halved below -6%, trading halted below -8%.

|   expectancy_R |   risk_% |   P(pass ph1) |   P(funded) |   payout|funded_% |   EV_per_attempt_$ |
|---------------:|---------:|--------------:|------------:|------------------:|-------------------:|
|          -0.1  |     0.25 |         0     |       0     |             0     |           -600     |
|          -0.1  |     0.5  |         0.01  |       0.002 |             1.429 |           -596.45  |
|          -0.1  |     0.75 |         0.044 |       0.009 |             1.946 |           -576.45  |
|          -0.1  |     1    |         0.084 |       0.025 |             2.088 |           -532.8   |
|          -0.05 |     0.25 |         0     |       0     |             0     |           -600     |
|          -0.05 |     0.5  |         0.039 |       0.008 |             2.315 |           -575.225 |
|          -0.05 |     0.75 |         0.111 |       0.042 |             2.456 |           -470.1   |
|          -0.05 |     1    |         0.171 |       0.069 |             3.241 |           -334.95  |
|           0    |     0.25 |         0.001 |       0     |             2     |           -599.35  |
|           0    |     0.5  |         0.092 |       0.038 |             4.313 |           -414.55  |
|           0    |     0.75 |         0.226 |       0.112 |             5.208 |             53.363 |
|           0    |     1    |         0.296 |       0.158 |             5.887 |            428.25  |
|           0.05 |     0.25 |         0.004 |       0.001 |             4     |           -596.55  |
|           0.05 |     0.5  |         0.163 |       0.082 |             6.604 |            -12.85  |
|           0.05 |     0.75 |         0.339 |       0.203 |             7.458 |           1033.84  |
|           0.05 |     1    |         0.41  |       0.258 |             7.635 |           1522.55  |
|           0.1  |     0.25 |         0.014 |       0.004 |             5.938 |           -573.85  |
|           0.1  |     0.5  |         0.301 |       0.2   |            10.072 |           1534.3   |
|           0.1  |     0.75 |         0.516 |       0.381 |            12.12  |           4246.2   |
|           0.1  |     1    |         0.574 |       0.43  |            12.306 |           4946.45  |
|           0.15 |     0.25 |         0.033 |       0.014 |             7.1   |           -494.125 |
|           0.15 |     0.5  |         0.43  |       0.33  |            13.007 |           3883.6   |
|           0.15 |     0.75 |         0.627 |       0.525 |            16.513 |           8384.14  |
|           0.15 |     1    |         0.679 |       0.557 |            16.941 |           9170.55  |
## Reading

- A challenge is an option: the loss is capped at the fee, while a funded account pays out positive
  excursions. Even a **zero-edge** stream at 0.75-1% risk shows a small positive EV in this model, but it
  is fragile (depends on payout terms, FTMO behaviour rules, patience caps) and turns negative as soon as
  costs push the expectancy below zero (-0.05 R loses money at every risk level).
- **+0.05 R after costs** with one trade per day is worth roughly +1,000 to +1,500 USD per attempt;
  **+0.10 R** roughly +4,000 to +5,000; **+0.15 R** roughly +8,000 to +9,000.
- Optimal risk per trade sits around **0.75-1%** across edges; 0.25% almost never reaches the target within
  the 120-day patience cap.
- Practical target for the research: a portfolio of low-correlation components with combined expectancy of at
  least +0.05 R per trade after realistic costs, about one trade per day. A single strong edge is not required.
