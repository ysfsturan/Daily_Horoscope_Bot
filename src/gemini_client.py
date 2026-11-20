"""Google Gemini Flash istemcisi: otomatik aktif model keşfi, zengin astrolojik prompt ve güvenli retry."""

from __future__ import annotations

import logging
import re
import time
from typing import Any, Optional

import httpx

from .astrology import format_date_localized
from .config import Config
from .models import AstroReport

logger = logging.getLogger(__name__)

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"
FALLBACK_FLASH_MODELS: tuple[str, ...] = (
    "gemini-3-flash-preview",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
)

_MODEL_VERSION_RE = re.compile(r"gemini-(\d+)(?:\.(\d+))?-flash")
_EXCLUDED_MODEL_TAGS = ("tts", "audio", "image", "embedding", "live", "robotics", "native")


class GeminiError(Exception):
    """Gemini API çağrısı başarısız olduğunda fırlatılır."""


def _rank_flash_model(model_name: str) -> tuple[int, int, int, int, int]:
    """Model adını önceliğe göre sıralar (büyük tuple önce seçilir)."""
    low = model_name.lower()
    m = _MODEL_VERSION_RE.search(low)
    major = int(m.group(1)) if m else 0
    minor = int(m.group(2) or 0) if m else 0
    is_not_lite = 0 if "lite" in low else 1
    is_stable = 1 if ("preview" not in low and "exp" not in low and "latest" not in low) else 0
    is_not_exp = 0 if "exp" in low else 1
    return (major, minor, is_not_lite, is_stable, is_not_exp)


def parse_and_rank_flash_models(models_payload: dict[str, Any]) -> list[str]:
    """Gemini /models JSON yanıtından aktif generateContent destekli Flash modelleri sırayla döndürür."""
    candidates: list[str] = []
    for entry in models_payload.get("models") or []:
        if not isinstance(entry, dict):
            continue
        raw_name = str(entry.get("name") or "").strip()
        short_name = raw_name.removeprefix("models/")
        low = short_name.lower()
        if "gemini" not in low or "flash" not in low:
            continue
        if any(tag in low for tag in _EXCLUDED_MODEL_TAGS):
            continue
        methods = entry.get("supportedGenerationMethods") or []
        if "generateContent" not in methods:
            continue
        candidates.append(short_name)

    candidates = sorted(set(candidates), key=_rank_flash_model, reverse=True)
    return candidates


def discover_flash_models(api_key: str, *, timeout: float = 15.0) -> list[str]:
    """Google AI API'den güncel ve aktif Gemini Flash modellerini sorgular."""
    headers = {"x-goog-api-key": api_key}
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.get(f"{GEMINI_API_BASE}/models", headers=headers)
            if resp.status_code != 200:
                logger.warning("Gemini model listesi alınamadı (HTTP %d); varsayılan liste kullanılacak.", resp.status_code)
                return []
            return parse_and_rank_flash_models(resp.json())
    except Exception as exc:
        logger.warning("Gemini model keşfi başarısız (%s); varsayılan liste kullanılacak.", exc)
        return []


def _format_planets_block(report: AstroReport, lang: str = "tr") -> tuple[str, str]:
    n_parts = [f"{p.name_tr if lang == 'tr' else p.name_en}: {p.format_degree(lang)}" for p in report.natal.planets.values()]
    if report.natal.ascendant:
        label = "Yükselen" if lang == "tr" else "Ascendant"
        n_parts.append(f"{label}: {report.natal.ascendant.format_degree(lang)}")
    if report.natal.midheaven:
        label = "MC"
        n_parts.append(f"{label}: {report.natal.midheaven.format_degree(lang)}")

    t_parts = [f"{p.name_tr if lang == 'tr' else p.name_en}: {p.format_degree(lang)}" for p in report.transit.planets.values()]
    return " | ".join(n_parts), " | ".join(t_parts)


