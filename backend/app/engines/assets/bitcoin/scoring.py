
from app.engines.assets.scorecard import (
    build_scorecard
)


from app.engines.assets.factors import (
    build_asset_factors,
    weighted_score
)




def build_bitcoin_score(
    macro
):


    weights = {'liquidity': 0.5, 'risk_appetite': 0.3, 'macro_momentum': 0.2}


    all_factors = build_asset_factors(
        macro
    )


    score = weighted_score(

        all_factors,

        weights

    )


    # =============================
    # FILTER ONLY THIS ASSET FACTORS
    # =============================

    asset_factors = {

        key:
        all_factors.get(
            key,
            50
        )

        for key
        in weights.keys()

    }



    return build_scorecard(

        "Bitcoin",

        score,

        asset_factors

    )





def build_bitcoin_engine(
    macro
):


    return build_bitcoin_score(
        macro
    )

