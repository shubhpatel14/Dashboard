from engines.helpers import (
    build_level_indicator,
    finalize_engine
)


VIX = "VIXCLS"
UMCSENT = "UMCSENT"
NFCI = "NFCI"


def build_sentiment_engine():

    output = {
        "VIX_LEVEL": build_level_indicator(
            VIX,
            12,
            35,
            lower_is_bullish=True
        ),
        "CONSUMER_SENTIMENT_LEVEL": build_level_indicator(
            UMCSENT,
            50,
            100
        ),
        "FINANCIAL_CONDITIONS_INDEX_LEVEL": build_level_indicator(
            NFCI,
            -1,
            1,
            lower_is_bullish=True
        )
    }

    weighted_scores = [
        (
            output["VIX_LEVEL"]["score"],
            40
        ),
        (
            output["CONSUMER_SENTIMENT_LEVEL"]["score"],
            35
        ),
        (
            output["FINANCIAL_CONDITIONS_INDEX_LEVEL"]["score"],
            25
        )
    ]

    return finalize_engine(
        weighted_scores,
        output
    )
