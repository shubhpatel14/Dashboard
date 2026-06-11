from pathlib import Path
from typing import Any

import pandas as pd

from app.core.config import get_settings
from app.services.macro_interpreter import interpret_category, interpret_indicator


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
    "global-liquidity": "Global Liquidity",
    "rates": "Rates",
    "inflation": "Inflation",
    "growth": "Growth",
    "labor": "Labor",
    "credit": "Credit",
    "sentiment": "Sentiment",
    "housing": "Housing",
    "recession": "Recession",
}


def _safe_float(value: Any, default: float = 50.0) -> float:
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return default


def _bias(score: float) -> str:
    if score >= 70:
        return "Bullish"
    if score <= 40:
        return "Bearish"
    return "Neutral"


def clean_label(value: Any) -> str:
    text = str(value or "N/A")
    text = text.encode("ascii", "ignore").decode("ascii").strip()
    return " ".join(text.split()) or "N/A"


def _history_path() -> Path:
    return get_settings().project_root / "dashboard_history.csv"


def dashboard_history(limit: int = 60) -> list[dict[str, Any]]:
    path = _history_path()
    if not path.exists():
        return []

    frame = pd.read_csv(path).tail(limit)
    return [
        {key: row[key] for key in frame.columns}
        for _, row in frame.iterrows()
    ]


def macro_category_history(category_slug: str, score: float) -> list[dict[str, Any]]:
    column_map = {
        "liquidity": "liquidity",
        "rates": "rates",
        "inflation": "inflation",
        "growth": "growth",
        "labor": "labor",
        "recession": "overall",
        "credit": "overall",
        "sentiment": "overall",
        "housing": "overall",
        "global-liquidity": "liquidity",
    }
    column = column_map.get(category_slug, "overall")
    rows = dashboard_history()

    if not rows:
        return [{"date": "Current", "score": score}]

    return [
        {"date": row.get("date"), "score": _safe_float(row.get(column), score)}
        for row in rows
    ]


def asset_history(asset_slug: str, score: float) -> list[dict[str, Any]]:
    rows = dashboard_history()
    if not rows:
        return [{"date": "Current", "score": score}]

    return [
        {"date": row.get("date"), "score": _safe_float(row.get("overall"), score)}
        for row in rows
    ]


def indicators_from_engine(engine: dict[str, Any]) -> list[dict[str, Any]]:
    data = engine.get("data") or {}
    indicators = []

    for key, values in data.items():
        if not isinstance(values, dict):
            continue
        if values.get("error"):
            continue

        score = _safe_float(values.get("score"))
        interpreted = interpret_indicator(key, values)
        interpreted["score"] = score
        interpreted["bias"] = values.get("bias") or _bias(score)
        indicators.append(interpreted)

    return indicators


def macro_category_intelligence(
    category_name: str,
    score: float,
    bias: str,
    indicators: list[dict[str, Any]],
) -> dict[str, Any]:
    return interpret_category(category_name, score, clean_label(bias), indicators)


def drivers_from_asset(engine: dict[str, Any]) -> list[dict[str, Any]]:
    indicators = indicators_from_engine(engine)
    if not indicators:
        return []

    weights = engine.get("weights", {})
    return [
        {
            "name": item["name"],
            "score": item["score"],
            "contribution": round(weights.get(item["name"].upper().replace(" ", "_"), 0), 2),
            "bias": item["bias"],
        }
        for item in indicators
    ]


def macro_summary(macro: dict[str, Any]) -> list[str]:
    scores = macro.get("scores", {})
    lines = []

    for label, score in scores.items():
        direction = "improving" if score >= 55 else "weakening" if score <= 45 else "neutral"
        lines.append(f"{label} {direction}")

    return lines[:4]


def asset_summary(asset_name: str, score: float, drivers: list[dict[str, Any]]) -> str:
    if not drivers:
        return f"{asset_name} has a {_bias(score).lower()} macro setup, but driver data is unavailable."

    leading = sorted(drivers, key=lambda row: row["score"], reverse=True)[:2]
    lagging = sorted(drivers, key=lambda row: row["score"])[:2]
    support = ", ".join(driver["name"].lower() for driver in leading)
    pressure = ", ".join(driver["name"].lower() for driver in lagging)
    return (
        f"{asset_name} remains {_bias(score).lower()} as {support} provide support, "
        f"while {pressure} create pressure."
    )
