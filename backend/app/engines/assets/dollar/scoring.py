
from app.engines.assets.scorecard import build_scorecard


def build_dollar_score(macro):

    score=(

        macro["rates"] * 0.35

        +

        (100-macro["growth"]) * 0.20

        +

        (100-macro["credit"]) * 0.25

        +

        (100-macro["liquidity"]) * 0.20

    )


    return build_scorecard(

        "US Dollar",

        score,

        {
            "rates":macro["rates"],
            "risk":100-macro["credit"],
            "growth_weakness":100-macro["growth"],
            "liquidity_tightness":100-macro["liquidity"]
        }

    )
