from __future__ import annotations

from typing import Any



# ======================================================
# HELPERS
# ======================================================

def clamp(
    value: float,
    low: float = 0,
    high: float = 100
):

    return max(
        low,
        min(
            high,
            value
        )
    )



def normalize(
    weights: dict[str, float]
):

    total = sum(
        weights.values()
    )


    if total == 0:

        return weights


    return {

        asset:
            round(
                value / total * 100,
                2
            )

        for asset, value
        in weights.items()

    }



# ======================================================
# PORTFOLIO ALLOCATION ENGINE
# ======================================================

# ======================================================
# PORTFOLIO ALLOCATION ENGINE V2
# ======================================================

def build_allocation(
    asset_scores: dict[str, Any],
    regime: dict[str, Any],
):


    weights = {

        "SP500": 35,

        "Nasdaq": 15,

        "Bonds": 25,

        "Gold": 10,

        "Dollar": 10,

        "Bitcoin": 5,

    }



    regime_name = regime.get(
        "regime",
        "Neutral"
    )



    probabilities = regime.get(
        "probabilities",
        {}
    )



    # =================================
    # NEW REGIME ENGINE V2 TILTS
    # =================================


    if regime_name == "Expansion":


        weights["SP500"] += 10

        weights["Nasdaq"] += 10

        weights["Bitcoin"] += 5


        weights["Bonds"] -= 10

        weights["Dollar"] -= 5





    elif regime_name == "Recovery":


        weights["SP500"] += 7

        weights["Nasdaq"] += 5

        weights["Bitcoin"] += 5

        weights["Gold"] += 3


        weights["Dollar"] -= 5





    elif regime_name == "Slowdown":


        weights["Bonds"] += 10

        weights["Gold"] += 10

        weights["Dollar"] += 5


        weights["Nasdaq"] -= 10

        weights["Bitcoin"] -= 5





    elif regime_name == "Stagflation":


        weights["Gold"] += 20

        weights["Dollar"] += 10


        weights["SP500"] -= 10

        weights["Nasdaq"] -= 10

        weights["Bonds"] -= 5





    elif regime_name == "Recession":


        weights["Bonds"] += 20

        weights["Gold"] += 10

        weights["Dollar"] += 10


        weights["SP500"] -= 15

        weights["Nasdaq"] -= 10

        weights["Bitcoin"] -= 5




    # =================================
    # PROBABILITY ADJUSTMENT
    # =================================


    recession_prob = probabilities.get(
        "Recession",
        0
    )


    expansion_prob = probabilities.get(
        "Expansion",
        0
    )



    if recession_prob > 30:


        weights["Gold"] += 5

        weights["Bonds"] += 5

        weights["SP500"] -= 5




    if expansion_prob > 35:


        weights["SP500"] += 5

        weights["Nasdaq"] += 5

        weights["Bonds"] -= 5






    # =================================
    # ASSET SCORE TILT
    # =================================


    for asset,data in asset_scores.items():


        score = float(
            data.get(
                "score",
                50
            )
        )


        adjustment = (
            score - 50
        ) / 5



        name = asset.capitalize()


        mapping = {

            "Sp500":
                "SP500",

            "Nasdaq":
                "Nasdaq",

            "Gold":
                "Gold",

            "Bitcoin":
                "Bitcoin",

            "Bonds":
                "Bonds",

            "Dollar":
                "Dollar"

        }



        if name in mapping:


            weights[
                mapping[name]
            ] += adjustment






    for asset in weights:


        weights[asset] = clamp(
            weights[asset]
        )




    final = normalize(
        weights
    )




    return {


        "allocation":

            final,


        "regime":

            regime_name,


        "largest_positions":

            sorted(
                final.items(),
                key=lambda x:x[1],
                reverse=True
            )[:3],



        "explanation":

            (
                f"Portfolio dynamically allocated "
                f"for {regime_name} regime."
            )

    }