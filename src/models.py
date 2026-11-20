"""Astrolojik konum, ay evresi, açı ve rapor veri modelleri."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class PlanetPosition:
    """Tek bir gökcisminin ekliptik konumu, burç derecesi ve retro durumu."""

    key: str
    name_tr: str
    name_en: str
    longitude: float  # [0, 360) Gerçek ekliptik boylam (ECT)
    sign_index: int  # 0..11
    sign_tr: str
    sign_en: str
    sign_symbol: str
    degree: int  # 0..29
    minute: int  # 0..59
    retrograde: bool = False
    speed_deg_per_day: float = 0.0

    def format_degree(self, lang: str = "tr") -> str:
        sign = self.sign_tr if lang == "tr" else self.sign_en
        retro = " ℞" if self.retrograde else ""
        return f"{self.sign_symbol} {self.degree:02d}°{self.minute:02d}' {sign}{retro}"


@dataclass(frozen=True)
class MoonPhaseInfo:
    """Anlık Ay evresi, aydınlanma yüzdesi ve yakın Ay/Tutulma olayları."""

    angle_deg: float  # [0, 360) 0=Yeni Ay, 90=İlk Dördün, 180=Dolunay, 270=Son Dördün
    illumination_pct: float  # 0.0 .. 100.0
    phase_key: str  # new_moon, waxing_crescent, first_quarter, ...
    name_tr: str
    name_en: str
    emoji: str
    is_special_now: bool = False  # Yeni Ay / Dolunay ±24 saat içinde mi
    next_new_moon_local: Optional[datetime] = None
    next_full_moon_local: Optional[datetime] = None
    nearby_eclipse_tr: Optional[str] = None
    nearby_eclipse_en: Optional[str] = None


@dataclass(frozen=True)
class Aspect:
    """Transit gezegen ile natal gezegen/nokta arasındaki major açı."""

    transit_key: str
    transit_name_tr: str
    transit_name_en: str
    natal_key: str
    natal_name_tr: str
    natal_name_en: str
    aspect_key: str  # conjunction, sextile, square, trine, opposition
    aspect_name_tr: str
    aspect_name_en: str
    symbol: str
    exact_angle: int
    orb: float
    nature: str  # harmonik, dinamik, nötr


@dataclass(frozen=True)
class ChartSnapshot:
    """Natal veya anlık (transit) gökyüzü haritası anlık görüntüsü."""

    moment_local: datetime
    latitude: float
    longitude: float
    planets: dict[str, PlanetPosition]
    ascendant: Optional[PlanetPosition] = None
    midheaven: Optional[PlanetPosition] = None
    element_counts: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class AstroReport:
    """Doğum ve anlık transit verilerini birleştiren tam astrolojik rapor."""

    user_name: str
    birth_city: str
    user_goal: str
    report_time_local: datetime
    natal: ChartSnapshot
    transit: ChartSnapshot
    moon: MoonPhaseInfo
    aspects: list[Aspect] = field(default_factory=list)
    active_retrogrades: list[PlanetPosition] = field(default_factory=list)
    is_birthday: bool = False
    is_monday: bool = False
    is_first_of_month: bool = False
    partner_sign: Optional[str] = None
