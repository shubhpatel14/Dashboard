from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from app.core.config import get_settings


DISPLAY_NAMES = {
    "gold": "Gold",
    "bitcoin": "Bitcoin",
    "sp500": "SP500",
    "nasdaq": "Nasdaq",
    "dollar": "Dollar",
    "bonds": "Bonds",
}

MACRO_LABELS = {
    "liquidity": "Liquidity",
    "global_liquidity": "Global Liquidity",
    "global-liquidity": "Global Liquidity",
    "rates": "Rates",
    "inflation": "Inflation",
    "growth": "Growth",
    "labor": "Labor",
    "credit": "Credit",
    "sentiment": "Sentiment",
    "housing": "Housing",
    "recession": "Recession",
    "trend": "Trend",
}


def _safe_float(value: Any, default: float = 50.0) -> float:
    try:
        number = float(value)
        if pd.isna(number):
            return default
        return round(number, 2)
    except (TypeError, ValueError):
        return default


def _safe_text(value: Any, default: str = "N/A") -> str:
    text = str(value if value not in (None, "") else default)
    text = text.encode("ascii", "ignore").decode("ascii").strip()
    return " ".join(text.split()) or default


def _bias(score: float) -> str:
    if score >= 65:
        return "Bullish"
    if score <= 35:
        return "Bearish"
    return "Neutral"


def _trend_state(score: float) -> str:
    if score >= 60:
        return "positive"
    if score <= 40:
        return "negative"
    return "neutral"


def _trend_label(score: float) -> str:
    if score >= 60:
        return "Improving"
    if score <= 40:
        return "Worsening"
    return "Stable"


def _impact(score: float) -> str:
    if score >= 60:
        return "Positive macro impact"
    if score <= 40:
        return "Negative macro impact"
    return "Neutral macro impact"


def clean_label(value: Any, default: str = "N/A") -> str:
    return _safe_text(value, default)


def _history_path() -> Path:
    return get_settings().project_root / "dashboard_history.csv"


def dashboard_history(limit: int = 120) -> list[dict[str, Any]]:
    path = _history_path()
    if not path.exists():
        return []

    try:
        frame = pd.read_csv(path).tail(limit)
    except Exception:
        return []

    rows: list[dict[str, Any]] = []
    for _, row in frame.iterrows():
        rows.append({key: row.get(key) for key in frame.columns})
    return rows


def macro_category_history(category_slug: str, score: float) -> list[dict[str, Any]]:
    column_map = {
        "liquidity": "liquidity",
        "global_liquidity": "liquidity",
        "global-liquidity": "liquidity",
        "rates": "rates",
        "inflation": "inflation",
        "growth": "growth",
        "labor": "labor",
        "recession": "overall",
        "credit": "overall",
        "sentiment": "overall",
        "housing": "overall",
        "trend": "overall",
    }
    column = column_map.get(category_slug, "overall")
    rows = dashboard_history()

    if not rows:
        return [{"date": "Current", "score": score}]

    return [
        {"date": _safe_text(row.get("date"), "Current"), "score": _safe_float(row.get(column), score)}
        for row in rows
    ]


def asset_history(asset_slug: str, score: float) -> list[dict[str, Any]]:
    rows = dashboard_history()
    if not rows:
        return [{"date": "Current", "score": score}]

    return [
        {"date": _safe_text(row.get("date"), "Current"), "score": _safe_float(row.get("overall"), score)}
        for row in rows
    ]


def _indicator_explanation(name: str, score: float, current: Any, previous: Any) -> str:
    bias = _bias(score).lower()
    return (
        f"{name} is reading {clean_label(current)} versus {clean_label(previous)} previously. "
        f"The current signal is {bias} for the macro model because it contributes to growth, inflation, "
        "liquidity, or risk appetite conditions."
    )


def _indicator_info(name: str, source: str, measures: str, score: float) -> str:
    return (
        f"Meaning: {name} tracks {measures or 'a macro input used by the scoring engine'}.\n"
        "Why it matters: changes in this indicator can shift expected policy, yields, USD, liquidity, "
        "and risk appetite.\n"
        "Formula: current reading versus previous reading, transformed by the existing scoring engine.\n"
        f"Current interpretation: {_impact(score)} with a score of {score}/100.\n"
        "Historical context: compare the current reading against the score history and percentile fields when available.\n"
        "Market impact: bullish readings generally support risk-on assets; bearish readings usually favor defensive posture.\n"
        f"Source: {source or 'Internal macro data pipeline'}."
    )


