<div align="right">
  <a href="#-english">🇬🇧 English</a> • <a href="#-türkçe">🇹🇷 Türkçe</a>
</div>

# 🇬🇧 English

# 🔮 AI-Powered Daily Horoscope & Astrology Bot

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![Gemini AI](https://img.shields.io/badge/Google%20Gemini-Auto%20Flash-orange?style=for-the-badge&logo=google)
![Astronomy](https://img.shields.io/badge/VSOP87-astronomy--engine-purple?style=for-the-badge)
![Telegram](https://img.shields.io/badge/Telegram-Bot-2CA5E0?style=for-the-badge&logo=telegram)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Automated-2088FF?style=for-the-badge&logo=github-actions)

**Daily Horoscope Bot** is a modern, server-free Python & Telegram assistant that computes real astronomical birth & transit charts using **VSOP87 ephemerides (`astronomy-engine`)** and crafts tailored astrological guidance using **Google Gemini Flash**.

---

## 🚀 Key Features

- **🌌 Full Astronomical Calculation (All 10 Planets + ASC & MC):** Computes exact ecliptic longitudes (`ECT`) for Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, plus true **Ascendant** & **Midheaven (MC)** with historical `Europe/Istanbul` DST awareness.
- **♻️ Retrograde & Transit-to-Natal Aspect Engine:** Detects planetary retrogrades mathematically (`°/day < 0`) and computes exact major transit aspects (`☌ Conjunction`, `⚹ Sextile`, `□ Square`, `△ Trine`, `☍ Opposition`) to your natal chart.
- **🌕 Moon Phases, Illumination & Eclipses:** Displays live Moon phase name/percentage, upcoming New Moon & Full Moon dates, and alerts when an eclipse occurs within ±3 days.
- **🤖 Self-Healing Gemini Flash Discovery:** Queries the Gemini API for active `generateContent` Flash models (e.g., `gemini-3-flash-preview` / `gemini-2.5-flash`) with secure `x-goog-api-key` headers, retries, and an offline astronomical fallback if the AI endpoint is busy.
- **📍 All 81 Turkish Provinces + Custom Lat/Lon:** Full Turkish character folding (`İstanbul`, `Şanlıurfa`, `Afyonkarahisar`, `Mersin/İçel`, etc.) plus optional `BIRTH_LAT` / `BIRTH_LON`.
- **🕹️ Multi-Mode & Interactive Telegram Commands:** Supports `daily`, `weekly`, `monthly`, `natal`, `moon`, `compatibility`, and interactive `/burc`, `/harita`, `/ay`, `/retro`, `/haftalik`, `/uyum <Sign>` commands.
- **☁️ 100% Cloud Automated:** Runs automatically every morning at **09:00 TR (`06:00 UTC`)** via GitHub Actions with IPv4-hardened Telegram delivery and HTML tag-safe message splitting.

---

## 🛠️ Setup & Secrets

All **8 original Secrets remain 100% compatible**:

1. **Fork** this repository.
2. Go to **Settings → Secrets and variables → Actions → Repository secrets** and add:

| Secret Name | Example | Description |
| :--- | :--- | :--- |
| `BOT_TOKEN` | `123456:ABC-DEF...` | Telegram Token from [@BotFather](https://t.me/BotFather) |
| `CHAT_ID` | `123456789` | Your Telegram ID from [@userinfobot](https://t.me/userinfobot) (comma-separated for multiple) |
| `GEMINI_API_KEY` | `AIzaSyD...` | Free API key from [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `USER_NAME` | `Yusuf` | Name shown in readings |
| `BIRTH_DATE` | `2000-09-26` | Birth date (`YYYY-MM-DD` or `DD.MM.YYYY`) |
| `BIRTH_TIME` | `04:00` | Birth time (`HH:MM`) |
| `BIRTH_CITY` | `Kastamonu` | Birth city (any of 81 Turkish cities) |
| `USER_GOAL` | `Career & Software` | Focus area for daily advice |

> **Optional Repository Variables (`Settings → Variables`):** `GEMINI_MODEL`, `LANGUAGE` (`tr`/`en`), `TONE` (`dengeli`/`motive`/`mistik`/`kisa`), `SHOW_CHART_SUMMARY` (`true`/`false`), `BIRTH_LAT`, `BIRTH_LON`, `TIMEZONE` (`Europe/Istanbul`), `PARTNER_SIGN`.

3. Open the **Actions** tab, enable workflows if prompted, and trigger **Daily Horoscope Bot → Run workflow** (`daily`, `weekly`, `natal`, `moon`, `compatibility`, `chart_only`, or `commands`).

---

# 🇹🇷 Türkçe

# 🔮 Yapay Zekâ & Gerçek Astronomi Destekli Günlük Burç Botu

**Daily Horoscope Bot**, sıradan burç kalıpları yerine **VSOP87 astronomi motoru (`astronomy-engine`)** ile doğum haritanı (Natal) ve anlık gökyüzünü (Transit) saniyesine kadar hesaplayan, ardından **Google Gemini Flash** ile sana özel astrolojik rehber hazırlayıp **Telegram**'dan gönderen sunucusuz Python asistanıdır.

---

## 🚀 Öne Çıkan Özellikler

* **🌌 Tam Astronomik Hesaplama (10 Gezegen + Yükselen + MC):** Güneş, Ay, Merkür, Venüs, Mars, Jüpiter, Satürn, Uranüs, Neptün ve Plüton'un gerçek ekliptik derecelerini, **Yükselen (ASC)** ve **Tepe Noktası (MC)** burçlarını hesaplar. Doğum tarihindeki geçmiş Türkiye yaz/kış saati (`+02:00` / `+03:00`) farkını otomatik doğru alır.
* **🔭 Gerçek Transit–Natal Açıları & Retro Tespiti:** Gökyüzündeki gezegenlerin senin doğum haritana yaptığı major açıları (`Kavuşum ☌`, `Sekstil ⚹`, `Kare □`, `Üçgen △`, `Karşıt ☍`) orb sırasıyla çıkarır ve aktif **Retro (℞)** gezegenleri otomatik saptar.
* **🌕 Ay Evresi, Aydınlanma & Tutulma Takvimi:** Ay'ın o günkü evresini, aydınlanma yüzdesini, bir sonraki **Yeni Ay / Dolunay** tarihlerini ve ±3 gün içindeki **Güneş/Ay tutulmalarını** algılar.
* **🤖 Otomatik Güncel Gemini Flash Keşfi:** Eski model adları kapatılsa bile Google AI API üzerinden aktif en güncel `gemini-*-flash` modellerini otomatik bulur, API anahtarını güvenli `x-goog-api-key` başlığında taşır ve geçici kesintilerde çevrimdışı özet üretir.
* **📍 81 İl Koordinat Desteği & Özel Enlem/Boylam:** Türkiye'nin 81 ilini Türkçe karakter uyumlu olarak tanır (`İstanbul`, `Şanlıurfa`, `Afyonkarahisar`, `Mersin/İçel` dâhil). Yurt dışı için `BIRTH_LAT` / `BIRTH_LON` girilebilir.
* **💬 Etkileşimli Telegram `/` Komutları:** `/burc`, `/harita`, `/ay`, `/retro`, `/haftalik`, `/uyum Boğa` komutlarını yalnızca tanımlı `CHAT_ID` hesaplarından kabul eder (`python main.py --listen` veya `Run workflow → commands`).

---

## 🛠️ Kurulum ve Kullanım (GitHub Actions — Ücretsiz)

1. Sağ üstten projeyi **Fork** edin.
2. Telegram'da [@BotFather](https://t.me/BotFather) üzerinden botunuzu oluşturun, botunuza mutlaka **`/start`** yazın ve [@userinfobot](https://t.me/userinfobot) ile Chat ID'nizi alın. [Google AI Studio](https://aistudio.google.com/app/apikey)'dan ücretsiz Gemini API anahtarınızı oluşturun.
3. Deponuzda **Settings → Secrets and variables → Actions → Repository secrets** bölümüne **8 sırrı** ekleyin:

| Değişken İsmi (Secret) | Örnek Değer | Açıklama |
| :--- | :--- | :--- |
| `BOT_TOKEN` | `123456:ABC-DEF...` | BotFather'dan alınan Telegram Token |
| `CHAT_ID` | `123456789` | Telegram Chat ID *(birden fazla kişi için virgülle ayırabilirsiniz)* |
| `GEMINI_API_KEY` | `AIzaSyD...` | Google AI Studio API Anahtarı |
| `USER_NAME` | `Yusuf` | Hitap edilecek ad |
| `BIRTH_DATE` | `2000-09-26` | Doğum tarihi (`YYYY-AA-GG` veya `GG.AA.YYYY`) |
| `BIRTH_TIME` | `04:00` | Doğum saati (`SS:DD`) |
| `BIRTH_CITY` | `Kastamonu` | Doğum şehri *(81 ilden biri)* |
| `USER_GOAL` | `Yazılım ve Kariyer` | Yorumların odaklanacağı ana hedef |

> **İsteğe Bağlı Ek Ayarlar (`Variables`):** `GEMINI_MODEL`, `LANGUAGE` (`tr`/`en`), `TONE` (`dengeli`/`motive`/`mistik`/`kisa`), `SHOW_CHART_SUMMARY` (`true`/`false`), `BIRTH_LAT`, `BIRTH_LON`, `TIMEZONE`, `PARTNER_SIGN`.

4. **Actions** sekmesine girin, iş akışlarını aktif edin. Bot her sabah **Türkiye saatiyle 09:00'da** (`0 6 * * *` UTC) otomatik çalışır.
5. **İstediğiniz An Test Etme:** **Actions → Daily Horoscope Bot → Run workflow** menüsünden `daily`, `weekly`, `monthly`, `natal`, `moon`, `compatibility`, `chart_only` veya `commands` kipini seçip hemen çalıştırabilirsiniz.

---

## 💻 Yerel Çalıştırma & CLI

```bash
python -m venv .venv
pip install -r requirements.txt

# Sadece astronomik harita ve Ay evresi (API anahtarı gerekmez)
python main.py --chart-only

# Telegram'a atmadan tam günlük yorum önizlemesi
python main.py --mode daily --dry-run

# Partner burç uyumu veya haftalık/aylık yorum
python main.py --mode compatibility --partner Boğa --dry-run
python main.py --mode weekly --dry-run

# VPS/Docker üzerinde anlık Telegram komut dinleyici (/burc, /ay, /retro ...)
python main.py --listen
```

---

## 📞 İletişim & Destek / Contact

Hata bildirimi veya özellik önerisi için **[Issues](https://github.com/ysfsturan/Daily_Horoscope_Bot/issues)** açabilirsiniz.

<div align="center">

---

## ⚠️ Yasal Uyarı / Disclaimer

Bu bot, VSOP87 astronomik gökyüzü hesaplamaları ve yapay zeka modelleri kullanarak içerik üretmektedir. Üretilen içerikler yatırım, sağlık veya hukuk tavsiyesi niteliği taşımaz; bilgi, eğlence ve kişisel motivasyon amaçlıdır.

---

Made with ❤️ by [Yusuf Sami Turan](https://www.linkedin.com/in/yusufsamituran).

</div>
