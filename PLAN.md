# Prop Firm Algoritmik Trading Botu: Ana Plan

> Hedef: Prop firm challenge'larını geçen ve fonlu hesapta istikrarlı ödeme alan, klasik indikatörlere (RSI, MACD vb.) dayanmayan, istatistiksel olarak doğrulanmış kurallarla işleyen bir bot.
>
> İlke: **Hiçbir fikre inanmıyoruz, her fikri ölçüyoruz.** Testi geçemeyen fikir ne kadar güzel olursa olsun çöpe gider.

---

## 1. Kararlar (piyasa, firma, zaman dilimi)

### Prop firm: **FTMO, 2-Step Challenge** (birincil seçim)

| Kriter | FTMO 2-Step | Neden önemli |
|---|---|---|
| EA / bot | İzinli, MT5 üzerinde | Botu VPS'te 7/24 çalıştırabiliriz |
| Günlük kayıp limiti | %5 (floating dahil) | Risk yöneticisi buna göre sert kural koyacak |
| Toplam kayıp limiti | %10, **statik** (trailing değil) | Statik drawdown sistematik trading için çok daha adil |
| Hedef | Faz 1 %10, Faz 2 %5 | Simülasyonla geçme olasılığını hesaplayacağız |
| Firma geçmişi | Sektörün en köklü firmalarından | Ödeme güvenilirliği |

**Neden futures firmaları (Topstep, Apex vb.) değil?**
- Çoğunda **trailing drawdown** var. Kâr ettikçe stop seviyesi yukarı çıkıyor, bu da sistematik stratejiyi gereksiz yere cezalandırıyor.
- Topstep botlara API ile izin veriyor ama yalnızca **yerel çalıştırma** şartıyla (VPS ve bulut yasak). Bilgisayarının sürekli açık olması gerekir.
- Kaliteli futures intraday verisi ücretli (Databento vb.).

İkinci seçenek olarak, ilk strateji hazır olduğunda **The5ers** gibi EA'ya izin veren başka bir CFD firması değerlendirilebilir. Birden fazla firmada aynı sistemi çalıştırmak firma riskini dağıtır.

> Kurallar sık değişiyor. Para ödemeden önce FTMO'nun güncel kural sayfası (EA, haber trading'i, hafta sonu pozisyonu, "gambling" tanımları) mutlaka tekrar okunacak.

### Piyasa: **US100 (Nasdaq), US500, GER40 endeks CFD'leri + XAUUSD (altın)**
- Endekslerde gün içi yapısal davranış (açılış dinamikleri, gün içi momentum, gece/gündüz farkı) akademik literatürde en iyi belgelenmiş alanlardan biri.
- Altın ve endeks farklı sürücülerle hareket ediyor, bu da düşük korelasyonlu bir portföy demek.
- Major FX (EURUSD, GBPUSD, USDJPY) ikinci aşamada çeşitlendirme ve pair/stat-arb araştırması için eklenecek.
- **Kripto hayır.** FTMO'da yüksek spread/swap var ve davranışı endekslerden çok farklı.

### Zaman dilimi: **Intraday. Sinyal M5/M15, pozisyon süresi dakikalar ile birkaç saat. Rejim filtresi için günlük veri.**
- **Scalping hayır:** Spread ve komisyon edge'i yer, ayrıca HFT benzeri davranış prop kurallarına takılabilir.
- **Swing ve çok günlü pozisyon hayır (başlangıçta):** Hafta sonu ve gap riski var, günlük %5 limiti kontrol edilemez, işlem sayısı istatistik için az kalır.
- **Intraday:** İşlem başına maliyet hareketin küçük bir kısmı. Yılda yüzlerce işlemle istatistiksel güç yüksek, günlük risk tamamen kontrol altında.

---

## 2. Asıl soru: Ne üzerine inşa edeceğiz?

### 2.1 Temel gerçek: Neyi tahmin edebiliriz, neyi edemeyiz?

Finansal matematiğin en sağlam bulgularından biri şu:

