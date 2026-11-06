# App-store categories and unhappy users: candidate app ideas

Date: 2026-11-06. Source type: ~13 web searches (standard mode, aggregated snippets). Researcher: subagent.

## 0. How to read this file

Evidence labels:
- [MEASURED] = a number from a named analytics source or the app store itself, as reported by the search results. Secondary coverage, so re-verify at the primary source before betting money.
- [ESTIMATE] = third-party modelled figure (AppGoblin, TrustMRR listing, etc.). Rough.
- [ANECDOTE] = review-aggregator summary, forum post, blog opinion. Directional only. Many of these aggregators (unstar.app, marlvel.ai, justuseapp, kimola) auto-generate summaries and have commercial interests.
- [INFERENCE] = my reasoning, not found in any source. Needs validation.

IMPORTANT limits of this research: I could NOT retrieve actual 1-3 star review text from the App Store or Google Play, nor Reddit threads (the search tool returned none). Complaint gaps below therefore rest on aggregator summaries plus inference. Before building, spend 1 hour reading real 1-3 star reviews (Turkish storefront too) of the named incumbents. No Turkey-specific complaint data was found; every "Turkish gap" claim is [INFERENCE] unless stated.

## 1. Category-level evidence (what is proven)

1. Image-AI drives downloads, but money is hard. [MEASURED, secondary coverage of an Appfigures report, May 2026] Image model launches produced ~6.5x more downloads than chatbot model updates; Nano Banana added >22M downloads in 28 days but only ~$181K estimated gross spend; ChatGPT image upgrade added >12M installs. Sources:
   - https://www.newsbytesapp.com/news/science/appfigures-finds-ai-image-models-beat-chatbots-65x-in-downloads/tldr
   - https://www.androguider.com/2026/05/image-ai-models-surge-in-app-downloads.html
   - Implication [INFERENCE]: frontier free apps (Gemini, ChatGPT) now give away generic image transformations. A paid niche app must offer something the free general tools do not: a template/ritual, a cultural context, a share format, or a social loop.
2. RevenueCat State of Subscription Apps 2026. [MEASURED, secondary coverage] Photo & Video has the highest AI share (61.4%) and the highest share of new apps crossing $1K MRR (21.4%); AI apps convert trials better (one report: median 8.5% vs 5.6%) but retain worse (one report: annual retention 21.1% vs 30.7%; sources disagree on exact figures). Sources:
   - https://www.revenuecat.com/state-of-subscription-apps-2026/
   - https://ppc.land/ai-apps-earn-41-more-per-user-but-churn-30-faster-revenuecat-finds/
   - Implication [INFERENCE]: favor one-time/credit packs and event-driven (seasonal, social) products over pure weekly-subscription retention bets.
3. Photo & Video downloads 2025. [MEASURED, AppTweak] CapCut 509.2M, Remini 132.6M. https://www.apptweak.com/en/reports/most-downloaded-photo-video-apps?format=md
4. Overall store economy. [MEASURED, Appfigures] Top 10 apps earned $1.3B in Jan 2026 (after fees). https://appfigures.com/resources/insights/most-downloaded-highest-earning-apps-january-2026
5. Turkey. [MEASURED via secondary report citing Sensor Tower/Adjust] Generative-AI app downloads in Turkiye grew 149% YoY in 2025 to 82.9M; revenue rose from $15M to $50.2M. Source: https://gamedevreports.substack.com/p/adjust-the-mobile-market-of-turkiye-58c  (single secondary source, verify). Implication [INFERENCE]: many downloads, low monetisation per user (~$0.6 per download), so Turkey is good for reach and virality, weak for ARPU. Pricing in TRY must be low; global/USD payers matter.
6. Indie proof points. [ESTIMATE / self-reported]
   - Photo AI (Pieter Levels, solo): reported ~$100K-$182K MRR, sources conflict. https://www.indiehackers.com/post/photo-ai-by-pieter-levels-complete-deep-dive-case-study-0-to-132k-mrr-in-18-months-3a9a2b1579
   - Lenz AI (Digital Camera Effect): $2,455 MRR, 297 subs, founded Mar 2026, Superwall-verified per TrustMRR listing. https://trustmrr.com/startup/lenz-ai-digital-camera-effect
   - PhotoAIGenerator ~$150-295 MRR; TaraSnap photo booth app ~$22 MRR (shows tiny outcomes are common). https://trustmrr.com/startup/photoaigenerator-1000-users-photos-ugc-videos-and-mobile-app , https://trustmrr.com/startup/photo-booth-app-tarasnap.md
