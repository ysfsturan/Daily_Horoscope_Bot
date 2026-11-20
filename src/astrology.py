"""Saf Python VSOP87 astronomi motoru (astronomy-engine) ile doğum haritası ve transit hesaplama."""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo

import astronomy

from .config import Config
from .models import Aspect, AstroReport, ChartSnapshot, MoonPhaseInfo, PlanetPosition

# 81 il merkezi koordinatları (enlem, boylam)
TURKEY_CITIES: dict[str, tuple[float, float]] = {
    "adana": (37.0000, 35.3213),
    "adiyaman": (37.7648, 38.2786),
    "afyon": (38.7507, 30.5567),
    "afyonkarahisar": (38.7507, 30.5567),
    "agri": (39.7191, 43.0503),
    "aksaray": (38.3687, 34.0370),
    "amasya": (40.6499, 35.8353),
    "ankara": (39.9334, 32.8597),
    "antalya": (36.8969, 30.7133),
    "ardahan": (41.1105, 42.7022),
    "artvin": (41.1828, 41.8183),
    "aydin": (37.8560, 27.8416),
    "balikesir": (39.6484, 27.8826),
    "bartin": (41.6344, 32.3375),
    "batman": (37.8812, 41.1351),
    "bayburt": (40.2552, 40.2249),
    "bilecik": (40.1451, 29.9799),
    "bingol": (38.8853, 40.4980),
    "bitlis": (38.4006, 42.1095),
    "bolu": (40.7392, 31.6089),
    "burdur": (37.7203, 30.2908),
    "bursa": (40.1885, 29.0610),
    "canakkale": (40.1553, 26.4142),
    "cankiri": (40.6013, 33.6134),
    "corum": (40.5506, 34.9556),
    "denizli": (37.7765, 29.0864),
    "diyarbakir": (37.9144, 40.2306),
    "duzce": (40.8438, 31.1565),
    "edirne": (41.6768, 26.5659),
    "elazig": (38.6810, 39.2264),
    "erzincan": (39.7500, 39.5000),
    "erzurum": (39.9000, 41.2700),
    "eskisehir": (39.7767, 30.5206),
    "gaziantep": (37.0662, 37.3833),
    "antep": (37.0662, 37.3833),
    "giresun": (40.9128, 38.3895),
    "gumushane": (40.4600, 39.4814),
    "hakkari": (37.5833, 43.7333),
    "hatay": (36.2028, 36.1604),
    "antakya": (36.2028, 36.1604),
    "igdir": (39.9196, 44.0404),
    "isparta": (37.7648, 30.5566),
    "istanbul": (41.0082, 28.9784),
    "izmir": (38.4237, 27.1428),
    "kahramanmaras": (37.5858, 36.9371),
    "maras": (37.5858, 36.9371),
    "karabuk": (41.2061, 32.6204),
    "karaman": (37.1759, 33.2287),
    "kars": (40.6172, 43.0974),
    "kastamonu": (41.3887, 33.7827),
    "kayseri": (38.7312, 35.4787),
    "kirikkale": (39.8468, 33.5153),
    "kirklareli": (41.7333, 27.2167),
    "kirsehir": (39.1425, 34.1709),
    "kilis": (36.7184, 37.1212),
    "kocaeli": (40.8533, 29.8815),
    "izmit": (40.8533, 29.8815),
    "konya": (37.8667, 32.4833),
    "kutahya": (39.4167, 29.9833),
    "malatya": (38.3552, 38.3095),
    "manisa": (38.6191, 27.4289),
    "mardin": (37.3212, 40.7245),
    "mersin": (36.8000, 34.6333),
    "icel": (36.8000, 34.6333),
    "mugla": (37.2153, 28.3636),
    "mus": (38.9462, 41.7539),
    "nevsehir": (38.6939, 34.6857),
    "nigde": (37.9667, 34.6833),
    "ordu": (40.9839, 37.8764),
    "osmaniye": (37.0742, 36.2478),
    "rize": (41.0201, 40.5234),
    "sakarya": (40.7569, 30.3783),
    "adapazari": (40.7569, 30.3783),
    "samsun": (41.2867, 36.3300),
    "siirt": (37.9333, 41.9500),
    "sinop": (42.0231, 35.1531),
    "sivas": (39.7477, 37.0179),
    "sanliurfa": (37.1591, 38.7969),
    "urfa": (37.1591, 38.7969),
    "sirnak": (37.5164, 42.4611),
    "tekirdag": (40.9833, 27.5167),
    "tokat": (40.3167, 36.5500),
    "trabzon": (41.0028, 39.7167),
    "tunceli": (39.1079, 39.5401),
    "usak": (38.6823, 29.4082),
    "van": (38.4891, 43.4089),
    "yalova": (40.6500, 29.2667),
    "yozgat": (39.8181, 34.8147),
    "zonguldak": (41.4564, 31.7987),
}