def build_horoscope_prompt(
    report: AstroReport,
    *,
    mode: str = "daily",
    lang: str = "tr",
    tone: str = "dengeli",
) -> str:
    """Hesaplanan astronomi verilerinden mod ve dil uyumlu Gemini promptu oluşturur."""
    date_str = format_date_localized(report.report_time_local, lang=lang)
    natal_line, transit_line = _format_planets_block(report, lang=lang)

    if report.aspects:
        aspect_lines = [
            f"- Transit {a.transit_name_tr} {a.symbol} Natal {a.natal_name_tr} ({a.aspect_name_tr}, orb {a.orb:.1f}°, {a.nature})"
            for a in report.aspects[:6]
        ]
        aspects_block = "\n".join(aspect_lines)
    else:
        aspects_block = "- Belirgin dar orblu major transit açısı yok; Ay evresi ve günün enerjisi ön planda."

    if report.active_retrogrades:
        retro_text = ", ".join(f"{r.name_tr} ({r.sign_tr})" for r in report.active_retrogrades)
    else:
        retro_text = "Şu an aktif majör gezegen retrosu yok."

    elem_text = ", ".join(f"{k}: {v}" for k, v in report.natal.element_counts.items())
    eclipse_note = report.moon.nearby_eclipse_tr or "Yok"
    moon_line = (
        f"{report.moon.emoji} {report.moon.name_tr} (Aydınlanma %{report.moon.illumination_pct:.1f}), "
        f"Yakın Tutulma: {eclipse_note}"
    )

    specials: list[str] = []
    if report.is_birthday:
        specials.append("BUGÜN KULLANICININ DOĞUM GÜNÜ! Güneş Dönüşü (Solar Return) tebriği ve yeni yaş vizyonu ekle.")
    if report.moon.is_special_now:
        specials.append(f"GÖKYÜZÜNDE ÖZEL AY EVRESİ VAR: {report.moon.name_tr}! Bu evrenin niyet/tamamlanma etkisini mutlaka vurgula.")
    if report.moon.nearby_eclipse_tr:
        specials.append(f"YAKIN TUTULMA DÖNEMİ: {report.moon.nearby_eclipse_tr}. Dönüşüm temasını işle.")
    if mode == "daily" and not report.is_birthday:
        if report.is_monday:
            specials.append("Bugün Pazartesi: Sona '📅 <b>Haftaya Genel Bakış</b>' bölümü ekle.")
        if report.is_first_of_month:
            specials.append("Bugün ayın 1'i: Sona '🗓️ <b>Bu Ayın Ana Teması</b>' bölümü ekle.")

    tone_instructions = {
        "dengeli": "Akıcı, sıcak, gerçekçi, somut adımlar içeren ve motive edici bir ton kullan.",
        "motive": "Yüksek enerjili, aksiyon odaklı, cesaretlendirici ve net bir koçluk tonu kullan.",
        "mistik": "Sezgisel, sembolik derinliği yüksek, zarif ve edebi bir astrolojik dil kullan.",
        "kisa": "Çok özlü ve doğrudan uygulanabilir maddeler yaz (toplam 150-220 kelimeyi geçme).",
    }
    tone_rule = tone_instructions.get(tone, tone_instructions["dengeli"])

    mode_tasks = {
        "daily": (
            "Günlük kapsamlı astroloji yorumu yaz:\n"
            "1. 🌌 <b>Günün Gökyüzü ve Başrol Transitleri</b> (Ay evresi, retrolar ve yukarıdaki transit açılarına doğrudan atıf yap)\n"
            f"2. 🎯 <b>Hedef & Kariyer ({report.user_goal})</b> (Somut, uygulanabilir strateji)\n"
            "3. 💫 <b>İlişkiler & İletişim</b> (Venüs, Mars ve Merkür etkileri)\n"
            "4. ⚡ <b>Günün Mottosu ve Somut Aksiyon</b>"
        ),
        "weekly": (
            "Önümüzdeki 7 gün için stratejik haftalık astroloji rehberi yaz: haftanın fırsat günleri, "
            "dikkat edilmesi gereken transit gerilimleri, kariyer/hedef odakları ve hafta sonu tavsiyesi."
        ),
        "monthly": (
            "Bu ayın astrolojik yol haritasını yaz: aylık ana temalar, retrolar ve Ay döngüleriyle uyumlu "
            "aksiyon zamanlamaları, kariyer ve ilişkiler özeti."
        ),
        "natal": (
            "Kullanıcının natal haritasının derin kişilik ve potansiyel analizini yaz: Güneş-Ay-Yükselen üçlüsü, "
            "element dengesi, doğal yetenekler, gelişim alanları ve hayat hedefiyle uyumu."
        ),
        "compatibility": (
            f"Kullanıcının haritası (Güneş {report.natal.planets['sun'].sign_tr}, "
            f"Ay {report.natal.planets['moon'].sign_tr}, Venüs {report.natal.planets['venus'].sign_tr}, "
            f"Mars {report.natal.planets['mars'].sign_tr}) ile partner burcu '{report.partner_sign or 'Koç'}' "
            "arasındaki uyum analizini yaz: iletişim, duygusal bağ, güçlü yanlar ve dikkat edilmesi gereken denge noktaları."
        ),
    }

    lang_rule = (
        "Yanıtı tamamen doğal ve akıcı TÜRKÇE yaz."
        if lang == "tr"
        else "Write the entire response in natural, fluent ENGLISH (translate sign names cleanly)."
    )

    return (
        f"SEN DENEYİMLİ VE GERÇEK VERİYE SADIK BİR ASTROLOGSUN. {lang_rule}\n"
        f"TON: {tone_rule}\n"
        f"KİŞİ: {report.user_name} | DOĞUM ŞEHRİ: {report.birth_city} | HEDEF: {report.user_goal} | TARİH: {date_str}\n\n"
        "‼️ KURAL: Yalnızca aşağıda verilen gerçek astronomi verilerine sadık kal; başka gezegen konumu veya hayali burç uydurma.\n\n"
        f"📌 NATAL HARİTA: {natal_line}\n"
        f"📌 NATAL ELEMENT DAĞILIMI: {elem_text}\n"
        f"📌 ANLIK TRANSİTLER: {transit_line}\n"
        f"📌 AY DURUMU: {moon_line}\n"
        f"📌 AKTİF RETROLAR: {retro_text}\n"
        f"📌 ÖNE ÇIKAN TRANSİT-NATAL AÇILARI:\n{aspects_block}\n\n"
        f"✍️ GÖREV:\n{mode_tasks.get(mode, mode_tasks['daily'])}\n"
        + (("\n✨ ÖZEL NOTLAR:\n- " + "\n- ".join(specials) + "\n") if specials else "")
        + "\n⚠️ BİÇİM KURALI: Sadece Telegram HTML etiketleri olan <b>, <i>, <code> kullan. "
        "Asla ``` veya Markdown **yıldız** kullanma; <style>, <div>, <br>, <p> yazma. Uygun yerlerde sade emojiler kullan."
    )


