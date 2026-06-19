
from app.engines.assets.scorecard import (
    build_scorecard
)


from app.engines.assets.factors import (
    build_asset_factors
)




def build_bonds_score(
    macro
):


    factors = build_asset_factors(
        "bonds",
        macro
    )


    score = (

        weighted_score(factors)

    )


    return build_scorecard(

        "Bonds",

        score,

        factors

    )





def build_bonds_engine():


    from app.services.regime_service import (
        build_regime_engine
    )


    regime = build_regime_engine()


    macro = regime[
        "macro"
    ]


    return build_bonds_score(
        macro
    )

