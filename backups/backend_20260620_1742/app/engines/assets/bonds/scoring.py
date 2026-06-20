
from app.engines.assets.scorecard import (
    build_scorecard
)


from app.engines.assets.factors import (
    build_asset_factors,
    weighted_score
)




def build_bonds_score(
    macro
):


    weights = {'rates': 0.3, 'inflation': 0.3, 'safe_haven': 0.25, 'growth': 0.15}


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

        "Bonds",

        score,

        asset_factors

    )





def build_bonds_engine(
    macro
):


    return build_bonds_score(
        macro
    )