# (sign_tr, sign_en, symbol, element_tr, element_en)
ZODIAC_SIGNS: tuple[tuple[str, str, str, str, str], ...] = (
    ("Koç", "Aries", "♈", "Ateş", "Fire"),
    ("Boğa", "Taurus", "♉", "Toprak", "Earth"),
    ("İkizler", "Gemini", "♊", "Hava", "Air"),
    ("Yengeç", "Cancer", "♋", "Su", "Water"),
    ("Aslan", "Leo", "♌", "Ateş", "Fire"),
    ("Başak", "Virgo", "♍", "Toprak", "Earth"),
    ("Terazi", "Libra", "♎", "Hava", "Air"),
    ("Akrep", "Scorpio", "♏", "Su", "Water"),
    ("Yay", "Sagittarius", "♐", "Ateş", "Fire"),
    ("Oğlak", "Capricorn", "♑", "Toprak", "Earth"),
    ("Kova", "Aquarius", "♒", "Hava", "Air"),
    ("Balık", "Pisces", "♓", "Su", "Water"),
)

# (key, name_tr, name_en, body_or_None)
PLANET_DEFS: tuple[tuple[str, str, str, astronomy.Body], ...] = (
    ("sun", "Güneş", "Sun", astronomy.Body.Sun),
    ("moon", "Ay", "Moon", astronomy.Body.Moon),
    ("mercury", "Merkür", "Mercury", astronomy.Body.Mercury),
    ("venus", "Venüs", "Venus", astronomy.Body.Venus),
    ("mars", "Mars", "Mars", astronomy.Body.Mars),
    ("jupiter", "Jüpiter", "Jupiter", astronomy.Body.Jupiter),
    ("saturn", "Satürn", "Saturn", astronomy.Body.Saturn),
    ("uranus", "Uranüs", "Uranus", astronomy.Body.Uranus),
    ("neptune", "Neptün", "Neptune", astronomy.Body.Neptune),
    ("pluto", "Plüton", "Pluto", astronomy.Body.Pluto),
)

# (key, name_tr, name_en, symbol, angle, max_orb, nature)
MAJOR_ASPECTS: tuple[tuple[str, str, str, str, int, float, str], ...] = (
    ("conjunction", "Kavuşum", "Conjunction", "☌", 0, 6.0, "güçlü"),
    ("sextile", "Sekstil", "Sextile", "⚹", 60, 4.0, "harmonik"),
    ("square", "Kare", "Square", "□", 90, 5.5, "dinamik"),
    ("trine", "Üçgen", "Trine", "△", 120, 5.5, "harmonik"),
    ("opposition", "Karşıt", "Opposition", "☍", 180, 6.0, "dinamik"),
)

TR_MONTHS = (
    "Ocak",
    "Şubat",
    "Mart",
    "Nisan",
    "Mayıs",
    "Haziran",
    "Temmuz",
    "Ağustos",
    "Eylül",
    "Ekim",
    "Kasım",
    "Aralık",
)
TR_WEEKDAYS = (
    "Pazartesi",
    "Salı",
    "Çarşamba",
    "Perşembe",
    "Cuma",
    "Cumartesi",
    "Pazar",
)
EN_MONTHS = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)
EN_WEEKDAYS = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)