1. **Getirinin yönü** neredeyse rastgeledir (zayıf otokorelasyon). Edge burada küçük ve kırılgan.
2. **Volatilite (oynaklık) ise güçlü biçimde tahmin edilebilir.** Volatilite kümelenir: bugün oynak ise yarın da muhtemelen oynaktır. Bu, GARCH ve HAR-RV modelleriyle onlarca yıldır gösterildi.
3. **Zaman yapısı** (seans açılışı, kapanış, ay sonu, haber saatleri) piyasa katılımcılarının davranışından kaynaklanır ve kalıcıdır. Fonlar belirli saatlerde rebalans yapmak, opsiyon hedge'cileri kapanışa doğru pozisyon ayarlamak zorundadır.

Bundan çıkan strateji felsefesi:

> **"Nereye gideceğini" tahmin etmeye çalışan tek bir sihirli sinyal yerine, (a) yapısal ve davranışsal nedeni olan küçük yön edge'lerini (b) güçlü volatilite tahminiyle boyutlandırıp filtreleyerek (c) birbirine bağımlı olmayan birkaç strateji halinde birleştirmek.**

Klasik indikatörlerin sorunu matematikleri değil, **bir neden hikâyesi olmaması**. "RSI 30'un altına indi" neden kâr getirsin? Bizim her hipotezimizin cevabı olacak: *Bu kâr kimden, neden geliyor?*

### 2.2 Edge aileleri (araştırma sırasına göre)

#### A) Gün içi yapısal etkiler (ilk ve en güçlü aday)

| Hipotez | Mekanizma (neden var?) | Literatür / kaynak |
|---|---|---|
| **A1. Gün içi momentum:** NY seansının ilk 30 dakikasının getirisi, son 30 dakikanın yönünü tahmin eder | Gamma hedge eden opsiyon dealer'ları, kapanışa doğru rebalans yapan fonlar, geç gelen bilgiye geç tepki | Gao, Han, Li, Zhou (2018), *Market Intraday Momentum*, JFE |
| **A2. Opening Range Breakout (ORB):** Açılıştan sonraki ilk N dakikanın aralığından kırılım, o günün trendini taşır | Gece biriken emirlerin açılışta boşalması, bilgi akışının yoğunlaşması | Zarattini & Aziz (2023), QQQ üzerinde 5 dakikalık ORB çalışmaları |
| **A3. Aşırı genişlemiş günde gün içi ortalamaya dönüş:** Volatilite tahminine göre "aşırı" uzamış hareketlerin kısmi geri dönüşü | Likidite sağlayıcıların dengesizlik sonrası fiyatı geri itmesi | Mikroyapı literatürü (likidite sağlama primi) |
| **A4. Seans geçiş etkileri:** Asya → Londra → NY geçişlerinde fiyat davranışı (GER40 açılışı, US açılışı) | Farklı katılımcı gruplarının farklı saatlerde piyasaya girmesi | Gün içi mevsimsellik literatürü |
| **A5. Takvim akışları:** Ay sonu ve çeyrek sonu rebalans, opsiyon vade günleri (OPEX) | Zorunlu, fiyata duyarsız akışlar | Etula vd., *Month-end liquidity* |

Neden ilk sırada? Mekanizmaları açık, kurallar basit, intraday zaman dilimine uygunlar ve test etmesi hızlı.

#### B) Volatilite modelleme (her stratejinin omurgası)

Bu tek başına strateji değil, **tüm stratejilerin çarpanı**:

