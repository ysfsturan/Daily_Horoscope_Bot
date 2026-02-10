import os
import requests
import json
from datetime import datetime
import pytz
import telebot
import time
import re
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

USER_NAME = os.environ.get("USER_NAME", "Kullanıcı")
BIRTH_DATE = os.environ.get("BIRTH_DATE", "2000-01-01") 
BIRTH_TIME = os.environ.get("BIRTH_TIME", "12:00")
BIRTH_CITY = os.environ.get("BIRTH_CITY", "Istanbul")
USER_GOAL = os.environ.get("USER_GOAL", "Genel")

LINKEDIN_URL = "https://www.linkedin.com/in/yusufsamituran"

bot = telebot.TeleBot(BOT_TOKEN)

TURKEY_CITIES = {
    "adana": (37.0000, 35.3213), "adiyaman": (37.7648, 38.2786), "afyon": (38.7507, 30.5567),
    "agri": (39.7191, 43.0503), "aksaray": (38.3687, 34.0370), "amasya": (40.6499, 35.8353),
    "ankara": (39.9334, 32.8597), "antalya": (36.8969, 30.7133), "ardahan": (41.1105, 42.7022),
    "artvin": (41.1828, 41.8183), "aydin": (37.8560, 27.8416), "balikesir": (39.6484, 27.8826),
    "bartin": (41.6344, 32.3375), "batman": (37.8812, 41.1351), "bayburt": (40.2552, 40.2249),
    "bilecik": (40.1451, 29.9799), "bingol": (38.8853, 40.498), "bitlis": (38.4006, 42.1095),
    "bolu": (40.7392, 31.6089), "burdur": (37.7203, 30.2908), "bursa": (40.1885, 29.0610),
    "canakkale": (40.1553, 26.4142), "cankiri": (40.6013, 33.6134), "corum": (40.5506, 34.9556),
    "denizli": (37.7765, 29.0864), "diyarbakir": (37.9144, 40.2306), "duzce": (40.8438, 31.1565),
    "edirne": (41.6768, 26.5659), "elazig": (38.6810, 39.2264), "erzincan": (39.7500, 39.5000),
    "erzurum": (39.9000, 41.2700), "eskisehir": (39.7767, 30.5206), "gaziantep": (37.0662, 37.3833),
    "giresun": (40.9128, 38.3895), "gumushane": (40.4600, 39.4814), "hakkari": (37.5833, 43.7333),
    "hatay": (36.4018, 36.3498), "igdir": (39.9196, 44.0404), "isparta": (37.7648, 30.5566),
    "istanbul": (41.0082, 28.9784), "izmir": (38.4237, 27.1428), "kahramanmaras": (37.5858, 36.9371),
    "karabuk": (41.2061, 32.6204), "karaman": (37.1759, 33.2287), "kars": (40.6172, 43.0974),
    "kastamonu": (41.3887, 33.7827), "kayseri": (38.7312, 35.4787), "kirikkale": (39.8468, 33.5153),
    "kirklareli": (41.7333, 27.2167), "kirsehir": (39.1425, 34.1709), "kilis": (36.7184, 37.1212),
    "kocaeli": (40.8533, 29.8815), "konya": (37.8667, 32.4833), "kutahya": (39.4167, 29.9833),
    "malatya": (38.3552, 38.3095), "manisa": (38.6191, 27.4289), "mardin": (37.3212, 40.7245),
    "mersin": (36.8000, 34.6333), "mugla": (37.2153, 28.3636), "mus": (38.9462, 41.7539),
    "nevsehir": (38.6939, 34.6857), "nigde": (37.9667, 34.6833), "ordu": (40.9839, 37.8764),
    "osmaniye": (37.0742, 36.2478), "rize": (41.0201, 40.5234), "sakarya": (40.7569, 30.3783),
    "samsun": (41.2867, 36.33), "siirt": (37.9333, 41.9500), "sinop": (42.0231, 35.1531),
    "sivas": (39.7477, 37.0179), "sanliurfa": (37.1591, 38.7969), "sirnak": (37.5164, 42.4611),
    "tekirdag": (40.9833, 27.5167), "tokat": (40.3167, 36.5500), "trabzon": (41.0028, 39.7167),
    "tunceli": (39.1079, 39.5401), "usak": (38.6823, 29.4082), "van": (38.4891, 43.4089),
    "yalova": (40.6500, 29.2667), "yozgat": (39.8181, 34.8147), "zonguldak": (41.4564, 31.7987)
}

def get_coordinates(city_name):
    clean_name = city_name.lower().replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c").strip()
    if clean_name in TURKEY_CITIES: return TURKEY_CITIES[clean_name]
    return TURKEY_CITIES["istanbul"]

def calculate_charts():
    try:
        coords = get_coordinates(BIRTH_CITY)
        lat, lon = coords
        
        date_parts = BIRTH_DATE.split("-") 
        time_parts = BIRTH_TIME.split(":") 
        natal_date = Datetime(date_parts[0] + "/" + date_parts[1] + "/" + date_parts[2], time_parts[0] + ":" + time_parts[1], '+03:00')
        pos = GeoPos(lat, lon)
        natal_chart = Chart(natal_date, pos)
        
        natal_data = {
            "Gunes": natal_chart.get(const.SUN).sign,
            "Ay": natal_chart.get(const.MOON).sign,
            "Yukselen": natal_chart.get(const.ASC).sign
        }

        tz = pytz.timezone('Europe/Istanbul')
        now = datetime.now(tz)
        transit_date = Datetime(now.strftime("%Y/%m/%d"), now.strftime("%H:%M"), '+03:00')
        transit_chart = Chart(transit_date, pos)
        
        transit_data = {
            "Gunes": transit_chart.get(const.SUN).sign,
            "Ay": transit_chart.get(const.MOON).sign,
            "Merkur": transit_chart.get(const.MERCURY).sign,
            "Venus": transit_chart.get(const.VENUS).sign,
            "Mars": transit_chart.get(const.MARS).sign,
            "Jupiter": transit_chart.get(const.JUPITER).sign,
            "Saturn": transit_chart.get(const.SATURN).sign
        }
        
        return natal_data, transit_data, None
    except Exception as e:
        return None, None, str(e)

