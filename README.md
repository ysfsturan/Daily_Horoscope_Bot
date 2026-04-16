<div align="right">
  <a href="#-english">🇬🇧 English</a> • <a href="#-türkçe">🇹🇷 Türkçe</a>
</div>

# 🇬🇧 English

# 🔮 AI-Powered Daily Horoscope Bot

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Gemini AI](https://img.shields.io/badge/Google%20Gemini-3%20Flash-orange?style=for-the-badge&logo=google)
![Telegram](https://img.shields.io/badge/Telegram-Bot-2CA5E0?style=for-the-badge&logo=telegram)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Automated-2088FF?style=for-the-badge&logo=github-actions)

**Daily Horoscope Bot** is an advanced Python bot that automatically sends personalized astrological readings via Telegram every morning.

Unlike standard horoscopes, this bot calculates your birth chart and current sky positions down to the second using the **Flatlib** library. The resulting scientific data is processed by the **Google Gemini 3 Flash** model to generate a pinpoint, custom daily reading just for you.

## 🚀 Features

* **🌌 Precise Astronomical Calculation:** Mathematically calculates the real-time positions and aspects of planets using Flatlib.
* **🤖 AI-Powered Interpretation:** Astronomical data is interpreted in a human-like, motivation-focused language using the Gemini 3 Flash API.
* **📅 Special Day Awareness:** Detects your birthdays, new moons, and days of the week to generate appropriate content.
* **⚡ Full Automation:** Runs automatically every day at your specified time without server costs, thanks to GitHub Actions.
* **📍 Location-Based Analysis:** Contains latitude/longitude data for all cities in Turkey, optimizing the birth chart according to the city.

---

## ⚙️ How It Works

1. **Data Processing:** When the bot runs, it retrieves the birth data defined for `USER_NAME` and the current date. It calculates planetary interactions between the birth chart and the current sky map.
2. **Prompt Engineering:** The calculated technical data is placed into a special prompt template. This template instructs the AI to focus on "Career", "Love", or "General" topics.
3. **AI Generation:** Google's state-of-the-art model transforms the provided mathematical data into a meaningful, fluent, and motivating daily horoscope reading.
4. **Notification:** The generated long text is split to avoid Telegram API limits and delivered to the user.

---

## 🛠️ Installation and Usage

This project is designed to run entirely cloud-based.

### 1. Fork the Project 🍴
Add this project to your own GitHub account by clicking the **Fork** button in the top right corner of the page.

### 2. Configure Settings (Secrets) 🔑
You need to define the necessary API keys and parameters in your GitHub repository for the bot to work.

> **ℹ️ Where to Get the Keys?**
> * **Google Gemini API Key:** Go to [Google AI Studio](https://aistudio.google.com/app/apikey), click the "Create API Key" button, and get your free key.
> * **Telegram Bot Token:** Start a chat with [@BotFather](https://t.me/BotFather) on Telegram and use the `/newbot` command to get a token.
> * **Telegram Chat ID:** Start the [@userinfobot](https://t.me/userinfobot) bot on Telegram. Copy the "Id" value it gives you.
> * **⚠️ VERY IMPORTANT:** Find the bot you created on Telegram and send the **`/start`** command. If you don't do this, the bot cannot send you messages!

1. Go to the **Settings** tab of your forked repository.
2. Navigate to **Secrets and variables > Actions** from the left menu.
3. Click the **New repository secret** button and add the following variables in order:

| Variable Name | Value (Secret) / Example | Description |
| :--- | :--- | :--- |
| `BOT_TOKEN` | `123456:ABC-DEF...` | Telegram Token from BotFather |
| `CHAT_ID` | `123456789` | Telegram Chat ID where messages will be sent |
| `GEMINI_API_KEY` | `AIzaSyD...` | Google AI Studio API Key |
| `USER_NAME` | `Yusuf` | User's Name |
| `BIRTH_DATE` | `2000-09-26` | Birth Date (Year-Month-Day format) |
| `BIRTH_TIME` | `04:00` | Birth Time |
| `BIRTH_CITY` | `Istanbul` | Birth City |
| `USER_GOAL` | `Career and Money` | Main theme the reading will focus on |

### 3. Activate the Bot 🚀
1. Click the **Actions** tab.
2. Click the green **"I understand my workflows, go ahead and enable them"** button that appears.
3. The bot will run automatically every morning at 10:00 Turkish time.

> **Manual Test:** You can trigger the bot manually by selecting the "Daily Horoscope Bot" workflow from the left menu in the Actions tab and clicking the **Run workflow** button on the top right.

---

## 📞 Contact & Support

If you notice a bug or have a feature request regarding the project, please open an **[Issue](https://github.com/ysfsturan/Kastamonu_UBYS_Bot/issues)**.

<div align="center">

---

## ⚠️ Legal Disclaimer

This bot generates content using astrological calculations and artificial intelligence models. 
* **Accuracy:** The generated content may not yield 100% accurate results or predict the future with certainty.
* **For Entertainment Purposes:** The provided advice is not a substitute for investment, health, or legal counseling. It should be used for entertainment and motivation purposes only.
* **AI Hallucination:** Artificial intelligence may rarely produce out-of-context or inaccurate information.

---

Made with ❤️ by [Yusuf Sami Turan](https://www.linkedin.com/in/yusufsamituran).

</div>

<br><br>

---

# 🇹🇷 Türkçe

# 🔮 AI-Powered Daily Horoscope Bot

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Gemini AI](https://img.shields.io/badge/Google%20Gemini-3%20Flash-orange?style=for-the-badge&logo=google)
![Telegram](https://img.shields.io/badge/Telegram-Bot-2CA5E0?style=for-the-badge&logo=telegram)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Automated-2088FF?style=for-the-badge&logo=github-actions)

**Daily Horoscope Bot**, kişiselleştirilmiş astrolojik yorumları her sabah otomatik olarak Telegram üzerinden gönderen gelişmiş bir Python botudur. 

Standart burç yorumlarının aksine, bu bot **Flatlib** kütüphanesini kullanarak doğum haritanızı ve anlık gökyüzü konumlarını saniyesi saniyesine hesaplar. Elde edilen bilimsel veriler, **Google Gemini 3 Flash** modelinde işlenerek size özel, nokta atışı bir günlük yorum oluşturulur.

## 🚀 Özellikler

* **🌌 Hassas Astronomik Hesaplama:** Flatlib ile gezegenlerin anlık konumlarını ve açılarını matematiksel bir şekilde hesaplar.
* **🤖 Yapay Zeka Destekli Yorum:** Gemini 3 Flash API kullanılarak, astronomik veriler insan benzeri ve motivasyon odaklı bir dille yorumlanır.
* **📅 Özel Gün Farkındalığı:** Doğum günlerinizi, yeni ayları ve haftanın günlerini algılayarak buna uygun içerik üretir.
* **⚡ Tam Otomasyon:** GitHub Actions sayesinde sunucu maliyeti olmadan her gün belirlediğiniz saatte otomatik çalışır.
* **📍 Konum Bazlı Analiz:** Türkiye'nin tüm şehirleri için enlem/boylam verisine sahiptir, doğum haritasını şehre göre optimize eder.

---

## ⚙️ Nasıl Çalışır?

1. **Veri İşleme:** Bot çalıştığında, `USER_NAME` için tanımlanan doğum verilerini ve o anki tarihi alır. Doğum haritası ve o anki gökyüzü haritası arasındaki gezegen etkileşimlerini hesaplar.
2. **Prompt Mühendisliği:** Hesaplanan teknik veriler özel bir prompt şablonuna yerleştirilir. Bu şablon, AI'a "Kariyer", "Aşk" veya "Genel" odaklı yorum yapması talimatını verir.
3. **Yapay Zeka Üretimi:** Google'ın son teknoloji modeli, verilen matematiksel verileri anlamlı, akıcı ve motive edici bir günlük burç yorumuna dönüştürür.
4. **Bildirim:** Oluşturulan uzun metin, Telegram API limitlerine takılmadan parçalanır ve kullanıcıya iletilir.

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
| `BIRTH_CITY` | `İstanbul` | Doğum Şehri |
| `USER_GOAL` | `Kariyer ve Para` | Yorumun odaklanacağı ana tema |

### 3. Botu Aktif Edin 🚀
1. **Actions** sekmesine tıklayınız.
2. Karşınıza çıkan yeşil renkli **"I understand my workflows, go ahead and enable them"** butonuna basınız.
3. Bot, her sabah Türkiye saati ile saat 10'da otomatik olarak çalışacaktır.

> **Manuel Test:** Actions sekmesinde sol menüden "Daily Horoscope Bot" akışını seçip, sağ üstteki **Run workflow** butonuna tıklayarak botu manuel olarak tetikleyebilirsiniz.

---

## 📞 İletişim & Destek

Proje ile ilgili bir hata fark ederseniz veya özellik isteğiniz varsa lütfen bir **[Issue](https://github.com/ysfsturan/Kastamonu_UBYS_Bot/issues)** açın.

<div align="center">

---

## ⚠️ Yasal Uyarı

Bu bot, astrolojik hesaplamalar ve yapay zeka modelleri kullanarak içerik üretmektedir. 
* **Kesinlik:** Üretilen içerikler %100 doğru sonuçlar vermeyebilir veya geleceği kesin olarak tahmin etmez.
* **Eğlence Amaçlıdır:** Sunulan tavsiyeler yatırım, sağlık veya hukuk danışmanlığı yerine geçmez. Sadece eğlence ve motivasyon amaçlı kullanılmalıdır.
* **Yapay Zeka Halüsinasyonu:** Yapay zeka nadiren de olsa bağlam dışı veya hatalı bilgiler üretebilir.

---

Made with ❤️ by [Yusuf Sami Turan](https://www.linkedin.com/in/yusufsamituran).

</div>
