
from app.engines.assets.scorecard import (
    build_scorecard
)


from app.engines.assets.factors import (
    build_asset_factors
)




def build_dollar_score(
    macro
):


    factors = build_asset_factors(
        "dollar",
        macro
    )


    score = (

        weighted_score(factors)

    )


    return build_scorecard(

        "Dollar",

        score,

        factors

    )





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

