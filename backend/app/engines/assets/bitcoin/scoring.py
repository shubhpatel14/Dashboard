
from app.engines.assets.scorecard import build_scorecard


def build_bitcoin_score(macro):

    score = (

        macro["liquidity"] * 0.55

        +

        macro["rates"] * 0.25

        +

        macro["growth"] * 0.20

    )


    return build_scorecard(

        "Bitcoin",

        score,

        {
            "liquidity": macro["liquidity"],
            "rates": macro["rates"],
            "growth": macro["growth"]
        }

    )




def build_bitcoin_engine(macro):

    return build_bitcoin_score(macro)

