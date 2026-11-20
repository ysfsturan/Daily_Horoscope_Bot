"""Daily Horoscope Bot birim ve entegrasyon testleri."""

from __future__ import annotations

import os
import unittest
from datetime import date, datetime, time, timezone
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

from src.astrology import (
    build_astro_report,
    build_chart_snapshot,
    format_date_localized,
    resolve_coordinates,
    to_astro_time,
)
from src.bot_commands import handle_command, parse_bot_command, process_telegram_commands
from src.config import Config, ConfigError, load_config, parse_birth_date
from src.gemini_client import (
    build_horoscope_prompt,
    build_offline_fallback,
    generate_astrology_text,
    parse_and_rank_flash_models,
)
from src.main import main as cli_main
from src.telegram_client import (
    TelegramClient,
    format_chart_summary_card,
    format_moon_report,
    sanitize_telegram_html,
    split_telegram_message,
)


class CityAndConfigTests(unittest.TestCase):
    def test_turkish_city_resolution_all_diacritics(self) -> None:
        self.assertEqual(resolve_coordinates("İstanbul"), (41.0082, 28.9784))
        self.assertEqual(resolve_coordinates("İZMİR"), (38.4237, 27.1428))
        self.assertEqual(resolve_coordinates("Şanlıurfa"), (37.1591, 38.7969))
        self.assertEqual(resolve_coordinates("Afyonkarahisar"), (38.7507, 30.5567))
        self.assertEqual(resolve_coordinates("İçel"), (36.8000, 34.6333))
        self.assertEqual(resolve_coordinates("Kastamonu"), (41.3887, 33.7827))
        self.assertEqual(resolve_coordinates("BilinmeyenŞehir"), (41.0082, 28.9784))
        self.assertEqual(resolve_coordinates("Londra", 51.5072, -0.1276), (51.5072, -0.1276))

    def test_load_config_validation_and_multi_chat(self) -> None:
        env = {
            "BOT_TOKEN": "123:TOKEN",
            "CHAT_ID": "111222, 333444",
            "GEMINI_API_KEY": "AIzaSecret",
            "USER_NAME": "Yusuf",
            "BIRTH_DATE": "26.09.2000",
            "BIRTH_TIME": "04:00",
            "BIRTH_CITY": "Kastamonu",
            "USER_GOAL": "Yazılım",
            "TONE": "kısa",
            "LANGUAGE": "tr",
        }
        with patch("src.config.load_dotenv", None), patch.dict(os.environ, env, clear=True):
            cfg = load_config()
        self.assertEqual(cfg.chat_ids, ["111222", "333444"])
        self.assertEqual(cfg.birth_date, date(2000, 9, 26))
        self.assertEqual(cfg.birth_time, time(4, 0))
        self.assertEqual(cfg.tone, "kisa")
        self.assertTrue(cfg.show_chart_summary)

        # Eksik BOT_TOKEN require_telegram=True iken ConfigError vermeli
        bad_env = {"CHAT_ID": "111222", "GEMINI_API_KEY": "AIzaSecret"}
        with patch("src.config.load_dotenv", None), patch.dict(os.environ, bad_env, clear=True):
            with self.assertRaises(ConfigError):
                load_config(require_telegram=True)
            dry_cfg = load_config(require_telegram=False)
            self.assertIsNone(dry_cfg.bot_token)

        self.assertEqual(parse_birth_date("2000-09-26"), date(2000, 9, 26))


