from __future__ import annotations

import re
from datetime import date, timedelta
from functools import lru_cache
from typing import Any

from data.economic_calendar import build_economic_calendar
from engines.macro_interpreter import (
    describe_surprise,
    describe_trend,
    explain_release,
    score_bias,
    tone_state,
)
from models.scoring import clamp_score, weighted_average


RELEASE_ALIASES = {
    "NON_FARM_PAYROLL_CHANGE": ["non farm payroll", "nonfarm payroll", "payrolls"],
    "ADP_EMPLOYMENT_CHANGE": ["adp employment"],
    "JOLTS_JOB_OPENINGS": ["jolts"],
    "UNEMPLOYMENT_RATE": ["unemployment rate"],
    "INITIAL_CLAIMS_WEEKLY_CHANGE": ["initial jobless claims"],
    "CONTINUING_CLAIMS_WEEKLY_CHANGE": ["continuing claims"],
    "CPI_MOM": ["cpi mom"],
    "CPI_YOY": ["cpi yoy"],
    "CORE_CPI_MOM": ["core cpi mom"],
    "CORE_CPI_YOY": ["core cpi yoy"],
    "PCE_MOM": ["pce mom"],
    "PCE_YOY": ["pce yoy"],
    "CORE_PCE_MOM": ["core pce mom"],
    "CORE_PCE_YOY": ["core pce yoy"],
    "PPI_MOM": ["ppi mom"],
    "PPI_YOY": ["ppi yoy"],
    "CORE_PPI_MOM": ["core ppi mom"],
    "CORE_PPI_YOY": ["core ppi yoy"],
    "GDP_QOQ_ANNUALIZED": ["gdp qoq"],
    "GDP_YOY": ["gdp yoy"],
    "RETAIL_SALES_MOM": ["retail sales"],
    "CORE_RETAIL_SALES_MOM": ["core retail sales"],
    "ISM_MANUFACTURING_PMI": ["ism manufacturing pmi"],
    "ISM_SERVICES_PMI": ["ism services pmi"],
    "INDUSTRIAL_PRODUCTION_MOM": ["industrial production"],
    "CONSUMER_CONFIDENCE": ["consumer confidence"],
    "FED_RATE_DECISION": ["fomc rate decision", "fed rate decision"],
}

DEFAULT_SCALE = {
    "labor": 100.0,
    "inflation": 0.2,
    "growth": 1.0,
    "rates": 0.25,
}


def _event_scale(name: str, category: str) -> float:
    name_lower = name.lower()

    if "unemployment" in name_lower:
        return 0.2
    if "claims" in name_lower:
        return 25.0
    if "jolts" in name_lower:
        return 500.0
    if "payroll" in name_lower or "employment" in name_lower:
        return 75.0
    if any(word in name_lower for word in ["cpi", "pce", "ppi", "inflation"]):
        return 0.2
    if "rate" in name_lower or "yield" in name_lower:
        return 0.25
    if "pmi" in name_lower or "confidence" in name_lower:
        return 2.0
    return DEFAULT_SCALE.get(category, 1.0)


def _normalize_text(value: Any) -> str:
    text = str(value or "").lower()
    text = text.replace("m/m", "mom").replace("y/y", "yoy")
    text = re.sub(r"[^a-z0-9% ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_macro_number(value: Any) -> float | None:
    if value in [None, "", "N/A", "Pending", "--"]:
        return None

    text = str(value).strip().replace(",", "")
    multiplier = 1.0

    if text.endswith("%"):
        text = text[:-1]
    if text.endswith(("K", "k")):
        multiplier = 1.0
        text = text[:-1]
    elif text.endswith(("M", "m")):
        multiplier = 1000.0
        text = text[:-1]
    elif text.endswith(("B", "b")):
        multiplier = 1_000_000.0
        text = text[:-1]

    try:
        return float(text) * multiplier
    except ValueError:
        return None


def _score_delta(delta: float, denominator: float, lower_is_bullish: bool) -> float:
    if denominator <= 0:
        denominator = 1.0

    signed = -delta if lower_is_bullish else delta
    score = 50 + max(-40, min(40, (signed / denominator) * 40))
    return clamp_score(score)


def release_score(
    name: str,
    actual: float,
    forecast: float,
    previous: float,
    category: str,
    lower_is_bullish: bool = False,
) -> dict[str, Any]:
    surprise = actual - forecast
    trend_change = actual - previous
    scale = _event_scale(name, category)
    trend_scale = _event_scale(name, category)
    surprise_score = _score_delta(surprise, scale, lower_is_bullish)
    trend_score = _score_delta(trend_change, trend_scale, lower_is_bullish)
    final_score = weighted_average([(surprise_score, 70), (trend_score, 30)])

    row = {
        "name": name,
        "actual": round(actual, 4),
        "forecast": round(forecast, 4),
        "previous": round(previous, 4),
        "current": round(actual, 4),
        "change": round(trend_change, 4),
        "surprise": round(surprise, 4),
        "trend_change": round(trend_change, 4),
        "surprise_score": surprise_score,
        "trend_score": trend_score,
        "final_score": final_score,
        "score": final_score,
        "bias": score_bias(final_score),
        "lower_is_bullish": lower_is_bullish,
        "trend_state": tone_state(final_score),
        "release_type": "economic_release",
        "market_surprise": describe_surprise(
            name,
            surprise,
            surprise_score,
            lower_is_bullish=lower_is_bullish,
        ),
        "trend": describe_trend(
            name,
            trend_change,
            trend_score,
            lower_is_bullish=lower_is_bullish,
        ),
    }
    row["explanation"] = explain_release(row)
    return row


@lru_cache(maxsize=1)
def _recent_calendar_events() -> tuple[dict[str, Any], ...]:
    today = date.today()
    calendar = build_economic_calendar(
        start_date=today - timedelta(days=45),
        end_date=today,
        horizon_days=0,
        lookback_days=45,
    )
    return tuple(calendar.get("events", []))


def clear_release_cache() -> None:
    _recent_calendar_events.cache_clear()


def latest_release_event(key: str) -> dict[str, Any] | None:
    aliases = RELEASE_ALIASES.get(key, [])
    if not aliases:
        return None

    candidates = []
    for event in _recent_calendar_events():
        normalized = _normalize_text(event.get("event"))
        if not any(alias in normalized for alias in aliases):
            continue
        actual = parse_macro_number(event.get("actual"))
        forecast = parse_macro_number(event.get("forecast"))
        previous = parse_macro_number(event.get("previous"))
        if actual is None or forecast is None or previous is None:
            continue
        candidates.append(event)

    if not candidates:
        return None

    return sorted(
        candidates,
        key=lambda item: (item.get("date") or "", item.get("time") or ""),
        reverse=True,
    )[0]


def release_from_calendar(
    key: str,
    name: str,
    category: str,
    lower_is_bullish: bool = False,
) -> dict[str, Any] | None:
    event = latest_release_event(key)
    if not event:
        return None

    actual = parse_macro_number(event.get("actual"))
    forecast = parse_macro_number(event.get("forecast"))
    previous = parse_macro_number(event.get("previous"))
    if actual is None or forecast is None or previous is None:
        return None

    row = release_score(
        name=name,
        actual=actual,
        forecast=forecast,
        previous=previous,
        category=category,
        lower_is_bullish=lower_is_bullish,
    )
    row.update(
        {
            "last_update": event.get("date", "N/A"),
            "last_updated": event.get("date", "N/A"),
            "source": event.get("source", "Economic Calendar"),
            "calendar_event": event.get("event"),
        }
    )
    return row