7. Astrology/fortune. [ESTIMATE] Co-Star revenue estimates conflict wildly (~$10K to ~$400K/mo); Co-Star reportedly acquired by Midjourney, ~4.3M MAU per Sensor Tower (via secondary). Sensor Tower 2019: top-10 US astrology apps $40M (+65%). https://techcrunch.com/2020/03/02/top-10-u-s-astrology-apps-drew-in-40m-in-2019-up-65-from-2018 (old). Turkish coffee-reading apps exist at small scale: Derya Abla Kahve Fali ~157K downloads, Falci Bacim ~22K (download-site counts, [ESTIMATE]); Faljı sells credits at TRY 49.99 / 99.99 on the Turkish App Store. https://apps.apple.com/tr/app/falj%C4%B1-kahve-fal%C4%B1/id1374152049?l=tr , https://www.tamindir.com/indir/derya-abla-kahve-fali/
8. Couples apps. [ESTIMATE] Paired claims 4M+ couples (self-reported), AppGoblin lists 10.7M installs, 461K MAU, $10K+/mo; Love Nudge ~1-1.8M installs, declining momentum. https://appgoblin.info/apps/1469609343/trends , https://appgoblin.info/apps/495326842
9. Personality tests. [ANECDOTE/MEASURED mix] Crowded: MBT+, AmIThis, 3D trading-card archetype apps, friend-guessing mechanics already exist. App Goblin shows 125,669 competing apps for keyword "share" on a 16 Personalities listing (single data point). https://apps.apple.com/app/id1658921537 , https://appgoblin.info/apps/1658921537/keywords/discovery
10. Voice/AI cover songs. [ESTIMATE] Most such apps under ~$10K/mo (VocalMe 1.3M installs, <$10K est.); one listing ~$44K/30d (RevenueCat-verified per tracker). VoiceFun listed 2.75 stars (2.3K ratings), complaints of crashes and no result after payment. https://appgoblin.info/apps/com.talentme.vocalme , https://trustmrr.com/startup/ai-cover-music-video , https://mwm.ai/it/apps/voicefun-voice-generator/6461690849 . Rights-holder/voice-cloning legal risk (see exclusions).
11. Baby predictors. [ANECDOTE] Complaint categories on one listing: inaccurate predictions (18), technical issues (7), deceptive marketing (6), gender-locked features (4); one review says poor for black couples; one aggregator rates a baby app 100% negative over 159 reviews. https://mwm.ai/pt/apps/ai-baby-maker-face-generator/1510970482 , https://justuseapp.com/en/app/1066687228/future-baby-test-gender-by-ai/reviews . Also: a $5.99 one-time, no-subscription competitor (Stork) exists. https://www.stork.ai/blog/ai-baby-generator-no-subscription
12. Headshots. [ANECDOTE] "Does not look like me" is the defining complaint; hidden weekly auto-renew complaints (unstar.app, biased blog; Trustpilot reviews). https://unstar.app/blog/aragon-betterpics-remini-headshotpro-photoai-ai-headshot-apps-ranked-2026
13. Astrology complaints. [ANECDOTE] Features moved behind paywall (compatibility/chart comparison reportedly behind $14.99/mo), recycled/generic readings, upsell notifications. Percentages quoted by aggregators are unsourced; ignore. https://unstar.app/blog/co-star-sanctuary-pattern-nebula-stellium-astrology-apps-ranked-2026 , https://kimola.com/reports/co-star-app-review-analysis-unveiling-user-insights-app-store-us-155484
14. Wrapped-style recap. [ANECDOTE] Reflection "2025 Annual Review" Product Hunt, 142 upvotes; WhatsApp-chat and photo "Wrapped" apps exist; the photo Wrapped app est. <$10K/mo, 171 MAU. https://www.producthunt.com/p/reflect-reset-by-reflection-app/2025-annual-review , https://appgoblin.info/apps/6756099706
15. Bias in AI image tools. [ANECDOTE/academic] FaceApp "hot" filter lightening skin (apologised); Portrait AI turned people of colour white; MENA under-representation argued in a perspective paper (does not address Turkey specifically). https://phoenix.danielpe.edsqa01.aws.sbs.com.au/news/article/faceapp-apologises-for-racist-artificial-intelligence-which-whitened-faces/ib03hwgho , https://pmc.ncbi.nlm.nih.gov/articles/PMC12416507
16. Apple guideline 4.3 (spam/copycat). [ANECDOTE] Developers report 4.3 rejections for photo editors and an AI passport-photo app (Sept 30, 2026) with unclear explanations; commentators say differentiation (niche, original content) is the remedy; appeals go to App Review Board. https://developer.apple.com/forums/thread/853129 , https://developer.apple.com/forums/thread/112848 , https://newly.app/guides/guideline-4-3-spam-rejection

