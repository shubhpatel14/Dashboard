from engines.helpers import (
    build_change_indicator,
    finalize_engine
)


M2 = "M2SL"
WALCL = "WALCL"
RRP = "RRPONTSYD"
BANK_RESERVES = "TOTRESNS"


def build_liquidity_engine():

    indicators = {
        "M2": {
            "code": M2,
            "weight": 40,
            "lower_is_bullish": False
        },
        "WALCL": {
            "code": WALCL,
            "weight": 30,
            "lower_is_bullish": False
        },
        "BANK_RESERVES": {
            "code": BANK_RESERVES,
            "weight": 10,
            "lower_is_bullish": False
        },
        "RRP": {
            "code": RRP,
            "weight": 20,
            "lower_is_bullish": True
        }
    }

    output = {}
    weighted_scores = []

    for name, info in indicators.items():

        result = build_change_indicator(
            info["code"],
            "yoy",
            -10,
            10,
            lower_is_bullish=info["lower_is_bullish"]
        )

        output[name] = result

        weighted_scores.append(
            (
                result["score"],
                info["weight"]
            )
        )

    return finalize_engine(
        weighted_scores,
        output
    )
