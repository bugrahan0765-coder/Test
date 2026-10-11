# Where institutional returns come from (quant funds, CTAs, pod shops, global macro) and what a single intraday prop trader can use

Scope: return sources and realistic Sharpe/return profiles of (1) Renaissance Medallion vs its public funds, (2) Two Sigma / D.E. Shaw / AQR, (3) CTAs and trend followers, including intraday time-series momentum, (4) multi-manager pod shops, (5) global macro, and (6) what transfers to one person trading US100/US500/GER40/XAUUSD on M5/M15 with ~$100k of FTMO capital (5% daily / 10% max loss).

Notation: **[audited/primary]** means a fund document, the paper itself or a peer-reviewed table. **[press]** means a press report, usually citing "a person familiar". **[weak]** means a blog, Substack, forum or aggregator. Most hedge-fund numbers below are [press]: private funds do not publish audited returns.

---

## 1. Renaissance Medallion: returns, methods, and the contrast with RIEF/RIDA

### Takeaway
Medallion is the largest documented outlier in finance. Its headline figures (66% gross, 39% net, 1988-2018) are simple averages of annual returns. The fund was capped (about $5bn from 2002, about $10bn from 2010) and paid out its profits, so the true compounded return is closer to about 32% gross. Its edge comes from thousands of tiny, short-horizon, barely-better-than-a-coin-flip bets, combined with leverage, execution and capacity limits. Renaissance's own outside-investor funds (RIEF/RIDA), run by the same firm on slower horizons, lost 19-34% in 2020 while Medallion made +76%. The Medallion edge does not scale to more capital or longer horizons, and nothing about it transfers to a 4-instrument retail setup.

