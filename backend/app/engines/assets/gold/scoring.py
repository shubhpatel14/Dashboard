
from app.engines.assets.scorecard import (
    build_scorecard
)


from app.engines.assets.factors import (
    build_asset_factors
)




def build_gold_score(
    macro
):


    factors = build_asset_factors(
        "gold",
        macro
    )


    score = (

        weighted_score(factors)

    )


    return build_scorecard(

        "Gold",

        score,

        factors

    )





def build_gold_engine():


    from app.services.regime_service import (
        build_regime_engine
    )


    regime = build_regime_engine()


    macro = regime[
        "macro"
    ]


    return build_gold_score(
        macro
    )

