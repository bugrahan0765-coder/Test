# TikTok signal validity: what predicts a winning app idea / content format, and a protocol to test it

Compiled 2026-11-06 from 12 web searches and 2 page fetches. Companion files:
`practitioner_methods.md` (what practitioners do) and `apify_tooling_legal.md` (tooling, ToS, KVKK/GDPR).
This file asks the prior question: **which of those numbers carry information, and how do we avoid
fooling ourselves with them.** The trading research in `pfbot/` uses the same discipline (pre-registration,
IS/OOS, locked final test, trial registry); analogies are made explicit where useful.

Evidence labels used throughout:
- **[E]** peer-reviewed / primary research (checked via abstract, publisher page or press coverage this session)
- **[E-mem]** primary research cited from my own background knowledge, not re-verified this session; check before relying on it
- **[P]** platform documentation (TikTok newsroom, help pages, transparency reports)
- **[V]** vendor or secondary source (commercial stake or thin sourcing)
- **[R]** my reasoning
- **[H]** heuristic threshold: a starting point to be calibrated, not a measured value

No industry benchmark numbers (e.g., "a good share rate is X%") are given anywhere below, because I found no
credible source for them. Every threshold is labelled [H].

---

## 0. The core finding in five lines

1. Ex-ante prediction of which single item goes viral is weak; prediction improves a lot only **after** early
   growth is observed [E: Cheng et al. 2014; Martin et al. 2016]. Visibility and predictability arrive together,
   so "early" and "certain" are a trade-off, not a choice.
2. Social influence makes single outcomes noisy and path-dependent: quality bounds the extremes but the middle
   is a lottery [E: Salganik, Dodds & Watts 2006]. **One viral video is one draw from that lottery.**
3. Popularity is mostly driven by the size of the largest broadcast, not by person-to-person spread [E: Goel et
   al. 2016]. Raw view totals for a format can therefore be one big account's audience, not demand.
4. The informative unit is therefore **replication across independent "worlds"**: many distinct creators, in
   different follower tiers and geos, each beating *their own* baseline with the same format, persisting in a
   later time window [R, built on 1-3].
5. Engagement measures attention and emotion; sharing in particular is driven by arousal [E: Berger & Milkman
   2012]. Neither is willingness to pay, and even stated WTP overstates real payment [E: Murphy et al. 2005].
   Money questions must be answered by a priced test, not by TikTok data.

---

## 1. What the research actually says (and what it does not)

### 1.1 Cheng, Adamic, Dow, Kleinberg, Leskovec (2014), "Can cascades be predicted?" (WWW 2014) [E]
- Data: Facebook photo reshare cascades. Task: given a cascade has reached k reshares, predict whether it will
  keep growing (the headline framing is "will it double?").
- Findings (abstract, fetched): "strong performance in predicting whether a cascade will continue to grow";
  temporal and structural features are the key predictors; prediction improves as more of the cascade is
  observed; "initially, breadth, rather than depth in a cascade is a better indicator of larger cascades."
- Press coverage (Stanford via phys.org) reports ~8/10 accuracy on doubling, approaching 88% for large cascades,
  and that speed alone predicted doubling 78% of the time. These numbers come from press coverage, not the paper
  tables; I did not verify them against the PDF.
- [E-mem] The doubling task is constructed so that roughly half the cascades double, i.e. the chance baseline
  is ~50%. "80% accuracy" is therefore a meaningful but modest improvement over a coin flip, and it is
  *conditional on the cascade already being in progress*.
- **What this does not show:** that you can predict from content at t=0, or that a format (as opposed to one
  cascade) will keep working. It shows that *velocity* and *breadth* of early spread carry information.
- Implication [R]: (a) velocity (growth per unit time at fixed age) is the best-supported single per-video
  signal; (b) "breadth over depth" maps naturally onto *many creators* over *one account*; (c) the
  predictable part of a cascade is the part that is already visible, so a scraper that finds a format "early"
  is trading certainty for timing.

### 1.2 Salganik, Dodds & Watts (2006), MusicLab, *Science* 311:854-856 [E]
- 14,341 participants, unknown songs; some saw download counts (social influence, split into 8 independent
  "worlds"), others did not (independent condition).
- Social influence increased both **inequality** and **unpredictability** of success. "The best songs rarely
  did poorly, and the worst rarely did well, but any other result was possible."
- The authors note real-world social influence (marketing, charts, algorithms) is much stronger than in the
  experiment.
- Implication [R]: a TikTok For You feed is a social-influence world with an extremely strong amplifier.
  The fact that a given video/format won *in one world* tells you little about intrinsic appeal. The
  experimental fix, many independent worlds, is approximated by **distinct creators with separate audiences,
  different geos, and different time windows**. That is the design principle of the protocol below.
