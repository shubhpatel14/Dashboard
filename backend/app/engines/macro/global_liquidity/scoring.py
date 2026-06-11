from app.engines.helpers.helpers import (
    build_change_indicator,
    finalize_engine
)


WALCL = "WALCL"
M2 = "M2SL"
DXY_PROXY = "DTWEXBGS"


def build_global_liquidity_engine():

    indicators = {
        "WALCL": {
            "code": WALCL,
            "weight": 40,
            "lower_is_bullish": False
        },
        "M2": {
            "code": M2,
            "weight": 40,
            "lower_is_bullish": False
        },
        "USD_INDEX": {
            "code": DXY_PROXY,
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


