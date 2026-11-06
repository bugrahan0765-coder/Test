# TikTok verisinden güvenilir kanıt toplama yöntemi

Kaynak notlar (İngilizce, kaynaklı, her iddia etiketli): `research/tiktok_scraping/`
- `practitioner_methods.md` — uygulama geliştiricilerin ve stüdyoların pratikte ne yaptığı
- `signal_validity.md` — hangi metrikler bilgi taşır, akademik bulgular, tuzaklar, tam protokol
- `apify_tooling_legal.md` — Apify araçları, fiyatlar, resmi alternatifler, yasal sınırlar

Bu belge onların Türkçe, uygulanabilir özetidir. Trading araştırmasındaki disiplinin aynısı:
önceden kaydet → bulma penceresi → bağımsız doğrulama penceresi → dış kaynaklarla teyit → kilitli son test.

## 1. Ana bulgu: "kanıtlanmış kazanan" TikTok'ta tek videoyla bulunmaz

1. **Tek bir videonun viral olacağını önceden tahmin etmek akademik olarak zayıf.** Tahmin ancak video
   büyümeye başladıktan sonra iyileşir (Cheng ve ark. 2014; Martin ve ark. 2016). Yani "erken" ile
   "kesin" arasında bir takas var.
2. **Tek viral video bir piyango çekilişidir.** Sosyal etki sonuçları rastgele ve yola bağımlı yapar
   (Salganik, MusicLab 2006).
3. **Büyük izlenme toplamları çoğunlukla tek büyük hesabın yayınından gelir,** kişiden kişiye yayılmadan değil
   (Goel ve ark. 2016). Bir formatın toplam izlenmesi talep değil, bir hesabın kitlesi olabilir.
4. **Bilgi taşıyan şey tekrardır:** farklı büyüklükte birçok bağımsız hesabın aynı formatla **kendi
   normalinin** üstüne çıkması ve bunun **sonraki bir zaman diliminde de** sürmesi.
5. **Etkileşim ilgiyi ölçer, ödeme isteğini değil.** Paylaşım çoğunlukla duygusal uyarılmadan gelir
   (Berger & Milkman 2012). İnsanlar "öderim" dediklerinden daha az öder (Murphy ve ark. 2005).
   **Para sorusu TikTok verisiyle değil, fiyatlı testle cevaplanır.**

Pratikten bir örnek (kendi beyanı): haftada ~500 bin izlenme alan bir otomatik slayt hesabı yalnızca
~600-700$ aylık gelir üretmiş. İzlenme ≠ talep.

## 2. Kanıt hiyerarşisi (güçlüden zayıfa)

1. Gerçekten ödenen para (kendi testiniz)
2. Fiyatlı bekleme listesine kayıt oranı (kendi testiniz)
3. Rakip uygulamaların gelir yönü + o nişte **uzun süredir yayında olan ücretli reklamlar**
   (biri bu kitleye para harcamaya devam ediyorsa, muhtemelen kazanıyor)
4. Birçok hesapta tekrar eden, **istenmeden yazılmış** "hangi uygulama / link?" yorumları
5. Birçok farklı hesapta, farklı büyüklüklerde, **sonraki dönemde de süren** sıra dışı başarı
6. Paylaşım ve kaydetme oranları
7. Tek bir viral video
8. Beğeni, ham izlenme, takipçi sayısı (sadece payda olarak kullanılır)

## 3. Metrikler: hangisi işe yarar, hangisi yanıltır

| Metrik | Ne ölçer | Nasıl kullanılır |
|---|---|---|
| **Sıra dışılık oranı** = videonun izlenmesi / hesabın **önceki** 15-20 videosunun medyanı | Hesap büyüklüğünden arındırılmış başarı | Ana ölçü. ≥3 kat = "isabet" (2x ve 5x ile duyarlılık kontrolü). Sadece önceki videolarla kıyas (geleceğe bakma hatası olmasın). |
| **Genişlik** = isabet alan farklı hesap sayısı (takipçi kademelerine göre) | Bağımsız tekrar | En önemli yapısal sinyal. Sadece büyük hesaplarda çalışıyorsa yayın etkisidir, format değil. |
| **Yoğunlaşma** = formatın izlenmelerinde en büyük hesabın payı | Tek hesaba bağımlılık | Yüksekse (~%30-40 üstü) şüpheli. |
| **İstenmemiş istek yorumları** ("hangi uygulama", "link", "iPhone'da var mı") | Kullanma isteği | Önceden yazılmış kelime listesiyle sayılır. "Link için yorum yaz" diyen videolar **hariç**. Cevapta mevcut bir uygulama adı geçiyorsa not edilir (rakip var demektir). |
| **Yeni hesap girişi / hafta** | Trend yükseliyor mu, sönüyor mu | Hızla düşüyorsa moda bitmiştir. |
| **Kaydetme oranı** | "Sonra döneceğim" niyeti | Faydalı ama tarif/eğitim içeriğinde doğal olarak yüksektir — aynı hesapların kendi ortalamasıyla kıyaslanır. |
| **Paylaşım oranı** | Yayılma potansiyeli | Uygulamanın çıktısı yayılır mı sorusu için iyi; talep sinyali değil. |
| **Uzun süreli ücretli reklam** | Birinin bu kitleden para kazandığı | Ödeme isteği yönünde en iyi TikTok içi kanıt; aynı zamanda rekabet uyarısı. |
| İzlenme tamamlama oranı | Girişin kalitesi | **Başkalarının videolarında görülemez.** Sadece kendi videolarınızda kullanılır. |
| Beğeni, ham izlenme, takipçi | Maruz kalma | En kolay sahte üretilen veriler. Başarı ölçütü **olamaz**. |

