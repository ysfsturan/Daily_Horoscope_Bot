"""Daily Horoscope Bot ana giriş noktası ve CLI yöneticisi."""

from __future__ import annotations

import argparse
import html
import logging
import re
import sys
import time
from typing import Optional

from .astrology import build_astro_report
from .bot_commands import process_telegram_commands
from .config import Config, ConfigError, load_config
from .gemini_client import generate_astrology_text
from .telegram_client import (
    TelegramClient,
    TelegramError,
    format_chart_summary_card,
    format_full_message,
    format_moon_report,
    format_retrograde_report,
)

logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def _strip_html_for_terminal(text: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", text))


def run_once(
    config: Config,
    *,
    mode: str = "daily",
    partner_sign: Optional[str] = None,
    chart_only: bool = False,
    dry_run: bool = False,
) -> int:
    """Astroloji haritasını hesaplar, yorumu üretir ve Telegram'a (veya --dry-run konsola) sunar."""
    report = build_astro_report(config, partner_sign=partner_sign)

    if chart_only:
        parts = [
            format_chart_summary_card(report, lang=config.language),
            "",
            format_retrograde_report(report, lang=config.language),
            "",
            format_moon_report(report, lang=config.language),
        ]
        print(_strip_html_for_terminal("\n".join(parts)))
        return 0

    if mode == "moon":
        message = format_moon_report(report, lang=config.language)
        if config.show_footer:
            message = format_full_message(
                report,
                message,
                show_chart_summary=False,
                show_footer=True,
                lang=config.language,
            )
    else:
        body_text, model_used = generate_astrology_text(config, report, mode=mode)
        logger.info("Astroloji metni üretildi (kip=%s, kaynak=%s).", mode, model_used)
        message = format_full_message(
            report,
            body_text,
            show_chart_summary=config.show_chart_summary,
            show_footer=config.show_footer,
            lang=config.language,
        )

    if dry_run:
        print(_strip_html_for_terminal(message))
        return 0

    if not config.bot_token or not config.chat_ids:
        raise ConfigError("Telegram gönderimi için BOT_TOKEN ve CHAT_ID gereklidir.")

    tg = TelegramClient(config.bot_token, config.chat_ids)
    tg.send_message(message)
    logger.info("Astroloji mesajı Telegram'a gönderildi (hedef sohbet: %d).", len(config.chat_ids))
    return 0


def run_listen_loop(config: Config) -> int:
    """VPS/Docker üzerinde 7/24 anlık Telegram komut dinleme döngüsü."""
    if not config.bot_token or not config.chat_ids:
        raise ConfigError("--listen kipi için BOT_TOKEN ve CHAT_ID gereklidir.")

    logger.info("Daily Horoscope Bot Telegram uzun-yoklama dinleyicisi başlatıldı...")
    last_id: Optional[int] = None
    first = True
    while True:
        try:
            _, last_id = process_telegram_commands(
                config,
                last_update_id=last_id,
                poll_timeout=25,
                register_menu=first,
            )
            first = False
        except KeyboardInterrupt:
            logger.info("Dinleme kullanıcı tarafından durduruldu.")
            return 0
        except Exception as exc:
            logger.warning("Komut dinleme hatası: %s", exc)
            time.sleep(5)


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Daily Horoscope Bot — Gerçek VSOP87 Gökyüzü Hesabı + Gemini Flash"
    )
    parser.add_argument(
        "--mode",
        choices=["daily", "weekly", "monthly", "natal", "moon", "compatibility"],
        default="daily",
        help="Üretilecek astroloji raporu kipi (varsayılan: daily).",
    )
    parser.add_argument(
        "--partner",
        default=None,
        help="Uyumluluk analizi için partner burcu (--mode compatibility ile).",
    )
    parser.add_argument(
        "--chart-only",
        action="store_true",
        help="API veya Telegram anahtarı gerekmeden yalnızca gerçek gökyüzü haritasını yazdırır.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Telegram'a mesaj atmadan üretilen sonucu ekrana yazdırır.",
    )
    parser.add_argument(
        "--commands",
        action="store_true",
        help="Bekleyen Telegram /komutlarını tek seferlik yanıtlar.",
    )
    parser.add_argument(
        "--listen",
        action="store_true",
        help="Telegram komutlarını sürekli (VPS/Docker) dinler.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    _configure_logging()
    args = parse_args(argv)

    need_tg = not (args.chart_only or args.dry_run)
    need_ai = not (args.chart_only or args.mode == "moon")
    try:
        config = load_config(require_telegram=need_tg, require_gemini=need_ai)
    except ConfigError as exc:
        logger.error("Yapılandırma hatası: %s", exc)
        return 1

    try:
        if args.listen:
            return run_listen_loop(config)
        if args.commands:
            handled, _ = process_telegram_commands(config, register_menu=True)
            logger.info("%d Telegram komutu yanıtlandı.", handled)
            return 0
        return run_once(
            config,
            mode=args.mode,
            partner_sign=args.partner,
            chart_only=args.chart_only,
            dry_run=args.dry_run,
        )
    except TelegramError as exc:
        logger.error("Telegram gönderim hatası: %s", exc)
        return 1
    except ConfigError as exc:
        logger.error("Yapılandırma hatası: %s", exc)
        return 1
    except Exception as exc:
        logger.exception("Beklenmeyen hata: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
