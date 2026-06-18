
from app.engines.assets.scorecard import build_scorecard


def build_nasdaq_score(macro):

    score = (
        macro["liquidity"] * 0.45
        +
        macro["growth"] * 0.20
        +
        macro["rates"] * 0.25
        +
        macro["credit"] * 0.10
    )


    return build_scorecard(

        "NASDAQ",

        score,

        {
            "liquidity": macro["liquidity"],
            "growth": macro["growth"],
            "rates": macro["rates"],
            "credit": macro["credit"]
        }

    )




def build_nasdaq_engine(macro):

    return build_nasdaq_score(macro)

