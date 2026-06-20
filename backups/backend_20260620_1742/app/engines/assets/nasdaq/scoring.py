
from app.engines.assets.scorecard import (
    build_scorecard
)


from app.engines.assets.factors import (
    build_asset_factors,
    weighted_score
)




def build_nasdaq_score(
    macro
):


    weights = {'liquidity': 0.45, 'growth': 0.25, 'sentiment': 0.2, 'rates': 0.1}


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

        "Nasdaq",

        score,

        asset_factors

    )





def build_nasdaq_engine(
    macro
):


    return build_nasdaq_score(
        macro
    )

