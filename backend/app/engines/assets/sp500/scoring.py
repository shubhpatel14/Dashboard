
from app.engines.assets.factors import weighted_score

from app.engines.assets.scorecard import (
    build_scorecard
)


from app.engines.assets.factors import (
    build_asset_factors
)




def build_sp500_score(
    macro
):


    factors = build_asset_factors(
        "sp500",
        macro
    )


    score = (

        weighted_score(factors)

    )


    return build_scorecard(

        "SP500",

        score,

        factors

    )





def build_sp500_engine():


    from app.services.regime_service import (
        build_regime_engine
    )


    regime = build_regime_engine()


    macro = regime[
        "macro"
    ]


    return build_sp500_score(
        macro
    )

