
from app.engines.assets.scorecard import (
    build_scorecard
)


from app.engines.assets.factors import (
    build_asset_factors,
    weighted_score
)




def build_dollar_score(
    macro
):


    weights = {'rates': 0.35, 'safe_haven': 0.3, 'liquidity': 0.2, 'inflation': 0.15}


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

        "Dollar",

        score,

        asset_factors

    )





def build_dollar_engine(
    macro
):


    return build_dollar_score(
        macro
    )