## 2. Candidate ideas (12)

Rating legend: Build 1-2 weeks with AI APIs: yes / maybe / no. 4.3 risk: LOW / MED / HIGH (HIGH = saturated category, many near-identical apps).

### 1. KahveAI (working: "Fincan")
- Pitch: Turkish coffee-cup reading as a beautiful, shareable "fortune card" in the user's own voice/dialect, with a daily ritual and a friend-compatibility reading.
- Target: Turkey first (women 18-45 [INFERENCE based on a 2013 Webrazzi note that downloaders were mostly women, outdated]); then Turkish diaspora, Arabic-speaking markets.
- Demand evidence: Several Turkish apps exist (Faljı with credit packs TRY 49.99/99.99, Derya Abla ~157K downloads, falnâme AI-based). [ESTIMATE/ANECDOTE] Turkey gen-AI downloads +149% [MEASURED secondary]. Horoscope apps are a proven US category (Sensor Tower 2019, old). Sources in section 1 items 5, 7.
- Incumbents/gap: Faljı, Derya Abla, falnâme, Kaave Fali (Falcı Bacı removed from Google Play per one result). Gap [INFERENCE, must verify in reviews]: dated UI, ad-heavy, readings not shareable. Fresh visual design + share cards + "does it feel like my abla said it" voice.
- 3-sec hook: photo of cup -> mystical cup overlay with glowing symbols highlighted, then a card "Fincanında bir yol görünüyor". Reaction-video format: "I let AI read my cup".
- Monetisation: credit packs (TRY and USD), weekly sub for daily readings, ad-free option.
- Build 1-2 wks: yes. Vision-capable LLM (image + prompt) plus card renderer. Dep: vision LLM quality in Turkish; entertainment disclaimer.
- Risk: fortune category is crowded in Turkey; 4.3 risk MED (many fal apps, so make visuals/brand distinct). Also store policy requires "entertainment only" framing; avoid claims about health/finance/relationship decisions.

### 2. Burç Eşleşmesi / "Kim Uyumlu?" couples-and-friends compatibility cards (working: "Uyum")
- Pitch: Two people enter birth dates (or take a quiz) and get a funny, brutally honest compatibility card in Turkish slang, built to send to the other person.
- Target: Turkey, Gen Z; later global in Spanish/Arabic/Portuguese.
- Evidence: Co-Star's best-known feature (chart comparison) reportedly paywalled, a repeated complaint [ANECDOTE] (items 13). Couples category: Paired 4M+ couples claimed, ~$10K+/mo est. [ESTIMATE]. Relationship-reflection category average ~$155K/mo claimed by Screens Design, unmethodological [ANECDOTE] (https://screensdesign.com/categories/relationship-reflection-apps/).
- Incumbents/gap: Co-Star, Nebula, Paired. Gap: compat feature paywalled; content English-centric and generic. Free first compatibility, viral invite loop.
- Hook: split-screen "Aslan x Akrep: 87% chaos" with a roast line; users post screenshots tagging friends.
- Monetisation: free card, paid deep-dive / group (5 friends) compat packs, one-time credits.
- Build: yes. Pure text LLM + card templates; no image model needed.
- Risk: astrology saturated globally; 4.3 MED-HIGH. Low defensibility (ChatGPT does this free), so the share loop and tone must be the product. Do not make relationship advice claims.

