from engines.helpers import (
    build_level_indicator,
    finalize_engine
)


HY_SPREAD = "BAMLH0A0HYM2"
IG_SPREAD = "BAMLC0A0CM"
TED_SPREAD = "TEDRATE"


def build_credit_engine():

    output = {
        "HY_SPREAD_LEVEL": build_level_indicator(
            HY_SPREAD,
            2,
            8,
            lower_is_bullish=True
        ),
        "IG_SPREAD_LEVEL": build_level_indicator(
            IG_SPREAD,
            0.5,
            3,
            lower_is_bullish=True
        ),
        "TED_SPREAD_LEVEL": build_level_indicator(
            TED_SPREAD,
            0,
            1,
            lower_is_bullish=True
        )
    }

    weighted_scores = [
        (
            output["HY_SPREAD_LEVEL"]["score"],
            50
        ),
        (
            output["IG_SPREAD_LEVEL"]["score"],
            30
        ),
        (
            output["TED_SPREAD_LEVEL"]["score"],
            20
        )
    ]

    return finalize_engine(
        weighted_scores,
        output
    )
