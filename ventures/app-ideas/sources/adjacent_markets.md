# Adjacent-market transfer ideas (Korea / Japan / China / SEA -> Turkey / MENA / West)

Compiled 2026-11-06 from ~15 web searches (WebSearch snippets only; most pages were NOT opened in full).
Evidence legend: [M] = measured/reported figure from a named source, [A] = anecdote or press description, [ASSUMP] = my assumption, not verified.
Constraints respected: no deepfakes of real people (all photo ideas operate only on the user's own / consenting-friend photos), no nudity, no gambling, no medical/financial advice, no hardware, fortune/face-reading only as entertainment.

## Cross-cutting context (read first)
- Turkey GenAI app downloads: Adjust, citing Sensor Tower, says 11.3M (2023) -> 27.4M (2024), +142.5% [M, secondary]. A later summary claims 82.9M in 2025, +149% [M, secondary, unconfirmed vs Sensor Tower]. Demand for AI-image apps in Turkey is real, but ChatGPT/Gemini dominate. https://www.adjust.com/blog/turkey-app-trends-2025/ , https://www.dailysabah.com/business/tech/ai-app-spending-surges-past-5b-as-usage-more-than-triples-in-2025
- Turkey is NOT empty in fortune apps: Kaave Falli reported 13M downloads and ~400M readings by 2016 [M, old] (https://webrazzi.com/2016/04/29/400-milyon-fal-yorumlayan-kaave-fali-uygulamasinda-artik-hedef-globallesme/); Tamindir lists Derya Abla/Falji at 10M+ Android downloads [M, inconsistent page] (https://www.tamindir.com/indir/derya-abla-kahve-fali/). So any fortune-adjacent idea must differentiate by format, not by "fortune" itself.
- I could not get any current Turkey store-ranking data for photo/lifestyle categories. Every "not saturated in Turkey" claim below is therefore [ASSUMP] unless stated. Verify with Sensor Tower / AppMagic / store search in Turkish before building.
- Pattern from China: single-tap portrait effect launches, spreads on Douyin/Xiaohongshu, rivals clone it within weeks (SCMP, Shine, Geo/Meitu pieces below). Implication: speed beats polish, moat is distribution + weekly content cadence.

---

## 1. Dort Kare (working title: "4Kare") - Korean 4-cut photo strip, remote/friends edition
- Pitch: Make a Life4Cuts-style 4-photo strip with a friend who is in another city, with Turkish-flavored frames (cay bahcesi, Bogaz vapuru, sinema bileti), date stamp and QR "album" link.
- Origin + evidence: Life Four Cuts began as one unmanned booth in Daegu in 2017; ~410 stores and 120M+ visits per company figures reported by Korea Herald [M, company-reported]. Revenue KRW 12.3B (2020) -> 49.4B (2023) per seoulz.com [M, unverified blog]. Expansion to Singapore/London reported [A]. Sources: https://www.koreaherald.com/article/10503226 , https://www.seoulz.com/korea-photo-booth-2026/ , https://www.koreajoongangdaily.com/korea/koreas-photo-booths-offer-creative-ways-of-leaving-memories/12031344
- Why not saturated: physical booths are only just reaching UK/Europe (seoulz claim, unverified). Apps for photo strips exist generally; a Turkish-localized, remote-collab one is [ASSUMP] unserved. The physical booth experience cannot be replicated, so the app wins on remote/anywhere use.
- Adaptation: Turkish frame packs, shared "ortak serit" where two friends each shoot 2 frames live from separate phones; seasonal packs (Ramazan Bayrami, 29 Ekim, mezuniyet).
- 3-second hook: screen-record of two split selfies snapping into a vertical 4-frame strip that "prints" with a paper-slide animation; output = strip PNG with date + frame.
- Monetization: free with watermark; frame pack IAP / weekly Pro unlock; ad-free.
- Buildable in 1-2 weeks: YES. Camera capture + canvas compositing; no AI required. Dependency: simple backend (or link-share via Firebase) for the remote-pair mode; solo mode is fully local.
- Main risk: low technical moat; booth-trend may be a Korea-specific offline fad; generic strip-maker apps already on stores.

## 2. Renk Mevsimi - inclusive personal-color (seasonal) analysis with a Turkish palette focus
- Pitch: Selfie in daylight -> season/tone result (e.g., "Sonbahar sicak") with a shareable palette card, plus clothing/makeup/scarf color swatches.
- Origin + evidence: Seoul personal-color studios became a tourist draw; TIME and others reported it; one report cites 375M TikTok views for "personal color analysis Korea" [M, single secondary report]. Korean AI self-test app Zamface reported 1.7M users [M, article year unclear]. Sources: https://time.com/6299099/personal-color-analysis-korea-tourism , https://thestar.com.my/lifestyle/style/2023/07/30/style-conscious-gen-zs-travel-to-seoul-for-039personal-colour-analysis039-service , https://popsugar.com.au/?p=924195
- Why not saturated: it is NOT saturated in English (several apps already: Color Analysis, ColorLover, PersonalColorAI per store/search results). Turkey-localized angle is [ASSUMP]. Known gap: color analysis historically fails on darker skin, AI bias flagged (same TIME/newsindiatimes coverage) - an explicitly inclusive Mediterranean/Middle Eastern/darker-skin model is a differentiator.
- Adaptation: palettes for headscarf/hijab colors, Turkish makeup brands' shade families (names only, no affiliation), "gelin/dugun misafiri" outfit palettes.
- 3-second hook: face with a color-drape sweeping over the shoulders (4 swatches flipping), ending on a "Your season" card.
- Monetization: free season result; paid full palette + celebrity-free "similar tone" lookbook; affiliate (assumption).
- Buildable: MAYBE-YES. Dependency: a vision LLM for undertone judgment is unreliable and bias-prone; better to compute skin/hair/eye color sampling in code and use LLM only for copy. Needs careful lighting guidance.
- Main risk: accuracy/credibility ("it told me the wrong season"), bias criticism, crowded English market.

## 3. Dort Sutun Karakter (saju-style "four pillars" personality card), entertainment-only
- Pitch: Enter birth date -> a saju-inspired elemental character card (Ates/Su/Toprak/Metal/Agac) with a quirky Turkish-voiced "mizac" description; clearly labeled eglence.
- Origin + evidence: Korean saju/fortune market estimated ~KRW 1.4T (~$1B) by a startup-analytics firm cited in a blog [M, weak]; Forteller ~628K MAU (+28% YoY) and Jeomsin 17M cumulative downloads per Asia Economy [M, press]. Sources: https://www.asiae.co.kr/en/article/2026051116060499682 , https://www.asiae.co.kr/en/article/2024100416312538845 , https://www.seoulz.com/korea-saju-industry/
- Why not saturated: partly it IS saturated - Turkish fal/astrology apps are huge (see context). The unserved piece is the East-Asian elemental framework as a visual character-card format [ASSUMP]. Treat as the riskiest "novelty" claim.
- Adaptation: fuse with Turkish cultural touchpoints (evil eye motifs, "kahve falindan farki"), no predictions of money/health/death - personality and "this week's vibe" only.
- 3-second hook: birth date typed -> five-element wheel spins -> collectible character card (illustrated animal/element), designed for story sharing and friend comparison.
- Monetization: weekly subscription for "compatibility" and weekly vibe; IAP card skins. Note: fortune apps monetize well in Korea (anecdotal press), Turkey [ASSUMP].
- Buildable: YES. Deterministic calendar math (lunisolar conversion via library) + LLM for copy + pre-generated art. Dependency: correct Chinese/Korean calendar conversion library.
- Main risk: store policy/health-finance prediction drift (keep strictly entertainment), cultural/religious sensitivity in Turkey and MENA (fortune-telling disliked by some), Turkish incumbents.

## 4. Ortak Gun (Between-style private couple space with widget-first design)
- Pitch: Home-screen widget showing "Birlikte X gun" plus a private shared photo wall and anniversary reminders (100th day, 1000th day), built mobile-widget-first.
- Origin + evidence: Between (VCNC, Korea/Japan, DeNA investment) is the reference couple app [A/M: investment reported] https://wirelesswatch.jp/dena-takes-position-in-between-app-maker-vcnc/ ; Been Together's store listing claims 20M+ users since 2012 [M, self-reported] https://apps.apple.com/bg/app/id539392422 ; many D-day counters exist (Couple D-Day, Couple Day...).
- Why not saturated: it is NOT. The category is crowded with D-day apps. Differentiation is only localization (Turkish milestone culture: 100. gun, sevgililer gunu, nisan) and design quality [ASSUMP].
- Adaptation: Turkish milestone packs ("ilk kahve", "ilk bayram"), long-distance mode with shared time zone clock, widget themes.
- 3-second hook: phone home screen tour showing a cute couple widget counting up; first-frame text "1000. gun" with confetti.
- Monetization: widgets/themes IAP, annual sub for private album + backup.
- Buildable: MAYBE. Widgets (iOS WidgetKit/Android) + sync backend + privacy handling; AI adds little. Dependency: native widget code (hard in a cross-platform builder).
- Main risk: saturated category, retention requires both partners, privacy of intimate photos (strict moderation needed).

## 5. Kil Portre (weekly rotating single-tap AI style effect, own photos only)
- Pitch: One-tap weekly "trend of the week" portrait style (clay figure, snow-dusted, plush toy, etc.) from the user's own selfie, with Turkish-landmark backdrops.
- Origin + evidence: Remini's clay filter pushed it to the top of China's free rankings with ~400K daily downloads in the week Apr 30-May 6 (2024) per SCMP/Chinese press [M, secondary]; Douyin added a free clay effect and Meitu cloned it [A]. Meitu's "AI snow" effect went viral in Nov 2025, paid after 3-day trial [A/M]. Sources: https://scmp.com/tech/tech-trends/article/3261879/ai-photo-enhancer-remini-latest-hot-app-china-surpassing-tiktoks-sister-platform-douyin , https://www.shine.cn/biz/tech/2405100158 , https://www.geo.tv/latest/633293-after-nano-banana-craze-netizens-embrace-meitus-ai-snow-photo-trend
- Why not saturated: not saturated as a cadence product, but big players (Meitu, Remini, ChatGPT/Gemini image models) clone any trend in days. Turkish-localized backdrops/captions [ASSUMP] are the thin angle.
- Adaptation: Turkish skylines and festivals, group/pair mode where friends are placed together (consenting uploaders only), Turkish captions.
- 3-second hook: before/after swipe: selfie -> clay/plush version, 1.5s transition.
- Monetization: credits / weekly sub (generation has real cost).
- Buildable: YES. Dependency: image-edit API (cost per call is the margin constraint; need rate limiting and a content filter; reject non-selfie / celebrity images).
- Main risk: unit economics, commoditization by frontier chat apps, platform policy on face uploads, abuse (must block use on others' photos/celebrities - add face-consent UX).

## 6. Arkadas Grubu Rolleri (MBTI-style, but for friend groups, shareable cards)
- Pitch: 12-question vibe quiz that sorts you into a friend-group role (the planner, the chaos agent, the group therapist), then compares roles across a group chat.
- Origin + evidence: MBTI craze in Korea (Hankook Research: over half of Koreans had taken a test, per Korea Times, Mar 2025 [M]) and Japan (one Sept 2024 survey: 41.3% of Gen Z women had taken it [M], some dating apps use it). Sources: https://www.koreatimes.co.kr/www/nation/2025/03/281_335268.html , https://www.fun-japan.jp/en/articles/14070 , https://www.koreajoongangdaily.com/kjd-special/why-blood-types-palm-reading-now-mbti-koreas-love-for-categorizing/11499280
- Why not saturated: 16Personalities dominates individual tests; group-role compatibility with Turkish humor is [ASSUMP] open. Do NOT claim MBTI itself is untouched in the West.
- Adaptation: Turkish meme language, "grup sohbeti" archetypes; result card fits WhatsApp/Instagram story size.
- 3-second hook: "Which friend in the group are you?" -> animated archetype card; second hook: group chat leaderboard.
- Monetization: low; light ads, cosmetic card packs, sponsorships. Likely a growth/viral vehicle rather than a revenue product.
- Buildable: YES. Static quiz web app + OG image generation. Dependency: none beyond a web host.
- Main risk: very low retention and monetization; copycat-ability.

## 7. Puri-Doodle (purikura-style sticker & doodle editor)
- Pitch: Import a photo or shoot in-app; draw glossy doodles, add stamps, date text and frames in the Japanese purikura / Heisei-retro style.
- Origin + evidence: FuRyu published a 2025 purikura trend survey; Fun-Japan reports a purikura revival among Gen Z with "Heisei retro" styling [A]; a 2023 Korean report citing Nikkei describes the same revival [A]. Sources: https://www.fun-japan.jp/en/articles/14506 , https://www.asiae.co.kr/en/article/2023061321594951773 . Correction on my search: results did not tie Snow/B612 to the revival, so I do not claim that.
- Why not saturated: generic sticker/photo editors are plentiful (B612, Snow listing: B612 has 100K+ ratings [M] https://apps.apple.com/app/id904209370). The Y2K / Heisei-retro doodle aesthetic for Turkish and Western Gen Z is [ASSUMP] less served.
- Adaptation: Turkish Y2K nostalgia (90s-2000s: Kral TV, Cafe Crown-era, Msn emoticons) as sticker packs; friend photo-collab doodle.
- 3-second hook: plain selfie -> hand-drawn glitter doodles, hearts and date stamp pop in with sparkle sound.
- Monetization: sticker pack IAP, weekly subscription, creator-sold packs later.
- Buildable: YES. Canvas drawing + sticker layers. Dependency: art assets (AI-generated sticker sets, check licensing).
- Main risk: no moat vs. B612/Snow/Canva; asset quality; low retention.

## 8. Gunluk Kolaj (digital sticker journal / diary decoration, one page per day)
- Pitch: Daily vertical collage page - photo + mood stickers + a one-line note - collected in a calendar "magazine".
- Origin + evidence: Japanese and global sticker/journal culture revived (CIJ Today, 2025 [A]); Apple iOS 17 camera-roll stickers sparked a digital sticker style trend per Ypulse [A]; Papelook is an older Japanese collage app (2013) [A, dated]. Sources: https://cijtoday.com/?p=169191 , https://www.ypulse.com/newsfeed/2025/12/09/gen-zs-japan-obsession-is-so-strong-that-just-slapping-tokyo-on-a-photo-makes-it-look-better/ , https://thebridge.jp/en/2013/07/papelook-digital-garage-investment
- Why not saturated: indie visual-journal apps exist (Daily Sticky, Daylit per search results), so it is not empty. Evidence of current Asian demand is the WEAKEST of the list: I did not find a Korean "diary-decorating (dagu)" source. Treat as speculative.
- Adaptation: Turkish prompts, Ramazan/bayram templates, share to story as a "my day" poster.
- 3-second hook: time-lapse of a blank day page being decorated with stickers in 3 seconds; output = poster for stories.
- Monetization: sticker packs, annual sub for cloud backup/print-ready export (print partnerships later).
- Buildable: MAYBE. Dependency: canvas editor with gesture handling and local storage; polish takes time.
- Main risk: weak evidence, journaling apps have poor retention, hard to demo virally.

## 9. Fan Kartim (K-pop-style photocard / fan-letter maker for fans' own content)
- Pitch: Make a collectible-style photocard of YOURSELF or your own fan art (holo foil effect, frame, serial number) and decorated fan letters/posters - no idol photos shipped in-app.
- Origin + evidence: Weverse's fan-letter editor lets fans write and decorate letters with templates [A], and fan platforms (Weverse, Lysn Bubble, Universe) monetize fan interaction [A, 2021 ABS-CBN piece is old]. Sources: https://abs-cbn.com/life/08/12/21/apps-give-k-pop-fans-spaces-to-interact-with-idols , https://scmp.com/lifestyle/k-pop/article/3144651/k-pop-artist-fan-interaction-increasingly-depends-apps-such-weverse . I did not find a source on the photocard-collecting trend itself (background-knowledge only) nor on Turkish K-pop fan size [ASSUMP].
- Why not saturated: [ASSUMP] no Turkish-language fan-card tool; global photocard makers exist.
- Adaptation: fan-community language packs (Turkish, Arabic) for MENA K-pop fans; "bias" cards with the user's own artwork and name.
- 3-second hook: flat selfie -> tilting phone shows holographic foil photocard with sparkles.
- Monetization: foil/frame packs, printing affiliate.
- Buildable: YES. Dependency: WebGL/CSS holo shader and gyroscope (device motion API, not extra hardware).
- Main risk: IP/copyright on idol images (block idol uploads or disclaim), narrow audience, fandom policing.

## 10. Yuz Okuma (physiognomy-style face reading, entertainment)
- Pitch: Selfie -> a playful "face reading" card (your face shape as an archetype with a lighthearted trait list); explicitly parody-grade entertainment.
- Origin + evidence: Face-reading/physiognomy (gwansang) is a staple of Korean fortune culture; I did NOT find a verified 2024-2026 source for specific apps. The fortune market evidence (idea 3) and Korea's love for categorizing (JoongAng Daily) are indirect [A]. https://www.koreajoongangdaily.com/kjd-special/why-blood-types-palm-reading-now-mbti-koreas-love-for-categorizing/11499280
- Why not saturated: [ASSUMP]. "Which celebrity do you look like" is a known category, so avoid celebrity comparison (consent/likeness concerns); use animal/character archetypes instead.
- Adaptation: Anatolian/Ottoman portrait style cards, humor tone.
- 3-second hook: face with scanning grid -> archetype card ("Kartal burunlu stratejist").
- Monetization: weekly sub for couple/friend compatibility.
- Buildable: MAYBE-YES. Dependency: on-device face landmarks (MediaPipe) for shape metrics + LLM copy.
- Main risk: weakest evidence; ethical concern of pseudo-physiognomy (frame as joke, never judge ethnicity/attractiveness/character seriously); policy risk for face-based inference.

## 11. Cizdik Bitirdik (2-tap async drawing game with friends, SEA-style)
- Pitch: Draw-and-guess chains with friends inside any chat via a link; Turkish word packs and humor, no accounts.
- Origin + evidence: Sensor Tower's 2025 SEA report says Vietnam is a hotbed of new viral hits; local casual game "Tro Ve Vui Tuoi Tho" led download growth and "456 Run Challenge: Clash" reached top-10 downloads in Q1 2025 [M, as summarized by the newsletter]; a Gamota analysis argues SEA players play for friends and "play with friends in 2 taps" is core design [A]. Sources: https://gamedevreports.substack.com/p/sensor-tower-southeast-asia-mobile?open=false , https://gamota.com/en_GB/?p=2748%2F
- Why not saturated: drawing-guess apps exist (e.g., the Pictionary genre); Turkish-language, link-first, no-install variant is [ASSUMP] unserved. I did not verify Turkish competitors.
- Adaptation: Turkish idioms/deyimler, TV-series references; aimed at WhatsApp groups.
- 3-second hook: sped-up drawing of an absurd prompt, then a friend's wrong guess in a speech bubble.
- Monetization: ads (rewarded), cosmetic packs.
- Buildable: YES-MAYBE. Dependency: realtime sync (Firebase / websockets), moderation of user drawings.
- Main risk: gaming CPI economics; ad-supported indie games are a hard business; moderation burden.

---

## Triage (my opinion, labeled as such)
- Best speed/risk fit for solo+TikTok: #1 (4Kare), #5 (Kil Portre, if unit economics are capped), #7 (Puri-Doodle), #6 (cheap viral top-of-funnel).
- Highest upside but crowded/contested: #2, #4.
- Speculative / weak evidence: #3, #8, #9, #10, #11. Validate demand with a landing-page or TikTok teaser before building.
- Known gaps in this research: no verified current Turkish chart data, no Rest of World article retrieved, Korean "diary decorating" and photocard trends not evidenced, Xiaohongshu-specific format evidence thin.