- Caveat [R]: TikTok creators are not independent worlds; copycats see the original before posting
  (bandwagon), and the same recommender serves all of them. Breadth is therefore an upper bound on
  independent replication, not a clean count.

### 1.3 Martin, Hofman, Sharma, Anderson & Watts (2016), "Exploring limits to prediction in complex social systems" (WWW 2016) [E]
- Even in a simulated world with perfect knowledge, predictability of cascade size has a ceiling; adding
  realistic heterogeneity in spreading probability cuts the achievable R² substantially (search excerpt:
  ~0.93 theoretical to ~0.60 with ~15% heterogeneity).
- Empirically on Twitter, the best models explained **less than half** the variance in cascade size.
- [E-mem] Features of the *poster* (past success) carried most of the predictive power; content features
  added comparatively little.
- Implication [R]: (a) the creator's own history is the right baseline, which is exactly what the "outlier
  ratio vs creator median" does; (b) any claim of "this hook predicts virality" from a scan of top videos
  should be met with "out of sample, how much variance?" The literature says: not much.

### 1.4 Goel, Anderson, Hofman & Watts (2016), "The structural virality of online diffusion", *Management Science* 62(1) [E]
- ~1 billion Twitter diffusion events. Popularity is driven mainly by the size of the largest broadcast;
  structural virality (multi-generation spread) is low at every size; size and virality correlate weakly;
  the vast majority of cascades are tiny.
- Implication [R]: a format whose total views are concentrated in one or two big accounts is a broadcast
  event, not evidence of a replicable format. Concentration metrics (top-creator share of views) belong in
  the protocol.

### 1.5 Berger & Milkman (2012), "What makes online content viral?", *JMR* 49(2) [E]
- NYT articles: high-arousal emotions (awe, anger, anxiety) increase sharing; low-arousal (sadness) decreases
  it; robust to controls for surprise, interest, practical usefulness and placement; experiments support
  causality via arousal.
- Implication [R]: **share rate measures emotional activation**. Great for distribution (and consistent with
  scorecard criterion 6), but it is not a demand or payment signal. A format can be highly shareable because
  it is outrageous, which says nothing about a paid app.

### 1.6 Murphy, Allen, Stevens & Weatherhead (2005), meta-analysis of hypothetical bias, *Env. & Resource Econ.* 30 [E]
- 28 studies, 83 observations: median hypothetical/actual WTP ratio ~1.35, with severe positive skew
  (some studies overstate by much more). Choice-based elicitation reduced bias.
- Implication [R]: even an explicit "would you pay X?" overstates; "I want this" comments and free waitlist
  signups are weaker still. TikTok data is upstream of WTP; it cannot substitute for a priced test.

### 1.7 Platform documentation [P]
- TikTok's 2020 newsroom post "How TikTok recommends videos #ForYou": ranking uses user interactions (likes,
  shares, follows, comments, content created), video information (captions, sounds, hashtags) and
  device/account settings (language, country, device), "weighted based on their value to a user". No
  weights are published; the post is from 2020 and the system has surely changed since. Third-party claims
  that watch time/completion are the strongest signals are plausible but [V].
- TikTok Creative Center "Top Ads" (help page, fetched): a collection of "high-performing creatives",
  all "authorized by advertisers"; filters by region, industry, objective; shows a second-by-second
  engagement graph. It does not say how "high-performing" is determined; search snippet of the same page
  says performance thresholds are applied by country and Top Ads is not exhaustive. Third-party guides say
  CTR is shown as a percentile and 2s/6s view rates are sortable [V, verify in the UI].
- Transparency reports: TikTok removes fake engagement at very large absolute scale, e.g. Q4 2023 ~1.03B fake
  likes and ~720M fake followers removed globally; US Q2 2026 ~781M fake followers removed and 14.6M fake
  accounts removed (secondary press summaries of TikTok reports; check the Transparency Center). These prove
  fake engagement is common in absolute terms; they do **not** give a rate per view, and they only count what
  was caught.

### 1.8 Data-access research [E/V]
- TikTok Research API audits: AI Forensics (2025) found ~1 in 8 videos without retrievable metadata (gaps
  included ads, official accounts, China-origin content); Entrena-Serrano et al. (arXiv 2506.09746) describe
  the API as incomplete and inconsistent; during the 2024 EU elections view/share counts were heavily
  under-reported (later apparently fixed); Bai & Gu (2026, Social Science Computer Review, 6,373 videos from
  14 creators) found systematically lower views but higher comments/shares in the API than in manual
  front-end collection. We are not eligible for this API anyway (see `apify_tooling_legal.md`), but the lesson
  generalizes [R]: **every collection path (API, scraper, manual) has its own missingness and its own
  measurement bias**, and these are not random.
