# How market makers, HFT firms and bank trading desks earn money, and what an FTMO CFD trader can copy

Scope: where the trading revenue of electronic market makers / HFT firms and bank sales & trading desks comes from, broken into components, and which of those components an individual trading index CFDs and gold intraday on ~$100k of prop-firm capital (a price taker on MT5, paying spread/commission, ~100 ms+ latency, no rebates, no client flow) can actually reach.

Source-quality legend: [PRIMARY] = SEC filing / regulator / company release; [PEER] = peer-reviewed or official working paper; [PRESS] = Reuters/Bloomberg/FT etc., usually citing unnamed sources or investor documents; [SECONDARY] = aggregator / blog.

## Q1. Virtu's IPO filing: the "1 losing day in 1,238" figure, revenue per trade, and what kind of edge it implies

### Takeaway
Virtu's 2014 S-1 says it had exactly one losing day in 1,238 trading days (1 Jan 2009 to 31 Dec 2013). That record comes from a market-neutral spread-capture business: thousands of instruments, instant hedging, and self-clearing cost advantages. It does not come from good directional calls. The CEO said only about 51-52% of individual trades were profitable. A tiny edge per trade is turned into a near-certain daily profit by huge trade counts and diversification, and that is a different kind of business from directional intraday trading.

### Cited Findings
- [PRIMARY] S-1 (filed 10 Mar 2014), exact wording: "we had only one losing trading day during the period depicted, a total of 1,238 trading days". The period is 1 Jan 2009 to 31 Dec 2013, and the chart shows daily Adjusted Net Trading Income. The filing also says "we have had only one losing trading day since January 1, 2008." — [Virtu S-1, SEC EDGAR](https://www.sec.gov/Archives/edgar/data/0001592386/000104746914002070/a2218589zs-1.htm)
- [PRIMARY] Average daily Adjusted Net Trading Income: $1.148M in 2011 ($289.1M over 252 days), $1.464M in 2012 ($366.3M over 250 days), $1.645M in 2013 ($414.5M over 252 days). For 2013, total revenues were $664.5M, "trading income, net" $623.7M, net income $182.2M and Adjusted Net Income $215.4M. — [Virtu S-1](https://www.sec.gov/Archives/edgar/data/0001592386/000104746914002070/a2218589zs-1.htm)
- [PRIMARY] Scale: "more than 10,000 securities and other financial instruments on more than 210 unique exchanges, markets and liquidity pools in 30 countries." — [Virtu S-1](https://www.sec.gov/Archives/edgar/data/0001592386/000104746914002070/a2218589zs-1.htm)
- [PRIMARY] The S-1 describes the business model as follows:
  - It earns "small amounts of money based on the difference between what buyers are willing to pay" and what sellers will accept.
  - It is "market neutral": "we are not dependent on the direction of a particular market and do not speculate".
  - It aims to "lock in returns through precise and nearly instantaneous hedging".
  - A strategy whose revenue falls outside preset limits is automatically frozen ("lockdown").
  
  — [Virtu S-1](https://www.sec.gov/Archives/edgar/data/0001592386/000104746914002070/a2218589zs-1.htm)
- [PRIMARY] Cost structure: "brokerage, exchange and clearance fees, net" were $195.1M in 2013, about 31% of trading income. Virtu is a self-clearing DTC member, avoids clearing fees in US equities, and pays no "licensing or per-trade processing fees to any third parties". Owning the infrastructure is part of the edge. — [Virtu S-1](https://www.sec.gov/Archives/edgar/data/0001592386/000104746914002070/a2218589zs-1.htm)
- [PRESS/SECONDARY] CEO Doug Cifu reportedly told Bloomberg in June 2014 that "51 to 52%" of Virtu's trades are profitable. This is relayed second-hand; the original Bloomberg piece is paywalled. — [1library document citing Bloomberg](https://1library.net/document/qv957wgy-greg-laughlin-figure-google-trends-chart-frequency-trading.html); Cifu also said publicizing the near-perfect record "backfired": [Bloomberg, 4 Jun 2014](https://www.bloomberg.com/news/articles/2014-06-04/virtu-touting-near-perfect-record-of-profits-backfired-ceo-says)
- [PRESS] The one losing day reportedly came from a missed special-dividend payment, not a market loss. In 2014 Virtu was profitable every day, with revenue of $723.1M and net income of $190.1M. — [Markets Media](https://www.marketsmedia.com/virtu-loses-well-never/)
- [PRIMARY] Recent scale: 2025 Adjusted Net Trading Income was about $2.145B, up from $1.598B in 2024. That is about $8.6M per day, of which Market Making was about $6.7M/day (Q4 2025: $7.8M/day) and Virtu Execution Services about $1.9M/day. Management called it the best year since 2021, not an all-time record. — [Virtu 10-K FY2025](https://www.sec.gov/Archives/edgar/data/1592386/000159238626000009/virt-20251231.htm); per-day figures from the earnings call via [Fintool Q4 2025](https://fintool.com/app/research/companies/VIRT/earnings/Q4%202025) [SECONDARY]
- [PRIMARY, broker-specific] Payment for order flow is one way wholesalers buy retail flow. Rule 606 reports on FINRA show:
  - Citadel Securities paying about 12.6 to 13.4 cents per 100 shares (≈$0.0013/share) in Q4 2025 / Q1 2026, depending on broker and order type.
  - Virtu paying about 15.9 to 17 cents per 100 shares, with one disclosure citing $0.0017 per executed share for listed stocks above $1.
  - Rates differ widely across brokers, and some rows are negative (the broker pays the wholesaler).
  
  — [FINRA 606 report example, 2025 Q4](https://cdn.finra.org/606/2025/48015_606_NMS_2025_Q4_V1.pdf); [FINRA 606, 2026 Q1](https://cdn.finra.org/606/2026/48015_606_NMS_2026_Q1_V1.pdf)

### Inferences
- The S-1 gives a profitable-day share of about 99.9% (1,237/1,238), but only about 51-52% of trades were winners. A daily Sharpe that high is only possible with a very large number of nearly independent, tiny-edge bets across 10,000+ instruments, plus strict inventory and loss limits. The "holy grail" readings in trader forums misunderstand this: the edge is the law of large numbers applied to a bid-ask spread, not prediction.
- Order of magnitude: if a wholesaler can pay about $0.0013-0.0017 per share for retail flow and still profit, its gross capture on that flow is in the low tenths of a cent per share. On a $50-$200 stock that is roughly 0.1-0.3 bp of notional. This is an inference; Virtu does not publish a capture-per-share figure in the parts of the S-1 I read.
- Even after all of Virtu's infrastructure advantages, fees took about 31% of trading income in 2013. Costs dominate this business; at retail cost levels the same edge would be negative.

### Gaps
- I did not find a verified Virtu figure for revenue per trade or per share (capture rate) in the S-1 excerpt I read (only the first ~100k characters). Later investor decks may report "capture per share"; not retrieved.
- Virtu's number of trades per day is not available, so revenue per trade cannot be computed directly.

## Q2. Citadel Securities, Jane Street, Optiver (plus HRT): recent results and what drives them

### Takeaway
The top electronic market makers have become extremely large:
- Jane Street: about $20.5B net trading revenue in 2024 and a reported $39.6B in 2025.
- Citadel Securities: about $9.7B (2024) and about $12.2B (2025).
- Hudson River Trading: about $12.3B (2025).
- Optiver: €4.56B net trading income in 2025.

The drivers are volatility and volume, retail options and equity flow, ETF creation/redemption and arbitrage, and options market making across thousands of related instruments. These are inventory-turnover and cross-asset relative-value businesses that need balance sheet, data and speed, not directional bets on one index. Except for Optiver, the figures are press reports based on investor or bond documents.

### Cited Findings
- [PRESS, from bond prospectus] Jane Street: 2024 net trading revenue was US$20.5B, almost double 2023's US$10.6B. It made these disclosures to debt investors in the prospectus for a US$1.35B senior secured note due 2033. A reported profit margin of about 70% also comes from investor documents. — [IFR](https://www.ifre.com/opinion/2056519/jane-streets-hot-streak-tradings-top-dog-pulls-further-away); [Global Trading](https://globaltrading.net/?p=38181); first nine months of 2024 were $14.2B per [BNN Bloomberg](https://www.bnnbloomberg.ca/business/2024/12/02/jane-street-reaps-142-billion-in-first-nine-months-of-trading/)
- [PRESS] Jane Street's 2024 footprint:
  - ETFs: about US$707B traded per month, about 24% of the primary market and 16% of the secondary market in US-listed ETFs.
  - Options: about 8% of all OCC volume, close to one billion contracts.
  - US equities: roughly 10% of the market in 2024.
  
  — [Global Trading](https://globaltrading.net/?p=38181)
- [PRESS, unnamed sources] 2025 per Reuters: Jane Street net trading revenue $39.6B, Citadel Securities about $12.2B (+25% y/y), Hudson River Trading about $12.3B. Q1 2026: Jane Street reported a record $16.1B trading revenue and profit of $10.3B, partly tied to volatility and to its stakes in AI companies (Anthropic, CoreWeave), so not all of it is market-making P&L. — [MarketScreener/Reuters, $40B haul](https://www.marketscreener.com/news/jane-street-s-40-billion-trading-haul-tops-rivals-sources-say-ce7f59dfdf8ff52d); [MarketScreener/Reuters, Q1 2026](https://in.marketscreener.com/news/jane-street-rakes-in-record-first-quarter-trading-haul-of-16-1-billion-sources-say-ce7f5bdbdf8af521)
- [PRESS] Jane Street's 2025 total compensation was about $9.38B, more than double the prior year (Bloomberg via a secondary site). — [Munich Startup feed](https://insights.munich-startup.de/news/feed/jane-street-s-pay-pool-hits-9-4b-as-trading-revenue-reaches-record-39-6b) [SECONDARY]
- [PRIMARY, regulator interim order] SEBI's interim order of 3 Jul 2025:
  - It barred Jane Street entities from Indian markets and impounded about ₹4,843.57 crore (~$567M).
  - It alleged manipulation of BANKNIFTY on expiry days: buying index constituents and futures in the morning and selling them in the afternoon, which made large index-options positions more profitable.
  - Alleged net gains were about ₹36,671 crore (~$4.3B): roughly ₹44,358 crore from index options, offset by losses in futures and cash.
  - These are allegations; Jane Street disputes them.
  
  — [DT Next](https://www.dtnext.in/news/business/sebi-bans-us-based-jane-street-from-securities-mkt-impounds-illegal-gains-of-rs-4843-crore-839094); [Kotak Securities](https://www.kotaksecurities.com/news/market-news/sebi-bars-jane-street); [NBC/CNBC](https://www.nbcwashington.com/news/business/money-report/indian-regulator-bars-u-s-trading-firm-jane-street-from-accessing-securities-market/3950472/?amp=1)
- [PRESS] Citadel Securities: Q1 2025 net trading revenue was $3.4B (+~45% y/y), a record. Q2 2025 was reported as $2.39B (-8.4%), with H1 at $5.77B. 9M 2025 was $8.4B per investor documents, against a 2024 record of $9.7B. A Hedgeweek headline reporting a "$7.3bn" Q2 conflicts with Bloomberg's figure and is probably mislabelled, possibly a different period. — [Bloomberg Q1](https://www.bloomberg.com/news/articles/2025-05-27/citadel-securities-mints-3-4-billion-in-record-first-quarter); [Bloomberg Q2](https://www.bloomberg.com/news/articles/2025-08-29/citadel-securities-second-quarter-trading-revenue-slumps-8-4); [IFR](https://www.ifre.com/ifr-awards/2327839/flow-marketmaker-citadel-securities); conflicting: [Hedgeweek](https://www.hedgeweek.com/news/citadel-securities-posts-record-7-3bn-trading-revenue)
- [PRESS] Citadel Securities had about 1,700 staff, each generating on average about $1M of profit in one quarter (Q1 2025). This shows how strongly the business scales per head. — [eFinancialCareers](https://www.efinancialcareers.com/news/citadel-securities-1-700-people-each-generated-an-average-of-1m-in-profit-in-3-months)
- [PRIMARY, company release] Optiver 2025:
  - Net trading income €4.556B (+30% vs €3.494B in 2024).
  - Net profit to equity holders €1.769B (+29% vs €1.369B).
  - Total equity €5.490B (vs €4.905B).
  
  Optiver is mainly an options and futures market maker. — [Optiver](https://www.optiver.com/insights/news/optiver-reports-robust-financial-results-for-2025/)
- [PRIMARY/PRESS] Retail order-flow purchase via PFOF: Citadel Securities (CDRG) and Virtu (NITE) are the main paying destinations in broker 606 reports, at about 12-17 cents per 100 shares (see Q1). — [FINRA 606](https://cdn.finra.org/606/2025/48015_606_NMS_2025_Q4_V1.pdf)

### Inferences
- Revenue moves with volatility and volume: 2022 and 2024-2026 were high-volatility and high-volume years. Market makers earn more when spreads widen and turnover rises, and they do not need to forecast the direction of the move. This is a convex, activity-linked revenue stream, essentially a toll on turnover.
- Jane Street's dominance is concentrated in ETF arbitrage (creation/redemption against baskets and futures) and options. Both need authorized-participant status, balance sheet, securities lending, cross-asset pricing models and low latency. None of these exists in the FTMO/MT5 CFD environment.
- The SEBI case is a reminder that some of the largest "edges" lie in a grey zone: using a large footprint in the underlying to move a settlement or close price that a large options book references. An individual with $100k cannot do this, and should not try.

### Gaps
- XTX Markets and Flow Traders 2025 figures were not retrieved (searches returned only Optiver). From memory, Flow Traders publishes semiannual NTI and XTX files UK accounts; neither is verified here.
- I found no reliable breakdown of Jane Street or Citadel Securities revenue by product (options vs ETF vs equities vs FICC); only volume shares exist.
- The Hudson River Trading 2025 figure ($12.3B) comes from a single Reuters report citing sources.

## Q3. Bank trading revenue: client flow/market making vs. proprietary bets, Volcker evidence, prop-desk performance, loss days

### Takeaway
Bank markets revenue is overwhelmingly client-facilitation and market making:
- FICC and equities across the 12 big banks totalled about $175B in FY2025, with prime services/financing a large and growing share.
- Stand-alone proprietary trading was a small, volatile and on net unprofitable slice even before Volcker. The GAO found the six largest US banks' stand-alone prop desks earned $15.6B in 13 quarters, lost $15.8B in 5 crisis quarters, and ended with a net loss of about $221M over mid-2006 to 2010.

Daily trading P&L is positive on most but not all days. JPM's 2025 backtesting P&L was positive on 174 of 259 days, and that measure excludes intraday client flow and fees. The near-perfect records come only from spread and flow, not from directional risk.

### Cited Findings
- [PRIMARY, GAO-11-529, July 2011] For June 2006 to December 2010:
  - The six largest US bank holding companies' stand-alone proprietary trading desks generated $15.6B in 13 profitable quarters.
  - That revenue was "3.1 percent or less" of the firms' combined quarterly revenues.
  - They lost $15.8B in 5 crisis quarters, for an overall net loss of about $221M over 4.5 years.
  - One firm had the largest single-firm quarterly revenue ($1.2B) and two of the largest single-firm quarterly losses ($8.7B and $1.9B).
  - GAO could only analyze stand-alone desks because the firms did not separately record prop activity embedded in market-making desks.
  
  — [GAO-11-529 PDF](https://www.gao.gov/assets/330/321006.pdf); [accessible text](https://gao.gov/assets/a321009.html)
- [SECONDARY, law-firm commentary on GAO] Over the 4.5 years four of the six firms made money and two lost money on stand-alone prop. Losses on lending and other risky activities in the crisis were "far greater" than prop-trading losses. — [Harvard Law School Forum](https://corpgov.law.harvard.edu/2011/08/26/general-accountability-office-struggles-with-dodd-franks-volcker-rule)
- [PEER/Fed working paper] Bao, O'Hara & Zhou (FEDS 2016-102), "The Volcker Rule and Market-Making in Times of Stress": the rule reduced bank dealers' willingness to absorb inventory in stress, worsening corporate-bond liquidity around downgrades. Non-bank dealers partly filled the gap. This shows that bank "market making" relied on balance-sheet risk-taking that regulation then constrained. — [getAbstract summary](https://www.getabstract.com/en/summary/the-volcker-rule-and-market-making-in-times-of-stress/28995) [SECONDARY summary of the Fed paper]
- [PRIMARY/industry data] Coalition Greenwich Index for FY2025, 12 banks (BofA, Barclays, BNP, Citi, DB, GS, HSBC, JPM, MS, SocGen, UBS, Wells Fargo):
  - Markets revenue $174.7B (+14.5%).
  - Equities $71.5B (+20.7%), of which prime services & futures $34.5B and equity derivatives $24.7B.
  - FICC $103.1B (+10.5%), led by G10 rates, G10 FX, securitization and EM macro.
  - The growth was explained by volatility and geopolitical uncertainty driving client activity.
  
  — [Coalition Greenwich](https://www.greenwich.com/market-structure-technology/volatility-and-geopolitical-uncertainty-drove-fy25-global-markets)
- [PRIMARY] JPMorgan FY2025 10-K:
  - For the 12 months to 31 Dec 2025, the firm posted backtesting gains on 174 of 259 days and had 12 VaR backtesting exceptions.
  - The 10-K stresses that backtesting P&L "exclude[s] certain components of total net revenue, such as client-driven intraday trading, fees, and net interest income". So actual Markets revenue loss days are fewer; they are disclosed separately in the CIB Markets section.
  
  — [JPM 10-K FY2025](https://www.sec.gov/Archives/edgar/data/19617/000162828026008131/jpm-20251231.htm)
- [PRIMARY] Goldman Sachs FY2024 10-K: firmwide period-end VaR was $91M (2024 range $75M to $116M), and the firmwide VaR limit was not exceeded. — [GS 10-K FY2024](https://www.sec.gov/Archives/edgar/data/886982/000088698225000005/gs-20241231.htm)
- [PRESS, Risk.net / Global Trading] VaR exceptions:
  - Goldman had two VaR exceptions totalling $295M ($153M and $142M) in a quarter including the April 2025 tariff shock, against an average daily trading revenue of $119M in that period.
  - Goldman had three exceptions in another period, pushing its capital multiplier above 3 for the first time in more than a decade (year unclear in the snippet).
  - JPM had two breaches in Q4 2024 and two in Q1 2025 ("lost $203m on two days in Q1").
  
  — [Global Trading: GS $687m on two days in August turmoil](https://globaltrading.net/?p=37058); [Risk.net: Wall Street giants rack up VaR breaches](https://www.risk.net/risk-quantum/7963546/wall-street-giants-rack-up-var-breaches); [Global Trading: JPM $203m on two days](https://www.globaltrading.net/?p=38577)

### Inferences
- Bank desks are mostly toll collectors: market making, client facilitation, and financing (prime brokerage, repo, securities lending). Revenue scales with client activity and volatility. The pieces that resemble what a retail trader does (stand-alone directional prop) earned about 3% of revenue in good quarters and wiped out all of it in the crisis. The best-resourced directional traders in the world, with information flow, financing and research, did not produce a net positive stand-alone prop P&L over 2006-2010 in the GAO sample.
- Even big flow banks have dozens of losing days per year on a risk-P&L basis, and occasional $100M-$700M losing days in shocks such as August 2024 and April 2025. Spread income makes most days positive; inventory risk makes some days very negative. That is the Menkveld decomposition (Q4) at bank scale.
- "Loss days" in VaR backtesting are not the same as "trading-revenue loss days". Reports that "bank X lost money on only N days" usually quote the revenue measure, which includes fees and intraday client spread.

### Gaps
- I did not retrieve Goldman's or JPM's official count of "days with trading losses" (CIB Markets revenue loss days) for 2024/2025; the 10-K figure cited above is backtesting P&L.
- Specific pre-2008 prop-desk blow-ups were not verified in this session: Deutsche Bank credit prop (Boaz Weinstein), Citi, the Morgan Stanley mortgage desk, and UBS (Dillon Read). The GAO's anonymized $8.7B single-quarter loss is widely believed to be Morgan Stanley Q4 2007, but the GAO does not name it, so treat that as unconfirmed.
- Primary text of Bao/O'Hara/Zhou not read; only a secondary summary.

## Q4. Academic evidence on who profits intraday (HFT profitability, concentration, decay, latency arms race)

### Takeaway
The peer-reviewed evidence on intraday profits points the same way:
- In the E-mini, HFT profits are large in Sharpe terms but tiny per contract: median Sharpe about 4.3, and profit per contract about $0.46 at the median firm (~0.1 bp of notional).
- Profits are concentrated in a few incumbent firms ("winner takes all"). New entrants underperform and exit.
- Liquidity-taking HFTs earn more than passive ones, and do so through relative speed.
- Per contract, the profit is extracted mostly from small (likely retail) traders, who lose about $3.49 per contract per trade at a 1-minute horizon to aggressive HFTs.
- Latency-arbitrage races decide outcomes in microseconds and are won by about six firms.

### Cited Findings
- [PEER] Baron, Brogaard, Hagströmer & Kirilenko, "Risk and Return in High-Frequency Trading", JFQA 54(3), 2019, pp. 993-1024. CFTC working-paper version (2014) studies E-mini S&P 500 audit-trail data with trader IDs, Aug 2010 to Aug 2012, regular trading hours. — [CFTC working paper PDF](http://www.cftc.gov/sites/default/files/idc/groups/public/@economicanalysis/documents/file/oce_riskandreturn0414.pdf); [JFQA listing (RePEc)](https://ideas.repec.org/a/cup/jfinqa/v54y2019i03p993-1024_00.html). Key numbers from the working paper:
  - Market setting: the E-mini is zero-sum with no designated market makers and "no maker-taker fees or liquidity rebates for the front-month contract". Trading fee is about $0.15/contract. Average volume is about 3.2M contracts/day; one contract is about $50,000 notional with a $12.50 tick.
  - Risk-adjusted returns: the median HFT firm has an annualized Sharpe of 4.3 and 4-factor alpha of 22.02%. By type, Sharpe is 5.85 for Passive, 5.26 for Mixed and 4.29 for Aggressive. 25% of HFTs have Sharpe above 9.10 and 10% above 12.68 (S&P 500 Sharpe: 0.31).
  - Aggressive vs passive: Aggressive (liquidity-taking) HFTs earn mean annualized alpha of 90.67% vs 23.22% for Passive. The average daily gross revenue per firm is about $74,000 for Aggressive, $27,910 for Mixed and $12,600 for Passive. Annualized, that is over $18.6M, $7.0M and $3.2M per firm, in the E-mini alone.
  - Profit per contract: the median firm earns about $0.46 per contract (the paper prints "0.46%", apparently a typo for $0.46), against $2.01 for the top-decile firm.
  - Who pays (August 2010, 1-minute horizon profits):
    - HFTs took $35.23M in total from non-HFTs over 31.96M contracts, i.e. about $1.10 per contract, an effective cost of about 0.22 bp on others.
    - Per contract, Fundamental (large institutional) traders lose the least to HFTs (-$1.92/contract vs Aggressive HFTs). Small traders (likely retail, under 20 contracts/day) lose the most (-$3.49/contract).
    - Aggressive HFTs make about 45% of their profits by adversely selecting other (passive/mixed) HFTs.
    - Most dollar profits come from "Opportunistic" traders.
  - Horizon: Aggressive HFTs lose money at very short horizons (paying the spread) but earn it back over longer, still intraday, horizons. Passive HFTs earn at short horizons and lose over longer horizons.
  - Concentration and entry: the profit Herfindahl for Passive HFTs rose from 0.287 (2010) to 0.545 (H2 2012); for Aggressive it was about 0.36-0.38. "New entrants are less profitable and more likely to exit", and the paper describes the industry as winner-takes-all. Relative latency (Weller's rank-order speed) explains large performance differences, most strongly for Aggressive HFTs.
- [PEER] Menkveld, "High frequency trading and the new market makers", Journal of Financial Markets 16(4), 2013 (Chi-X/Euronext, 2007-08). One large HFT market maker earned:
  - €1.55 per trade on the spread, net of fees,
  - minus €0.68 per trade of "positioning" (inventory) loss,
  - for about €0.88 gross profit per trade.
  
  The positioning result splits into a +€0.45 profit on positions held under 5 seconds and a -€1.13 loss on longer-held positions. Chi-X's success depended on this HFT's participation and its low fees. — [Tinbergen working paper](https://repec.tinbergen.nl/tin/wpaper/11076.rdf); [NBER meeting summary](https://nber.org/confer/2011/MMf11/summary.html); [publication page](https://tinbergen.nl/publication/165303/high-frequency-trading-and-the-new-market-makers). The paper's HFT Sharpe of about 9.35 is quoted by Baron et al. in the [CFTC paper](http://www.cftc.gov/sites/default/files/idc/groups/public/@economicanalysis/documents/file/oce_riskandreturn0414.pdf).
- [PEER] Aquilina, Budish & O'Neill, "Quantifying the High-Frequency Trading 'Arms Race'", QJE 2022. Data: LSE message data for all FTSE 350 stocks over 9 weeks in 2015.
  - Frequency and speed: latency-arbitrage races happen about once per minute per FTSE 100 symbol. The modal race lasts 5-10 microseconds. Races account for about 20% of trading volume.
  - Value: the average race is worth about half a tick, which amounts to a latency-arbitrage "tax" of about 0.5 bp on trading volume and about $5B/yr in global equities.
  - Who wins: the top 6 firms account for over 80% of race wins and losses.
  - Policy implication: removing latency arbitrage would cut the cost of liquidity by 17%.
  
  — [Harvard Law Forum summary](https://corpgov.law.harvard.edu/2021/11/05/quantifying-the-high-frequency-trading-arms-race); [BIS WP 955](https://www.bis.org/publ/work955.pdf); [FCA Occasional Paper 50](https://www.fca.org.uk/publications/occasional-papers/occasional-paper-no-50-quantifying-high-frequency-trading-arms-race-new-methodology); [NBER w29011](https://www.nber.org/system/files/working_papers/w29011/w29011.pdf)

### Inferences
- The size of the edge is the key fact. Compare:
  - The median E-mini HFT's profit: about $0.46 per $50,000 contract, ≈0.09 bp.
  - The whole HFT "tax" on others: ≈0.22 bp.
  - The latency-arbitrage tax: ≈0.5 bp.
  - This project's frozen cost model for an FTMO CFD trader: ≈1.4 bp round trip (1.0 bp spread + 0.2 bp slippage per side; `research/reports/cost_model.md`). Measured FTMO-like quotes are about 0.5-1.5 bp round trip.
  
  So a retail CFD trader pays per round trip roughly 3-15x what the professional intermediary earns per contract. Any edge the trader exploits must be at least an order of magnitude larger per trade than a market maker's.
- High Sharpe ratios and near-zero losing days come from huge N and inventory control. They do not come from directional skill and cannot be reached at retail trade frequency.
- The most relevant finding for this user: in the E-mini, small traders were the most profitable counterparty per contract for HFTs. Short-horizon retail trading in index futures is, on average, the source of HFT profit, not a competitor to it. A CFD trader is one layer further out, since the CFD broker or prop firm hedges or internalizes, so the trader also pays the broker's markup.
- Aggressive HFTs lose at the shortest horizons and win over longer intraday horizons, and passive HFTs show the opposite pattern. Both are microsecond-to-minutes effects tied to order-book state and relative speed. A trader with about 100 ms of latency on M1-M15 bars sees none of this information.

### Gaps
- I did not verify whether HFT profitability in the E-mini declined after 2012. Industry consolidation (e.g. Virtu-KCG in 2017) and the papers' finding of persistently high concentration point to competition among HFTs compressing per-contract margins rather than retail gaining access. No source checked in this session quantifies post-2012 decay.
- Other relevant papers were not retrieved in this session (from memory, not verified):
  - Kirilenko, Kyle, Samadi & Tuzun on the Flash Crash.
  - Brogaard, Hendershott & Riordan (2014, RFS) on HFT and price discovery.
  - Hagströmer & Nordén (2013) on market-making vs opportunistic HFT.
  - Budish, Cramton & Shim (2015) on frequent batch auctions.

## Q5. Which of these edges can an FTMO-style CFD trader access? (skeptical decomposition)

### Takeaway
Almost none of the core sources of intermediary profit are available. The prop-firm CFD trader is structurally on the other side of them: a liquidity taker paying spread, commission and latency costs, with no flow, no rebates, no balance sheet and no microstructure data. The only parts that are even partly accessible are those that do not depend on being an intermediary:
- slower risk premia and structural flows that last minutes to hours (rebalancing, month-end, overnight vs intraday, volatility-risk-premium-like effects);
- volatility-scaled risk management;
- the discipline of strict loss limits and "lockdown".

Each of these still has to beat about 1.4 bp round trip, plus the prop firm's rule constraints.

### Cited Findings
- Spread capture. Market makers earn the bid-ask spread: Virtu "earning small amounts of money based on the difference" between bid and ask, and Menkveld's €1.55 per trade spread profit. — [Virtu S-1](https://www.sec.gov/Archives/edgar/data/0001592386/000104746914002070/a2218589zs-1.htm); [Menkveld WP](https://repec.tinbergen.nl/tin/wpaper/11076.rdf). On FTMO MT5 the trader can only trade against the broker's quote; there is no exchange order book in which to post a resting limit order. The project's cost model assumes the trader pays about 1.0 bp spread plus 0.2 bp slippage per side (`research/reports/cost_model.md`). **Status: inaccessible; the trader pays it.**
- Order-flow information and PFOF. Wholesalers pay about $0.0013-0.0017/share for retail flow because it is less informed. Per contract, small traders were the most profitable counterparty for E-mini HFTs (-$3.49/contract). — [FINRA 606](https://cdn.finra.org/606/2025/48015_606_NMS_2025_Q4_V1.pdf); [Baron et al. CFTC WP](http://www.cftc.gov/sites/default/files/idc/groups/public/@economicanalysis/documents/file/oce_riskandreturn0414.pdf). **Status: inaccessible.** The trader is the flow, not the recipient.
- Speed / latency arbitrage. Modal races last 5-10 µs and the top 6 firms win over 80% of them. — [Aquilina-Budish-O'Neill](https://www.bis.org/publ/work955.pdf). A retail MT5 setup with ~100 ms+ latency is about 10,000x slower than the modal race. **Status: inaccessible.** Worse, a CFD trader trying to "latency-arb" a broker's stale quote would breach typical prop-firm terms, so it should not be considered.
- Rebates / fee tiers / self-clearing. Virtu avoids clearing fees as a DTC member; fees were still about 31% of 2013 trading income. The E-mini front month has no maker rebates at all. — [Virtu S-1](https://www.sec.gov/Archives/edgar/data/0001592386/000104746914002070/a2218589zs-1.htm); [Baron et al.](http://www.cftc.gov/sites/default/files/idc/groups/public/@economicanalysis/documents/file/oce_riskandreturn0414.pdf). **Status: inaccessible.**
- Scale and diversification. Virtu covers 10,000+ instruments on 210+ venues, with only 51-52% winning trades but about 99.9% winning days. — [Virtu S-1](https://www.sec.gov/Archives/edgar/data/0001592386/000104746914002070/a2218589zs-1.htm); [1library/Bloomberg](https://1library.net/document/qv957wgy-greg-laughlin-figure-google-trends-chart-frequency-trading.html). With 3-4 highly correlated instruments (US100, US500, GER40 and partly XAUUSD), the trader cannot diversify a tiny edge into a smooth P&L. **Status: inaccessible.**
- Balance sheet, financing and ETF/options arbitrage. Bank prime services and futures reached $34.5B in FY2025. Jane Street holds 24% of ETF primary-market activity. — [Coalition Greenwich](https://www.greenwich.com/market-structure-technology/volatility-and-geopolitical-uncertainty-drove-fy25-global-markets); [Global Trading](https://globaltrading.net/?p=38181). **Status: inaccessible.**
- Directional proprietary bets, the only category resembling retail trading. Stand-alone bank prop desks lost about $221M net over 2006-2010 (+$15.6B in 13 quarters, -$15.8B in 5). — [GAO-11-529](https://www.gao.gov/assets/330/321006.pdf). **Status: accessible in form, but the best-resourced practitioners did not show a robust net edge.**
- Risk management practices (instantly transferable). Virtu's automated "lockdown" when a strategy's P&L leaves preset bounds, and VaR limits with backtesting at banks. — [Virtu S-1](https://www.sec.gov/Archives/edgar/data/0001592386/000104746914002070/a2218589zs-1.htm); [JPM 10-K](https://www.sec.gov/Archives/edgar/data/19617/000162828026008131/jpm-20251231.htm). **Status: accessible.** This maps directly onto FTMO's 5% daily / 10% total loss rules and the project's `RiskPolicy`.

### Inferences
- Summary matrix for an individual on FTMO trading index CFDs and gold on M5/M15:

  | Edge source | Who earns it | Accessible to FTMO CFD trader? |
  |---|---|---|
  | Spread capture | Market makers | No, the trader pays it |
  | Payment for order flow / informed-vs-uninformed flow | Wholesalers, banks | No, the trader is the flow |
  | Latency / speed | Top HFTs | No (~100 ms vs ~10 µs) |
  | Rebates, self-clearing, fee tiers | Exchange members | No |
  | Breadth and scale | MMs, banks | No (3-4 correlated symbols) |
  | Balance sheet, financing, ETF/options arbitrage | Banks, Jane Street, Citadel, Optiver | No |
  | Directional intraday prediction | Prop desks, Aggressive HFTs (at µs-min horizons with order-book data) | Possible in principle, but no robust evidence of net edge even for banks; retail is the documented loser |
  | Structural flows and risk premia (rebalancing, month-end, overnight, vol-scaled exposure) | Systematic funds | Partly; the edge must exceed ~1.4 bp round-trip plus FTMO rule friction |
  | Risk discipline (loss limits, lockdown, VaR-style sizing) | Everyone above | Yes, the most transferable lesson |

- The professional evidence here is consistent with the project's own research results: none of A1-D2 survived out of sample. The intermediaries' profits come from structure (being the house), not from forecasting index direction on 5-15 minute bars. Retail's measurable role in that structure is as the counterparty that pays.
- The "1 losing day in 1,238" record should not be a benchmark for a prop-challenge bot. An honest directional intraday strategy with a real but modest edge will have losing days on perhaps 40-50% of days. The FTMO problem is to keep that distribution's left tail inside 5% daily / 10% total, which is a sizing problem (`propsim.risk_sweep`), not a market-making problem.
- If the user ever wants an intermediary-like edge, it requires a different business: exchange membership or a DMA futures account, co-location, rebates and capital. That is not a $100k prop-firm account.

### Gaps
- FTMO's own execution model (whether its liquidity provider internalizes trader flow or hedges it, and its typical latency) is not publicly documented in sources found here. The ~100 ms latency figure comes from the task brief, not a measured source.
- No academic study was found that measures the profitability of prop-firm CFD challenge traders specifically. FTMO pass and payout statistics belong in a separate research note (see `research/reports/prop_economics.md`).