### 3. Face-Shape Archetype Reveal for non-Western faces (working: "Yüzüm Hangi Karakter?")
- Pitch: Selfie -> stylised character/archetype portrait (e.g. Anatolian folk-tale, Ottoman miniature, Turkish drama poster styles) that keeps the person's real features, ethnicity and skin tone.
- Target: Turkey + MENA + Balkans (Turkic diaspora) first.
- Evidence: bias complaints in FaceApp/Portrait AI [ANECDOTE], MENA under-representation paper [academic]; "does not look like me" top complaint in headshot apps [ANECDOTE]. Image-AI trends spike downloads [MEASURED] but monetise poorly, so culturally specific styles are the differentiator [INFERENCE].
- Incumbents: Remini (132.6M dl [MEASURED]), Lensa-style avatar apps, ChatGPT/Gemini free image gen. Gap: generic Western style packs, likeness drift. Culturally native styles (miniature art, Yeşilçam poster, Karagöz).
- Hook: before/after swipe; "Yeşilçam filminin afişinde ben". Strong local nostalgia.
- Monetisation: first style free with watermark; style packs $2.99-4.99 one-time; weekly sub optional.
- Build: maybe. Dep: identity-preserving image model (e.g. reference-image edit models via API); per-render API cost must be capped (credits). Test likeness on 30 Turkish faces before committing.
- Risk: free ChatGPT/Gemini can do this with a prompt (Ghibli trend precedent: downloads without revenue [MEASURED]). 4.3 HIGH for generic avatar category; mitigated by cultural-niche design. Only uses user's own selfie (no third-party deepfake): add consent screen, face of self only, no celebrity inputs.

### 4. Pet-Personality Cards (working: "Patim")
- Pitch: Upload your cat/dog photo -> funny AI-written "personality + horoscope + dating bio" in a collectible card.
- Target: Global, pet owners (Turkey has strong cat culture [INFERENCE]).
- Evidence: No direct measured data found for this niche. Indirect: photo-AI share-driven apps lead new-app $1K MRR success in Photo & Video (21.4%) [MEASURED, RevenueCat secondary]. Treat demand as UNPROVEN.
- Incumbents: generic pet-photo AI apps and filters (not individually researched). Gap [INFERENCE]: most are filters, not a text-led personality card.
- Hook: pet photo with a tarot-like card and a savage caption ("Tuna. Does not pay rent. Judges you.").
- Monetisation: free card, paid "trading card pack" or print-ready card; sponsor/affiliate later.
- Build: yes. Vision LLM caption + card renderer.
- Risk: low willingness to pay; 4.3 MED. Safe from ethical issues (animals only). Good cheap test.

### 5. İsim Analizi / "Name Story" cards for Turkish names (working: "Adın Hikayesi")
- Pitch: Enter a Turkish name -> origin, hidden meanings, a "fictional character" and an art card; compare with friends' names.
- Target: Turkey + diaspora (Germany); both baby-name parents and curious users.
- Evidence: not measured here. Baby-name apps appear as cross-sell in baby apps (e.g. "AI Baby Generator: Baby Names") [ANECDOTE]. UNPROVEN demand; Turkish name-meaning search is a known Turkish web habit [INFERENCE].
- Incumbents: generic name-meaning apps and websites [not researched]; gap: mostly English-first, Western names.
- Hook: type your name -> animated reveal "Ece: 'ay yüzlü'" with a card.
- Monetisation: ads/low; baby-name pack one-time; premium art cards.
- Build: yes.
- Risk: accuracy of etymology (LLM hallucination: must use curated sources); weak revenue; 4.3 MED.

### 6. Aile Fotoğrafı Düzelt: "Eski Foto Canlandır" old family photo restore + gentle animation (working: "Nostalji")
- Pitch: Restore, colorize and lightly animate old family photos; share clip to relatives.
- Target: Turkey + global 35+ (children of the migrants; family WhatsApp groups).
- Evidence: Remini 132.6M downloads [MEASURED, AppTweak 2025]; Lightroom AI estimated $5-10M/mo (AppSprint, estimate). Photo enhancement a proven category.
- Incumbents: Remini, MyHeritage "Deep Nostalgia" (not verified in this research), Photoroom. Complaint gap [ANECDOTE/INFERENCE]: weekly auto-renew traps, over-smoothed "plastic" faces, no Turkish UI. One-time payment, honest "before/after slider", no sub trap.
- Hook: grandparent's black-and-white photo blinks and smiles; emotional reaction videos.
- Monetisation: pay per photo pack (credits), no subscription.
- Build: yes/maybe. Dep: restoration + image-to-video API costs; per-photo cost must be below price.
- Risk: very saturated (4.3 HIGH). Only restore and animate the user's own family photos; add policy against animating third-party/public figures (deepfake exclusion). Emotional but ethics-sensitive (deceased relatives).