### Cited Findings
- Cornell (JPM 2020, "Medallion Fund: The Ultimate Counterexample?") reports for 1988-2018: $100 grows to $398.7m gross, a "63.3%" gross compound rate. The average gross annual return is 66.1% and the average net is 39.2%, with standard deviations of 31.7% (gross) and 20.3% (net). The comparison is a perfect-foresight market timer, who grows $100 to only $331,288 gross. [press summary of the paper] — [Institutional Investor](https://www.institutionalinvestor.com/article/2bswymr8cih3jeaslxc00/portfolio/famed-medallion-fund-stretches-explanation-to-the-limit-professor-claims)
- Guo & Liu (arXiv 2405.10917) rebuild the series from fund sizes and trading profits in Zuckerman's Appendix 1. Fund size was $20m in 1988, about $5.2bn in 2002-2009 and capped at about $10bn in 2010-2018. Total trading profit over 1988-2018 was "a little bit over $100 billion". Compounding the yearly returns naively would turn $20m into $78 trillion, which is impossible because profits were paid out rather than reinvested. Their corrected annualized compounded return is **31.8% before fees** (log return 27.6%, volatility 19.65%, return/vol about **1.40**). By sub-period it was **51.8%** for the first 14 years and **19.1%** for the last 17 years, so returns fell as size grew. Simons' wealth grew about 25.6%/yr over 1988-2020. Annual returns in their table include 152% (2008), 137% (2007), 74.6% (2009), 57.5% (2010) and 88.8% (2013). [primary-ish: working paper based on Zuckerman's data] — [Guo & Liu, arXiv](https://arxiv.org/pdf/2405.10917v2)
- Same paper: the about $10bn cap held for nearly a decade suggests the fund's maximum capacity is about $10bn. — [Guo & Liu](https://arxiv.org/pdf/2405.10917v2)
- 2020: Medallion was **+76%** while RIEF fell **22.6%** and RIDA **33.6%** through Dec 25 (HSBC scoreboard). A later Institutional Investor piece gives full-year losses of **-19.4%** (RIEF) and **-31.6%** (RIDA). [press] — [Institutional Investor 2021](https://www.institutionalinvestor.com/article/2bswms7wco7as686o8ikg/portfolio/renaissances-medallion-fund-surged-76-in-2020-but-funds-open-to-outsiders-tanked); [Institutional Investor, "Renaissance's 2024 rebirth"](https://www.institutionalinvestor.com/article/2e0uykr3vn5booz0smrcw/hedge-funds/renaissances-2024-rebirth)
- Early 2020: Medallion was +24% YTD to Apr 14 (+9.9% in March), while RIEF, RIDA and RIDGE were each down 7-9% YTD. [press] — [Institutional Investor](https://www.institutionalinvestor.com/article/2bswzoz7x91fqht87wvsw/portfolio/the-famed-medallion-fund-is-crushing-it-other-rentech-funds-not-so-much)
- Robert Mercer, as quoted in Zuckerman's book: "We're right 50.75 percent of the time... but we're 100 percent right 50.75 percent of the time". The point is a tiny edge per trade, realised across a huge number of trades. [weak: secondhand book excerpt] — [Goodreads excerpt of *The Man Who Solved the Market*](https://www.goodreads.com/notes/44698571-the-man-who-solved-the-market/58027759-thomas-wolf/800f9239-07c1-4032-a735-d1e2b9f74842)

### Inferences
- Using Cornell's moments, the mean/sd ratio is about 2.1 gross and about 1.9 net before subtracting the risk-free rate. Guo & Liu's corrected ratio is about 1.4. Either way it is extraordinary, but it is not "Sharpe 5+" on an investable, compounding basis.
- **What the 50.75% hit rate means.** With symmetric payoffs, 50.75% is a per-bet edge of about 0.015 standard deviations. To reach an annual Sharpe of about 2 you need roughly (2/0.015)² ≈ **18,000 independent bets per year**, about 70 a day. That breadth comes from trading thousands of instruments with low-latency, low-cost execution. One person on 4 highly correlated index/gold CFDs cannot reach it.
- RIEF/RIDA vs Medallion is the cleanest natural experiment available. The same firm, data and people, moved to longer holding periods and larger capital, produced ordinary hedge-fund results with large losses. **The edge sits in short horizon × breadth × execution × limited capacity, not in a transferable insight.**
- Medallion charges very high fees and is still worth it, which means the gross edge is huge per unit of capacity. That capacity is rationed to insiders, so no public replication is plausible.

### Gaps
- No primary, verified source in this research gives Medallion's average holding period, leverage ratio (press often cites about 12.5x) or exact fee schedule (often cited as 5% + 44%). These figures come from Zuckerman's book, which could not be checked directly here.
- No audited Medallion statements are public. All figures trace back to Zuckerman's Appendix 1 (investor letters).

---

## 2. Two Sigma, D.E. Shaw, AQR: return sources, per-signal Sharpe, and how signals are combined

### Takeaway
Large quant firms run many weak, weakly correlated signals (factor/risk premia, statistical arbitrage, short-horizon alphas) across thousands of securities, then combine them with a risk model. Single signals typically have low Sharpe after costs. The portfolio Sharpe comes from breadth (Grinold's fundamental law). Long-run net results for flagship funds are about 10-13% a year. Pure risk-premia products earn about Sharpe 0.4-0.5 with multi-year drawdowns.

### Cited Findings
- **D.E. Shaw Composite** (multi-strategy, quant plus discretionary): about **+18.5% net in 2025**, with an **annualized net return of 12.9% since its 2001 inception**. [press, Reuters "person familiar"] — [Reuters via WSAU](https://wsau.com/2026/01/02/d-e-shaws-flagship-funds-trump-market-volatility-to-beat-sp-500-in-2025-source-says/). Earlier reporting gave 12.7% annualized through 2024. — [BNN Bloomberg](https://bnnbloomberg.ca/business/company-news/2025/01/02/de-shaw-to-return-billions-after-flagship-hedge-fund-gains-18)
- **Two Sigma**: Spectrum returned **10.9%** and Absolute Return Enhanced **14.3%** in 2024. [press] — [Hedgeweek](https://hedgeweek.com/two-sigma-posts-solid-gains-despite-year-of-drama). In 2026 through March, Spectrum was +3% and the Absolute Return fund +3.7%. [press] — [Bloomberg](https://www.bloomberg.com/news/articles/2026-04-06/two-sigma-profits-from-chaotic-march-beating-multistrat-peers)
- **AQR Style Premia Alternative Fund** (multi-factor risk premia: value, momentum, carry, defensive, long/short across asset classes), per the fund page as of 2026-03-31: realized volatility since inception **12.42%**, Sharpe since inception **0.46**, beta to the S&P 500 **-0.01**. [audited/primary: fund page] — [AQR funds](https://funds.aqr.com/funds/aqr-style-premia-alternative-fund)
- The same fund's drawdown was **-14.2% from Feb 2018 to Apr 2019** (data through Apr 2019), driven by the value factor's underperformance. AQR liquidated related smaller funds after outflows. Morningstar describes "strong 2025 results" extending the recovery. [primary/press] — [ProForza fund report PDF](https://files.constantcontact.com/3050ea0a401/0dcc42b5-1c56-4708-9a00-d4adb13a8e87.pdf); [Institutional Investor](https://www.institutionalinvestor.com/article/2bsx6zgnm2qunwsxihyps/portfolio/aqr-to-liquidate-some-funds-after-persistent-outflows); [Morningstar](https://www.morningstar.com/funds/xnas/qsprx/analysis)
- **Per-signal evidence:** Kakushadze, Lauprete & Tulchinsky (WorldQuant), "101 Formulaic Alphas", publish 101 real production alphas. Average holding periods are about **0.6-6.4 days** and the average pairwise correlation is **15.9%**. The paper frames the problem as combining "numerous weak, short-lived trading signals". [primary] — [arXiv 1601.00991](https://arxiv.org/abs/1601.00991). A secondary summary reports an average Sharpe of about 2.26 per alpha, *gross of costs*, 2010-2013 on US equities. That figure is not verified against the paper. — [CXO Advisory](https://www.cxoadvisory.com/technical-trading/performance-of-actual-quant-strategies/)
- **Grinold's fundamental law:** IR ≈ IC × √(breadth), where breadth means the number of *independent* bets per year. Critiques note that genuinely independent forecasts are rare, IC falls as AUM grows, and theoretical IR overstates achievable IR. — [CFI](https://corporatefinanceinstitute.com/resources/capital-markets/fundamental-law-of-active-management/); [New Frontier Advisors PDF](https://newfrontieradvisors.com/media/1744/fundamental-law-september-2019.pdf)

### Inferences
- The flagship products deliver about **10-13% net a year at Sharpe roughly 1-2**, though volatility is not published. They get there by netting hundreds to thousands of signals across thousands of stocks, futures and FX, under strict factor and beta neutrality. The product is breadth plus a risk model plus cheap execution and financing, not one clever signal.
- The 101-alphas paper shows **gross** single-signal Sharpe can look high on paper (about 2 claimed) but is earned on hundreds of stocks with multi-day holding. Pairwise correlation of about 0.16 is what lets a portfolio of them reach a high IR. Our setting has 4 instruments where US100/US500 move almost together, so effective breadth is tiny.
- AQR's style premia (Sharpe about 0.46, with a 2018-2020 drawdown lasting years) are an honest benchmark for "structural risk premia" returns. Even run professionally across many assets, they would not pass a prop challenge with a 10% max loss on a reasonable timetable.
- Grinold arithmetic for our setting: suppose we run about 250-500 effectively independent bets a year (4 correlated instruments, about one setup per day each). An IR of 1 then needs an IC of about **0.045-0.065**, roughly a 52-53% hit rate at symmetric payoff with per-trade Sharpe of about 0.05-0.06 *after costs*. That is 3-4x the per-bet edge Medallion needs. Our own D2 result (per-trade Sharpe +0.199 in-sample, -0.180 out-of-sample, `research/reports/D2_OOS.md`) is typical of how such per-trade edges look before they are found to be noise.

### Gaps
- No public, audited Sharpe or volatility figures for Two Sigma or D.E. Shaw funds were found. Only annual returns via press.
- AQR Style Premia annual returns for 2020 (the deepest part of the value drawdown) and 2022-2025 were not retrieved, so the full drawdown depth is unknown here.
- No source was found that quantifies a typical per-signal *net* Sharpe inside a large quant fund. Practitioner lore says "0.3-1 per signal", but this is unsourced.

---

## 3. CTAs / trend followers: long-run evidence, horizons, diversification, and intraday time-series momentum

### Takeaway
Diversified trend following (about 60-150 futures markets, 1-12 month lookbacks) has more than a century of positive backtested evidence: about **Sharpe 0.77 net of 2/20 fees, 1880-2013**, with weak or mixed post-2008 results and drawdowns of 15-26% lasting up to about 6 years. The Sharpe comes from diversification across many weakly correlated markets, and a single index on its own earns far less. Intraday market momentum (the first half-hour, or rest-of-day, return predicting the last 30 minutes) is published, peer-reviewed and replicated across about 60 futures. The gross edge is only a few basis points per day, it depends partly on dealer gamma hedging, and our own pre-registered CFD test (A1) **rejected** it on 2015-2020 data.

### Cited Findings — long-horizon trend following
- Hurst, Ooi & Pedersen, "A Century of Evidence on Trend-Following Investing" (AQR; JPM 2017). The strategy is an equal-weighted combination of 1-, 3- and 12-month time-series momentum across **67 markets** (29 commodities, 11 equity indices, 15 bond markets, 12 currency pairs), with each position vol-scaled and the portfolio targeted at 10% volatility. Results are net of estimated transaction costs, which are assumed higher in the past. [primary] — [paper PDF](https://www.trendfollowing.com/whitepaper/Century_Evidence_Trend_Following.pdf); [AQR page](https://www.aqr.com/Insights/Research/Journal-Article/A-Century-of-Evidence-on-Trend-Following-Investing)
  - Full sample **Jan 1880-Dec 2013: 14.9% gross, 11.2% net of 2/20, volatility 9.7%, net Sharpe 0.77**, correlation 0.00 to US equities and -0.04 to US 10-year bonds.
  - By decade, net Sharpe ranged from **0.13 (1910s)** to **1.70 (1970s)**, with 0.98 in the 1990s and **0.62 in 2000-2013**. Every decade was positive.
  - Ten largest drawdowns: the worst were **-26.3% (1947-48, 45 months peak-to-recovery)** and **-25.3% (1937-40, 75 months peak-to-recovery)**.
  - The authors note returns have been "mixed since 2008". Trend-follower AUM grew from $22bn (1999) to more than $280bn (2014, BarclayHedge), but they estimate positions are still only about 0.2% of the underlying equity markets.
  - Diversification value: an 80% 60/40 + 20% TSMOM mix raised the Sharpe from 0.38 to 0.54 and cut the max drawdown from -62.3% to -50.2% (1880-2013).
- **Recent industry performance:** the SG Trend Index fell **-10.48%** in H1 2025 (to Jun 26), and the SG CTA Index was down more than 8% by late May 2025. [press] — [Alternatives Watch, Jul 2025](https://www.alternativeswatch.com/2025/07/01/trend-following-hedge-funds-loss-h1-societe-generale-index/); [Alternatives Watch, Jun 2025](https://www.alternativeswatch.com/2025/06/02/trend-following-hedge-funds-endure-more-pain-societe-generale-indices/). Top Traders Unplugged reported the SG Trend Index at +3.86% trailing 12 months in Oct 2025 and +2.39% for full-year 2025. [weak/press; not checked against SocGen's own data] — [TTU Oct 2025 report](https://www.toptradersunplugged.com/trend-following-performance-report-october-2025/)

### Cited Findings — intraday time-series momentum
- **Gao, Han, Li & Zhou, "Market intraday momentum"** (JFE 2018, 129:394-414), using SPY 1993-2013. The first half-hour return (since the previous close) predicts the last half-hour return. Out-of-sample R² is **1.2%** (1.8% when combined with the 12th half-hour). The timing strategy (sign of the first half-hour, held over the last 30 minutes) earns **6.67%/yr at 6.19% volatility, Sharpe 1.08**. Always-long-last-half-hour has Sharpe -0.18, and buy-and-hold has Sharpe 0.29. The effect is stronger on high-volatility days, high-volume days, recessions (Sharpe 2.10) and macro-news days. Ten other ETFs and two international index futures show it too. [primary] — [working-paper copy](https://c.mql5.com/forextsd/forum/173/intraday_momentum_-_the_first_half-hour_return_predicts_the_last_half-hour_return.pdf); [citation via Harbourfront](https://harbourfrontquant.substack.com/p/does-intraday-momentum-exist-in-stock)
  - **Costs (same paper, Sec. 5.2):** after decimalization (Jul 2001 onward), the bid-ask spread cuts the return to **4.46%/yr, 2.47 points lower**. From 2005 onward (spread about **1.2 bp**) it is **6.52% after vs 7.96% before costs**. Commissions are ignored. The volatility of about 6% means the trade carries risk for only 30 minutes a day.
- **Baltussen, Da, Lammers & Martens, "Hedging demand and market intraday momentum"** (JFE 2021, 142:377-403). They test more than **60 futures** (equities, bonds, commodities, FX) over **1974-2020**. The rest-of-day return predicts the last 30 minutes "everywhere", and the effect reverts over the following days. The proposed mechanism is **short-gamma hedging** by option market makers and leveraged ETFs. Intraday momentum is much stronger on negative net-gamma days and **not significant on positive-gamma days**. — [Erasmus repository](https://pure.eur.nl/en/publications/hedging-demand-and-market-intraday-momentum/); [Alpha Architect summary](https://alphaarchitect.com/hot-topic-does-gamma-hedging-actually-affect-stock-prices/)
- **International replications:** a 16-developed-market study finds significant first→last half-hour predictability in **12 of 16** markets, with out-of-sample power in most of them. [paper; attribution of the exact URL to this study is uncertain] — [Nottingham repository](https://nottingham-repository.worktribe.com/OutputFile/5273196). In Asia-Pacific the effect shows up mainly in China and Japan, with **none in Hong Kong or Singapore**. — [AUT/ACFR paper](https://acfr.aut.ac.nz/__data/assets/pdf_file/0008/686816/4a-Z-Ivy-Zhou.pdf)
- **Practitioner variant:** Zarattini, Aziz & Barbon, "Beat the Market: An Effective Intraday Momentum Strategy for SPY" (SFI RP 24-97). It enters on intraday breaks of a "noise area" and exits with trailing stops. On SPY from 2007 to early 2024 it reports **19.6%/yr net of costs, total return 1,985%, Sharpe 1.33**. It won 4th place in the Quantpedia Awards 2025. [authors' own backtest; no independent replication found] — [Concretum](https://concretumgroup.com/beat-the-market-an-effective-intraday-momentum-strategy-for-sp500-etf-spy/); [SFI](https://www.sfi.ch/de/publications/n-24-97-beat-the-market-an-effective-intraday-momentum-strategy-for-s-p500-etf-spy); [Univ. St. Gallen news](https://fsi.unisg.ch/de/newsdetail/news/quantpedia-awards-2025-fsis-barbon-and-team-secure-4th-place-with-intraday-momentum-strategy/)
- **Our own pre-registered tests** (US100/US500 CFD data, in-sample 2015-2020, cost model v2 = 1.4 bp round trip):
  - **A1 market intraday momentum, last half-hour:** best config US100 +0.02 R (t 0.51), US500 -0.01 R → **rejected**.
  - **A2 opening-range breakout:** US100 +0.18 R (t 1.84), US500 -0.03 R → **rejected**.
  - **B3 weekly time-series momentum:** +0.03 R or less, t < 1.5 → **rejected**.
  - Source: [research/reports/cost_model.md](/home/user/Test/research/reports/cost_model.md).

### Inferences
- **Per-trade arithmetic for the Gao et al. effect:** 6.67%/yr over about 252 trades is about **2.6 bp gross per trade**. Our frozen v3 cost for US500 is 0.7 bp round trip plus 2 × 0.1 bp slippage, about 0.9 bp, so costs take about 35% of the gross edge. That would be acceptable if the gross edge persisted, but our A1 test found roughly zero gross edge in 2015-2020 on CFD data.
- Possible reasons for A1's failure, all unverified: the effect is regime-dependent (gamma, high-volatility days); CFD/US100 data differs from SPY; publication decay after 2014. The Baltussen gamma mechanism implies the edge is conditional, so an unconditional rule averages good and bad days into nothing.
- **Single-market vs diversified trend Sharpe (approximation):** SR_portfolio ≈ SR_single × √(N / (1 + (N−1)ρ)). With N = 67 and an assumed average ρ of about 0.1, the multiplier is about 3. A net portfolio Sharpe of 0.77 then implies a **single-market Sharpe of only about 0.25**. Our 4 instruments are highly correlated (US100/US500/GER40), so effective N is about 2, the diversification multiplier is near 1.2-1.4, and a trend book on them would expect Sharpe around 0.3 at best. That is far too little to pass a 10% target before a 10% loss limit.
- CTAs operate on **days to months** horizons. Intraday "trend following" on one index is a different, much weaker (and gamma-dependent) phenomenon, not the century of CTA evidence.
- The noise-area/trailing-stop variant (Zarattini et al.) is the most promising public intraday momentum claim, but it is an authors' backtest with many design choices and no independent out-of-sample check. Under our protocol it would need pre-registration and a fresh out-of-sample test. It is also partly the same signal family as the A1/A2 tests, which failed.

### Gaps
- No independent study was found that reports Gao et al.'s strategy **net of costs after 2013** (post-publication decay) on US index futures. That is the key missing piece.
- No source was found for intraday momentum on **GER40/DAX** or **XAUUSD** specifically. Baltussen's 60 futures likely include DAX and gold, but their per-market tables were not retrieved.
- Official SG CTA / SG Trend full-year 2025 and 2026 YTD figures from SocGen were not retrieved.

---

## 4. Multi-manager pod shops (Millennium, Citadel, Balyasny, ExodusPoint)

### Takeaway
Pods produce about 10-15% net with low volatility. They get there through hundreds of independent PM teams, each held to tight hard drawdown limits (about **5% → capital halved, about 7.5% (sometimes 10%) → fired**), plus firm-level leverage and pass-through fees that absorb 40-60% of gross returns. The structure looks like FTMO's 5%/10% rules, but the PMs mostly run **market- and factor-neutral fundamental equity long/short, relative value and macro books**, not directional intraday index punting. They also have firm capital, data, research analysts and unlimited time.

### Cited Findings
- **Risk rules (WSJ via eFinancialCareers):** Millennium PMs who lose 5% of allocated capital typically have it halved, and a further 2.5% loss (about 7.5% total) usually gets them fired. For example, a PM running $1bn can lose $50m before half is removed, and around $75m usually means termination. [press, secondhand WSJ] — [eFinancialCareers](https://www.efinancialcareers.com/news/pratik-madhvani-glen-scheinberg); [eFinancialCareers](https://www.efinancialcareers.com/news/john-curtice-millennium)
- Other accounts put the wind-down/firing threshold at **7.5-10%**. Limits vary by firm and contract, and Citadel is described as similar to the industry default with exceptions. [weak] — [Wall Street Oasis forum](https://www.wallstreetoasis.com/forum/hedge-fund/multi-manager-risk-limits); [Young & Calculated Substack](https://youngandcalculated.substack.com/p/risk-management-inside-a-pod-how)
- **Returns:** Millennium is said to have returned about **14%/yr since 1989** (attributed to Institutional Investor; no primary source). [press/weak] — [Motley Fool](https://www.fool.com/investing/how-to-invest/famous-investors/millennium-management). Millennium made **+15% in 2024**, lagging the S&P 500's 23% (FT via Hedgeweek). — [Hedgeweek](https://www.hedgeweek.com/news/millennium-posts-15-2024-gain-but-lags-sp-500)
- **2025:** Millennium **+10.5%**, Citadel Wellington **+10.2%**, Balyasny **+16.7%**, D.E. Shaw Composite **+18.5%**. [press] — [Fortune](https://www.fortune.com/2026/01/02/top-hedge-fund-performers-2025-bridgewater-de-shaw-citadel-millennium); [Hedgeweek](https://www.hedgeweek.com/millennium-and-citadel-post-double-digit-2025-gains-but-lag-smaller-hedge-funds/)
- **Pass-through fees:** in 2023, investors in multi-strategy funds kept only **41 cents of each dollar of gross gains**, down from 54 cents in 2021 (BNP Paribas data). Another Hedgeweek piece gives 59%, so the two sources conflict. Fee disclosures at Millennium, Citadel, Point72, Balyasny and ExodusPoint rose about 40% over seven years. Balyasny's flagship made about **15.2% gross but 2.8% net in 2023**, with more than $768m of pass-through fees. [press] — [Hedgeweek](https://hedgeweek.com/news/investors-push-back-on-multi-strategy-hedge-fund-fee-structures); [Hedgeweek](https://www.hedgeweek.com/hedge-funds-charging-billions-in-no-limit-passthrough-fees/); [Bloomberg graphic](https://www.bloomberg.com/graphics/2025-hedge-fund-investment-fees/)
- **Pod structure:** pods are autonomous, PMs choose their own strategy within an assigned risk budget, and a strict drawdown limit of about 5% triggers immediate capital reduction. [weak/press] — [Hedgeweek/marketscreener on Millennium](https://ae.marketscreener.com/news/millennium-management-84bn-set-to-conquer-europe-ce7e50ddda8dff2c)

### Inferences
- **Why pods survive 5%/7.5% limits:**
  - Each PM's book is hedged to the market and factors, so day-to-day P&L volatility is a few percent a year on allocated capital. A 5% drawdown is then a 1.5-2.5 sigma event, and the firm adds leverage *on top*.
  - The firm is diversified across hundreds of PMs. Firing PMs at the drawdown threshold truncates the left tail of each PM's track record (a "free option" for the firm).
  - Many PMs fail. The firm's return is the survivors' P&L after paying them about 15-20% payouts and passing through costs.
- **Parallels with FTMO:** both are a principal–agent setup with a hard loss limit and a profit split, and the firm/prop shop profits from variance plus selection. The **differences** matter:
  - A pod PM has no profit target and no time pressure. FTMO requires +10% / +5% to pass.
  - A pod PM trades a hedged book with low volatility. An FTMO trader has only directional CFD exposure, so drawdown and volatility are tied together.
  - A pod PM has research analysts, data, borrow and cheap financing.
  - The pod parallel therefore argues for **low volatility and many small independent bets**, which our 4-instrument universe cannot provide.
- The edge in pods is mostly (iii) information/research (fundamental stock analysis, earnings and event trading) and (iv) organisation, risk management and capital allocation, plus firm-level leverage. It is not structural intraday index patterns.

### Gaps
- No primary Millennium, Citadel or ExodusPoint document on risk limits was found. Whether drawdown is measured from the high-water mark or from allocated capital is unclear.
- Credible data on PM-level volatility targets, typical gross leverage, payout percentages and PM turnover (the fraction fired per year) were not found in this pass.
- Since-inception audited figures for Citadel Wellington, Balyasny and ExodusPoint were not retrieved.

---

## 5. Global macro (Soros/Druckenmiller, Tudor, Brevan Howard, Bridgewater)

### Takeaway
Discretionary macro returns are real at the top. The best-known records are about 20-30%/yr for Tudor's early decades and Druckenmiller, and about 11-13% for Bridgewater over 30+ years. They are concentrated in a few exceptional people and periods and are mostly press-reported. The edge comes from research, information flow and access to policymakers, plus judgment on central bank and policy regimes and very asymmetric, leveraged position sizing on rare high-conviction trades. Strategy-level results show large dispersion and survivorship bias. None of it is an intraday M5/M15 structural edge.

### Cited Findings
- **Druckenmiller/Duquesne:** about **30% average annual return over 1981-2010** with reportedly no losing year. In 2010 the fund was down about 5% intra-year before closing slightly positive. [weak/press, not audited] — [Wikipedia](https://en.wikipedia.org/wiki/Stanley_Druckenmiller)
- **Tudor Global:** **22.1%/yr from Oct 1986 to mid-2009** (Opalesque database). Bloomberg (2008) reported average annual returns "as much as 22%". Withdrawals from BVI Global were gated in Dec 2008. [press] — [Opalesque](https://www.opalesque.com/OFI189/Top_have_a_surprise_for_you_the89.html); [MarketFolly](https://www.marketfolly.com/2008/12/tudor-investment-corp-halts-withdrawals.html). BVI Global returned +3.2% in 2014. [press] — [Institutional Investor](https://www.institutionalinvestor.com/article/2btfkd1a923af7l2383r4/premium/31-paul-tudor-jones-ii)
- **Brevan Howard Master Fund:** **15.4%/yr from Apr 2003 to 2009**. [press] — [Opalesque](https://www.opalesque.com/OFI189/Top_have_a_surprise_for_you_the89.html). It lost **-5.4% in 2017, its worst year since launch**. [press] — [Bloomberg](https://www.bloomberg.com/news/articles/2018-01-04/brevan-howard-s-hedge-fund-suffers-biggest-annual-loss-in-2017)
- **Bridgewater Pure Alpha** (systematized macro):
  - About **+33-34% in 2025**, reported as its best year. [press] — [ValueTheMarkets](https://www.valuethemarkets.com/cryptocurrency/news/bridgewater-associates-pure-alpha-and-aia-macro-performance-insights); [Fortune](https://www.fortune.com/2026/01/02/top-hedge-fund-performers-2025-bridgewater-de-shaw-citadel-millennium)
  - **+8.1% in H1 2026**. [press, Reuters] — [The Star](https://www.thestar.com.my/tech/tech-news/2026/07/02/bridgewater039s-flagship-macro-fund-gains-81-in-first-half-amid-market-volatility-sources-say)
  - About 11.4%/yr since Dec 1991 at a 12% volatility target. [weak, needs verification] — [Substack](https://navnoorbawa.substack.com/p/bridgewaters-pure-alpha-returned)
- **LCH Investments ranking (end-2025):**
  - Bridgewater made **$15.6bn net in 2025** (2nd) and has **$79.1bn net gains since inception** (3rd). TCI made a record $18.9bn in 2025.
  - The top 20 managers earned $115.8bn net in 2025 and **$969.8bn since inception**, which is **41% of all hedge-fund net gains** while managing **16.6% of assets**.
  - The top 20 had a money-weighted return of 15.7% in 2025 vs 12.6% for the HFRI composite.
  - [press summary of LCH data] — [Hedge Fund Alpha](https://hedgefundalpha.com/news/top-20-hedge-funds-earn-115b-in-2025/); [Institutional Investor](https://www.institutionalinvestor.com/article/chris-hohns-tci-tops-hedge-fund-gains-2025)

### Inferences
- Macro P&L is concentrated in rare regime shifts: currency pegs breaking, rate cycles, inflation shocks in 2022 and 2025. It is captured by sizing very large on a thesis built from research and policy insight. Holding periods are weeks to months, and survival relies on cutting losers fast (Tudor's and Druckenmiller's widely quoted rules).
- An individual intraday CFD trader cannot replicate the information or policy edge. The transferable piece is **risk discipline**: small size when uncertain, cut losers, size up only with evidence. That is a property of risk management, not an alpha source.
- The LCH concentration figures (16.6% of assets earning 41% of gains) imply **heavy survivorship and skill concentration**. The median hedge fund adds little after fees, which argues for humility about an individual's chances.

### Gaps
- No verified annualized return was found for **Soros's Quantum Fund 1969-2000** (often quoted at about 30%) or for Brevan Howard and Tudor after 2009. Audited series are not public.
- Pure Alpha's long-run annualized return and volatility are not verified by a primary source.

---

## 6. Overall: decomposition of institutional alpha and what is accessible to one person on 4 instruments intraday

### Takeaway
Across all institution types, returns come mainly from (ii) **breadth**: many weak, weakly correlated bets across hundreds to thousands of instruments. (iv) **Execution, financing, leverage and scale** turn tiny edges into large returns (Medallion, stat-arb, pods), (iii) **information and research** drives pods and macro, and (i) **structural risk premia** (trend, carry, value) earn about Sharpe 0.4-0.8 only when diversified across dozens of markets. No source quantifies the split precisely. A solo trader on US100/US500/GER40/XAUUSD at M5/M15 has essentially no access to (ii), (iii) or (iv), and only a diluted, low-Sharpe slice of (i) such as conditional intraday momentum or overnight/turn-of-month flows. Our own pre-registered tests of that slice have so far failed.

### Cited Findings
- **Breadth:** Medallion's edge per bet is about a 50.75% hit rate ([Goodreads/Zuckerman excerpt](https://www.goodreads.com/notes/44698571-the-man-who-solved-the-market/58027759-thomas-wolf/800f9239-07c1-4032-a735-d1e2b9f74842)). WorldQuant alphas have about 16% pairwise correlation and 0.6-6.4 day holding periods ([arXiv 1601.00991](https://arxiv.org/abs/1601.00991)). IR ≈ IC·√breadth ([CFI](https://corporatefinanceinstitute.com/resources/capital-markets/fundamental-law-of-active-management/)).
- **Capacity and execution:** Medallion's compounded return fell from 51.8% (first 14 years) to 19.1% (last 17 years) as size grew, and capacity is about $10bn ([Guo & Liu](https://arxiv.org/pdf/2405.10917v2)). The same firm's slower public funds lost 19-34% in 2020 ([Institutional Investor](https://www.institutionalinvestor.com/article/2bswms7wco7as686o8ikg/portfolio/renaissances-medallion-fund-surged-76-in-2020-but-funds-open-to-outsiders-tanked)).
- **Structural premia:** diversified TSMOM has net Sharpe 0.77 across 67 markets over 1880-2013, and 0.62 in 2000-2013 ([Hurst-Ooi-Pedersen](https://www.trendfollowing.com/whitepaper/Century_Evidence_Trend_Following.pdf)). AQR multi-asset style premia have Sharpe 0.46 since inception ([AQR](https://funds.aqr.com/funds/aqr-style-premia-alternative-fund)).
- **Fees and pass-through:** multi-strategy investors keep about 41-59% of gross gains ([Hedgeweek](https://hedgeweek.com/news/investors-push-back-on-multi-strategy-hedge-fund-fee-structures)).
- **Intraday index momentum:** the gross edge is about 6.7%/yr (Sharpe about 1.1) on SPY 1993-2013 and about 2.5 points/yr lower after spreads 2001-2013 ([Gao et al.](https://c.mql5.com/forextsd/forum/173/intraday_momentum_-_the_first_half-hour_return_predicts_the_last_half-hour_return.pdf)). It is gamma-conditional ([Baltussen et al.](https://pure.eur.nl/en/publications/hedging-demand-and-market-intraday-momentum/)), and our A1 test on CFDs in 2015-2020 rejected it ([cost_model.md](/home/user/Test/research/reports/cost_model.md)).

### Inferences (explicitly skeptical; these are the writer's judgments, not sourced numbers)
- **Rough attribution by institution type** (qualitative; no source gives these shares):
  - **Medallion / HFT / stat-arb:** mostly (ii) breadth + (iv) execution and capacity. **Not accessible.**
  - **Two Sigma / D.E. Shaw:** (ii) + (iv) + some (i). **Not accessible**, apart from the general lesson of combining weak signals.
  - **AQR-style premia and CTAs:** mostly (i) structural premia × diversification across 50-150 markets. **Partially accessible**, but on 4 correlated instruments the Sharpe collapses to about 0.2-0.3, at horizons (days to months) that conflict with "flat before weekend, intraday".
  - **Pods:** (iii) fundamental research + (iv) organisational risk management and leverage. **Not accessible.** The prop-firm format copies the pods' *risk rules* but not their *edge or diversification*.
  - **Global macro:** (iii) research and information + judgment + asymmetric sizing on rare events. **Not accessible** at M5/M15. The risk-discipline lessons transfer.
- **What is plausibly accessible to us:**
  - (a) A small number of **conditional structural intraday effects** with a flow or mechanical story: gamma-driven late-day momentum, month-end/OPEX flows, overnight/turn-of-month drift, session transitions.
  - (b) **Volatility forecasting for sizing and filtering** (HAR-RV). This is a risk-management gain, not alpha. It raises Sharpe modestly by cutting risk in high-volatility regimes, and it is the one institutional technique that transfers fully.
  - (c) **Cost minimisation.** Our measured CFD costs (US100 about 0.3-0.5 bp spread) are at or below SPY spreads, so costs are not the binding constraint; the gross edge is.
- **Realistic ceiling:** suppose a handful of intraday effects at single-instrument Sharpe about 0.3-0.5 each, with correlation 0.2-0.5 between them. They might combine to about **Sharpe 0.5-1.0 before parameter decay**. At an annual volatility of about 8-10% (needed to keep the 10% max-loss probability modest), that is roughly **4-10% a year**. Hitting FTMO's +10% phase-1 target at that pace typically takes many months, with a meaningful probability of hitting the 10% loss limit first. Prop economics then depend more on fees, refunds and the profit split than on alpha (cross-check with `research/reports/prop_economics.md`).
- **Evidence that this ceiling is optimistic:** out of about 5,000 logged trials (A1-D2), none survived out-of-sample. That matches the institutional picture: in liquid index futures and CFDs, simple publicly documented intraday rules are either arbitraged away, conditional on regimes, or too small after costs.
- **Honest summary for the user:** the institutions that earn reliable returns do so through breadth, infrastructure, information or scale, none of which a single trader on 4 instruments has. What remains is low-Sharpe structural effects plus good risk management. That is enough to make prop challenges a positive-expected-value lottery at best, not a reliable income stream.

### Gaps
- No academic or industry source was found that quantitatively decomposes hedge-fund alpha into risk premia, breadth, information and execution. The split above is judgment.
- No study was found of the realised net performance of retail or prop-firm traders using published intraday index anomalies (e.g. pass rates of systematic EAs at FTMO). FTMO pass-rate data would be the most relevant evidence but was not retrieved here.
- The post-2013 decay of intraday momentum on US index futures, net of costs, remains unverified by an independent source.
