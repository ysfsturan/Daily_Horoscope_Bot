"""Telegram Bot API istemcisi, HTML temizleyici, etiket-güvenli parçalayıcı ve formatlayıcılar."""

from __future__ import annotations

import html
import logging
import re
import time
from typing import Any, Optional

import httpx

from .astrology import format_date_localized
from .config import LINKEDIN_URL
from .models import AstroReport

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org"

_SUPPORTED_TAGS = ("b", "i", "u", "s", "code", "pre")
_BLOCK_BREAK_RE = re.compile(r"</?(?:p|div|br\s*/?|h[1-6]|tr)\b[^>]*>", re.IGNORECASE)
_STYLE_SCRIPT_RE = re.compile(r"<(?:style|script)[^>]*>.*?</(?:style|script)>", re.IGNORECASE | re.DOTALL)
_MD_BOLD_RE = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)
_MD_HEADER_RE = re.compile(r"(?m)^#{1,4}\s+(.+)$")
_TAG_TOKEN_RE = re.compile(r"</?([a-zA-Z0-9]+)(?:\s+[^>]*)?>")


class TelegramError(Exception):
    """Telegram mesajı gönderilirken oluşan kalıcı hata."""


def sanitize_telegram_html(raw: str) -> str:
    """Gemini veya dış kaynaktan gelen metni Telegram HTML kurallarına güvenli hale getirir."""
    text = (raw or "").replace("\r\n", "\n")
    text = re.sub(r"```(?:html|markdown|md)?\s*", "", text, flags=re.IGNORECASE)
    text = text.replace("```", "")
    text = _STYLE_SCRIPT_RE.sub("", text)
    text = _BLOCK_BREAK_RE.sub("\n", text)
    text = _MD_HEADER_RE.sub(r"<b>\1</b>", text)
    text = _MD_BOLD_RE.sub(r"<b>\1</b>", text)

    # Sadece izin verilen Telegram HTML etiketlerini koru; diğer etiketleri soy
    def _filter_tag(match: re.Match[str]) -> str:
        tag = match.group(1).lower()
        full = match.group(0)
        if tag in _SUPPORTED_TAGS:
            return f"</{tag}>" if full.startswith("</") else f"<{tag}>"
        if tag == "strong":
            return "</b>" if full.startswith("</") else "<b>"
        if tag == "em":
            return "</i>" if full.startswith("</") else "<i>"
        if tag == "a":
            if full.startswith("</"):
                return "</a>"
            href_m = re.search(r"""href\s*=\s*(['"])(https?://[^'"]+)\1""", full, re.IGNORECASE)
            if href_m:
                return f'<a href="{html.escape(href_m.group(2), quote=True)}">'
            return ""
        return ""

    text = _TAG_TOKEN_RE.sub(_filter_tag, text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _track_open_tags(text: str) -> list[str]:
    stack: list[str] = []
    for m in _TAG_TOKEN_RE.finditer(text):
        tag = m.group(1).lower()
        full = m.group(0)
        if tag not in _SUPPORTED_TAGS and tag != "a":
            continue
        if full.startswith("</"):
            if tag in stack:
                # En son eşleşeni kapat
                idx = len(stack) - 1 - stack[::-1].index(tag)
                stack.pop(idx)
        else:
            stack.append(tag)
    return stack


def split_telegram_message(text: str, max_length: int = 4000) -> list[str]:
    """Mesajı satır bütünlüğünü ve açık HTML etiketlerini bozmadan parçalara ayırır."""
    if len(text) <= max_length:
        return [text]

    raw_chunks: list[str] = []
    remaining = text
    while len(remaining) > max_length:
        split_at = remaining.rfind("\n", 0, max_length - 40)
        if split_at <= 0:
            split_at = remaining.rfind(" ", 0, max_length - 40)
        if split_at <= 0:
            split_at = max_length - 40
        chunk = remaining[:split_at].rstrip()
        remaining = remaining[split_at:].lstrip("\n")
        if chunk:
            raw_chunks.append(chunk)
    if remaining:
        raw_chunks.append(remaining)

    balanced: list[str] = []
    carry_open: list[str] = []
    for idx, chunk in enumerate(raw_chunks):
        prefix = "".join(f"<{t}>" for t in carry_open if t != "a")
        current = prefix + chunk
        open_tags = _track_open_tags(current)
        if idx < len(raw_chunks) - 1 and open_tags:
            closing = "".join(f"</{t}>" for t in reversed(open_tags) if t != "a")
            current = current + closing
        balanced.append(current)
        carry_open = open_tags

    return balanced


def format_chart_summary_card(report: AstroReport, lang: str = "tr") -> str:
    """Mesajın başına eklenen gerçek astronomik özet kartını (Natal, Transit, Ay, Retro) üretir."""
    n = report.natal.planets
    t = report.transit.planets
    date_label = format_date_localized(report.report_time_local, lang=lang)
    retros = ", ".join(r.name_tr if lang == "tr" else r.name_en for r in report.active_retrogrades)

    if lang == "en":
        asc_txt = report.natal.ascendant.format_degree("en") if report.natal.ascendant else "-"
        lines = [
            f"🔮 <b>Daily Astrological Digest — {html.escape(report.user_name, quote=False)}</b>",
            f"📅 <i>{html.escape(date_label, quote=False)} | {html.escape(report.birth_city, quote=False)}</i>",
            "",
            f"🌟 <b>Natal:</b> ☀️ {html.escape(n['sun'].format_degree('en'), quote=False)} | 🌙 {html.escape(n['moon'].format_degree('en'), quote=False)} | ⬆️ Asc: {html.escape(asc_txt, quote=False)}",
            f"🪐 <b>Transit:</b> ☀️ {html.escape(t['sun'].format_degree('en'), quote=False)} | 🌙 {html.escape(t['moon'].format_degree('en'), quote=False)} | ☿ {html.escape(t['mercury'].format_degree('en'), quote=False)}",
            f"{report.moon.emoji} <b>Moon Phase:</b> {html.escape(report.moon.name_en, quote=False)} (<code>%{report.moon.illumination_pct:.0f}</code>)"
            + (f" | ♻️ <b>Retrograde:</b> {html.escape(retros, quote=False)}" if retros else " | ✨ No active major retrogrades"),
        ]
        if report.moon.nearby_eclipse_en:
            lines.append(f"🌑 <b>Eclipse Alert:</b> {html.escape(report.moon.nearby_eclipse_en, quote=False)}")
        return "\n".join(lines)

    asc_txt = report.natal.ascendant.format_degree("tr") if report.natal.ascendant else "-"
    lines = [
        f"🔮 <b>Günlük Gökyüzü Özeti — {html.escape(report.user_name, quote=False)}</b>",
        f"📅 <i>{html.escape(date_label, quote=False)} | {html.escape(report.birth_city, quote=False)}</i>",
        "",
        f"🌟 <b>Natal:</b> ☀️ {html.escape(n['sun'].format_degree('tr'), quote=False)} | 🌙 {html.escape(n['moon'].format_degree('tr'), quote=False)} | ⬆️ Yükselen: {html.escape(asc_txt, quote=False)}",
        f"🪐 <b>Transit:</b> ☀️ {html.escape(t['sun'].format_degree('tr'), quote=False)} | 🌙 {html.escape(t['moon'].format_degree('tr'), quote=False)} | ☿ {html.escape(t['mercury'].format_degree('tr'), quote=False)}",
        f"{report.moon.emoji} <b>Ay Evresi:</b> {html.escape(report.moon.name_tr, quote=False)} (<code>%{report.moon.illumination_pct:.0f}</code>)"
        + (f" | ♻️ <b>Retro:</b> {html.escape(retros, quote=False)}" if retros else " | ✨ Aktif majör retro yok"),
    ]
    if report.moon.nearby_eclipse_tr:
        lines.append(f"🌑 <b>Tutulma Etkisi:</b> {html.escape(report.moon.nearby_eclipse_tr, quote=False)}")
    return "\n".join(lines)


def format_moon_report(report: AstroReport, lang: str = "tr") -> str:
    """/ay ve --mode moon için ayrıntılı Ay evresi ve tutulma takvimi mesajı üretir."""
    m = report.moon
    moon_t = report.transit.planets["moon"]
    new_txt = format_date_localized(m.next_new_moon_local, lang) + f" {m.next_new_moon_local.strftime('%H:%M')}" if m.next_new_moon_local else "-"
    full_txt = format_date_localized(m.next_full_moon_local, lang) + f" {m.next_full_moon_local.strftime('%H:%M')}" if m.next_full_moon_local else "-"

    if lang == "en":
        lines = [
            f"{m.emoji} <b>Moon Phase & Eclipse Calendar</b>",
            f"📅 <i>{html.escape(format_date_localized(report.report_time_local, 'en'), quote=False)}</i>",
            "",
            f"🌙 <b>Position:</b> {html.escape(moon_t.format_degree('en'), quote=False)}",
            f"🌓 <b>Phase:</b> {html.escape(m.name_en, quote=False)} (Illumination: <code>%{m.illumination_pct:.1f}</code> | Angle: <code>{m.angle_deg:.1f}°</code>)",
            f"🌑 <b>Next New Moon:</b> {html.escape(new_txt, quote=False)}",
            f"🌕 <b>Next Full Moon:</b> {html.escape(full_txt, quote=False)}",
        ]
        if m.nearby_eclipse_en:
            lines.append(f"🌒 <b>Nearby Eclipse (±3 days):</b> {html.escape(m.nearby_eclipse_en, quote=False)}")
        return "\n".join(lines)

    lines = [
        f"{m.emoji} <b>Ay Evresi & Tutulma Takvimi</b>",
        f"📅 <i>{html.escape(format_date_localized(report.report_time_local, 'tr'), quote=False)}</i>",
        "",
        f"🌙 <b>Ay Konumu:</b> {html.escape(moon_t.format_degree('tr'), quote=False)}",
        f"🌓 <b>Evre:</b> {html.escape(m.name_tr, quote=False)} (Aydınlanma: <code>%{m.illumination_pct:.1f}</code> | Faz Açısı: <code>{m.angle_deg:.1f}°</code>)",
        f"🌑 <b>Sonraki Yeni Ay:</b> {html.escape(new_txt, quote=False)}",
        f"🌕 <b>Sonraki Dolunay:</b> {html.escape(full_txt, quote=False)}",
    ]
    if m.nearby_eclipse_tr:
        lines.append(f"🌒 <b>Yakın Tutulma (±3 gün):</b> {html.escape(m.nearby_eclipse_tr, quote=False)}")
    return "\n".join(lines)


def format_retrograde_report(report: AstroReport, lang: str = "tr") -> str:
    """/retro komutu için aktif retrolar ve tam transit konumları raporunu üretir."""
    lines = ["♻️ <b>Gökyüzü Gezegen Konumları & Retro Durumu</b>", ""]
    if report.active_retrogrades:
        names = ", ".join(f"{r.name_tr} ({r.sign_tr})" for r in report.active_retrogrades)
        lines.append(f"⚠️ <b>Aktif Retrolar:</b> {html.escape(names, quote=False)}")
    else:
        lines.append("✨ <b>Şu an retro harekette gezegen bulunmuyor.</b>")
    lines.append("")
    for p in report.transit.planets.values():
        flag = " ♻️ <b>[RETRO]</b>" if p.retrograde else ""
        lines.append(f"• <b>{html.escape(p.name_tr, quote=False)}:</b> {html.escape(p.format_degree(lang), quote=False)}{flag}")
    if report.aspects:
        lines.append("")
        lines.append("🔭 <b>En Yakın Transit–Natal Açıları:</b>")
        for a in report.aspects[:5]:
            lines.append(
                f"• {html.escape(a.transit_name_tr, quote=False)} {a.symbol} Natal {html.escape(a.natal_name_tr, quote=False)} "
                f"(<i>{html.escape(a.aspect_name_tr, quote=False)}, orb {a.orb:.1f}°</i>)"
            )
    return "\n".join(lines)


def format_full_message(
    report: AstroReport,
    body_text: str,
    *,
    show_chart_summary: bool = True,
    show_footer: bool = True,
    lang: str = "tr",
) -> str:
    """Özet kartı + Gemini yorumu + imzayı birleştirip temiz HTML döndürür."""
    sections: list[str] = []
    if show_chart_summary:
        sections.append(format_chart_summary_card(report, lang=lang))
    cleaned_body = sanitize_telegram_html(body_text)
    if cleaned_body:
        sections.append(cleaned_body)
    if show_footer:
        footer = (
            f'Made with ❤️ by <a href="{LINKEDIN_URL}">Yusuf Sami Turan</a>'
            if lang == "en"
            else f'✨ Made with ❤️ by <a href="{LINKEDIN_URL}">Yusuf Sami Turan</a>'
        )
        sections.append(footer)
    return "\n\n".join(sections)


def format_help_message(lang: str = "tr") -> str:
    if lang == "en":
        return "\n".join(
            [
                "🔮 <b>Daily Horoscope Bot Commands</b>",
                "",
                "• /burc — Today's personalized transit & horoscope",
                "• /harita — Full Natal & Transit planetary chart",
                "• /ay — Moon phase, illumination & eclipse calendar",
                "• /retro — Active retrogrades & exact transit aspects",
                "• /haftalik — 7-day astrological outlook",
                "• /uyum <code>Sign</code> — Compatibility check (e.g. /uyum Libra)",
            ]
        )
    return "\n".join(
        [
            "🔮 <b>Günlük Burç & Astroloji Asistanı Komutları</b>",
            "",
            "• /burc — Bugünün kişiselleştirilmiş gökyüzü yorumu",
            "• /harita — Tam Natal & Transit harita konumların",
            "• /ay — Anlık Ay evresi, aydınlanma % ve tutulma takvimi",
            "• /retro — Aktif retrolar ve transit–natal açılar",
            "• /haftalik — Önümüzdeki 7 günün haftalık özeti",
            "• /uyum <code>Burç</code> — İlişki ve enerji uyumu <i>(ör. /uyum Boğa)</i>",
        ]
    )


class TelegramClient:
    """IPv4 zorlamalı ve yeniden denemeli Telegram Bot API istemcisi."""

    def __init__(self, bot_token: str, chat_ids: list[str], timeout: float = 30.0) -> None:
        self.bot_token = bot_token
        self.chat_ids = [str(cid).strip() for cid in chat_ids if str(cid).strip()]
        self.timeout = timeout

    def _build_client(self, read_timeout: Optional[float] = None) -> httpx.Client:
        transport = httpx.HTTPTransport(local_address="0.0.0.0")
        t_out = httpx.Timeout(
            connect=15.0,
            read=read_timeout if read_timeout is not None else self.timeout,
            write=15.0,
            pool=10.0,
        )
        return httpx.Client(transport=transport, timeout=t_out)

    def _post_with_retry(self, method: str, payload: dict[str, Any], *, read_timeout: Optional[float] = None) -> httpx.Response:
        url = f"{TELEGRAM_API_BASE}/bot{self.bot_token}/{method}"
        last_exc: Optional[Exception] = None
        for attempt in range(1, 4):
            try:
                with self._build_client(read_timeout=read_timeout) as client:
                    resp = client.post(url, json=payload)
                if resp.status_code == 429:
                    retry_after = 2
                    try:
                        retry_after = int(resp.json().get("parameters", {}).get("retry_after", 2))
                    except Exception:
                        pass
                    time.sleep(min(retry_after, 10))
                    continue
                if resp.status_code >= 500 and attempt < 3:
                    time.sleep(attempt)
                    continue
                return resp
            except httpx.HTTPError as exc:
                last_exc = exc
                logger.warning("Telegram isteği başarısız (%d/3): %s", attempt, exc)
                if attempt < 3:
                    time.sleep(attempt)
        raise TelegramError(f"Telegram API bağlantısı başarısız: {last_exc}")

    def send_message(self, text: str, *, chat_ids_override: Optional[list[str]] = None) -> None:
        targets = chat_ids_override if chat_ids_override is not None else self.chat_ids
        chunks = split_telegram_message(text, max_length=4000)

        for chat_id in targets:
            for idx, chunk in enumerate(chunks):
                resp = self._post_with_retry(
                    "sendMessage",
                    {
                        "chat_id": chat_id,
                        "text": chunk,
                        "parse_mode": "HTML",
                        "disable_web_page_preview": True,
                    },
                )
                if resp.status_code != 200:
                    # HTML ayrıştırma hatası olursa düz metin fallback ile göndermeyi dene
                    plain = re.sub(r"<[^>]+>", "", chunk)
                    resp_plain = self._post_with_retry(
                        "sendMessage",
                        {
                            "chat_id": chat_id,
                            "text": plain,
                            "disable_web_page_preview": True,
                        },
                    )
                    if resp_plain.status_code != 200:
                        raise TelegramError(
                            f"Telegram mesajı gönderilemedi (HTTP {resp_plain.status_code}): {resp_plain.text[:200]}"
                        )
                if idx < len(chunks) - 1:
                    time.sleep(0.5)

    def get_updates(self, *, offset: Optional[int] = None, timeout_seconds: int = 0) -> list[dict[str, Any]]:
        payload: dict[str, Any] = {
            "timeout": max(0, int(timeout_seconds)),
            "allowed_updates": ["message"],
        }
        if offset is not None:
            payload["offset"] = offset
        try:
            resp = self._post_with_retry("getUpdates", payload, read_timeout=float(timeout_seconds) + 15.0)
            if resp.status_code != 200:
                return []
            data = resp.json()
            result = data.get("result")
            return result if isinstance(result, list) else []
        except Exception as exc:
            logger.warning("Telegram getUpdates başarısız: %s", exc)
            return []

    def set_my_commands(self, commands: list[dict[str, str]]) -> bool:
        try:
            resp = self._post_with_retry("setMyCommands", {"commands": commands})
            return resp.status_code == 200
        except Exception:
            return False