- Google Trends: indices are computed on a random sample of searches, so identical queries pulled at
  different times differ, especially for low-volume terms, small geos and daily granularity; low volume is
  floored to zero; averaging many pulls and using weekly data helps; results are cached ~24h so repeated
  pulls the same day do not add information (arXiv 2504.07032 and survey-methods papers; one secondary source
  cites cross-extraction correlations of 0.79-0.94, [V] unverified).
- App download/revenue estimators (Sensor Tower, Appfigures): no independent published error benchmark found.
  Vendors claim accuracy without error bars; estimates are model outputs from public proxies (ranks, reviews),
  revenue is net of store fees; secondary sources suggest errors of tens of percent and anecdotes of 2x misses
  [V]. Consensus among practitioners [V]: more reliable for **direction and rank order** than for levels.

---

## 2. Signal-by-signal assessment

Columns: what it really measures / evidence status / main failure modes / how to use it.

| Signal | Measures | Status | Failure modes | Use |
|---|---|---|---|---|
| **Share rate per view** (shares / views) | Emotional activation; willingness to put content in front of friends | Shares are a documented ranking input [P]; arousal drives sharing [E] | Outrage/novelty shares; denominator noise (views); share counts can be faked; API/scraper under-reporting differs by path [E] | Distribution-potential signal; strong for "will the app's output spread" (scorecard 1, 5, 6). Not a demand signal. |
| **Save rate per view** (collectCount / views) | "I want to come back to this": utility/intent to act later | No academic validation found; heuristic [R] | Saves for recipes/tutorials are high regardless of app need; small counts at low views | Better than likes as a utility proxy [R]. Use per format, relative to the same creators' baseline. |
| **Completion / watch time** | Hook and retention quality | Widely claimed to be a top ranking signal [V]; TikTok doc mentions interactions generically [P] | **Not observable for other people's videos** (only in your own analytics; for ads via Creative Center view-rate percentiles [V]); confounded by video length | Use only on your own fake-door videos and as a qualitative look at Top Ads. Do not pretend scraped data contains it. |
| **Comment intent** ("what app", "link?", "name?", "where can I get this", "does it work on iPhone") | Expressed desire to use the thing shown | No academic validation; strongest direct demand proxy available organically [R] | **Prompted comments** ("comment LINK and I'll DM you" automations) inflate it mechanically; bots; the question may already be answered (an incumbent app exists); language/geo variation | Pre-registered keyword lexicon per language, exclude videos whose caption/overlay solicits comments, measure per 1,000 comments and per 100k views, hand-audit a random sample. Record whether the answer names an existing app. |
| **Breadth: # distinct creators succeeding with the same format** | Replication in quasi-independent worlds | Grounded in Salganik [E] + Goel [E] + Cheng "breadth over depth" [E] by analogy; the specific metric is [R] | Copycat dependence (bandwagon); breadth grows as a trend saturates (late signal); format definition is subjective | **Primary structural signal.** Count creators with ≥1 outlier hit, across follower tiers; pair with concentration (top-creator share of format views). |
| **Outlier ratio vs creator's own median** | Excess performance after removing audience size | Supported indirectly: poster history is the dominant predictor [E-mem, Martin et al.]; practitioners use it [V] | Regression to the mean (selected outliers shrink later); look-ahead if the median uses posts after the target; small creators have noisy medians; age mismatch of views | Like excess return vs benchmark. Use log ratio, median of prior N posts only, minimum N, fixed-age views. |
| **Persistence / velocity** | Growth speed at fixed age; whether the format keeps producing hits | Velocity is the top predictor of cascade growth [E, Facebook]; format persistence is [R] | View counts are cumulative, requiring repeated snapshots; algorithm regime changes | Velocity at the video level (views at age 24h/72h); persistence at the format level via the temporal holdout (section 4.5). |
| **Cross-geo replication** | Robustness to culture/audience; another independent world | [R] | Geo attribution is weak (creator location, language, proxy country); account rules forbid VPN spoofing on posting accounts; cultural formats legitimately don't travel | Secondary confirmation; also tells you which market to launch in. Identify geo by language + creator location, not spoofing. |
| **Paid-ad longevity** | Revealed preference of an advertiser: they keep paying, so probably ROI-positive (or not yet killed) | Logic is sound [R]; practice is common in ad-spy workflows [V]; Top Ads is curated, threshold-based, non-exhaustive [P] | Spend not shown; long-running ≠ profitable (brand budgets, VC-funded burn, low-spend ads left on); library coverage is region-limited (EU Commercial Content Library) | Strong evidence that **someone monetizes this audience with this kind of creative**. Useful for WTP direction; also a competition warning. |
| **App-store rank / revenue estimates** | Whether apps answering this need make money | Estimates have no published error bars [V]; rank is a black-box function of recent downloads [R] | Levels can be off by large factors [V]; category ranks are noisy for small apps; rank-buying | Use direction and rank order; look for apps that TikTok comments name and check their rank trajectory over the same weeks. |
| **Google Trends / search volume** | Off-platform intent | Sampling noise documented [E/V] | Zeros for low volume; noise at daily/small-geo level; keyword-tool volumes are modelled | Average several pulls on different days, weekly granularity, compare to fixed control terms in the same geo. Direction only. |
| **Likes, raw views, follower counts** | Exposure and passive approval | Mostly vanity [R] | Cheapest to fake [P: removal volumes]; cumulative and age-dependent; dominated by largest broadcast [E] | Use only as denominators and baselines, never as the success criterion. |