- **HAR-RV modeli** (Corsi, 2009): Günlük, haftalık ve aylık gerçekleşmiş volatiliteden yarının volatilitesini tahmin eder. Basit bir lineer regresyon olmasına rağmen çok güçlüdür.
- **Gün içi volatilite profili:** Volatilite gün içinde U şeklinde değişir. Stop ve hedefler sabit pip ile değil, *o saatin beklenen volatilitesine* göre belirlenir.
- **Kullanım alanları:**
  1. **Volatilite hedefleme:** Pozisyon büyüklüğü beklenen volatiliteyle ters orantılı olur, böylece her gün yaklaşık aynı risk alınır. Moreira & Muir (2017) bunun Sharpe oranını belirgin şekilde artırdığını gösteriyor. **Prop firm için kritik:** Günlük kayıp dağılımını daraltır.
  2. **Rejim filtresi:** Bazı stratejiler sadece düşük volatilitede, bazıları sadece genişleme anında çalışır.
  3. **Sinyal normalizasyonu:** "Fiyat 2 beklenen sapma kadar hareket etti" ifadesi her piyasada ve her rejimde aynı anlamı taşır.

#### C) Rejim tespiti (piyasa trend modunda mı, ortalamaya dönüş modunda mı?)

- **Varyans oranı testi** (Lo & MacKinlay, 1988): VR > 1 ise trend (pozitif otokorelasyon), VR < 1 ise ortalamaya dönüş var demektir. Kayan pencerede hesaplanıp hangi strateji ailesinin aktif olacağına karar vermekte kullanılır.
- **Hurst üsteli:** Aynı sorunun farklı bir ölçümü (H > 0,5 trend, H < 0,5 ortalamaya dönüş).
- **Hidden Markov Model (HMM):** Getiri ve volatiliteden 2–3 gizli piyasa durumu ("sakin-trend", "gergin-volatil", "yatay") çıkarır. Strateji ağırlıkları duruma göre değişir.

> Uyarı: Bunlar kolayca aşırı uydurmaya (overfitting) yol açar. Sadece önceden tanımlanmış, az parametreli filtreler olarak kullanılacak.

#### D) İstatistiksel arbitraj ve göreli değer (ikinci aşama)

- **US100 ve US500 spread'i**, **EURUSD ve GBPUSD**, **altın ve reel faiz/dolar** gibi ilişkiler.
- **Matematik:** Engle-Granger / Johansen eşbütünleşme (cointegration) testi, spread'in **Ornstein-Uhlenbeck süreci** olarak modellenmesi (yarı ömür = ortalamaya dönüş hızı) ve **Kalman filtresi** ile zamanla değişen hedge oranı.
- **Avantajı:** Piyasa yönünden büyük ölçüde bağımsızdır, yani diğer stratejilerle düşük korelasyonludur.
- **Dezavantajı:** CFD'de çift spread maliyeti ve ilişkilerin kırılması. Bu yüzden ikinci aşamada ele alınacak.

#### E) Makine öğrenmesi: Kâhin olarak değil, filtre olarak

- **Meta-labeling** (López de Prado): Birincil strateji (ör. ORB) yönü belirler. ML modeli ise yalnızca *"bu sinyali alayım mı, ne kadar büyüklükte?"* sorusuna cevap verir. Özellikler: volatilite rejimi, gün, saat, gap büyüklüğü, önceki günün aralığı vb.
- **Triple-barrier etiketleme:** Hedef, stop ve zaman bariyeri. Etiketler gerçek işlem mantığıyla birebir uyumlu olur.
- **Purged / embargoed çapraz doğrulama:** Zaman serisinde geleceğin bilgisinin modele sızmasını engeller.
- Model basit tutulacak (lojistik regresyon, gradient boosting). Derin öğrenme yok, çünkü veri az ve gürültü çok.

#### Bilinçli olarak yapmayacaklarımız
- RSI, MACD, stokastik vb. klasik indikatörler.
- Fibonacci, Elliott ve "SMC/ICT kavramları" (istersen birini *test edip çürütmek* için kullanabiliriz, ama inşa etmeyeceğiz).
- Martingale, ızgara (grid) ve ortalama düşürme. Bunlar challenge'ı geçirip fonlu hesabı patlatır, ayrıca prop firmlar da sevmez.
- Haber anında işlem (FTMO fonlu hesapta kısıtlı, slippage öngörülemez).