def get_horoscope(natal, transit):
    tz = pytz.timezone('Europe/Istanbul')
    now = datetime.now(tz)
    today_str = now.strftime("%d %B %Y, %A")
    
    is_monday = now.weekday() == 0  
    is_first_of_month = now.day == 1
    birth_month = int(BIRTH_DATE.split("-")[1])
    birth_day = int(BIRTH_DATE.split("-")[2])
    is_birthday = (now.month == birth_month) and (now.day == birth_day)

    special_instruction = ""
    if is_birthday:
        special_instruction = (
            "🎉 BUGÜN KULLANICININ DOĞUM GÜNÜ! 🎂 "
            "Normal yorum yerine harika bir doğum günü mesajı ve yeni yaş vizyonu yaz."
        )
    else:
        if is_monday:
            special_instruction += "\n📅 EKSTRA GÖREV: Bugün Pazartesi, en alta '📅 HAFTALIK GENEL BAKIŞ' ekle."
        if is_first_of_month:
            special_instruction += "\n🗓️ EKSTRA GÖREV: Bugün ayın 1'i, en alta '🗓️ BU AYIN TEMASI' ekle."

    prompt = (
        f"GÖREV: {USER_NAME} için {today_str} tarihli DETAYLI ve KAPSAMLI bir astrolojik yorum yaz. Hedef: {USER_GOAL}.\n"
        f"‼️ ÇOK ÖNEMLİ KURAL: Sana verdiğim TRANSİT gezegen konumlarına (Burçlarına) SADIK KAL. Asla kafandan gezegen konumu uydurma.\n\n"
        
        f"📌 ASTRONOMİK VERİLER (GERÇEK VERİLER BUNLAR): "
        f"NATAL: Güneş {natal['Gunes']}, Ay {natal['Ay']}, Yükselen {natal['Yukselen']}. "
        f"TRANSİT: Güneş {transit['Gunes']}, Ay {transit['Ay']}, Mars {transit['Mars']}, Jüpiter {transit['Jupiter']}, Satürn {transit['Saturn']}. "
        
        f"✍️ İÇERİK ŞABLONU (Her maddeyi en az 4-5 cümle ile detaylandır):\n"
        f"1. 🌍 GENEL GÖKYÜZÜ ENERJİSİ: Bugünün genel ruh hali nedir? Hangi gezegenler baskın?\n"
        f"2. 🎓 EĞİTİM & KARİYER ({USER_GOAL}): Öğrenci/iş hayatı için somut, stratejik ve detaylı tavsiyeler ver. Jüpiter ve Merkür etkilerini kullan.\n"
        f"3. ❤️ İLİŞKİLER & SOSYAL YAŞAM: Arkadaşlar, aşk veya aile ilişkilerinde nelere dikkat etmeli? Mars ve Venüs etkileri neler?\n"
        f"4. 🚀 GÜNÜN MOTİVASYON MESAJI: Onu gaza getirecek, güçlü bir kapanış yap.\n"
        f"5. {special_instruction}\n\n"
        
        f"⚠️ FORMAT: Sadece <b>, <i> etiketleri kullan. ASLA CSS, HTML BLOKLARI veya <style> kullanma. Bol emoji kullan! ✨"
    )

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=" + GEMINI_API_KEY
    
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            text = response.json()['candidates'][0]['content']['parts'][0]['text']
            
            text = text.replace("```html", "").replace("```", "").strip()
            text = re.sub(r"<style>.*?</style>", "", text, flags=re.DOTALL)
            text = text.replace("<body>", "").replace("</body>", "")
            
            return text
        else:
            return f"API Hatası ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Bağlantı hatası: {str(e)}"

def send_long_message(chat_id, text):
    signature = f"\n\nMade with ❤️ by <a href='{LINKEDIN_URL}'>Yusuf Sami Turan</a>"
    
    full_text = text + signature

    max_length = 4000
    if len(full_text) <= max_length:
        try: bot.send_message(chat_id, full_text, parse_mode="HTML", disable_web_page_preview=True)
        except: 
            clean_text = re.sub('<[^<]+?>', '', full_text)
            bot.send_message(chat_id, clean_text)
        return

    parts = [full_text[i:i+max_length] for i in range(0, len(full_text), max_length)]
    for part in parts:
        try: bot.send_message(chat_id, part, parse_mode="HTML", disable_web_page_preview=True)
        except: 
            clean_text = re.sub('<[^<]+?>', '', part)
            bot.send_message(chat_id, clean_text)
        time.sleep(1)

def send_daily_message():
    if not BOT_TOKEN: return
    natal, transit, error = calculate_charts()
    if error:
        bot.send_message(CHAT_ID, f"⚠️ Hata: {error}")
        return
    message = get_horoscope(natal, transit)
    send_long_message(CHAT_ID, message)

if __name__ == "__main__":
    send_daily_message()