def build_offline_fallback(report: AstroReport, mode: str = "daily", lang: str = "tr") -> str:
    """Gemini API geçici olarak yanıt veremezse hesaplanan gerçek verilerle temiz bir özet üretir."""
    sun_t = report.transit.planets["sun"]
    moon_t = report.transit.planets["moon"]
    merc_t = report.transit.planets["mercury"]
    retros = ", ".join(r.name_tr for r in report.active_retrogrades) if report.active_retrogrades else "Yok"

    if lang == "en":
        lines = [
            f"⚠️ <i>AI commentary service was temporarily busy; here is today's verified astronomical digest ({mode}):</i>",
            "",
            f"☀️ <b>Transit Sun:</b> {sun_t.format_degree('en')}",
            f"{report.moon.emoji} <b>Moon:</b> {moon_t.format_degree('en')} — {report.moon.name_en} (%{report.moon.illumination_pct:.0f})",
            f"☿ <b>Mercury:</b> {merc_t.format_degree('en')}",
        ]
        if report.aspects:
            top = report.aspects[0]
            lines.append(
                f"🔭 <b>Key Transit:</b> Transit {top.transit_name_en} {top.symbol} Natal {top.natal_name_en} (orb {top.orb:.1f}°)"
            )
        return "\n".join(lines)

    lines = [
        f"ℹ️ <i>Yapay zekâ yorum servisine geçici olarak ulaşılamadı; bugünün gerçek gökyüzü verileri aşağıdadır ({mode}):</i>",
        "",
        f"☀️ <b>Transit Güneş:</b> {sun_t.format_degree('tr')}",
        f"{report.moon.emoji} <b>Transit Ay:</b> {moon_t.format_degree('tr')} — {report.moon.name_tr} (%{report.moon.illumination_pct:.0f})",
        f"☿ <b>Merkür:</b> {merc_t.format_degree('tr')} | <b>Aktif Retro:</b> {retros}",
    ]
    if report.aspects:
        lines.append("")
        lines.append("🔭 <b>Bugünün Öne Çıkan Transit Açıları:</b>")
        for a in report.aspects[:4]:
            lines.append(
                f"• Transit {a.transit_name_tr} {a.symbol} Natal {a.natal_name_tr} (<i>{a.aspect_name_tr}, orb {a.orb:.1f}°</i>)"
            )
    return "\n".join(lines)


