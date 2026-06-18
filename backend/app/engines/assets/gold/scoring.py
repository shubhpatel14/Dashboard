
from app.engines.assets.scorecard import build_scorecard


def build_gold_score(macro):

    score = (

        macro["inflation"] * 0.35

        +

        (100 - macro["rates"]) * 0.35

        +

        (100 - macro["growth"]) * 0.15

        +

        (100 - macro["credit"]) * 0.15
    )


    return build_scorecard(

        "Gold",

        score,

        {
            "inflation": macro["inflation"],
            "rates": macro["rates"],
            "risk": 100-macro["credit"]
        }

    )




def build_gold_engine(macro):

    return build_gold_score(macro)

