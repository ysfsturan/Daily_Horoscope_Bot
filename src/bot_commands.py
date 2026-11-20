"""Telegram etkileşimli astroloji komutları (/burc, /harita, /ay, /retro, /haftalik, /uyum)."""

from __future__ import annotations

import html
import logging
from typing import Any, Callable, Optional

from .astrology import build_astro_report
from .config import Config
from .gemini_client import generate_astrology_text
from .telegram_client import (
    TelegramClient,
    format_full_message,
    format_help_message,
    format_moon_report,
    format_retrograde_report,
)

logger = logging.getLogger(__name__)

BOT_COMMANDS_MENU: list[dict[str, str]] = [
    {"command": "yardim", "description": "Tüm astroloji komutlarını listeler"},
    {"command": "burc", "description": "Bugünün kişisel burç & transit yorumu"},
    {"command": "harita", "description": "Doğum (Natal) haritan ve element dengen"},
    {"command": "ay", "description": "Anlık Ay evresi, aydınlanma % ve tutulma takvimi"},
    {"command": "retro", "description": "Aktif retrolar ve transit–natal açılar"},
    {"command": "haftalik", "description": "Önümüzdeki 7 günün haftalık astroloji özeti"},
    {"command": "uyum", "description": "Partner burç uyumu (/uyum Boğa)"},
]

_COMMAND_ALIASES: dict[str, str] = {
    "start": "yardim",
    "help": "yardim",
    "yardim": "yardim",
    "yardım": "yardim",
    "burc": "burc",
    "burç": "burc",
    "gunluk": "burc",
    "günlük": "burc",
    "daily": "burc",
    "horoscope": "burc",
    "harita": "harita",
    "natal": "harita",
    "chart": "harita",
    "ay": "ay",
    "moon": "ay",
    "retro": "retro",
    "retrolar": "retro",
    "transit": "retro",
    "haftalik": "haftalik",
    "haftalık": "haftalik",
    "weekly": "haftalik",
    "uyum": "uyum",
    "uyumluluk": "uyum",
    "compatibility": "uyum",
}


def parse_bot_command(text: str) -> tuple[Optional[str], list[str]]:
    """Telegram mesajından /komut adını ve argümanlarını ayrıştırır."""
    cleaned = (text or "").strip()
    if not cleaned.startswith("/"):
        return None, []
    parts = cleaned.split()
    raw_cmd = parts[0][1:]
    if "@" in raw_cmd:
        raw_cmd = raw_cmd.split("@", 1)[0]
    norm = raw_cmd.replace("İ", "i").replace("I", "ı").lower().strip()
    canonical = _COMMAND_ALIASES.get(norm)
    if not canonical:
        return None, parts[1:]
    return canonical, parts[1:]


def handle_command(
    command: str,
    args: list[str],
    config: Config,
) -> str:
    """Yetkili Telegram kullanıcısından gelen astroloji komutunu yanıtlar."""
    if command == "yardim":
        return format_help_message(config.language)

    partner_arg = " ".join(args).strip() if args else None
    if command == "uyum" and not partner_arg and not config.partner_sign:
        return (
            "💞 Kullanım: <code>/uyum Boğa</code> (veya başka bir burç adı yazın)."
            if config.language == "tr"
            else "💞 Usage: <code>/uyum Taurus</code> (or pass any zodiac sign)."
        )

    report = build_astro_report(config, partner_sign=partner_arg)

    if command == "ay":
        return format_moon_report(report, lang=config.language)

    if command == "retro":
        return format_retrograde_report(report, lang=config.language)

    mode_map = {
        "burc": "daily",
        "harita": "natal",
        "haftalik": "weekly",
        "uyum": "compatibility",
    }
    mode = mode_map.get(command, "daily")
    try:
        body, _ = generate_astrology_text(config, report, mode=mode)
    except Exception as exc:
        return f"⚠️ Yorum üretilirken hata oluştu: {html.escape(str(exc))}"

    return format_full_message(
        report,
        body,
        show_chart_summary=config.show_chart_summary,
        show_footer=config.show_footer,
        lang=config.language,
    )


def process_telegram_commands(
    config: Config,
    *,
    last_update_id: Optional[int] = None,
    poll_timeout: int = 0,
    register_menu: bool = False,
    client_factory: Optional[Callable[[], TelegramClient]] = None,
) -> tuple[int, Optional[int]]:
    """Yetkili sohbetlerden gelen Telegram /komutlarını işler."""
    if not config.bot_token or not config.chat_ids:
        return 0, last_update_id

    tg = (
        client_factory()
        if client_factory is not None
        else TelegramClient(config.bot_token, config.chat_ids)
    )
    if register_menu:
        tg.set_my_commands(BOT_COMMANDS_MENU)

    allowed_ids = {str(cid).strip() for cid in config.chat_ids if str(cid).strip()}
    offset = (last_update_id + 1) if isinstance(last_update_id, int) else None
    updates = tg.get_updates(offset=offset, timeout_seconds=poll_timeout)
    if not updates:
        return 0, last_update_id

    max_id = last_update_id
    handled = 0
    for upd in updates:
        uid = upd.get("update_id")
        if isinstance(uid, int) and (max_id is None or uid > max_id):
            max_id = uid
        msg = upd.get("message")
        if not isinstance(msg, dict):
            continue
        chat_id = str((msg.get("chat") or {}).get("id") or "").strip()
        if not chat_id or chat_id not in allowed_ids:
            continue

        command, args = parse_bot_command(str(msg.get("text") or ""))
        if not command:
            continue

        reply = handle_command(command, args, config)
        try:
            tg.send_message(reply, chat_ids_override=[chat_id])
            handled += 1
        except Exception as exc:
            logger.warning("Komut yanıtı gönderilemedi: %s", exc)

    return handled, max_id