class AstrologyEngineTests(unittest.TestCase):
    def test_historical_turkey_dst_and_vernal_equinox(self) -> None:
        ist = ZoneInfo("Europe/Istanbul")
        winter_2000 = datetime(2000, 1, 15, 12, 0, tzinfo=ist)
        summer_2000 = datetime(2000, 7, 15, 12, 0, tzinfo=ist)
        winter_2020 = datetime(2020, 1, 15, 12, 0, tzinfo=ist)

        self.assertEqual(winter_2000.utcoffset().total_seconds(), 2 * 3600)
        self.assertEqual(summer_2000.utcoffset().total_seconds(), 3 * 3600)
        self.assertEqual(winter_2020.utcoffset().total_seconds(), 3 * 3600)

        # 20 Mart 2026 14:46 UTC (17:46 TR) İlkbahar Ekinoksu: Güneş 0° Koç yakınında olmalı
        eq_dt = datetime(2026, 3, 20, 17, 46, tzinfo=ist)
        snap_eq = build_chart_snapshot(eq_dt, 41.0082, 28.9784)
        sun_lon = snap_eq.planets["sun"].longitude
        self.assertTrue(sun_lon < 1.0 or sun_lon > 359.0, f"Beklenmeyen ekinoks Güneşi: {sun_lon}")
        self.assertEqual(sum(snap_eq.element_counts.values()), 10)
        self.assertIsNotNone(snap_eq.ascendant)
        self.assertIsNotNone(snap_eq.midheaven)
        quad_diff = (snap_eq.ascendant.longitude - snap_eq.midheaven.longitude) % 360.0
        self.assertTrue(0.0 < quad_diff < 180.0)

        # 15 Ağustos 2024 Merkür bilinen retro dönemindeydi
        merc_retro_dt = datetime(2024, 8, 15, 12, 0, tzinfo=timezone.utc)
        t_astro = to_astro_time(merc_retro_dt)
        self.assertGreater(t_astro.ut, 0)
        snap_retro = build_chart_snapshot(merc_retro_dt, 41.0082, 28.9784)
        self.assertTrue(snap_retro.planets["mercury"].retrograde)

    def test_full_astro_report_moon_and_aspects(self) -> None:
        cfg = Config(
            user_name="Yusuf",
            birth_date=date(2000, 9, 26),
            birth_time=time(4, 0),
            birth_city="Kastamonu",
            user_goal="Yazılım Mühendisliği",
        )
        # Doğum günü testi: 26 Eylül 2026
        bday = datetime(2026, 9, 26, 9, 0, tzinfo=ZoneInfo("Europe/Istanbul"))
        report = build_astro_report(cfg, now_local=bday)
        self.assertTrue(report.is_birthday)
        self.assertEqual(len(report.natal.planets), 10)
        self.assertEqual(len(report.transit.planets), 10)
        self.assertTrue(0.0 <= report.moon.illumination_pct <= 100.0)
        self.assertIsNotNone(report.moon.next_full_moon_local)
        self.assertIsNotNone(report.moon.next_new_moon_local)
        self.assertEqual(format_date_localized(bday, "tr"), "26 Eylül 2026, Cumartesi")

        card = format_chart_summary_card(report, "tr")
        self.assertIn("Kastamonu", card)
        self.assertIn("Yükselen", card)
        moon_card = format_moon_report(report, "tr")
        self.assertIn("Ay Evresi", moon_card)