def indicators_from_engine(engine: dict[str, Any] | None) -> list[dict[str, Any]]:

        # =============================
    # MACRO SURPRISE EVENTS SUPPORT
    # =============================

    if "events" in engine:

        return [

            {
                "name": event.get(
                    "name"
                ),

                "actual": event.get(
                    "actual"
                ),

                "forecast": event.get(
                    "forecast"
                ),

                "previous": event.get(
                    "previous"
                ),

                "current_display":
                    f"{event.get('actual')} vs {event.get('forecast')}",

                "surprise": event.get(
                    "surprise"
                ),

                "trend": event.get(
                    "trend"
                ),

                "trend_state": event.get(
                    "trend_state"
                ),

                "score": event.get(
                    "score"
                ),

                "bias": event.get(
                    "bias"
                ),

                "weight": event.get(
                    "weight"
                ),

                "explanation": event.get(
                    "explanation"
                ),
            }

            for event in engine.get(
                "events",
                []
            )
        ]
    
    if not isinstance(engine, dict):
        return []

    data = engine.get("data", {})
    if not isinstance(data, dict):
        return []

    indicators: list[dict[str, Any]] = []
    count = max(len(data), 1)

    for index, (key, item) in enumerate(data.items()):
        if not isinstance(item, dict):
            continue

        score = _safe_float(item.get("score"), 50)
        weight = _safe_float(item.get("weight"), round(100 / count, 2))
        name = clean_label(item.get("name", key), key)
        source = clean_label(item.get("source", item.get("provider", "Internal model")))
        measures = clean_label(item.get("measures", item.get("description", "macro conditions")))
        current = item.get("current", item.get("actual", "N/A"))
        previous = item.get("previous", "N/A")
        change = item.get("change", item.get("trend_change", "N/A"))
        state = item.get("trend_state") or _trend_state(score)

        indicators.append({
            "key": clean_label(item.get("key", key), f"indicator-{index}"),
            "name": name,
            "code": clean_label(item.get("code", key)),
            "source": source,
            "measures": measures,
            "score": score,
            "bias": clean_label(item.get("bias", _bias(score))),
            "current": current,
            "previous": previous,
            "change": change,
            "current_display": clean_label(item.get("current_display", current)),
            "previous_display": clean_label(item.get("previous_display", previous)),
            "change_display": clean_label(item.get("change_display", change)),
            "trend": clean_label(item.get("trend", _trend_label(score))),
            "trend_state": clean_label(state, _trend_state(score)),
            "impact": clean_label(item.get("impact", _impact(score))),
            "market_impact": clean_label(item.get("market_impact", _impact(score))),
            "last_update": clean_label(item.get("last_update", item.get("last_updated", "N/A"))),
            "explanation": clean_label(item.get("explanation", _indicator_explanation(name, score, current, previous))),
            "info": _indicator_info(name, source, measures, score),
            "weight": weight,
            "contribution": round((score - 50) * (weight / 100), 2),
            "percentile": _safe_float(item.get("percentile"), 50),
            "z_score": _safe_float(item.get("z_score"), 0),
            "distance_from_average": _safe_float(item.get("distance_from_average"), 0),
        })

    return indicators


def drivers_from_asset(engine: dict[str, Any] | None) -> list[dict[str, Any]]:
    drivers: list[dict[str, Any]] = []

    for item in indicators_from_engine(engine):
        score = _safe_float(item.get("score"), 50)
        drivers.append({
            "name": item.get("name", "Unknown"),
            "score": score,
            "bias": item.get("bias", _bias(score)),
            "contribution": item.get("contribution", 0),
            "impact": _impact(score),
            "current": item.get("current", "N/A"),
            "change": item.get("change", "N/A"),
            "last_updated": item.get("last_update", "N/A"),
        })

    return drivers


