
from app.engines.assets.scorecard import (
    build_scorecard
)


from app.engines.assets.factors import (
    build_asset_factors,
    weighted_score
)




def build_gold_score(
    macro
):


    weights = {'real_yield_support': 0.25, 'dollar_weakness': 0.2, 'inflation_hedge': 0.25, 'safe_haven': 0.2, 'liquidity': 0.1}


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

        "Gold",

        score,

        asset_factors

    )





def build_gold_engine(
    macro
):


    return build_gold_score(
        macro
    )