### 2.3 Prop firm'in kendi matematiği (çoğu trader'ın hiç düşünmediği kısım)

Challenge aslında bir **bariyer problemi**: Sermaye önce +%10'a mı, yoksa -%10 / günlük -%5 sınırına mı değecek? Bu, rastgele yürüyüşlerde "ilk geçiş zamanı" (first-passage) ve "kumarbazın iflası" (gambler's ruin) problemidir.

Örnek simülasyon (bu repoda çalıştırıldı): Kazanma oranı %45, kazanç/kayıp = 1,55R (işlem başı beklenti ≈ +0,15R), günde en fazla 2 işlem, sınır 120 işlem günü:

| İşlem başı risk | Gerçek edge'li sistem: Geçme olasılığı | **Edge'siz** sistem (beklenti 0) |
|---|---|---|
| %0,25 | %48 (çoğunlukla süre bitiyor) | — |
| %0,50 | %86 | %28 |
| **%0,75** | **%90** | — |
| %1,00 | %87 | %48 |
| %1,50 | %78 | — |
| %2,00 | %72 | %47 |
| %3,00 | %34 | — |

Bu tablodan çıkan dersler:
1. **Edge'siz bir sistem bile challenge'ı yaklaşık %50 ihtimalle geçebilir.** Yani bir challenge'ı geçmek "sistemim çalışıyor" demek değil. Senin geçmişteki sonuçların da bu yüzden yanıltıcı olmuş olabilir.
2. **Risk arttıkça geçme olasılığı bir noktadan sonra düşer.** Optimal risk, Kelly kriterinden çok daha düşüktür. Bunu her strateji için kendi işlem dağılımıyla hesaplayacağız.
3. **Challenge ve fonlu hesap farklı problemlerdir.** Challenge'da amaç hedefe varma olasılığını maksimize etmek. Fonlu hesapta ise hesabı kaybetmeden uzun süre ödeme almak, yani daha düşük risk.
4. Ekonomik hesap: Beklenen değer = P(geçme) × E(fonlu hesaptan ödemeler) − challenge ücreti. Botun her sürümü için bu sayı hesaplanacak.

---

## 3. Bilimsel test protokolü (kendimizi kandırmamak için)

Her hipotez şu adımlardan geçer. Bir adımda kalırsa elenir.

1. **Ön kayıt:** Hipotez, mekanizma, kurallar ve parametre aralığı test başlamadan önce `research/hypotheses/` altına yazılır.
2. **Veri ayrımı:**
   - In-sample (keşif): ~2015–2020
   - Out-of-sample (doğrulama): ~2021–2023
   - **Kilitli test seti: 2024 ve sonrası.** Sadece en sonda, bir kez açılır.
3. **Gerçekçi maliyetler:** FTMO'ya yakın spread, komisyon, slippage ve swap. Ayrıca 1,5x ve 2x maliyetle stres testi.
4. **Robustluk:**
   - Parametre komşuluğu: Optimum etrafındaki değerler de kârlı olmalı ("plato", "zirve" değil).
   - Farklı enstrümanlarda benzer davranış (US100'de çalışan, US500 ve GER40'ta da en azından pozitif olmalı).
   - Walk-forward analizi.
5. **İstatistiksel anlamlılık:**
   - **Deflated Sharpe Ratio** (Bailey & López de Prado): Kaç deneme yaptığımızı hesaba katar.
   - **PBO (Probability of Backtest Overfitting)**, CSCV yöntemiyle.
   - Bootstrap ile Sharpe güven aralığı.
6. **Prop simülasyonu:** İşlem dağılımından Monte Carlo ile P(Faz 1), P(Faz 2), fonlu hesapta beklenen ömür ve ödeme.
7. **Forward test:** FTMO **Free Trial / demo** hesapta en az 4–8 hafta canlı. Sonuçlar backtest dağılımının içinde kalmalı.
8. **Para ödeme kararı:** Ancak tüm adımlar geçilirse.