### 7. Couple Photo-Booth Strips with styles (working: "Fotoğraf Kabini")
- Pitch: A two-person remote photo booth: each partner takes selfies, app merges into a retro strip/collage with film styles; share to Stories.
- Target: Global Gen Z couples/friends + Turkey.
- Evidence: weak. TaraSnap photo booth app shows $21.73 MRR [ESTIMATE, TrustMRR]. Lenz AI (digital camera effect) $2.4K MRR within months [ESTIMATE/self-reported], so aesthetic-camera apps can work. Treat as LOW-ceiling.
- Incumbents: Many photo-booth/collage apps. Gap: remote two-person collaboration (not found in my research as a feature [INFERENCE]).
- Hook: side-by-side strip animating frame by frame.
- Monetisation: sub for filters/layouts or one-time pack.
- Build: yes. No heavy AI; mostly client-side rendering.
- Risk: 4.3 HIGH (saturated). Low differentiation; mostly a distribution-experiment.

### 8. Journal Wrapped: "Yıllık Özet" for your notes/chats (working: "Sen Wrapped")
- Pitch: Import your own exported WhatsApp chat or photos locally and produce a funny year-in-review (top words, who ghosts, mood curve) as share cards.
- Target: Turkey Gen Z; seasonal (Dec-Jan peak).
- Evidence: Wrapped apps exist: WhatsApp recap, photo Wrapped (est. <$10K/mo, 171 MAU) [ESTIMATE]; Reflection annual review 142 PH upvotes [ANECDOTE]. Seasonal spike but small.
- Incumbents: WA Wrapped 2025, 2025 Recap for WhatsApp, You Wrapped. Gap: not Turkish, privacy concerns (chats uploaded to servers) [INFERENCE]. On-device parsing of exported chat is a privacy selling point.
- Hook: "Arkadaş grubunun en çok kim konuşuyor?" ranking card.
- Monetisation: one-time purchase per export; group pack.
- Build: yes. Dep: parse WhatsApp export text on device; LLM summary of aggregated stats only (not raw messages).
- Risk: seasonal; other people's messages are in chats (privacy); WhatsApp ToS/export is user-initiated so OK, but avoid scraping. 4.3 MED-HIGH.

### 9. Audio postcards: "Sesli Kart" voice message to song snippet (working)
- Pitch: Record a 10-second message in your own voice -> AI turns it into a short stylised jingle/rap with your lyrics (your own voice or stock singers), made for birthday/anniversary sharing.
- Target: Turkey + global; gifting use case.
- Evidence: AI cover/voice apps have 1M+ installs but low revenue (<$10K/mo est. for VocalMe) and poor ratings (VoiceFun 2.75 stars) [ESTIMATE/MEASURED listing]. One tracker shows $44K/30 days for AI Cover - Music Video [ESTIMATE]. Mixed.
- Incumbents: VocalMe, VoiceFun, Cover AI, Sing AI. Gap [ANECDOTE]: aggressive billing, failures after payment. Gifting framing + refunds-if-fail.
- Hook: reaction to a friend receiving a rap about them.
- Monetisation: per-song credits (gift tied).
- Build: maybe. Dep: music/song-generation API and licensing terms for commercial use; costs.
- Risk: MUST NOT clone third-party/celebrity voices (excluded; also copyright). Use stock voices or the user's own voice only. 4.3 HIGH (many cover apps). Legal risk with song rights.

### 10. Roast-My-Style: "Tarz Analizi" outfit/room/desk aesthetic scoring with share card (working)
- Pitch: Upload a photo of your outfit/desk/room -> AI assigns an "aesthetic" (e.g. "dark academia") with a witty score and shop-free styling tips.
- Target: Global Gen Z; Turkey.
- Evidence: weak/anecdotal; I found no measured data for this niche. Its lean on visual share cards matches RevenueCat observation that Photo & Video attracts new subscription apps [MEASURED secondary].
- Incumbents: Not researched; generic AI stylist apps. Gap [INFERENCE]: serious stylists vs fun roast.
- Hook: red-pen "scorecard" overlay on photo.
- Monetisation: credits for deeper analysis; affiliate disabled in v1.
- Build: yes. Vision LLM.
- Risk: body-judgment harm (do not rate bodies/faces, only objects/outfits); 4.3 MED.

