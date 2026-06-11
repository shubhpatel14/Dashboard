from __future__ import annotations

from typing import Any


def score_bias(score: float) -> str:
    if score >= 80:
        return "Very Bullish"
    if score >= 65:
        return "Bullish"
    if score >= 45:
        return "Neutral"
    if score >= 25:
        return "Bearish"
    return "Very Bearish"


def tone_state(score: float) -> str:
    if score >= 60:
        return "positive"
    if score <= 40:
        return "negative"
    return "neutral"


def describe_surprise(
    name: str,
    surprise: float,
    surprise_score: float,
    lower_is_bullish: bool = False,
) -> str:
    if abs(surprise) < 0.0001:
        return "In line with expectations"

    positive_for_market = surprise < 0 if lower_is_bullish else surprise > 0
    
    if surprise_score >= 80:
        strength = "Strong"
    elif surprise_score >= 65:
        strength = "Moderate"
    elif surprise_score >= 45:
        strength = "Slight"
    elif surprise_score >= 25:
        strength = "Moderate"
    else:
        strength = "Strong"

    result = "Beat" if positive_for_market else "Miss"
    surprise_abs = abs(surprise)
    return f"{strength} {result} ({'+' if surprise > 0 else ''}{surprise_abs:.2f})"


def describe_trend(
    name: str,
    trend_change: float,
    trend_score: float,
    lower_is_bullish: bool = False,
) -> str:
    if abs(trend_change) < 0.0001:
        return "Little Changed"

    improving = trend_change < 0 if lower_is_bullish else trend_change > 0
    
    if "claim" in name.lower():
        direction = "Improving" if improving else "Rising"
    elif any(word in name.lower() for word in ["cpi", "pce", "ppi", "inflation"]):
        direction = "Cooling" if improving else "Heating Up"
    elif any(word in name.lower() for word in ["payroll", "employment"]):
        direction = "Accelerating" if improving else "Cooling"
    else:
        direction = "Improving" if improving else "Weakening"
    
    magnitude = "significantly" if abs(trend_score - 50) > 20 else "modestly"
    return f"{direction} {magnitude}"


def explain_release(row: dict[str, Any]) -> str:
    name = str(row.get("name") or "The release")
    actual = float(row.get("actual") or 0)
    forecast = float(row.get("forecast") or 0)
    previous = float(row.get("previous") or 0)
    surprise = float(row.get("surprise") or 0)
    trend_change = float(row.get("trend_change") or 0)
    surprise_score = float(row.get("surprise_score") or 50)
    lower_is_bullish = bool(row.get("lower_is_bullish"))

    surprise_positive = surprise < 0 if lower_is_bullish else surprise > 0
    trend_positive = trend_change < 0 if lower_is_bullish else trend_change > 0
    name_lower = name.lower()

    # Magnitude descriptors based on score distance from neutral
    def magnitude(score: float) -> str:
        if score >= 80:
            return "significantly"
        if score >= 70:
            return "notably"
        if score >= 60:
            return "moderately"
        if score >= 45:
            return "slightly"
        return "well"

    if any(word in name_lower for word in ["cpi", "pce", "ppi", "inflation"]):
        mag = magnitude(surprise_score)
        if surprise_positive and trend_positive:
            return f"Inflation cooled {mag} faster than expected and improved versus the prior release, increasing expectations for easier monetary policy."
        if surprise_positive and not trend_positive:
            return f"Inflation was {mag} cooler than expected, although the sequential trend remains sticky or elevated."
        if not surprise_positive and trend_positive:
            return f"Inflation improved versus the prior release but came in {mag} hotter than markets expected."
        return f"Inflation came in {mag} hotter than expected and moved in the wrong direction versus the prior release."

    if any(word in name_lower for word in ["payroll", "employment", "adp", "jolts", "job"]):
        mag = magnitude(surprise_score)
        if surprise_positive and not trend_positive:
            return f"Labor demand remains {mag} stronger than expected, although hiring momentum is gradually cooling."
        if surprise_positive and trend_positive:
            return f"Labor demand beat expectations {mag} and strengthened versus the prior release."
        if not surprise_positive and trend_positive:
            return f"Labor momentum improved from the prior release, but the headline disappointed expectations."
        return f"Labor data missed expectations and softened versus the prior release."

    if any(word in name_lower for word in ["unemployment", "claims"]):
        mag = magnitude(surprise_score)
        if surprise_positive and trend_positive:
            return f"Labor stress was {mag} lower than expected and improved versus the prior reading."
        if surprise_positive and not trend_positive:
            return f"Labor stress was {mag} lower than expected, although the trend deteriorated from the prior reading."
        if not surprise_positive and trend_positive:
            return f"Labor stress improved from the prior reading but was {mag} worse than expected."
        return f"Labor stress was {mag} worse than expected and deteriorated versus the prior reading."

    mag = magnitude(surprise_score)
    if surprise_positive and trend_positive:
        return f"{name} beat expectations {mag} and improved versus the prior release."
    if surprise_positive and not trend_positive:
        return f"{name} beat expectations {mag}, although momentum cooled versus the prior release."
    if not surprise_positive and trend_positive:
        return f"{name} improved versus the prior release but disappointed market expectations."
    return f"{name} missed expectations and weakened versus the prior release."


def explain_trend(row: dict[str, Any]) -> str:
    name = str(row.get("name") or "This indicator")
    change = float(row.get("change") or 0)
    lower_is_bullish = bool(row.get("lower_is_bullish"))
    improving = change < 0 if lower_is_bullish else change > 0

    if abs(change) < 0.0001:
        return f"{name} was broadly stable versus the previous reading."
    if improving:
        return f"{name} moved in a market-supportive direction, improving the macro input score."
    return f"{name} moved in a less supportive direction, reducing the macro input score."


# compatibility wrapper
def interpret_category(*args, **kwargs):

    try:
        return explain_trend(*args, **kwargs)

    except Exception:
        return "No interpretation available"



# compatibility wrapper
def interpret_indicator(*args, **kwargs):

    try:
        return explain_trend(*args, **kwargs)

    except Exception:
        return "No indicator interpretation available"
