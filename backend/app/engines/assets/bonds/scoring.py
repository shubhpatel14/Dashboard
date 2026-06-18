
from app.engines.assets.scorecard import build_scorecard


def build_bonds_score(macro):

    score=(

        (100-macro["growth"]) * 0.30

        +

        (100-macro["inflation"]) * 0.25

        +

        (100-macro["rates"]) * 0.30

        +

        (100-macro["credit"]) * 0.15
    )


    return build_scorecard(

        "Bonds",

        score,

        {
            "growth_slowdown":100-macro["growth"],
            "inflation_cooling":100-macro["inflation"],
            "rates":100-macro["rates"],
            "risk":100-macro["credit"]
        }

    )




def build_bonds_engine(macro):

    return build_bonds_score(macro)