### 11. Kimlik Kartı: "Retro Photo-ID / Passport-Style Character Card" (working: "Hangi Dizi Karakteri?")
- Pitch: Quiz + selfie -> which Turkish TV series archetype (e.g. 'Mafia boss', 'Kader kurbanı', 'Sevimli komşu') you are, rendered as a retro ID/poster card.
- Target: Turkey (strong TV-series culture [INFERENCE]); diaspora.
- Evidence: personality card apps with archetypes and 3D cards already exist (AmIThis, MBT+) [ANECDOTE]; local-culture version not found. Demand for Turkish version UNPROVEN.
- Incumbents: MBT+, AmIThis, Personality test apps. Gap: not localized, no culture-specific archetypes.
- Hook: reveal animation; friends compare cards ("sen kimsin?").
- Monetisation: free type; paid styled card pack; friend-compare multiplayer.
- Build: yes. Quiz logic + LLM text; optional image styling.
- Risk: IP: do not use real series names, actors or characters (use generic archetypes). 4.3 MED-HIGH (personality category crowded: App Goblin shows enormous app counts for "share" keyword, single data point).

### 12. "Gerçek Kız/Erkek Arkadaş Testi": Relationship-Style Quiz for Two (working: "İkimiz")
- Pitch: Each partner answers 15 quick questions separately; app reveals differences with humorous shareable "who knows whom" results; no therapy claims.
- Target: Turkey + global couples.
- Evidence: Paired (4M+ couples self-reported, 10.7M installs [ESTIMATE]) and Love Nudge show demand but weak momentum (Love Nudge declining per AppGoblin) [ESTIMATE]. Friend-guessing mechanics already exist in personality apps [ANECDOTE].
- Incumbents: Paired, Love Nudge, Between. Gap [INFERENCE/unverified]: Paired is English-centric and subscription-led; a game-first, share-first Turkish-language product could fit.
- Hook: split-screen "Cevabın vs onun cevabı" tension video.
- Monetisation: weekly sub or one-time question packs.
- Build: yes. Needs two-device sync (simple backend, e.g. Firebase) and LLM question generation.
- Risk: retention (relationship apps churn when novelty fades; AI-apps churn data [MEASURED secondary]); 4.3 MED. Must avoid therapy/medical claims.

## 3. Ranking suggestion (my judgment, not data)

Best fit to constraints (cheap, Turkish moat, share-native, low API cost): #1 KahveAI, #2 Uyum, #5 Adın Hikayesi, #4 Patim, #3 Yüzüm Hangi Karakter (higher cost, higher risk), #12 İkimiz.
Highest evidence of large revenue but most competitive/risky: #6 Nostalji (photo restore), #3 (avatars), #9 (voice).

## 4. Cross-cutting risks and mitigations

- Free general models (Gemini/ChatGPT) cheaply replicate any single-prompt transformation; Appfigures shows download spikes without matching revenue [MEASURED]. Mitigation: ritual + local culture + social loop + packaged shareable card.
- Turkey monetisation is thin (about $0.6 gen-AI revenue per download in 2025, derived from the two secondary numbers above [INFERENCE]). Price in USD for global traffic; use TikTok in English-language variants for the same product.
- AI-app retention weaker than non-AI (RevenueCat secondary [MEASURED]) -> favor one-time credits and seasonal triggers.
- 4.3: differentiate with unique content, brand, and Turkish-first UX; avoid reskins of white-label templates; keep one bundle per app; write review notes explaining unique features. Evidence of rejections is anecdotal (forum posts).
- Excluded by constraints and avoided: deepfakes of real people, nudity, gambling, medical/financial advice, trading signals, ToS-violating scraping, hardware dependency. Entertainment-only disclaimers for fortune/astrology/relationship ideas.

## 5. Gaps / next verification steps

1. Pull actual 1-3 star reviews (Turkish and US storefronts) for Faljı, Derya Abla, Co-Star, Paired, Remini, MBT+, VocalMe via Appfigures/Sensor Tower free tiers or direct store pages. 2. Reddit threads (r/astrology_apps, r/relationship_apps, r/iosapps) were not reachable. 3. Verify original Appfigures May 2026 report and RevenueCat report figures at the primary source. 4. Run TikTok search for each hook to see whether comparable videos already get organic reach in Turkish.