def _extract_gemini_text(payload: dict[str, Any]) -> Optional[str]:
    candidates = payload.get("candidates") or []
    if not candidates or not isinstance(candidates[0], dict):
        return None
    content = candidates[0].get("content") or {}
    parts = content.get("parts") or []
    texts = [str(p.get("text") or "") for p in parts if isinstance(p, dict) and p.get("text")]
    combined = "\n".join(texts).strip()
    return combined or None


def generate_astrology_text(
    config: Config,
    report: AstroReport,
    *,
    mode: str = "daily",
    timeout: float = 60.0,
) -> tuple[str, str]:
    """
    Aktif Gemini Flash modelleri üzerinden astroloji metni üretir.
    Dönüş: (oluşturulan_metin, kullanılan_model_veya_'offline_fallback')
    """
    if not config.gemini_api_key:
        raise GeminiError("GEMINI_API_KEY tanımlı değil.")

    prompt = build_horoscope_prompt(
        report,
        mode=mode,
        lang=config.language,
        tone=config.tone,
    )

    candidate_models: list[str] = []
    if config.gemini_model:
        candidate_models.append(config.gemini_model.removeprefix("models/"))

    discovered = discover_flash_models(config.gemini_api_key)
    for m in discovered:
        if m not in candidate_models:
            candidate_models.append(m)
    for m in FALLBACK_FLASH_MODELS:
        if m not in candidate_models:
            candidate_models.append(m)

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": config.gemini_api_key,
    }
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.85,
            "maxOutputTokens": 2048,
        },
    }

    last_error = "Bilinmeyen hata"
    with httpx.Client(timeout=timeout) as client:
        for model_name in candidate_models[:5]:
            url = f"{GEMINI_API_BASE}/models/{model_name}:generateContent"
            for attempt in range(2):
                try:
                    resp = client.post(url, headers=headers, json=body)
                    if resp.status_code == 200:
                        text = _extract_gemini_text(resp.json())
                        if text:
                            logger.info("Gemini yanıtı alındı (model: %s).", model_name)
                            return text, model_name
                        last_error = f"{model_name}: Boş içerik döndü"
                        break
                    if resp.status_code in {400, 404}:
                        last_error = f"{model_name}: HTTP {resp.status_code}"
                        logger.warning("Model kullanılamadı (%s: HTTP %d), sıradaki deneniyor.", model_name, resp.status_code)
                        break
                    if resp.status_code in {429, 500, 502, 503, 504}:
                        last_error = f"{model_name}: HTTP {resp.status_code}"
                        if attempt == 0:
                            time.sleep(1.5)
                            continue
                        break
                    last_error = f"{model_name}: HTTP {resp.status_code}"
                    break
                except httpx.HTTPError as exc:
                    last_error = f"{model_name}: {exc}"
                    if attempt == 0:
                        time.sleep(1.5)
                        continue
                    break

    logger.warning("Tüm Gemini modelleri başarısız (%s); çevrimdışı özet üretiliyor.", last_error)
    return build_offline_fallback(report, mode=mode, lang=config.language), "offline_fallback"
