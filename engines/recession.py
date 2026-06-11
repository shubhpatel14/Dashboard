from data.fred_client import (
    get_current_value,
    get_previous_value,
    get_series
)

from engines.helpers import (
    build_change_indicator,
    build_level_indicator,
    finalize_engine,
    score_level
)

from models.scoring import indicator_result


T10Y2Y = "T10Y2Y"
UNRATE = "UNRATE"
HY_SPREAD = "BAMLH0A0HYM2"
ICSA = "ICSA"


def build_yield_curve_indicator():

    series = get_series(T10Y2Y)
    current = get_current_value(series)
    previous = get_previous_value(series)
    change = current - previous
    score = score_level(
        current,
        -1,
        2
    )

    return indicator_result(
        current,
        previous,
        change,
        score
    )


def build_recession_engine():

    output = {
        "YIELD_CURVE": build_yield_curve_indicator(),
        "UNEMPLOYMENT_RATE": build_level_indicator(
            UNRATE,
            3.5,
            7,
            lower_is_bullish=True
        ),
        "HY_SPREAD_LEVEL": build_level_indicator(
            HY_SPREAD,
            2,
            8,
            lower_is_bullish=True
        ),
        "INITIAL_CLAIMS_WEEKLY_CHANGE": build_change_indicator(
            ICSA,
            "mom",
            -15,
            15,
            lower_is_bullish=True
        )
    }

    weighted_scores = [
        (
            output["YIELD_CURVE"]["score"],
            35
        ),
        (
            output["UNEMPLOYMENT_RATE"]["score"],
            25
        ),
        (
            output["HY_SPREAD_LEVEL"]["score"],
            25
        ),
        (
            output["INITIAL_CLAIMS_WEEKLY_CHANGE"]["score"],
            15
        )
    ]

    final = finalize_engine(
        weighted_scores,
        output
    )

    final["recession_probability"] = round(
        100 - final["score"],
        2
    )

    return final