## 4. Tuzaklar ve önlemleri

| Tuzak | Önlem |
|---|---|
| **Hayatta kalma yanılgısı:** sadece kazananları görmek | Formatı kullanan her hesabın **tüm** video geçmişini çek; başarısız denemeler de sayılsın. |
| **Görünür olan zaten doymuştur** | Yeni hesap girişi eğrisine bak; trendin zirvesinden sonra girmek kopya yarışıdır. Fikirde fark (kültür, dil, niş) şart. |
| **Birikimli izlenme:** eski video doğal olarak daha çok izlenir | Videoları aynı yaşta karşılaştır; geçmiş verilerde en az 2-3 haftalık videoları kullan (izlenme büyük ölçüde oturmuş olur). |
| **Sahte etkileşim / botlar** | Hesabın kendi dağılımının çok dışındaki videoları işaretle; sonuç onlar çıkarılınca da geçerli olmalı. |
| **Çoklu karşılaştırma:** binlerce video taranınca bir şey mutlaka "çıkar" | Denenen her format bir kayıt defterine yazılır (trading'deki TrialRegistry gibi); Benjamini-Hochberg düzeltmesi; en fazla 3-5 format sonraki aşamaya geçer. |
| **Arama sonuçları yanlı örneklemdir** | Arama sonuçları sadece **bulmak** için; oranlar hesapların tam zaman çizelgelerinden hesaplanır. |
| **İlgi ≠ ödeme** | Son karar her zaman fiyatlı testte. |
| **Küçük örnek** | 5 girişin 4'ünün hesap ortalamasını geçmesi tesadüfen %19 olasılıkla olur. Karar tek ölçüte değil, birkaç zayıf ölçütün **birlikte** sağlanmasına dayanır. |

## 5. Protokol (fikir başına)

### Adım 0 — Önceden kayıt (veri çekmeden önce, commit edilir)
`research/hypotheses/T<no>_<fikir>.md`:
- Format tanımı (başka biri de aynı videoları seçebilecek kadar net)
- Sabit arama listesi: 10-20 anahtar kelime / hashtag / ses, dil ve ülke bazında
- Zaman pencereleri, isabet tanımı (≥3x), istek-yorumu kelime listesi, hariç tutulanlar
- Geçme/kalma kuralları ve hangi 2 dış kaynağa bakılacağı
- `scorecard.md` puanı (zaten testten önce yazılmış)

### Adım 1 — Bulma penceresi (W1) ve doğrulama penceresi (W2), geçmiş tarihli
Videoların paylaşım tarihi kayıtlı olduğu için 8 hafta beklemek gerekmez:
- **Normal fikirler:** W1 = 11-7 hafta önce paylaşılan videolar, W2 = 7-3 hafta önce paylaşılanlar.
  (Son 3 haftanın videoları hariç: izlenmeleri henüz oturmadı.)
- **Mevsimsel fikirler:** geçen sezon. Örn. Grup Karnesi için W1 = 1-20 Aralık 2025, W2 = 21 Aralık 2025 -
  15 Ocak 2026.
- W1'de format bulunur, eşikler **dondurulur**, sonra W2'ye bakılır. W2'de **yeni hesapların** da isabet
  alması gerekir.
- Sınırlama: silinen videolar görünmez, algoritma o dönemden beri değişmiş olabilir → bu yüzden son karar
  yine kendi testiniz.

### Adım 2 — Hesaplama (format düzeyinde, hesap = küme)
Bir hesabın 20 videosu 20 bağımsız tekrar sayılmaz. Güven aralıkları hesap bazında bootstrap ile.
Çıktı: isabet oranı farkı, genişlik (takipçi kademelerine göre), yoğunlaşma, istek-yorumu oranı,
yeni hesap girişi eğrisi.

### Adım 3 — Dış kaynaklarla teyit (en az 2'si aynı yönü göstermeli)
- **Google Trends:** 2-5 terim + 2 kontrol terimi, haftalık, farklı günlerde birkaç kez çekilip ortalaması.
- **Uygulama mağazaları:** yorumlarda adı geçen veya anahtar kelimede çıkan uygulamaların sıralama yönü,
  yorum artış hızı, 1-3 yıldızlı yorumlardaki boşluk (Apple'ın ücretsiz yorum akışı; Google Play).
- **Reklam kütüphaneleri:** TikTok Ad Library / Creative Center Top Ads, Meta Ad Library: bu nişte uzun
  süredir yayında reklam var mı?
- Önceden seçilen bir kaynak ters yönü gösterirse yazılı açıklama gerekir, yoksa hipotez elenir.

### Adım 4 — Kilitli son test: kendi "yakında" videolarınız + fiyatlı bekleme listesi
`test_protocol.md`. **Ana ölçü: link tıklayanlar içinde fiyatı görüp kayıt olanların oranı** (video sayısı
değil ziyaretçi sayısı kadar bağımsız deneme içerir, algoritma şansından daha az etkilenir).

### Adım 5 — Kalibrasyon
Her döngüden sonra: hangi TikTok metrikleri kendi testinizin sonucunu gerçekten tahmin etti? Eşikler
sadece döngüler arasında ve kayıt altına alınarak değiştirilir.

## 6. Araçlar, maliyet ve yasal çerçeve

| Kaynak | Ne verir | Maliyet (listelenen, değişebilir) |
|---|---|---|
| Apify `clockworks/tiktok-scraper` | Arama/hashtag/profil videoları: izlenme, beğeni, paylaşım, kaydetme, yorum sayısı, tarih, takipçi | ~1,7-5 $ / 1.000 sonuç (sayfalar çelişiyor, yüksek olanla bütçelenir) |
| Apify TikTok yorum aracı | Yorum metinleri | ~0,5-5 $ / 1.000 |
| Apify otomatik tamamlama aracı | Arama önerileri (hacim yok) | ~0,2 $ / 1.000 |
| Apple yorum akışı (RSS) | Ülke bazında son ~500 yorum | Ücretsiz, script ile |
| Google Play yorum aracı/kütüphanesi | Yorumlar | ~0,1 $ / 1.000 veya ücretsiz kütüphane |
| TikTok Creative Center, Ad Library | Trendler, en iyi reklamlar, reklam tarihleri | Ücretsiz, tarayıcıda (elle) |
| TikTok Research API | Resmi veri | **Uygun değil:** sadece akademik/kâr amacı gütmeyen araştırmacılar |

Apify planları: ücretsiz plan ayda 5 $ kredi; Starter 19 $/ay. 3 fikir için tahmini tam tur
(~10 bin video + yorum örneklemi): **kabaca 20-40 $**. Önce 2-5 $'lık bir pilot çalıştırılır.

**Yasal durum (dürüstçe):**
- TikTok'un kullanım koşulları otomatik veri toplamayı **yasaklıyor**. Herkese açık verinin giriş
  yapılmadan toplanması bazı mahkeme kararlarında (Meta - Bright Data, 2024) sözleşme ihlali sayılmadı,
  ama bu karar TikTok'u bağlamaz. **Gri alan; karar sizin.**
- Kullanıcı adları ve yorum metinleri KVKK/GDPR kapsamında kişisel veridir.

**Uyulacak kurallar (en düşük risk):**
- Giriş yapmadan toplama; hiçbir TikTok hesabı kullanılmaz, kimseyle iletişime geçilmez.
- Düşük hacim; sadece araştırma için gereken kadar.
- Toplama anında anonimleştirme: kullanıcı adı, profil fotoğrafı, biyografi saklanmaz (hesaplar sadece
  rastgele bir kimlikle ayırt edilir). Yorumlardan sadece kelime eşleşmesi sayıları tutulur; ham veri
  en geç 30 günde silinir ve repoya **asla** commit edilmez.
- İçerik kopyalanmaz veya yeniden yayınlanmaz; sadece sayılar ve formatlar incelenir.

## 7. Mevcut 3 fikre uygulama (anahtar gelince)

| Fikir | Örnek arama listesi (önceden kayıtta dondurulacak) | Pencereler |
|---|---|---|
| Dizi Sahnesi | "türk dizisi olsaydı", "dizi versiyonu", "türk dizisi gibi", "if my life was a turkish drama", "turkish drama be like" | Normal (W1: 11-7 hafta önce, W2: 7-3 hafta önce) |
| Göz Kararı | "ninemin tarifi", "anneannemin tarifi", "göz kararı tarif", "grandma recipe", "nonna recipe" | Normal |
| Grup Karnesi | "whatsapp wrapped", "chat wrapped", "grup özeti", "whatsapp istatistik", "yıl sonu arkadaş grubu" | Geçen sezon (Aralık 2025 - Ocak 2026) |

Bu analiz 14 Kasım'daki video testinin **yerini almaz**; testten önce veya testle paralel çalışır.
Sonuç: hangi fikir güçlü dış kanıta sahip, hangisi zayıf — gerekirse yedekteki bir fikirle değişim.
Test öncesi puanlar (`ideas.csv`) değişmez; TikTok kanıt sonuçları ayrı dosyaya yazılır.
