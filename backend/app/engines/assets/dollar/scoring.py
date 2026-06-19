
from app.engines.assets.scorecard import build_scorecard


def build_dollar_score(macro):

    score=(

        macro["rates"] * 0.35

        +

        (100-macro["growth"]) * 0.20

        +

        (100-macro["credit"]) * 0.25

        +

        (100-macro["liquidity"]) * 0.20

    )


    return build_scorecard(

        "US Dollar",

        score,

        {
            "rates":macro["rates"],
            "risk":100-macro["credit"],
            "growth_weakness":100-macro["growth"],
            "liquidity_tightness":100-macro["liquidity"]
        }

    )


# =================================
# ENGINE REGISTRY COMPATIBILITY
# =================================




def build_dollar_engine():

    from app.services.regime_service import (
        build_regime_engine
    )


    regime = build_regime_engine()


    macro = regime[
        "macro"
    ]


    return build_dollar_score(
        macro
    )
