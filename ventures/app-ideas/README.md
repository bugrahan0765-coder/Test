# Uygulama fikri bulma ve dağıtım süreci

Bu klasör, trading araştırmasından (`pfbot/`) bağımsızdır. Amaç: TikTok/Reels ile organik olarak
dağıtılabilecek tüketici uygulaması fikirlerini sistematik olarak bulmak, puanlamak, **uygulamayı
yapmadan önce** videoyla test etmek ve sadece kanıt çıkan fikri inşa etmek.

Süreç, üç farklı görüşün (içerikten fikir çıkarma / önce kitle / ürün mekaniği) iki turluk
tartışmasında ortak kabul edilen yöntemdir.

## Temel ilke

TikTok'ta tanıtılabilir fikir = **kullanılınca kendiliğinden paylaşılacak içerik üreten fikir.**
Dağıtım ürünü büyütür, kurtaramaz. Kopya ürünün paylaşımı orijinalin reklamını yapar.

## 3 haftalık döngü

1. **Topla** (3 kaynak): TikTok yorum/arama sinyalleri, mevcut uygulamaların 1-3 yıldızlı
   yorumları, kültür/pazar farkları (Kore/Japonya'dan aktarım, Türk kültürü).
2. **Puanla:** `scorecard.md` — 12/20 altı ve "3 saniyede görsel etki" = 0 olanlar elenir.
   Puan **test öncesi** `ideas.csv`'ye yazılır (sonradan değiştirilmez; puanlamanın işe yarayıp
   yaramadığını görmek için).
3. **Videoyla test et** (2-3 hafta): en iyi 3 fikir × 5 giriş = ~15 "yakında" videosu,
   fiyat gösteren bekleme listesi sayfası. Kriterler `test_protocol.md`'de.
4. **İnşa et:** sadece kriteri geçen fikir; filigran/isim paylaşılan sonuçta; ilk günden e-posta.

## Telefon dağılımı

| Telefon | Görev |
|---|---|
| 1 | Türkçe ana niş hesabı (6 ay sürdürülebilir konu, sürekli paylaşım) |
| 2 | İngilizce/global hesap |
| 3 | Fikir test hesabı ("yakında" videoları) |
| 4 | Sadece araştırma (paylaşım/etkileşim yok) |

Kurallar: her hesapta orijinal içerik, aynı video çoklu hesapta yok, hesaplar birbirine
beğeni/yorum/paylaşım yapmaz, ayrı e-posta (mümkünse ayrı SIM), VPN ile konum taklidi yok,
paylaşımdan önce 5-7 gün ısınma, yapay zeka içeriği TikTok etiketiyle belirtilir.

## Dosyalar

- `scorecard.md` — puanlama kriterleri
- `test_protocol.md` — video testi, metrikler, yap/bırak kriterleri
- `tiktok_evidence_method.md` — TikTok verisinden güvenilir kanıt toplama yöntemi (kaynak notlar `research/tiktok_scraping/`)
- `sources/` — ham fikir araştırmaları (kaynaklı)
- `ideas.csv` — tüm fikirler ve puanları
- `shortlist.md` — seçilen 3 fikir, gerekçe
- `test_plan/videos.md` — 15 video senaryosu ve takvim
- `test_plan/waitlist.md` — fiyatlı bekleme listesi formu kurulumu ve metinleri
- `test_plan/results.csv` — video sonuç takip tablosu
- `test_plan/mockups/` — videolarda kullanılacak örnek çıktı görselleri (1080×1920; kaynak HTML `src/`)
