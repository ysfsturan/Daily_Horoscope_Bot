"""Yapılandırma yükleme ve doğrulama modülü."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import date, datetime, time
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None


LINKEDIN_URL = "https://www.linkedin.com/in/yusufsamituran"


class ConfigError(Exception):
    """Geçersiz veya eksik ortam değişkeni yapılandırma hatası."""


def _parse_bool(raw: Optional[str], default: bool, name: str) -> bool:
    if raw is None or raw.strip() == "":
        return default
    norm = raw.strip().lower()
    if norm in {"1", "true", "yes", "on", "evet"}:
        return True
    if norm in {"0", "false", "no", "off", "hayir", "hayır"}:
        return False
    raise ConfigError(f"{name} geçerli bir mantıksal değer değil: {raw!r}")


def _parse_optional_float(
    raw: Optional[str], name: str, minimum: float, maximum: float
) -> Optional[float]:
    if raw is None or raw.strip() == "":
        return None
    try:
        val = float(raw.strip().replace(",", "."))
    except ValueError as exc:
        raise ConfigError(f"{name} geçerli bir sayı olmalıdır: {raw!r}") from exc
    if not (minimum <= val <= maximum):
        raise ConfigError(f"{name} [{minimum}, {maximum}] aralığında olmalıdır: {val}")
    return val


def parse_birth_date(raw: Optional[str]) -> date:
    """YYYY-MM-DD, YYYY/MM/DD veya GG.AA.YYYY biçimindeki doğum tarihini çözümler."""
    text = (raw or "2000-01-01").strip() or "2000-01-01"
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d.%m.%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ConfigError(
        f"BIRTH_DATE 'YYYY-AA-GG' veya 'GG.AA.YYYY' biçiminde olmalıdır: {text!r}"
    )


def parse_birth_time(raw: Optional[str]) -> time:
    """SS:DD biçimindeki doğum saatini çözümler."""
    text = (raw or "12:00").strip() or "12:00"
    norm = text.replace(".", ":")
    match = re.fullmatch(r"(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?", norm)
    if not match:
        raise ConfigError(f"BIRTH_TIME 'SS:DD' biçiminde olmalıdır: {text!r}")
    hour = int(match.group(1))
    minute = int(match.group(2))
    second = int(match.group(3) or "0")
    try:
        return time(hour=hour, minute=minute, second=second)
    except ValueError as exc:
        raise ConfigError(f"BIRTH_TIME geçersiz saat değeri: {text!r}") from exc


def parse_chat_ids(raw: Optional[str]) -> list[str]:
    """Virgül, noktalı virgül veya yeni satırla ayrılmış Telegram Chat ID listesini ayırır."""
    if not raw or not raw.strip():
        return []
    return [part.strip() for part in re.split(r"[,;\s]+", raw.strip()) if part.strip()]


@dataclass(frozen=True)
class Config:
    """Daily Horoscope Bot çalışma yapılandırması."""

    bot_token: Optional[str] = None
    chat_ids: list[str] = field(default_factory=list)
    gemini_api_key: Optional[str] = None
    user_name: str = "Kullanıcı"
    birth_date: date = field(default_factory=lambda: date(2000, 1, 1))
    birth_time: time = field(default_factory=lambda: time(12, 0))
    birth_city: str = "Istanbul"
    user_goal: str = "Genel"
    gemini_model: Optional[str] = None
    birth_lat: Optional[float] = None
    birth_lon: Optional[float] = None
    timezone_name: str = "Europe/Istanbul"
    language: str = "tr"
    tone: str = "dengeli"
    show_chart_summary: bool = True
    show_footer: bool = True
    partner_sign: Optional[str] = None


def load_config(
    *,
    env_file: Optional[Path] = None,
    require_telegram: bool = True,
    require_gemini: bool = True,
) -> Config:
    """Ortam değişkenlerinden ve varsa .env dosyasından yapılandırmayı yükler."""
    if load_dotenv is not None:
        if env_file is not None:
            load_dotenv(dotenv_path=env_file, override=False)
        else:
            default_env = Path(".env")
            if default_env.exists():
                load_dotenv(dotenv_path=default_env, override=False)

    bot_token = (
        os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or ""
    ).strip() or None
    chat_ids = parse_chat_ids(os.getenv("CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID"))
    gemini_api_key = (os.getenv("GEMINI_API_KEY") or "").strip() or None

    if require_telegram:
        if not bot_token:
            raise ConfigError("Eksik zorunlu ortam değişkeni: BOT_TOKEN")
        if not chat_ids:
            raise ConfigError("Eksik zorunlu ortam değişkeni: CHAT_ID")
    if require_gemini and not gemini_api_key:
        raise ConfigError("Eksik zorunlu ortam değişkeni: GEMINI_API_KEY")

    user_name = (os.getenv("USER_NAME") or "Kullanıcı").strip() or "Kullanıcı"
    birth_date = parse_birth_date(os.getenv("BIRTH_DATE"))
    birth_time = parse_birth_time(os.getenv("BIRTH_TIME"))
    birth_city = (os.getenv("BIRTH_CITY") or "Istanbul").strip() or "Istanbul"
    user_goal = (os.getenv("USER_GOAL") or "Genel").strip() or "Genel"
    gemini_model = (os.getenv("GEMINI_MODEL") or "").strip() or None

    birth_lat = _parse_optional_float(os.getenv("BIRTH_LAT"), "BIRTH_LAT", -90.0, 90.0)
    birth_lon = _parse_optional_float(os.getenv("BIRTH_LON"), "BIRTH_LON", -180.0, 180.0)
    if (birth_lat is None) != (birth_lon is None):
        raise ConfigError("BIRTH_LAT ve BIRTH_LON birlikte verilmelidir.")

    timezone_name = (os.getenv("TIMEZONE") or "Europe/Istanbul").strip() or "Europe/Istanbul"
    try:
        ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise ConfigError(f"Geçersiz saat dilimi (TIMEZONE): {timezone_name!r}") from exc

    raw_lang = (os.getenv("LANGUAGE") or "tr").strip().lower()
    language = raw_lang if raw_lang in {"tr", "en"} else "tr"

    raw_tone = (
        (os.getenv("TONE") or "dengeli")
        .strip()
        .replace("ı", "i")
        .replace("İ", "i")
        .lower()
    )
    tone = raw_tone if raw_tone in {"dengeli", "motive", "mistik", "kisa"} else "dengeli"

    show_chart_summary = _parse_bool(
        os.getenv("SHOW_CHART_SUMMARY"), True, "SHOW_CHART_SUMMARY"
    )
    show_footer = _parse_bool(os.getenv("SHOW_FOOTER"), True, "SHOW_FOOTER")
    partner_sign = (os.getenv("PARTNER_SIGN") or "").strip() or None

    return Config(
        bot_token=bot_token,
        chat_ids=chat_ids,
        gemini_api_key=gemini_api_key,
        user_name=user_name,
        birth_date=birth_date,
        birth_time=birth_time,
        birth_city=birth_city,
        user_goal=user_goal,
        gemini_model=gemini_model,
        birth_lat=birth_lat,
        birth_lon=birth_lon,
        timezone_name=timezone_name,
        language=language,
        tone=tone,
        show_chart_summary=show_chart_summary,
        show_footer=show_footer,
        partner_sign=partner_sign,
    )
