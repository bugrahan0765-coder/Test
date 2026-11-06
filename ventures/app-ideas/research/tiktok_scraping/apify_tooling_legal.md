# TikTok + app-store data via Apify: tooling, cost, legal boundaries (as of 2026-11)

Method note: ~14 searches + page fetches on 2026-11-06. Prices are Apify "from" prices read from actor pages; many pages show conflicting figures (header vs FAQ). Nothing here is legal advice. Items marked [UNVERIFIED] could not be confirmed from a readable source.

## 1. Apify plans (apify.com/pricing, fetched)
| Plan | $/mo | Included usage | CU price |
|---|---|---|---|
| Free | 0 | $5 credit/mo | $0.20 |
| Starter | 19 | $19 | $0.20 |
| Scale | 199 | $199 | $0.16 |
| Business | 999 | $999 | $0.13 |
Annual billing -10%. Residential proxy $8/GB (Free/Starter). Pay-per-event/pay-per-result actors bill a flat per-item price and do NOT charge platform usage on top; higher plans get lower per-item prices.
Rough research run: 5,000 TikTok videos at ~$1.70-2.00/1k = ~$8.5-10 (Free credit covers ~2,500-3,000 videos). Say 10 hashtags x 500 videos + 20 profiles x 100 + comments on 100 videos x 100 = ~$10-15 total. Free plan = one small run/month; Starter ($19) is plenty for a solo founder.

## 2. TikTok actors
Fields below are from actor READMEs. Success rates/user counts are Apify's own stats.

**clockworks/tiktok-scraper** (general; apify.com/clockworks/tiktok-scraper)
- Price: "from $1.70 / 1,000 results", pay-per-event. Extras charged: date/popularity filters (oldestPostDateUnified, mostDiggs...), video search sort/date filters, video downloads, transcripts, AI description/summary (per video-second). Per-event amounts were not readable on the page (pricing tab gave no breakdown). Avoid the paid filters/downloads; filter in pandas instead.
- Input: hashtags, profiles, searchQueries, postURLs, searchSection, resultsPerPage, commentsPerPost, proxyCountryCode, profileSorting (Latest/Oldest/Popular), followers/following scraping.
- Output: playCount (views), diggCount (likes), shareCount, collectCount (saves), commentCount, createTime/createTimeISO, authorMeta.fans (followers)/following/heart/video, musicMeta (name, author, original, id, playUrl), locationCreated (not always present), textLanguage, hashtags, isAd.
- Reliability: 4.75 stars, 382,913 users (34,900 monthly), 98.9% runs succeeded. Rate limits: none published; Apify-side concurrency/memory only. Residential proxy via proxyCountryCode.
- Note: no "views by region" breakdown; region is only creator-location/proxy country.

**clockworks/tiktok-hashtag-scraper**: from $1.00/1,000 videos (FAQ says $5/1k; conflict). Input hashtags, resultsPerPage. Same engagement/author/music fields as above. 4.92 stars, 20.6k users, 100% success.
**clockworks/tiktok-profile-scraper**: from $1.00/1,000 results (FAQ $5/1k). Input profiles, sorting, date/likes filters (paid). Author block incl. region, fans, verified, bio. 4.73 stars, 64k users, 99.8%.
**clockworks/tiktok-comments-scraper**: from $0.50/1,000 comments (FAQ $5/1k; conflict). Input postURLs, commentsPerPost, replies cap. Output text, diggCount, replyCommentTotal, createTimeISO, uniqueId, uid, cid, avatarThumbnail. 4.73 stars, 52.8k users, 99.8%. (Comment output contains usernames/avatars = personal data, see section 6.)
**clockworks/tiktok-sound-scraper**: from $2.00/1,000 videos (README: $5/1k on Free plan). Input musics (URL/ID). Returns videos using the sound + counts + musicMeta. 5.0 stars, 2.5k users, 95.9% (lowest of the family). Transcription $0.048/min extra.
**clockworks/free-tiktok-scraper ("TikTok Data Extractor")** and **tiktok-video-scraper** ($10/1,000 videos listed in search snippet only) exist; pages not fetched.
**Search autocomplete**: automation-lab/tiktok-keywords-discovery(-scraper) (pay per event, price not read), solalab_digital/tiktok-keywords-discovery (from $0.20/1,000 per search snippet), maximedupre/tiktok-keywords-discovery-tool. None return search volume (TikTok's preview endpoint doesn't expose it); results vary by region/time. No login required. Prices [UNVERIFIED beyond snippet].
**Creative Center / Top Ads** (all third-party, vendor-written listings, unverified): symphonic_mullite/tiktok-creative-center-trends, hyperbach/tiktok-creative-center-scraper, locaihost/tiktok-trends, automation-lab/tiktok-creative-center-scraper & tiktok-trends-scraper. Snippets list ~$0.55-3.00/1,000 items. WARNING: two listings state TikTok removed Songs, Creators, Top Products and Keyword Insights from the public Creative Center in a 2026 redesign (routes 404/deprecated); automation-lab still advertises sounds/creators with sample output dated Jan 2025. Assume hashtags + top ads + videos only; test with a tiny run first.
**Ad Library scrapers** (EU Commercial Content Library data): jaybird/, bovi/tiktok-ads-library-scraper, datascoutlab/, lentic_clockss/, constructive_calm/tiktok-ad-library-pro, zadexinho/. Prices not read. Covers EU/EEA/UK ads (one source adds Switzerland and Turkey - unverified).
Other scrapers (mscraper, apidojo, seemuapps, nifty.codes) exist; clockworks is the incumbent with the most users.

