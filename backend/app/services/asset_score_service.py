
from app.services.regime_service import (
    build_regime_engine
)


from app.engines.assets.sp500.scoring import (
    build_sp500_score
)

from app.engines.assets.nasdaq.scoring import (
    build_nasdaq_score
)

from app.engines.assets.gold.scoring import (
    build_gold_score
)

from app.engines.assets.bitcoin.scoring import (
    build_bitcoin_score
)

from app.engines.assets.bonds.scoring import (
    build_bonds_score
)

from app.engines.assets.dollar.scoring import (
    build_dollar_score
)





def build_asset_scores():


    regime = build_regime_engine()


    macro = regime[
        "macro"
    ]



    return {


        "regime":

            regime[
                "regime"
            ],


        "probabilities":

            regime[
                "probabilities"
            ],


        "transition":

            regime[
                "transition"
            ],



        "assets": {


            "sp500":

                build_sp500_score(
                    macro
                ),


            "nasdaq":

                build_nasdaq_score(
                    macro
                ),


            "gold":

                build_gold_score(
                    macro
                ),


            "bitcoin":

                build_bitcoin_score(
                    macro
                ),


            "bonds":

                build_bonds_score(
                    macro
                ),


            "dollar":

                build_dollar_score(
                    macro
                )

        }

    }