def normalize_tr_ascii(text: str) -> str:
    """Türkçe büyük/küçük harf (İ/ı) ve şapkalı karakterleri güvenli biçimde sadeleştirir."""
    folded = text.replace("İ", "i").replace("I", "i").replace("\u0307", "").lower()
    trans = str.maketrans(
        {
            "ı": "i",
            "ç": "c",
            "ğ": "g",
            "ö": "o",
            "ş": "s",
            "ü": "u",
            "â": "a",
            "î": "i",
            "û": "u",
        }
    )
    return " ".join(folded.translate(trans).split())


def resolve_coordinates(
    city_name: str,
    lat_override: Optional[float] = None,
    lon_override: Optional[float] = None,
) -> tuple[float, float]:
    """Şehir adı veya özel enlem/boylam ayarından koordinatları döndürür."""
    if lat_override is not None and lon_override is not None:
        return lat_override, lon_override
    clean = normalize_tr_ascii(city_name)
    if clean in TURKEY_CITIES:
        return TURKEY_CITIES[clean]
    return TURKEY_CITIES["istanbul"]


def format_date_localized(dt: datetime, lang: str = "tr") -> str:
    """Yerel ayar bağımsız Türkçe veya İngilizce tarih metni üretir."""
    if lang == "en":
        return f"{dt.day} {EN_MONTHS[dt.month - 1]} {dt.year}, {EN_WEEKDAYS[dt.weekday()]}"
    return f"{dt.day} {TR_MONTHS[dt.month - 1]} {dt.year}, {TR_WEEKDAYS[dt.weekday()]}"


def to_astro_time(dt_local: datetime) -> astronomy.Time:
    """Yerel saat dilimine sahip datetime nesnesini UTC astronomy.Time'a dönüştürür."""
    dt_utc = dt_local.astimezone(timezone.utc)
    sec_frac = dt_utc.second + (dt_utc.microsecond / 1_000_000.0)
    return astronomy.Time.Make(
        dt_utc.year,
        dt_utc.month,
        dt_utc.day,
        dt_utc.hour,
        dt_utc.minute,
        sec_frac,
    )


def _astro_time_to_local(astro_t: astronomy.Time, tz: ZoneInfo) -> datetime:
    utc_dt = astro_t.Utc()
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    return utc_dt.astimezone(tz)


def _wrap_diff_deg(a: float, b: float) -> float:
    """a - b açı farkını (-180, 180] aralığına indirger."""
    return ((a - b + 180.0) % 360.0) - 180.0