Reliability caveat: TikTok anti-bot changes frequently break scrapers; failed items are returned as errorCode rows (not billed as normal results per README convention, but verify in run log). Cheap actors from tiny authors can be abandoned; prefer ones with >1k users.

## 3. App stores
**Apple (free, no Apify needed)**: public iTunes RSS JSON `https://itunes.apple.com/{cc}/rss/customerreviews/page={1..10}/id={appid}/sortBy=mostRecent/json` (cc=tr for Turkey). Hard cap about 10 pages x 50 = ~500 most recent reviews per app per country; page 11+ repeats. Rating-only entries not included. Undocumented by Apple (only third-party docs found); sortBy vs sortby casing varies, test it. Also free: iTunes Search/Lookup API (`itunes.apple.com/search?term=..&country=tr&entity=software`, `/lookup?id=`) for app metadata and rating counts; I did not verify its rate limit in this research (commonly cited ~20 req/min, [UNVERIFIED]).
**Apify Apple reviews**: bovi/appstore-reviews (wraps the RSS; header "from $0.97/1k", README $2/1k; country input; 500 cap; only 10 users, so low trust), also scrapio/, glassventures/, automation-lab/, hearthkit/, betterscrapers/. Since they wrap the same RSS, a 30-line Python script is cheaper and more controllable. Rankings/top charts by country: no Apify actor priced in my results; Apple's marketing RSS top-charts feeds exist [UNVERIFIED, not fetched].
**Google Play on Apify**: reviews scrapers at $0.09-0.10/1k (skython, thewolves, agents/googleplay-reviews), $1-2/1k (prince.sh [under maintenance], makework36). bovi/google-play-scraper does apps+reviews (price not read). Country + language inputs exist.
**Free library**: facundoolano/google-play-scraper (npm, v10.1.3): app, search, list (collections/charts, `country` param e.g. 'tr'), reviews, developer. README says author no longer actively maintains it; last push seen Feb 2025; parser breaks when Google changes layout. Python equivalent: `google-play-scraper` on PyPI (JoMingyu) [not checked]. Rankings by country are feasible via `list`.
Recommendation: Apple RSS + iTunes Search by script (free); Google Play reviews on Apify at $0.10/1k (trivial cost) or the library.

## 4. Official / legitimate alternatives
- **TikTok Research API** (developers.tiktok.com/products/research-api): "independent and academic researchers conducting research on a not-for-profit basis". Eligible: non-profit academic institutions in US, EEA, UK, Switzerland; not-for-profit research bodies in the EU; must be independent of commercial interests. A solo founder building a product is NOT eligible. Even for eligible NGOs access is reportedly restricted (Virtual Compute Environment only; Kinit, Democracy Reporting Intl).
- **Commercial Content API / Commercial Content Library** (ads & advertiser transparency, DSA): free, OAuth, but gated by developer-portal application; one guide says an approved research account is required [UNVERIFIED]. Web UI of the library is public for EU/EEA/UK ads. Does not cover organic video stats.
- **TikTok Creative Center** (ads.tiktok.com/business/creativecenter): free in-browser; trending hashtags, top ads, trending videos by country/period/industry. 2026 redesign reportedly cut songs/creators/keyword insights. Manual browsing is clearly within ToS (it is a TikTok-provided product); automating it is not clearly so.
- Display/Login Kit APIs only serve data of users who authorize your app (not market research).
- Practical legit tier: manual browsing of TikTok, Creative Center and Ad Library for hypothesis checking; scrapers for volume.