def macro_summary(macro: dict[str, Any] | None) -> list[str]:
    if not isinstance(macro, dict):
        return ["Macro conditions are neutral while data availability is limited."]

    scores = macro.get("scores", {})
    if not isinstance(scores, dict) or not scores:
        score = _safe_float(macro.get("score"), 50)
        return [f"Macro conditions remain {_bias(score).lower()} with an overall score of {score}."]

    ordered = sorted(scores.items(), key=lambda item: abs(_safe_float(item[1]) - 50), reverse=True)
    lines = ["Macro conditions remain neutral as cross-asset signals are mixed."]

    for label, value in ordered[:4]:
        score = _safe_float(value)
        state = "supportive" if score >= 60 else "tightening" if score <= 40 else "balanced"
        lines.append(f"{clean_label(label).title()}: {state} ({score}/100)")

    return lines


def asset_summary(asset_name: str, score: float, drivers: list[dict[str, Any]]) -> str:
    if not drivers:
        return f"{asset_name} has a {_bias(score).lower()} macro setup, but driver data is unavailable."

    leading = sorted(drivers, key=lambda row: _safe_float(row.get("score")), reverse=True)[:2]
    lagging = sorted(drivers, key=lambda row: _safe_float(row.get("score")))[:2]
    support = ", ".join(clean_label(driver.get("name")).lower() for driver in leading)
    pressure = ", ".join(clean_label(driver.get("name")).lower() for driver in lagging)
    return (
        f"{asset_name} remains {_bias(score).lower()} as {support} provide support, "
        f"while {pressure} create pressure."
    )


def macro_category_intelligence(
    name: str,
    score: float,
    bias: str,
    indicators: list[dict[str, Any]]
) -> dict[str, Any]:

    drivers = []


    # ==========================
    # MACRO SURPRISE SUPPORT
    # ==========================

    if indicators and "actual" in indicators[0]:

        for indicator in indicators:

            drivers.append(
                {
                    "name": indicator.get(
                        "name",
                        "Unknown"
                    ),

                    "trend": indicator.get(
                        "bias",
                        "Neutral"
                    ),

                    "trend_state": indicator.get(
                        "trend_state",
                        "neutral"
                    ),

                    "value": (
                        f"Actual {indicator.get('actual')} "
                        f"vs Forecast {indicator.get('forecast')}"
                    ),

                    "score": _safe_float(
                        indicator.get(
                            "score"
                        ),
                        50
                    ),

                    "contribution": indicator.get(
                        "surprise",
                        0
                    ),

                    "weight": indicator.get(
                        "weight",
                        10
                    ),

                    "explanation": indicator.get(
                        "explanation",
                        ""
                    ),
                }
            )


        strongest = sorted(
            indicators,
            key=lambda item:
            abs(
                _safe_float(
                    item.get("score"),
                    50
                )
                - 50
            ),
            reverse=True
        )[:2]


        driver_text = " while ".join(
            clean_label(
                item.get("name")
            ).lower()

            for item in strongest
        )


        return {

    "trend": _trend_label(score),

    "summary": (
        f"{name.replace('_',' ')} is currently "
        f"{bias.lower()} as {driver_text} "
        "are driving the latest economic surprise signal."
    ),

    "drivers": drivers,
}
    # ==========================
    # NORMAL OLD MACRO ENGINES
    # ==========================

    for indicator in indicators:

        indicator_score = _safe_float(
            indicator.get(
                "score"
            ),
            50
        )


        drivers.append(
            {
                "name": indicator.get(
                    "name",
                    "Unknown"
                ),

                "trend": indicator.get(
                    "trend",
                    _trend_label(
                        indicator_score
                    )
                ),

                "trend_state": indicator.get(
                    "trend_state",
                    _trend_state(
                        indicator_score
                    )
                ),

                "value": indicator.get(
                    "current_display",
                    "N/A"
                ),

                "score": indicator_score,

                "contribution": indicator.get(
                    "contribution",
                    0
                ),

                "weight": indicator.get(
                    "weight",
                    10
                ),
            }
        )


    if indicators:

        strongest = sorted(
            indicators,
            key=lambda item:
            abs(
                _safe_float(
                    item.get("score")
                )
                - 50
            ),
            reverse=True
        )[:2]


        driver_text = " while ".join(
            clean_label(
                item.get("name")
            ).lower()

            for item in strongest
        )


        summary = (
            f"{name} remains {bias.lower()} as "
            f"{driver_text} shape the current macro signal."
        )


    else:

        summary = (
            f"{name} remains {bias.lower()} "
            "with limited indicator detail available."
        )


    return {
        "trend": _trend_label(
            score
        ),

        "summary": summary,

        "drivers": drivers,
    }