**Başarı kriterleri (out-of-sample, maliyetler dahil):**
- Portföy Sharpe > 1,0 (intraday, volatilite hedeflemeli)
- İşlem sayısı > 300 (istatistiksel güç için)
- Simüle edilen Faz 1 geçme olasılığı > %60
- Hiçbir tek strateji toplam kârın > %60'ını taşımamalı

---

## 4. Sistem mimarisi

```
                ┌───────────────────────────────┐
  Veri ────────▶│ data/  (indirme, temizleme,   │
 (Dukascopy,    │  saat dilimi, parquet)        │
  MT5 export)   └──────────────┬────────────────┘
                               ▼
                ┌───────────────────────────────┐
                │ features/  volatilite (HAR),  │
                │  seans/zaman, rejim (VR, HMM) │
                └──────────────┬────────────────┘
                               ▼
                ┌───────────────────────────────┐
                │ strategies/  A1, A2, A3, ...  │  ← her biri bağımsız modül
                └──────────────┬────────────────┘
                               ▼
                ┌───────────────────────────────┐
                │ portfolio/  vol-hedefleme,    │
                │  strateji ağırlıkları         │
                └──────────────┬────────────────┘
                               ▼
                ┌───────────────────────────────┐
                │ risk/  PROP RİSK YÖNETİCİSİ   │  ← mutlak veto yetkisi
                │  günlük kayıp freni, toplam   │
                │  DD koruması, haber kilidi    │
                └──────────────┬────────────────┘
                     ┌─────────┴─────────┐
                     ▼                   ▼
            backtest/ + propsim/    live/ (MT5 Python API
            (olay tabanlı motor,     veya MQL5 EA, VPS)
             Monte Carlo)
```

**Prop Risk Yöneticisi kuralları (taslak):**
- Günlük kayıp FTMO limitinin altında, ör. **%3'e ulaşınca** o gün tüm pozisyonlar kapanır ve işlem durur (floating dahil).
- Toplam drawdown %6'yı geçerse risk yarıya iner, %8'de bot durur.
- İşlem başı risk Monte Carlo ile belirlenir (muhtemelen %0,5–0,8 arası).
- Yüksek etkili haberlerden ±5 dakika önce ve sonra yeni işlem açılmaz.
- Hafta sonuna pozisyon taşınmaz.

**Teknoloji:** Python (pandas, numpy, numba, statsmodels, scikit-learn, hmmlearn) ve Parquet veri depolama. Canlı işlem için MetaTrader 5 Python paketi (Windows VPS) veya stratejinin MQL5'e aktarılması kullanılacak.

---

## 5. Veri

| Kaynak | Ne verir | Ücret | Not |
|---|---|---|---|
| **Dukascopy historical data** | Tick ve dakikalık veri: endeks CFD'leri (USA500, USATECH, DEU), XAUUSD, FX. 2003+ | Ücretsiz | **Birincil kaynak.** CFD fiyatı FTMO'nun işlem yaptığı fiyata çok yakın |
| **FTMO / MT5 geçmiş verisi** | Broker'ın kendi M1 verisi | Ücretsiz (FTMO Free Trial) | Spread ve fiyat farkı kalibrasyonu için |
| HistData.com | FX M1 | Ücretsiz | Yedek |
| Databento | CME futures tick | Ücretli (kayıtta deneme kredisi) | Futures'a geçersek |
| Forex Factory / Investing takvimi | Ekonomik takvim | Ücretsiz | Haber filtresi |

**Şu anki engel:** Bu bulut ortamının ağ politikası `datafeed.dukascopy.com` adresine erişimi engelliyor. İki çözüm var:

1. **(Önerilen)** Ortam ayarlarından (oturum başlığındaki cloud environment menüsü → Edit → Network access) **Custom** seçeneğini seç ve şu alan adlarını *Allowed domains* listesine ekle. Varsayılan paket yöneticisi listesini koru:
   - `datafeed.dukascopy.com`
   - `www.dukascopy.com`
   - `nfs.faireconomy.media` (ekonomik takvim)

   Detaylar: https://code.claude.com/docs/en/cloud-environments#network-access
   Bundan sonra veriyi otomatik indiren script'i ben yazıp çalıştırırım.