## 5. Legal
**TikTok ToS** (tiktok.com/legal/page/row/terms-of-service/en, fetched): Section 5 prohibits using "automated scripts to collect information from or otherwise interact with the Services", bypassing access-restriction measures, and using content "for any commercial or unauthorized purpose" without written consent; Services are "for private, non-commercial use". Scraping is therefore a ToS breach in TikTok's view; commercial use of content is also barred. No explicit "scraping" word. (Region-specific ToS e.g. EEA/UK versions not compared.)
**Case law** (US; not Turkish/EU):
- Meta v. Bright Data (N.D. Cal., Jan 2024, Judge Chen): summary judgment for Bright Data; Meta's terms bind only logged-in users, so logged-off scraping of public data did not breach contract. Limits per law-firm commentary: concerns Meta's terms only; says nothing on logged-in scraping. Appeal outcome not confirmed.
- hiQ v. LinkedIn (9th Cir. 2022; from my background knowledge, searches returned only a passing mention): scraping public pages is unlikely to be "without authorization" under the CFAA (after Van Buren 2021 too). But the case ultimately ended against hiQ on breach of contract/user-agreement grounds with a permanent injunction and data destruction (Nov 2022) [from memory, UNVERIFIED here]. Lesson: CFAA risk is low for public logged-out data; contract/ToS and other claims remain.
- TikTok is not a party to either case. Real-world risk for small low-volume research use: account/IP bans, C&D letter; litigation against small users is rare but unquantified.
**Apify**: Apify's blog says scraping public data is legal but be careful with personal data, IP, confidential data. Apify's Terms of Service / Acceptable Use Policy were NOT retrieved; a third-party site (use-apify.com) cites EDPB Opinion 28/2024 (personal data stays regulated even if public). Under Apify's model, the actor user (you) is responsible for lawful use; read the AUP yourself. Third-party actor authors set their own terms.
**GDPR / KVKK**: Usernames, avatars, comment text linked to a handle, and `authorMeta` bios are personal data under both GDPR and KVKK (Law 6698); "publicly available" is not a free pass (GDPR needs a lawful basis e.g. legitimate interest + balancing test, transparency duty, minimization; KVKK has an "alenileştirme" (made public by data subject) ground but it only permits processing consistent with the purpose of making it public). KVKK also requires VERBIS registration above thresholds and aydınlatma (notice) duties. A source claiming 2026 KVKK amendments with fines up to 2% of global turnover for scraping is unreliable and unverified; confirm against Resmi Gazete/KVKK Kurumu. Turkish-language KVKK sources found were general academic papers; no authoritative scraping-specific guidance found.

## 6. Minimal-risk practice (recommended)
1. Use hashtag/search/sound scrapers (video-level, public, logged-out). Never provide cookies or a TikTok login; never run logged-in actors.
2. Aggregate immediately: keep per-video metrics, hashtag/sound/caption-topic counts; drop authorMeta name/nickName/avatar/bio/uid and comment usernames (hash or delete at ingest). Keep only author follower count bucket if needed.
3. Comments: skip, or collect small samples and store only text themes (no handles), delete raw after coding. Comments cost little ($0.50-5/1k) but are the highest personal-data risk.
4. Low volume: a few thousand items per run, 1-2 runs/week; no mass profile crawling, no follower/following lists.
5. Retention: raw dumps deleted within ~30 days; keep only aggregates. Do not republish or resell scraped content; do not download videos/covers.
6. Never contact, DM, or target individuals found in the data; no creator outreach list built from scrape without a separate lawful basis.
7. Prefer official/free sources first (Creative Center, Ad Library UI, Apple RSS, Google Play library) and use Apify TikTok scraping only for what they cannot give.
8. Keep a short log (purpose, source, date, fields kept, deletion date) - cheap evidence of data minimization. Consult a Turkish/EU data-protection lawyer before storing personal data or before commercializing a dataset.

## 7. Suggested stack for a solo founder
- TikTok: clockworks/tiktok-scraper (or hashtag scraper at $1/1k) with only hashtags/searchQueries; no paid filters; Free plan or Starter.
- Keyword ideas: a keywords-discovery actor (~$0.20/1k) or TikTok search box manually.
- Trends/ads: Creative Center + Ad Library in the browser.
- App stores: Apple RSS (tr) + iTunes Search API by script; Google Play library or $0.10/1k Apify actor.
- Expected monthly spend: $0-19.

## Sources
- https://apify.com/clockworks/tiktok-scraper ; /tiktok-hashtag-scraper ; /tiktok-profile-scraper ; /tiktok-comments-scraper ; /tiktok-sound-scraper
- https://apify.com/pricing
- https://apify.com/bovi/appstore-reviews ; https://apify.com/thewolves/google-play-reviews-scraper
- https://apify.com/automation-lab/tiktok-trends-scraper ; https://apify.com/symphonic_mullite/tiktok-creative-center-trends ; https://apify.com/hyperbach/tiktok-creative-center-scraper
- https://github.com/facundoolano/google-play-scraper
- https://developers.tiktok.com/products/research-api ; https://developers.tiktok.com/products/commercial-content-api ; https://kinit.sk/when-research-apis-close-the-door-when-you-finally-get-it-it-is-not-what-you-have-asked-for/
- https://www.tiktok.com/legal/page/row/terms-of-service/en
- https://www.fbm.com/business-litigation/publications/major-decision-affects-law-of-scraping-and-online-data-collection-meta-platforms-v-bright-data/ ; https://techcrunch.com/2024/01/24/court-rules-in-favor-of-a-web-scraper-bright-data-which-meta-had-used-and-then-sued
- https://dev.to/apify/is-web-scraping-legal-1h6n ; https://use-apify.com/docs/what-is-apify/is-apify-legal