**Hierarchy of evidence for an app idea [R]:**
money actually paid (own test) > priced-waitlist conversion (own test) > competitors' revenue direction +
long-running paid ads in the niche > organic intent comments replicated across many creators >
breadth of outlier hits across creators/geos, persisting out of sample > share/save rates >
one viral video > likes / raw views.

---

## 3. Biases and traps (mechanism and mitigation)

### 3.1 Survivorship bias
- **Mechanism:** search and For You surface winners. You see 30 hits of format F and never see the 3,000
  attempts that got 200 views. "30 creators succeeded with F" is meaningless without the denominator.
- **Trading analogue:** backtesting only on stocks that are in the index today.
- **Mitigation [R]:** sample the denominator. The best practical frame is **creator-timeline sampling**: for
  every creator found using F, pull their full recent timeline (all posts in the window). That yields all their
  F attempts (hits and flops) and their non-F posts as a within-creator control. The quantity of interest is
  **lift** = P(hit | F) / P(hit | same creators, not F), not the count of hits.

### 3.2 "Visible = already saturated" timing
- **Mechanism:** Cheng et al.: predictability comes from observing growth, so by the time a format is
  provably working it is already spreading; by the time it fills search results, many creators (and maybe
  apps) have entered. For apps there is a second layer: if every "what app?" comment is answered with an
  app name, the demand is already served and your entry is the copy (scorecard: "kopya ürünün paylaşımı
  orijinalin reklamını yapar").
- **Mitigation [R]:** (a) measure *trajectory* (new creators entering per week, lift in W2 vs W1) rather than
  level; (b) separate the content trend from the *underlying need*: formats die, needs persist; the protocol
  tests the need via intent comments and off-platform sources; (c) treat "answered with a named incumbent" as
  a competition flag that requires a stated differentiation (language, culture, price, platform) before
  proceeding; (d) accept that a 4-8 week protocol finds medium-lived opportunities, not two-week fads.
  Racing two-week fads is a different (and, per the literature, mostly unpredictable) game.

### 3.3 Algorithm volatility / non-stationarity
- **Mechanism:** ranking weights change without notice (the only official description is from 2020 [P]);
  seasonal effects (December "year-in-review" formats, Ramadan, exams); policy changes in labelling AI content.
- **Mitigation [R]:** never compare absolute levels across months; compare format vs matched control **in the
  same time window** (difference-in-differences logic); keep W1 and W2 adjacent; log known platform events in
  the registry and treat a window containing one as suspect, as one would treat a data-vendor change in
  trading.

### 3.4 Fake engagement / bots
- **Mechanism:** fake likes and followers exist at the scale of hundreds of millions to billions removed per
  quarter [P]; we only see what was not caught. Comment bots and engagement pods exist. Scraped comment
  sections may also include the creator's own "comment X" automation replies.
- **Mitigation [R]:** weight signals by cost-to-fake (specific, context-relevant comments > shares/saves >
  likes > views); use medians and log scales so a few manipulated videos cannot drive a format's statistic;
  flag anomalies (likes/view far outside the creator's own distribution, duplicate or generic comments,
  follower spikes) and run every key result **with and without flagged videos**; require breadth across many
  creators, which is expensive to fake.

### 3.5 Cumulative views inflated by older content
- **Mechanism:** a video posted 60 days ago has had more time to accumulate views than one posted 3 days ago;
  search ranking may favour older, already-popular videos; creator medians computed from all-time counts mix
  ages. Displayed counts are rounded ("1.2M"). Exactly how TikTok counts views (e.g., replays) is not
  documented in the sources I found, so views are a noisy denominator.
- **Trading analogue:** look-ahead bias and comparing returns over different holding periods.
- **Mitigation [R]:** record `createTime` and scrape time for every observation; compare videos at **fixed age**
  (e.g., views at ~72h and ~7d); for the creator baseline, use only posts that were already at least as old as
  the comparison age when observed, and only posts **before** the target; use raw counts from the scraper
  fields (playCount, shareCount, collectCount) rather than rounded UI text.

### 3.6 Sampling bias of scrapers and search results
- **Mechanism:** search results are ranked and personalized (language, country, device, account history);
  hashtag and sound pages have their own ranking; API audits show non-random missingness (ads, official
  accounts, some origins) and count discrepancies between paths [E]; scrapers break silently when TikTok
  changes anti-bot measures; `locationCreated` is not always present.
- **Mitigation [R]:** fix and log the access context (research phone/account or logged-out scraper with a stated
  proxy country), the exact query, timestamp and result rank; draw from several entry points (search,
  hashtag, sound, creator timelines); keep the "top results" stream and the "denominator" stream separate and
  never compute rates from the top-results stream alone; re-collect a small random subset manually to measure
  the scraper's discrepancy; record failed/missing rows rather than dropping them.

### 3.7 Multiple comparisons when scanning thousands of videos
- **Mechanism:** formats × hooks × geos × metrics × thresholds × windows is a garden of forking paths. With
  hundreds of candidate formats, a handful will look extraordinary by chance, and the *selected* winners will
  regress toward the mean in the next window even if nothing changed.
- **Trading analogue:** the ~5,000 logged trials in `research/trials.jsonl`; D2 passed IS and failed OOS.
- **Mitigation:** pre-register the format definitions, metrics and thresholds; log **every** format examined,
  including the ones dropped after a glance (same idea as `TrialRegistry`); use the false-discovery rate
  (Benjamini-Hochberg) to choose which W1 candidates are promoted; cap promotions at a small number; make W2
  confirmatory with a correction over the promoted set; define W2 success as "still above baseline" (lift CI
  lower bound > 1), not "as good as W1", because shrinkage is expected.

### 3.8 Confusing interest with willingness to pay
- **Mechanism:** sharing is driven by arousal [E]; stated WTP overstates real payment (median ~1.35x with a long
  tail) [E]; free waitlist signups are weaker than stated WTP; a highly engaged teenage audience may have no
  payment method. Scorecard warning already says: ideas that max criteria 1-6 and zero on 7-9 go viral and
  make no money.
- **Mitigation [R]:** demand a monetization signal from outside the organic feed (competitor revenue direction,
  long-running paid ads in the niche) before spending on fake-door tests; in the fake-door test, make price
  visible *before* the signup and record conversion at each rung of a WTP ladder (section 4.7).

### 3.9 Other traps worth naming [R]
- **Format definition drift:** redefining "the format" after seeing which videos did well is p-hacking. Freeze
  an operational definition (observable features a second person could code) before W1.
- **Coder bias:** classifying comments as "intent" after knowing a video's views. Code blind to views where
  possible; double-code a random 10-20% and report agreement.
- **Selection on the outcome via creator choice:** sampling creators *because* they had a hit. Seed creators
  from keyword/sound pages over a window, not from the hit list alone.
- **Ecological fallacy:** "this format works for creators" ≠ "an app producing this output will be shared by
  ordinary users". The app's users are not professional creators; your fake-door test should show the *user's*
  output, not a creator performance.

---

## 4. Protocol

Structure mirrors PLAN.md section 3: pre-register → discovery window (IS) → holdout window (OOS) →
triangulation → own fake-door test (the locked one-shot final test). Each idea/format is one hypothesis.

### 4.1 Pre-registration (written and committed before any scraping for that idea)
One file per hypothesis (e.g. `ventures/app-ideas/research/hypotheses/T01_<slug>.md`, folder to be created when
the first one is written), containing:
1. **Hypothesis:** "Format F, defined by observable features {…}, which demonstrates app concept C, shows (a)
   higher hit rate than the same creators' other posts, (b) breadth across ≥ N creators, (c) organic intent
   comments, and (d) persists in the holdout window; plus ≥ 2 non-TikTok sources agree in direction."
2. **Operational format definition** a second person could apply (on-screen result type, before/after
   structure, sound or template if part of the definition, language).
3. **Seed queries:** frozen list of keywords, hashtags and sounds per language/geo (e.g., 10-20 per idea [H]),
   plus how new seeds may be added (only from a rule, e.g. co-occurring hashtags above a frequency, applied
   mechanically).
4. **Windows:** W1 = weeks 1-4 (discovery), W2 = weeks 5-8 (holdout). Only videos *posted* inside the window
   count for that window.
5. **Geos:** 1-3 pre-declared markets (e.g., TR, EN-global), identified by language + creator location.
6. **Primary metric** (exactly one; recommended: format-level lift in hit rate with creator-clustered CI),
   secondary metrics (breadth, concentration, intent-comment rate, share/save rate lift), and the decision rule.
7. **Hit definition**, fake-engagement filters, comment lexicon, exclusions (prompted-comment videos, ads
   unless studying ads).
8. **Kill criteria** and the maximum number of formats that may be promoted from W1 to W2.
9. Pre-registered score from `scorecard.md` (already required to be written before testing).

### 4.2 Sample design
- **Unit of analysis:** video → aggregated to creator → aggregated to format. Inference at format level, with
  **creator as the cluster** (a creator with 20 format videos must not count as 20 independent replications).
  Use a cluster bootstrap by creator for all CIs.
- **Two streams, kept separate:**
  - *Discovery stream* (what users see): top search/hashtag/sound results for each seed query, with rank,
    captured on a fixed schedule (e.g., twice a week [H]). Used only to *find* creators and candidate formats.
  - *Denominator stream* (for rates): for every creator found, their **full timeline** over the window plus
    enough prior history for a baseline. If feasible, also all videos on the format's sound/hashtag page in
    the window, including low-view ones. Rates and lifts are computed only from this stream.
- **Random vs top:** top results are a biased sample by construction; use them for discovery, never for rates.
  If a random sample is possible (e.g., all videos on a small hashtag page), prefer it for rate estimation.
- **Follower tiers:** stratify creators (e.g., <10k, 10k-100k, >100k followers [H]) and report breadth per tier.
  A format working only for >100k accounts is a broadcast effect [E: Goel et al.]; one working in the small
  tier is evidence that the format itself carries distribution.
- **Snapshots:** re-measure each video at fixed ages (~24h, ~72h, ~7d [H]) so velocity and fixed-age views
  exist. Store raw scrape rows with scrape timestamp; never overwrite.
- **Power reality check [R, illustrative arithmetic, not a claim about TikTok]:** to detect a hit rate of 10%
  vs a 5% baseline with a two-sided 5% test at 80% power needs roughly 430 videos per group *before*
  accounting for creator clustering. With 40 format videos only very large lifts are detectable. Consequence:
  for most niches, the hit-rate lift will have a wide CI, and the decision must rest on the **conjunction** of
  several weaker criteria (breadth, concentration, intent comments, holdout persistence, external sources),
  not on one significant p-value.

### 4.3 Metrics (normalized per view and per creator)
Per video (at fixed age *a*, from the denominator stream):
- `views_a`, `share_rate = shares/views`, `save_rate = saves/views`, `comment_rate = comments/views`
- `intent_comments` (lexicon match, prompted videos excluded), `intent_per_1k_comments`, `intent_per_100k_views`
- `outlier_ratio = log(views_a / median(views_a of the creator's previous N posts))`, N ≥ 15-20 [H], previous
  posts only; skip creators with fewer than N prior posts or mark them as low-confidence.
- `velocity = views_24h` or `views_72h / views_24h` [R].
- flags: `is_ad`, `prompted_comments`, `anomaly` (engagement far outside creator's own distribution).

Per creator × format:
- hit rate on F posts vs hit rate on the same creator's non-F posts (within-creator difference).

Per format (the decision level):
- **lift** in hit rate (primary), with creator-clustered bootstrap CI
- **breadth** = # distinct creators with ≥ 1 hit, by follower tier and geo
- **concentration** = share of format views from the top creator (and Herfindahl index over creators)
- median within-creator lift in share and save rate
- intent-comment rate, and fraction of intent questions already answered with a named app
- **new-creator inflow** per week (trajectory; rising, flat or falling)

Hit definition [H]: `outlier_ratio ≥ log(3)` (i.e., ≥ 3x the creator's median at the same age). Report results
at 2x and 5x as a sensitivity check, but decide on the pre-registered 3x.

### 4.4 Discovery window W1 (in-sample)
1. Collect for 4 weeks per the sample design.
2. Log every candidate format considered in a registry (one JSON line per format: definition, date, who
   proposed it, metrics, decision). This is the multiple-testing denominator.
3. Compute W1 metrics; apply Benjamini-Hochberg at q = 0.10 [H] on the lift tests across all registered formats;
   among survivors, promote at most 3-5 [H] that also pass the pre-registered secondary screens:
   - breadth ≥ ~8-10 distinct creators with hits, including ≥ 2 follower tiers [H]
   - top-creator share of views ≤ ~30-40% [H]
   - intent comments present on a meaningful fraction of format videos (pre-register the fraction; no
     benchmark exists, so start from the distribution observed in a pilot week and freeze it) [H]
   - results hold with anomaly-flagged videos removed
4. Freeze definitions. No changes after W2 data starts arriving.

### 4.5 Holdout window W2 (out-of-sample, weeks 5-8)
- Only videos posted in weeks 5-8; same definitions, same pipeline, same thresholds; include both returning
  creators and newly found ones (report separately).
- **Pass** requires all of:
  - lift CI lower bound > 1 (one-sided test, Bonferroni over the promoted formats), not "lift ≥ W1 lift"
  - breadth criterion met again with **new** creators contributing (the format is not one cohort's habit)
  - intent comments persist
  - new-creator inflow not collapsing (a sharp collapse = the fad is over)
- Expect shrinkage vs W1 (regression to the mean); that alone is not failure.
- Cross-geo check: if 2+ geos were registered, report each; replication in a second geo is a plus, absence is
  not automatically a fail for culture-specific ideas (decide in pre-registration which applies).

### 4.6 Triangulation (≥ 2 non-TikTok sources, pre-declared, collected over the same 8 weeks)
Pick at least two, stated in advance with the direction expected:
- **Google Trends:** 2-5 pre-declared terms + 2 control terms, same geo, weekly granularity, averaged over
  several pulls on different days; criterion: non-declining or rising vs controls.
- **App stores:** apps that the intent comments name (or the top apps for the concept's keywords): rank
  trajectory (Apple RSS / Play lists), review-count velocity (free, see `apify_tooling_legal.md`), revenue
  estimates as order-of-magnitude only. Criterion: at least one app in the niche monetizes (positive WTP
  evidence) *and* its 1-3 star reviews show a gap you can serve (link to `sources/appstore_reviews.md` method).
- **Ad libraries:** TikTok Commercial Content Library / Creative Center Top Ads and Meta Ad Library: are apps in
  this niche running ads, and for how long? Criterion: ≥ 1 advertiser with long-running ads in the niche [H for
  "long"; define in weeks beforehand].
- **Search/community:** Reddit / YouTube search for the need, if it fits the idea.
- Decision rule: ≥ 2 sources agree in direction; any pre-declared source contradicting must be explained in
  writing or the hypothesis fails. Incumbent strength is recorded as a separate competition score, not mixed
  into demand.

### 4.7 Final validation: own fake-door videos + priced waitlist (the "locked" test)
Builds on `test_protocol.md`; additions for statistical rigor [R]:
- **Pre-register** per idea: hooks (5), posting slots, the primary metric and the go/no-go rule, before posting.
- **Counterbalance** posting order and time slots across ideas (e.g., rotate idea A/B/C across days and hours)
  so one idea does not get all the good slots or the account's warm-up period.
- **Funnel metrics per video at fixed age:** views → profile visits → link clicks → page views → priced signups.
  The *primary* metric should be **priced signups per link click (or per page view)**, because it has many
  more independent trials (visitors) than videos and is less exposed to algorithm luck; report a binomial CI.
  Views-based criteria are secondary.
- **Honest small-sample arithmetic [R]:** with 5 hooks per idea, "≥ 4 of 5 hooks beat the account median"
  happens by chance with probability 6/32 ≈ 0.19 under a coin-flip null; 5 of 5 has 1/32 ≈ 0.03. Fifteen
  videos are weak evidence about views; rely on the visitor-level conversion and on replication of the best
  hook (already in `test_protocol.md`).
- **WTP ladder** (record which rung each signup reached): saw price → joined waitlist → chose a paid plan/tier
  on the form → (optional, user decision) refundable deposit or pre-order. `test_protocol.md` currently says
  no money is taken; moving up the ladder to a deposit would be a protocol change that requires the user's
  explicit decision (and store-policy/legal check). Without it, treat signups as an upper bound on demand
  (hypothetical bias [E]).
- **Validity conditions** (from `test_protocol.md`): warmed accounts, all 15 videos posted, working link.
  Add: no cross-engagement between own accounts (already a rule), and the result page/time of each signup
  logged so it can be attributed to a video.

### 4.8 After each cycle: calibration
- Record pre-test predictions (scorecard score, W1/W2 metrics) and the fake-door outcome per idea in
  `ideas.csv` / a results log. After several cycles, check which TikTok metrics actually predicted fake-door
  conversion (rank correlation; Brier score if a probability was stated). Re-tune [H] thresholds **only**
  between cycles, and only with the change logged. This is the only way the heuristics in this file become
  evidence for *this* founder's niche.

---

## 5. Mapping to the trading research discipline

| Trading (pfbot) | This protocol |
|---|---|
| Hypothesis file in `research/hypotheses/` | Pre-registration per format/idea (4.1) |
| In-sample 2015-2020 | W1 discovery, weeks 1-4 |
| Out-of-sample 2021-2023 | W2 holdout, weeks 5-8 (new videos only) |
| 2024+ locked one-shot test | Own fake-door + priced waitlist, rule fixed in advance |
| `TrialRegistry`, deflated Sharpe, PBO | Format registry + BH-FDR + Bonferroni on promoted set |
| Realistic + stressed costs | Results with and without anomaly-flagged videos; scraper-vs-manual discrepancy check |
| Survivorship-free universe | Creator-timeline denominator stream |
| Look-ahead bias | Fixed-age views; baselines from prior posts only |
| Regime filters | Same-window matched controls; logged platform events |
| Profitable backtest ≠ payout | Viral format ≠ paying users (hierarchy in section 2) |

---

## 6. Honest bottom line [R]
- The literature implies that **no** TikTok metric will reliably predict a winner from a single video or at t=0;
  the achievable edge is to (a) filter out the majority of false positives (one-account flukes, broadcast
  effects, bot inflation, saturated trends), and (b) rank a short list of ideas for a cheap, priced test.
- The strongest organic signals are replication-based (many creators beating their own baseline, persisting
  out of sample) and intent-based (unprompted "what app / link" comments). The strongest economic signals are
  outside TikTok (competitor revenue direction, long-running paid ads) and in your own priced test.
- Expect most candidates to fail the holdout, as most trading hypotheses did. That is the protocol working.

---

## Sources
Research
- Cheng, Adamic, Dow, Kleinberg, Leskovec (2014), Can cascades be predicted? WWW 2014. https://arxiv.org/abs/1403.4608 ; https://www.microsoft.com/en-us/research/?p=190947 ; press: https://phys.org/news/2014-04-scientists-photos-viral.pdf
- Salganik, Dodds, Watts (2006), Experimental study of inequality and unpredictability in an artificial cultural market, Science 311. https://www.cs.toronto.edu/~bor/303s19/docs/salganik_dodds_watts.pdf ; https://acawiki.org/Experimental_Study_of_Inequality_and_Unpredictability_in_an_Artificial_Cultural_Market
- Martin, Hofman, Sharma, Anderson, Watts (2016), Exploring limits to prediction in complex social systems, WWW 2016. https://arxiv.org/abs/1602.01013
- Goel, Anderson, Hofman, Watts (2016), The structural virality of online diffusion, Management Science 62(1). https://www.5harad.com/papers/twiral.pdf ; https://pubsonline.informs.org/doi/fpi/10.1287/mnsc.2015.2158
- Berger, Milkman (2012), What makes online content viral? JMR 49(2). https://cir.nii.ac.jp/crid/1360292620129675648?lang=en
- Murphy, Allen, Stevens, Weatherhead (2005), A meta-analysis of hypothetical bias in stated preference valuation, Env. & Resource Econ. 30. https://econpapers.repec.org/RePEc:kap:enreec:v:30:y:2005:i:3:p:313-325 ; https://ageconsearch.umn.edu/record/14518

Platform
- TikTok Newsroom (2020), How TikTok recommends videos #ForYou. https://newsroom.tiktok.com/how-we-recommend-videos?lang=en-IE
- TikTok Ads help, Top Ads. https://ads.tiktok.com/help/article/top-ads?lang=en
- TikTok Community Guidelines Enforcement Reports. https://www.tiktok.com/transparency/en-us/community-guidelines-enforcement-2023-1/ ; summaries: https://www.contentgrip.com/tiktok-fake-account-crackdown/ , https://www.tubefilter.com/2021/10/14/tiktok-community-guidelines-enforcement-report-april-june-2021/

Data access / measurement
- AI Forensics, TikTok's Research API: Problems without explanations. https://www.aiforensics.org/work/tk-api ; Entrena-Serrano et al. https://arxiv.org/abs/2506.09746
- Tech Policy Press, Researcher data access under the DSA (2024 EU elections). https://techpolicy.press/-researcher-data-access-under-the-dsa-lessons-from-tiktoks-api-issues-during-the-2024-european-elections
- Bai, Gu (2026), Evaluating TikTok Research API. https://repository.essex.ac.uk/42550/
- Restoring the forecasting power of Google Trends. https://ar5iv.labs.arxiv.org/html/2504.07032 ; Supermetrics, discrepancies in Google Trends data: https://docs.supermetrics.com/docs/about-discrepancies-in-google-trends-data ; secondary: https://ppc.land/google-trends/
- Appfigures estimate methodology: https://help.appfigures.com/en/article/how-appfigures-estimates-downloads-and-revenue-for-ios-and-android-apps-na7a2h/ ; Sensor Tower: https://sensortower.com/blog/how-to-get-estimated-downloads-and-revenue-for-apps ; secondary [V]: https://www.appalize.com/blog/mobile-trends/app-download-and-revenue-estimation-tools-methods-and-accuracy , https://trysonar.app/blog/app-revenue-estimates-how-they-work-and-fail.md
- Third-party Creative Center metric descriptions [V]: https://segwise.ai/blog/tiktok-top-ads-dashboard-guide.md