2. **(Alternatif)** Kendi bilgisayarında `npx dukascopy-node -i usatechidxusd -from 2015-01-01 -to 2025-12-31 -t m1 -f csv` komutuyla veriyi indirip repoya (veya bir depolama alanına) yükleyebilirsin.

---

## 6. Yol haritası

| Faz | İçerik | Çıktı | Tahmini süre |
|---|---|---|---|
| **0. Altyapı** | Repo yapısı, veri indirici, temizleme, Parquet | 10 yıllık M1 veri: US100, US500, GER40, XAUUSD | 1 hafta |
| **1. Volatilite çekirdeği** | Gerçekleşmiş volatilite, HAR-RV, gün içi profil | Tahmin kalitesi raporu | 1 hafta |
| **2. Backtest + propsim motoru** | Olay tabanlı backtest, maliyet modeli, FTMO kural simülatörü, Monte Carlo | Test edilmiş motor (rastgele stratejide ~%0 edge çıkmalı) | 1–2 hafta |
| **3. Hipotez taraması A1–A5** | Her hipotez protokolden geçer | Hipotez başına rapor, hayatta kalanlar listesi | 3–4 hafta |
| **4. Rejim ve meta-labeling** | Hayatta kalan stratejilere filtre | Out-of-sample iyileşme var mı? | 2 hafta |
| **5. Portföy** | Strateji birleşimi, vol-hedefleme, risk optimizasyonu | P(geçme) ve beklenen değer raporu | 1 hafta |
| **6. Kilitli test** | 2024+ verisinde tek seferlik test | Git / gitme kararı | 1 gün |
| **7. Canlı altyapı** | MT5 bağlantısı, risk yöneticisi, loglama, VPS | Demo hesapta çalışan bot | 1–2 hafta |
| **8. Forward test** | FTMO Free Trial veya demo | 4–8 haftalık canlı karşılaştırma | 1–2 ay |
| **9. Challenge** | Gerçek challenge | — | — |

Toplam: Ücretli challenge'a kadar gerçekçi olarak **3–5 ay**.

---

## 7. Riskler ve dürüst beklentiler

- Hipotezlerin **çoğu elenecek.** Bu başarısızlık değil, sistemin çalıştığının kanıtı.
- Akademik etkiler yayınlandıktan sonra zayıflayabilir (alpha decay). Bu yüzden tek strateji yerine portföy ve sürekli izleme şart.
- CFD maliyetleri edge'in büyük kısmını yiyebilir. Maliyet modeli en baştan muhafazakâr kurulacak.
- Prop firm kuralları ve firmanın kendisi değişebilir veya kapanabilir (operasyonel risk). Birden fazla firmaya yayılmak bu riski azaltır.
- **Sonunda "bu verilerde güvenilir edge yok" sonucuna varmak da mümkün.** Böyle olursa bunu kanıtla bilmek, para yakmaya devam etmekten iyidir.

---

## Kaynakça (temel)
- Gao, Han, Li, Zhou (2018). *Market Intraday Momentum.* Journal of Financial Economics.
- Zarattini, Aziz (2023). *Can Day Trading Really Be Profitable?* (ORB, SSRN).
- Corsi (2009). *A Simple Approximate Long-Memory Model of Realized Volatility* (HAR-RV).
- Moreira, Muir (2017). *Volatility-Managed Portfolios.* Journal of Finance.
- Lo, MacKinlay (1988). *Stock Market Prices Do Not Follow Random Walks* (Variance Ratio).
- López de Prado (2018). *Advances in Financial Machine Learning* (meta-labeling, triple barrier, purged CV).
- Bailey, López de Prado (2014). *The Deflated Sharpe Ratio.*
- Bailey, Borwein, López de Prado, Zhu (2016). *The Probability of Backtest Overfitting.*
