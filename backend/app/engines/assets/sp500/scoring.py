
from app.engines.assets.scorecard import (
    build_scorecard
)


from app.engines.assets.factors import (
    build_asset_factors,
    weighted_score
)




def build_sp500_score(
    macro
):


    weights = {'growth': 0.35, 'liquidity': 0.3, 'sentiment': 0.2, 'credit': 0.15}


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

        "SP500",

        score,

        asset_factors

    )





def build_sp500_engine(
    macro
):


    return build_sp500_score(
        macro
    )

