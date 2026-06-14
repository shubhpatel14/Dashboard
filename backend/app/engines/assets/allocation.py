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

def build_allocation(
    asset_scores: dict[str, Any],
    regime: dict[str, Any],
):


    # --------------------------------
    # BASE 60/40 STYLE PORTFOLIO
    # --------------------------------

    weights = {

        "SP500": 35,

        "Nasdaq": 15,

        "Bonds": 25,

        "Gold": 10,

        "Dollar": 10,

        "Bitcoin": 5,

    }



    regime_name = (
        regime
        .get(
            "regime",
            "Neutral"
        )
    )



    # =================================
    # REGIME TILTS
    # =================================


    if regime_name == "Goldilocks":

        weights["SP500"] += 10

        weights["Nasdaq"] += 5

        weights["Bitcoin"] += 5

        weights["Gold"] -= 5



    elif regime_name == "Reflation":

        weights["SP500"] += 5

        weights["Gold"] += 5

        weights["Bitcoin"] += 5

        weights["Bonds"] -= 10



    elif regime_name == "Late Cycle Slowdown":

        weights["Gold"] += 10

        weights["Bonds"] += 5

        weights["Dollar"] += 5

        weights["Nasdaq"] -= 10



    elif regime_name == "Stagflation":

        weights["Gold"] += 20

        weights["Dollar"] += 10

        weights["SP500"] -= 15

        weights["Nasdaq"] -= 10



    elif regime_name == "Deflationary Slowdown":

        weights["Bonds"] += 20

        weights["Dollar"] += 10

        weights["SP500"] -= 15

        weights["Bitcoin"] -= 5



    elif regime_name == "Liquidity Stress":

        weights["Gold"] += 15

        weights["Dollar"] += 15

        weights["Bitcoin"] -= 5

        weights["Nasdaq"] -= 10




    # =================================
    # SCORE BASED ADJUSTMENT
    # =================================

    for asset, data in asset_scores.items():


        score = float(
            data.get(
                "score",
                50
            )
        )


        adjustment = (
            score - 50
        ) / 5


        if asset in weights:

            weights[asset] += adjustment



    # no negatives

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
                f"Portfolio tilted for "
                f"{regime_name} conditions."
            )

    }