class GeminiClientTests(unittest.TestCase):
    def test_model_discovery_ranking_and_api_fallback(self) -> None:
        models_json = {
            "models": [
                {"name": "models/gemini-2.5-flash-tts", "supportedGenerationMethods": ["generateContent"]},
                {"name": "models/gemini-2.5-flash", "supportedGenerationMethods": ["generateContent"]},
                {"name": "models/gemini-2.5-flash-lite", "supportedGenerationMethods": ["generateContent"]},
                {"name": "models/gemini-3-flash-preview", "supportedGenerationMethods": ["generateContent"]},
                {"name": "models/gemini-3-pro", "supportedGenerationMethods": ["generateContent"]},
                {"name": "models/gemini-3.5-flash-image", "supportedGenerationMethods": ["generateContent"]},
            ]
        }
        ranked = parse_and_rank_flash_models(models_json)
        self.assertEqual(
            ranked,
            ["gemini-3-flash-preview", "gemini-2.5-flash", "gemini-2.5-flash-lite"],
        )

        cfg = Config(
            gemini_api_key="AIzaTestKey",
            user_name="Yusuf",
            birth_date=date(2000, 9, 26),
            birth_time=time(4, 0),
            birth_city="Kastamonu",
        )
        report = build_astro_report(cfg, now_local=datetime(2026, 11, 20, 9, 0, tzinfo=ZoneInfo("Europe/Istanbul")))
        prompt = build_horoscope_prompt(report, mode="daily", lang="tr", tone="dengeli")
        self.assertIn("AKTİF RETROLAR", prompt)
        self.assertIn("NATAL ELEMENT", prompt)

        # İlk model 404 dönse bile sıradaki modelden başarılı yanıt almalı; API key header'da olmalı
        resp_404 = MagicMock(status_code=404, text="Not found")
        resp_200 = MagicMock(status_code=200)
        resp_200.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "<b>Harika bir gün</b> seni bekliyor!"}]}}]
        }

        with (
            patch("src.gemini_client.discover_flash_models", return_value=["gemini-3-flash-preview", "gemini-2.5-flash"]),
            patch("src.gemini_client.httpx.Client") as mock_client_cls,
        ):
            client_inst = mock_client_cls.return_value.__enter__.return_value
            client_inst.post.side_effect = [resp_404, resp_200]
            text, model_used = generate_astrology_text(cfg, report)

        self.assertEqual(model_used, "gemini-2.5-flash")
        self.assertIn("Harika bir gün", text)
        posted_url = client_inst.post.call_args_list[0].args[0]
        posted_headers = client_inst.post.call_args_list[0].kwargs["headers"]
        self.assertNotIn("AIzaTestKey", posted_url)
        self.assertEqual(posted_headers["x-goog-api-key"], "AIzaTestKey")

        # Tüm modeller hata verirse offline fallback üretmeli
        with (
            patch("src.gemini_client.discover_flash_models", return_value=[]),
            patch("src.gemini_client.httpx.Client") as mock_client_cls,
        ):
            mock_client_cls.return_value.__enter__.return_value.post.return_value = MagicMock(status_code=503, text="down")
            with patch("src.gemini_client.time.sleep"):
                fb_text, fb_model = generate_astrology_text(cfg, report)
        self.assertEqual(fb_model, "offline_fallback")
        self.assertIn("Transit Güneş", fb_text)
        self.assertIn("Bugünün", build_offline_fallback(report))


class TelegramAndCommandTests(unittest.TestCase):
    def test_sanitize_tag_safe_chunking_and_commands(self) -> None:
        dirty = "```html\n<style>body{color:red}</style><div>**Merhaba**</div><i>Dünya\n<p>Test</p>```"
        cleaned = sanitize_telegram_html(dirty)
        self.assertNotIn("<style>", cleaned)
        self.assertNotIn("<div>", cleaned)
        self.assertIn("<b>Merhaba</b>", cleaned)

        long_html = "<b>Başlık\n" + "\n".join(f"Satır {i}: " + ("a" * 80) for i in range(60)) + "</b>"
        chunks = split_telegram_message(long_html, max_length=1200)
        self.assertGreater(len(chunks), 2)
        self.assertTrue(chunks[0].endswith("</b>"))
        self.assertTrue(chunks[1].startswith("<b>"))

        self.assertEqual(parse_bot_command("/burç@TestBot"), ("burc", []))
        self.assertEqual(parse_bot_command("/UYUM İkizler"), ("uyum", ["İkizler"]))
        self.assertEqual(parse_bot_command("normal mesaj"), (None, []))

        cfg = Config(
            bot_token="123:BOT",
            chat_ids=["12345"],
            gemini_api_key="AIzaTest",
            birth_date=date(2000, 9, 26),
            birth_time=time(4, 0),
            birth_city="Kastamonu",
        )
        ay_reply = handle_command("ay", [], cfg)
        self.assertIn("Ay Evresi", ay_reply)

        mock_tg = MagicMock(spec=TelegramClient)
        mock_tg.set_my_commands.return_value = True
        mock_tg.get_updates.return_value = [
            {"update_id": 50, "message": {"chat": {"id": 99999}, "text": "/yardim"}},
            {"update_id": 51, "message": {"chat": {"id": 12345}, "text": "/retro"}},
        ]
        handled, max_uid = process_telegram_commands(cfg, register_menu=True, client_factory=lambda: mock_tg)
        self.assertEqual(handled, 1)
        self.assertEqual(max_uid, 51)
        mock_tg.send_message.assert_called_once()
        self.assertEqual(mock_tg.send_message.call_args.kwargs["chat_ids_override"], ["12345"])

    def test_cli_chart_only_smoke(self) -> None:
        with patch.dict(os.environ, {"BIRTH_DATE": "2000-09-26", "BIRTH_CITY": "Kastamonu"}, clear=False):
            code = cli_main(["--chart-only"])
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