def _longitude_to_position(
    key: str,
    name_tr: str,
    name_en: str,
    lon_deg: float,
    retrograde: bool = False,
    speed: float = 0.0,
) -> PlanetPosition:
    lon = lon_deg % 360.0
    sign_idx = int(lon // 30.0) % 12
    deg_in_sign = lon - (sign_idx * 30.0)
    whole_deg = int(deg_in_sign)
    minutes = int(round((deg_in_sign - whole_deg) * 60.0))
    if minutes >= 60:
        minutes = 0
        whole_deg += 1
        if whole_deg >= 30:
            whole_deg = 0
            sign_idx = (sign_idx + 1) % 12
    sign_tr, sign_en, symbol, _, _ = ZODIAC_SIGNS[sign_idx]
    return PlanetPosition(
        key=key,
        name_tr=name_tr,
        name_en=name_en,
        longitude=round(lon, 4),
        sign_index=sign_idx,
        sign_tr=sign_tr,
        sign_en=sign_en,
        sign_symbol=symbol,
        degree=whole_deg,
        minute=minutes,
        retrograde=retrograde,
        speed_deg_per_day=round(speed, 4),
    )


def _ecliptic_lon_of_date(body: astronomy.Body, t: astronomy.Time) -> float:
    """True Ecliptic of Date (ECT) üzerinde yermerkezli gezegen boylamını (derece) hesaplar."""
    if body == astronomy.Body.Sun:
        return astronomy.SunPosition(t).elon % 360.0
    if body == astronomy.Body.Moon:
        return astronomy.EclipticGeoMoon(t).lon % 360.0
    vec_eqj = astronomy.GeoVector(body, t, True)
    rot = astronomy.Rotation_EQJ_ECT(t)
    vec_ect = astronomy.RotateVector(rot, vec_eqj)
    return astronomy.Ecliptic(vec_ect).elon % 360.0


def _true_obliquity_rad(t: astronomy.Time) -> float:
    """Tarihin gerçek ekliptik eğikliğini (nutasyon dahil) radyan olarak hesaplar."""
    rot = astronomy.Rotation_ECT_EQD(t)
    north_pole_eqd = astronomy.RotateVector(rot, astronomy.Vector(0.0, 0.0, 1.0, t))
    cos_eps = max(-1.0, min(1.0, north_pole_eqd.z))
    return math.acos(cos_eps)


def compute_asc_mc(
    t: astronomy.Time, latitude_deg: float, longitude_deg: float
) -> tuple[float, Optional[float]]:
    """Doğum/transit anı için gerçek MC (Tepe Noktası) ve Yükselen (ASC) boylamını hesaplar."""
    eps = _true_obliquity_rad(t)
    lst_deg = (astronomy.SiderealTime(t) * 15.0 + longitude_deg) % 360.0
    ramc = math.radians(lst_deg)
    lat = math.radians(latitude_deg)

    mc_rad = math.atan2(math.sin(ramc), math.cos(ramc) * math.cos(eps))
    mc_deg = math.degrees(mc_rad) % 360.0

    # Kutup daireleri (|lat| >= ~66.5°) dışında yükselen noktası kesin tanımlıdır
    if abs(latitude_deg) >= 66.0:
        return mc_deg, None

    asc_y = math.cos(ramc)
    asc_x = -((math.sin(ramc) * math.cos(eps)) + (math.tan(lat) * math.sin(eps)))
    asc_deg = math.degrees(math.atan2(asc_y, asc_x)) % 360.0
    if not (0.0 < ((asc_deg - mc_deg) % 360.0) < 180.0):
        asc_deg = (asc_deg + 180.0) % 360.0
    return mc_deg, asc_deg


def build_chart_snapshot(
    moment_local: datetime,
    latitude: float,
    longitude: float,
    *,
    include_retrograde: bool = True,
) -> ChartSnapshot:
    """Belirli bir yerel an ve koordinat için eksiksiz astrolojik harita oluşturur."""
    t = to_astro_time(moment_local)
    t_prev = to_astro_time(moment_local - timedelta(hours=6))
    t_next = to_astro_time(moment_local + timedelta(hours=6))

    planets: dict[str, PlanetPosition] = {}
    for key, name_tr, name_en, body in PLANET_DEFS:
        lon = _ecliptic_lon_of_date(body, t)
        speed = 0.0
        retro = False
        if include_retrograde:
            lon_before = _ecliptic_lon_of_date(body, t_prev)
            lon_after = _ecliptic_lon_of_date(body, t_next)
            speed = _wrap_diff_deg(lon_after, lon_before) * 2.0  # derece / gün
            if key not in {"sun", "moon"} and speed < 0.0:
                retro = True
        planets[key] = _longitude_to_position(
            key=key,
            name_tr=name_tr,
            name_en=name_en,
            lon_deg=lon,
            retrograde=retro,
            speed=speed,
        )

    mc_deg, asc_deg = compute_asc_mc(t, latitude, longitude)
    mc_pos = _longitude_to_position("mc", "Tepe Noktası (MC)", "Midheaven (MC)", mc_deg)
    asc_pos = (
        _longitude_to_position("asc", "Yükselen", "Ascendant", asc_deg)
        if asc_deg is not None
        else None
    )

    elem_counts = {"Ateş": 0, "Toprak": 0, "Hava": 0, "Su": 0}
    for pos in planets.values():
        elem_tr = ZODIAC_SIGNS[pos.sign_index][3]
        elem_counts[elem_tr] = elem_counts.get(elem_tr, 0) + 1

    return ChartSnapshot(
        moment_local=moment_local,
        latitude=latitude,
        longitude=longitude,
        planets=planets,
        ascendant=asc_pos,
        midheaven=mc_pos,
        element_counts=elem_counts,
    )


def _describe_moon_phase(angle_deg: float) -> tuple[str, str, str, str]:
    a = angle_deg % 360.0
    if a < 22.5 or a >= 337.5:
        return ("new_moon", "Yeni Ay", "New Moon", "🌑")
    if a < 67.5:
        return ("waxing_crescent", "Hilal (Büyüyen)", "Waxing Crescent", "🌒")
    if a < 112.5:
        return ("first_quarter", "İlk Dördün", "First Quarter", "🌓")
    if a < 157.5:
        return ("waxing_gibbous", "Şişkin Ay (Büyüyen)", "Waxing Gibbous", "🌔")
    if a < 202.5:
        return ("full_moon", "Dolunay", "Full Moon", "🌕")
    if a < 247.5:
        return ("waning_gibbous", "Şişkin Ay (Küçülen)", "Waning Gibbous", "🌖")
    if a < 292.5:
        return ("last_quarter", "Son Dördün", "Last Quarter", "🌗")
    return ("waning_crescent", "Hilal (Küçülen)", "Waning Crescent", "🌘")


def compute_moon_info(moment_local: datetime, tz: ZoneInfo) -> MoonPhaseInfo:
    """Ay evresi, aydınlanma %, yaklaşan Yeni Ay / Dolunay ve ±3 günlük tutulmaları hesaplar."""
    t_now = to_astro_time(moment_local)
    angle = astronomy.MoonPhase(t_now) % 360.0
    illum_pct = round(astronomy.Illumination(astronomy.Body.Moon, t_now).phase_fraction * 100.0, 1)
    phase_key, name_tr, name_en, emoji = _describe_moon_phase(angle)

    next_new_ev = astronomy.SearchMoonPhase(0.0, t_now, 32)
    next_full_ev = astronomy.SearchMoonPhase(180.0, t_now, 32)
    next_new_local = _astro_time_to_local(next_new_ev, tz) if next_new_ev is not None else None
    next_full_local = _astro_time_to_local(next_full_ev, tz) if next_full_ev is not None else None

    # ±24 saat içinde Yeni Ay veya Dolunay var mı?
    t_prev_window = to_astro_time(moment_local - timedelta(hours=24))
    is_special = False
    for target_deg in (0.0, 180.0):
        ev = astronomy.SearchMoonPhase(target_deg, t_prev_window, 2)
        if ev is not None:
            ev_local = _astro_time_to_local(ev, tz)
            if abs((ev_local - moment_local).total_seconds()) <= 86400:
                is_special = True
                if target_deg == 0.0:
                    phase_key, name_tr, name_en, emoji = ("new_moon", "Yeni Ay", "New Moon", "🌑")
                else:
                    phase_key, name_tr, name_en, emoji = ("full_moon", "Dolunay", "Full Moon", "🌕")
                break

    # ±3 gün içinde Güneş veya Ay tutulması var mı?
    t_ecl_start = to_astro_time(moment_local - timedelta(days=3))
    eclipse_tr: Optional[str] = None
    eclipse_en: Optional[str] = None
    solar_ecl = astronomy.SearchGlobalSolarEclipse(t_ecl_start)
    if solar_ecl is not None:
        s_dt = _astro_time_to_local(solar_ecl.peak, tz)
        if abs((s_dt - moment_local).total_seconds()) <= 3 * 86400:
            eclipse_tr = f"Güneş Tutulması ({s_dt.strftime('%d.%m %H:%M')})"
            eclipse_en = f"Solar Eclipse ({s_dt.strftime('%Y-%m-%d %H:%M')})"

    if eclipse_tr is None:
        lunar_ecl = astronomy.SearchLunarEclipse(t_ecl_start)
        if lunar_ecl is not None and lunar_ecl.kind != astronomy.EclipseKind.Penumbral:
            l_dt = _astro_time_to_local(lunar_ecl.peak, tz)
            if abs((l_dt - moment_local).total_seconds()) <= 3 * 86400:
                eclipse_tr = f"Ay Tutulması ({l_dt.strftime('%d.%m %H:%M')})"
                eclipse_en = f"Lunar Eclipse ({l_dt.strftime('%Y-%m-%d %H:%M')})"

    return MoonPhaseInfo(
        angle_deg=round(angle, 2),
        illumination_pct=illum_pct,
        phase_key=phase_key,
        name_tr=name_tr,
        name_en=name_en,
        emoji=emoji,
        is_special_now=is_special,
        next_new_moon_local=next_new_local,
        next_full_moon_local=next_full_local,
        nearby_eclipse_tr=eclipse_tr,
        nearby_eclipse_en=eclipse_en,
    )


def compute_transit_aspects(
    transit: ChartSnapshot,
    natal: ChartSnapshot,
    *,
    max_items: int = 8,
) -> list[Aspect]:
    """Transit gezegenler ile natal (özellikle kişisel) gezegenler/ASC arasındaki major açıları bulur."""
    natal_targets: list[PlanetPosition] = [
        natal.planets["sun"],
        natal.planets["moon"],
        natal.planets["mercury"],
        natal.planets["venus"],
        natal.planets["mars"],
    ]
    if natal.ascendant is not None:
        natal_targets.append(natal.ascendant)
    if natal.midheaven is not None:
        natal_targets.append(natal.midheaven)

    transit_movers = [
        pos for key, pos in transit.planets.items() if key != "moon"
    ] + [transit.planets["moon"]]

    aspects: list[Aspect] = []
    for t_pos in transit_movers:
        for n_pos in natal_targets:
            sep = abs(_wrap_diff_deg(t_pos.longitude, n_pos.longitude))
            for a_key, a_tr, a_en, sym, exact_deg, max_orb, nature in MAJOR_ASPECTS:
                # Hızlı hareket eden Ay için orb eşiği daha dar tutulur (3°)
                orb_limit = min(max_orb, 3.0) if t_pos.key == "moon" else max_orb
                orb = abs(sep - exact_deg)
                if orb <= orb_limit:
                    aspects.append(
                        Aspect(
                            transit_key=t_pos.key,
                            transit_name_tr=t_pos.name_tr,
                            transit_name_en=t_pos.name_en,
                            natal_key=n_pos.key,
                            natal_name_tr=n_pos.name_tr,
                            natal_name_en=n_pos.name_en,
                            aspect_key=a_key,
                            aspect_name_tr=a_tr,
                            aspect_name_en=a_en,
                            symbol=sym,
                            exact_angle=exact_deg,
                            orb=round(orb, 2),
                            nature=nature,
                        )
                    )
                    break

    aspects.sort(key=lambda a: (a.orb, 1 if a.transit_key == "moon" else 0))
    return aspects[:max_items]


def build_astro_report(
    config: Config,
    *,
    now_local: Optional[datetime] = None,
    partner_sign: Optional[str] = None,
) -> AstroReport:
    """Yapılandırmaya göre tam doğum haritası, anlık transit, Ay ve açı raporu oluşturur."""
    tz = ZoneInfo(config.timezone_name)
    lat, lon = resolve_coordinates(
        config.birth_city, config.birth_lat, config.birth_lon
    )
    natal_dt_local = datetime.combine(config.birth_date, config.birth_time).replace(
        tzinfo=tz
    )
    report_dt_local = now_local.astimezone(tz) if now_local is not None else datetime.now(tz)

    natal_chart = build_chart_snapshot(natal_dt_local, lat, lon, include_retrograde=True)
    transit_chart = build_chart_snapshot(report_dt_local, lat, lon, include_retrograde=True)
    moon_info = compute_moon_info(report_dt_local, tz)
    aspects = compute_transit_aspects(transit_chart, natal_chart)
    retros = [p for p in transit_chart.planets.values() if p.retrograde]

    is_birthday = (
        report_dt_local.month == config.birth_date.month
        and report_dt_local.day == config.birth_date.day
    )
    return AstroReport(
        user_name=config.user_name,
        birth_city=config.birth_city,
        user_goal=config.user_goal,
        report_time_local=report_dt_local,
        natal=natal_chart,
        transit=transit_chart,
        moon=moon_info,
        aspects=aspects,
        active_retrogrades=retros,
        is_birthday=is_birthday,
        is_monday=(report_dt_local.weekday() == 0),
        is_first_of_month=(report_dt_local.day == 1),
        partner_sign=partner_sign or config.partner_sign,
    )
