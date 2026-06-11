from data.fred_client import (
    get_12m_value,
    get_current_date,
    get_current_value,
    get_previous_date,
    get_previous_value,
    get_series,
    get_value_months_ago
)

from models.scoring import (
    engine_result,
    indicator_result,
    normalize,
    pct_change,
    weighted_average
)
from engines.macro_trend import trend_scores


def percent_change(current, previous):

    return pct_change(current, previous)


def score_change(change, low, high, lower_is_bullish=False):

    value = -change if lower_is_bullish else change

    return normalize(
        value,
        low,
        high
    )


def score_level(current, low, high, lower_is_bullish=False):

    value = -current if lower_is_bullish else current
    minimum = -high if lower_is_bullish else low
    maximum = -low if lower_is_bullish else high

    return normalize(
        value,
        minimum,
        maximum
    )


def score_change_indicator(current, change, low, high, lower_is_bullish=False):

    level_score = score_change(
        current,
        low,
        high,
        lower_is_bullish=lower_is_bullish
    )
    direction_score = normalize(
        -change if lower_is_bullish else change,
        -20,
        20
    )

    return weighted_average(
        [
            (level_score, 70),
            (direction_score, 30)
        ]
    )


def build_change_indicator(
    code,
    period,
    low,
    high,
    lower_is_bullish=False,
    percent_change=True
):

    series = get_series(code)
    current_level = get_current_value(series)

    if period == "yoy":
        current_base = get_12m_value(series)
        previous_level = get_previous_value(series)
        previous_base = get_value_months_ago(series[1:], 12)
    else:
        current_base = get_previous_value(series)
        previous_level = get_previous_value(series)
        previous_base = series[2]["value"] if len(series) > 2 else previous_level

    if percent_change:
        current = pct_change(current_level, current_base)
        previous = pct_change(previous_level, previous_base)
    else:
        current = current_level - current_base
        previous = previous_level - previous_base

    change = current - previous
    direction_score, momentum_score = trend_scores(
        current,
        previous,
        change,
        low,
        high,
        lower_is_bullish=lower_is_bullish
    )
    score = weighted_average(
        [
            (direction_score, 60),
            (momentum_score, 40)
        ]
    )

    return indicator_result(
        current,
        previous,
        change,
        score,
        last_update=get_current_date(series).date().isoformat(),
        direction_score=direction_score,
        momentum_score=momentum_score,
        final_score=score,
        lower_is_bullish=lower_is_bullish,
        release_type="macro_trend",
        history={
            "type": "change",
            "code": code,
            "period": period,
            "percent_change": percent_change,
            "label": "YoY %" if period == "yoy" else "MoM %"
        }
    )


def build_level_indicator(
    code,
    low,
    high,
    lower_is_bullish=False
):

    series = get_series(code)
    current = get_current_value(series)
    previous = get_previous_value(series)
    change = current - previous
    level_score = score_level(
        current,
        low,
        high,
        lower_is_bullish=lower_is_bullish
    )
    momentum_score = normalize(
        -change if lower_is_bullish else change,
        -10,
        10
    )
    score = weighted_average(
        [
            (level_score, 80),
            (momentum_score, 20)
        ]
    )

    return indicator_result(
        current,
        previous,
        change,
        score,
        last_update=get_current_date(series).date().isoformat(),
        direction_score=level_score,
        momentum_score=momentum_score,
        final_score=score,
        lower_is_bullish=lower_is_bullish,
        release_type="macro_trend",
        history={
            "type": "level",
            "code": code
        }
    )


def finalize_engine(weighted_scores, data, **extra):

    score = weighted_average(weighted_scores)

    return engine_result(
        score,
        data,
        **extra
    )
