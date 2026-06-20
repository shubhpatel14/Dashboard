from __future__ import annotations

from typing import Any

from app.services.macro_interpreter import explain_trend, score_bias, tone_state
from app.models.scoring import clamp_score, normalize, weighted_average


def trend_indicator(
    name: str,
    current: float,
    previous: float,
    direction_score: float,
    momentum_score: float,
    lower_is_bullish: bool = False,
    **extra: Any,
) -> dict[str, Any]:
    change = current - previous
    final_score = weighted_average([(direction_score, 60), (momentum_score, 40)])
    row = {
        "name": name,
        "current": round(current, 4),
        "previous": round(previous, 4),
        "change": round(change, 4),
        "direction_score": clamp_score(direction_score),
        "momentum_score": clamp_score(momentum_score),
        "final_score": final_score,
        "score": final_score,
        "bias": score_bias(final_score),
        "lower_is_bullish": lower_is_bullish,
        "trend_state": tone_state(final_score),
        "release_type": "macro_trend",
    }
    row.update(extra)
    row["explanation"] = explain_trend(row)
    return row


def trend_scores(
    current: float,
    previous: float,
    change: float,
    low: float,
    high: float,
    lower_is_bullish: bool = False,
) -> tuple[float, float]:
    direction_value = -current if lower_is_bullish else current
    direction_low = -high if lower_is_bullish else low
    direction_high = -low if lower_is_bullish else high
    momentum_value = -change if lower_is_bullish else change

    return (
        normalize(direction_value, direction_low, direction_high),
        normalize(momentum_value, -abs(high - low), abs(high - low)),
    )


