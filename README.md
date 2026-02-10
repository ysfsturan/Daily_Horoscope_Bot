# 🔮 AI-Powered Daily Horoscope Bot

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Gemini AI](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-orange?style=for-the-badge&logo=google)
![Telegram](https://img.shields.io/badge/Telegram-Bot-2CA5E0?style=for-the-badge&logo=telegram)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Automated-2088FF?style=for-the-badge&logo=github-actions)

**Daily Horoscope Bot**, kişiselleştirilmiş astrolojik yorumları her sabah otomatik olarak Telegram üzerinden gönderen gelişmiş bir Python botudur. 

Standart burç yorumlarının aksine, bu bot **Flatlib** kütüphanesini kullanarak doğum haritanızı ve anlık gökyüzü konumlarını saniyesi saniyesine hesaplar. Elde edilen bilimsel veriler, **Google Gemini 2.5 Flash** modelinde işlenerek size özel, nokta atışı bir günlük yorum oluşturulur.

## 🚀 Özellikler

* **🌌 Hassas Astronomik Hesaplama:** Flatlib ile gezegenlerin anlık konumlarını ve açılarını matematiksel bir şekilde hesaplar.
* **🤖 Yapay Zeka Destekli Yorum:** Gemini 2.5 Flash API kullanılarak, astronomik veriler insan benzeri ve motivasyon odaklı bir dille yorumlanır.
* **📅 Özel Gün Farkındalığı:** Doğum günlerinizi, yeni ayları ve haftanın günlerini algılayarak buna uygun içerik üretir.
* **⚡ Tam Otomasyon:** GitHub Actions sayesinde sunucu maliyeti olmadan her gün belirlediğiniz saatte otomatik çalışır.
* **📍 Konum Bazlı Analiz:** Türkiye'nin tüm şehirleri için enlem/boylam verisine sahiptir, doğum haritasını şehre göre optimize eder.

---

## ⚙️ Nasıl Çalışır?

1.  **Veri İşleme:** Bot çalıştığında, `USER_NAME` için tanımlanan doğum verilerini ve o anki tarihi alır. Doğum haritası ve o anki gökyüzü haritası arasındaki gezegen etkileşimlerini hesaplar.
2.  **Prompt Mühendisliği:** Hesaplanan teknik veriler özel bir prompt şablonuna yerleştirilir. Bu şablon, AI'a "Kariyer", "Aşk" veya "Genel" odaklı yorum yapması talimatını verir.
3.  **Yapay Zeka Üretimi:** Google'ın son teknoloji modeli, verilen matematiksel verileri anlamlı, akıcı ve motive edici bir günlük burç yorumuna dönüştürür.
4.  **Bildirim:** Oluşturulan uzun metin, Telegram API limitlerine takılmadan parçalanır ve kullanıcıya iletilir.

---

## 🛠️ Kurulum ve Kullanım

Bu proje, tamamen bulut tabanlı çalışacak şekilde tasarlanmıştır.

### 1. Projeyi Forklayın 🍴
Sayfanın sağ üst köşesindeki **Fork** butonuna tıklayarak bu projeyi kendi GitHub hesabınıza ekleyiniz.

### 2. Ayarları Yapılandırın (Secrets) 🔑
Botun çalışabilmesi için gerekli API anahtarlarını ve parametreleri GitHub deponuza tanımlamanız gerekmektedir.

> **ℹ️ Anahtarlar Nereden Alınır?**
> * **Google Gemini API Key:** [Google AI Studio](https://aistudio.google.com/app/apikey) adresine giderek "Create API Key" butonuna basınız ve ücretsiz anahtarınızı alınız.
> * **Telegram Bot Token:** Telegram'da [@BotFather](https://t.me/BotFather) ile sohbet başlatıp `/newbot` komutunu kullanarak token alabilirsiniz.
> * **Telegram Chat ID:** Telegram'da [@userinfobot](https://t.me/userinfobot) botunu başlatınız. Size vereceği "Id" değerini kopyalayınız.
> * **⚠️ ÇOK ÖNEMLİ:** Kendi oluşturduğunuz botu Telegram'da bulun ve **`/start`** komutunu gönderin. Bunu yapmazsanız bot size mesaj atamaz!

1. Forkladığınız deponun **Settings** sekmesine gidiniz.
2. Sol menüden **Secrets and variables > Actions** yolunu izleyiniz.
3. **New repository secret** butonuna tıklayarak aşağıdaki değişkenleri sırasıyla ekleyiniz:

| Değişken İsmi (Name) | Değer (Secret) / Örnek | Açıklama |
| :--- | :--- | :--- |
| `BOT_TOKEN` | `123456:ABC-DEF...` | BotFather'dan alınan Telegram Token |
| `CHAT_ID` | `123456789` | Mesajın gönderileceği Telegram Chat ID |
| `GEMINI_API_KEY` | `AIzaSyD...` | Google AI Studio API Anahtarı |
| `USER_NAME` | `Yusuf` | Kullanıcının Adı |
| `BIRTH_DATE` | `2000-09-26` | Doğum Tarihi (Yıl-Ay-Gün formatında) |
| `BIRTH_TIME` | `04:00` | Doğum Saati |
| `BIRTH_CITY` | `İstanbul` | Doğum Şehri (Türkçe karakter desteklenir) |
| `USER_GOAL` | `Kariyer ve Para` | Yorumun odaklanacağı ana tema |

### 3. Botu Aktif Edin 🚀
1. **Actions** sekmesine tıklayınız.
2. Karşınıza çıkan yeşil renkli **"I understand my workflows, go ahead and enable them"** butonuna basınız.
3. Bot, her sabah Türkiye saati ile saat 9'da otomatik olarak çalışacaktır.

> **Manuel Test:** Actions sekmesinde sol menüden "Daily Horoscope Bot" akışını seçip, sağ üstteki **Run workflow** butonuna tıklayarak botu manuel olarak tetikleyebilirsiniz.

## ⚠️ Yasal Uyarı

Bu bot, astrolojik hesaplamalar ve yapay zeka modelleri kullanarak içerik üretmektedir. 
* **Kesinlik:** Üretilen içerikler %100 doğru sonuçlar vermeyebilir veya geleceği kesin olarak tahmin etmez.
* **Eğlence Amaçlıdır:** Sunulan tavsiyeler yatırım, sağlık veya hukuk danışmanlığı yerine geçmez. Sadece eğlence ve motivasyon amaçlı kullanılmalıdır.
* **Yapay Zeka Halüsinasyonu:** Yapay zeka nadiren de olsa bağlam dışı veya hatalı bilgiler üretebilir.

---

*Made with ❤️ by [Yusuf Sami Turan](https://www.linkedin.com/in/yusufsamituran).*
