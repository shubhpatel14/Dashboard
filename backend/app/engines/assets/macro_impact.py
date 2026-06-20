from __future__ import annotations

from typing import Any


# =====================================
# HELPERS
# =====================================

def clamp(value: float) -> float:

    return max(
        0,
        min(
            100,
            round(
                value,
                2
            )
        )
    )



def asset_bias(score: float) -> str:

    if score >= 55:
        return "Bullish"

    if score <= 45:
        return "Bearish"

    return "Neutral"



def get_macro_score(
    macro: dict[str, Any],
    key: str,
    default: float = 50
) -> float:

    try:

        return float(
            macro
            .get(
                "scores",
                {}
            )
            .get(
                key,
                default
            )
        )

    except Exception:

        return default



# =====================================================
# MULTI FACTOR ASSET IMPACT ENGINE
# =====================================================

def macro_asset_impact(
    surprise: dict[str, Any],
    macro: dict[str, Any]
) -> dict[str, Any]:


    inflation = get_macro_score(
        macro,
        "Inflation"
    )


    growth = get_macro_score(
        macro,
        "Economic Growth"
    )


    liquidity = get_macro_score(
        macro,
        "Liquidity & Financial Conditions"
    )


    sentiment = get_macro_score(
        macro,
        "Market Sentiment"
    )


    monetary = get_macro_score(
        macro,
        "Monetary Policy"
    )


    surprise_score = float(
        surprise.get(
            "score",
            50
        )
    )


    assets = {}


    assets["Gold"] = {

        "score": clamp(
            (100-inflation)*0.25
            +(100-sentiment)*0.25
            +(100-growth)*0.20
            +(100-surprise_score)*0.20
            +(100-monetary)*0.10
        ),

        "drivers":[
            "Inflation pressure",
            "Risk aversion",
            "Policy expectations",
            "Macro uncertainty",
        ],
    }



    assets["SP500"] = {

        "score": clamp(
            growth*0.35
            + liquidity*0.30
            + sentiment*0.20
            + surprise_score*0.15
        ),

        "drivers":[
            "Economic growth",
            "Liquidity conditions",
            "Risk appetite",
            "Earnings environment",
        ],
    }



    assets["Nasdaq"] = {

        "score": clamp(
            liquidity*0.45
            + growth*0.20
            + sentiment*0.20
            + surprise_score*0.15
        ),

        "drivers":[
            "Liquidity",
            "Rate sensitivity",
            "Growth expectations",
        ],
    }



    assets["Bonds"] = {

        "score": clamp(
            (100-inflation)*0.35
            +(100-growth)*0.30
            +(100-surprise_score)*0.20
            +(100-monetary)*0.15
        ),

        "drivers":[
            "Inflation trend",
            "Growth slowdown",
            "Fed policy expectations",
        ],
    }



    assets["Dollar"] = {

        "score": clamp(
            monetary*0.35
            +(100-sentiment)*0.30
            +(100-liquidity)*0.20
            +inflation*0.15
        ),

        "drivers":[
            "Interest rate expectations",
            "Safe haven demand",
            "Liquidity environment",
        ],
    }



    assets["Bitcoin"] = {

        "score": clamp(
            liquidity*0.50
            +sentiment*0.30
            +surprise_score*0.20
        ),

        "drivers":[
            "Global liquidity",
            "Risk appetite",
            "Macro momentum",
        ],
    }



    # ==========================
    # FINAL METADATA
    # ==========================

    for asset,data in assets.items():


        score = data[
            "score"
        ]


        data[
            "bias"
        ] = asset_bias(
            score
        )


        data[
            "trend"
        ] = "Neutral"



        if score >= 55:

            data[
                "positive_drivers"
            ] = data[
                "drivers"
            ]

            data[
                "negative_drivers"
            ] = []



        elif score <= 45:

            data[
                "positive_drivers"
            ] = []


            data[
                "negative_drivers"
            ] = data[
                "drivers"
            ]



        else:

            split = len(
                data["drivers"]
            ) // 2


            data[
                "positive_drivers"
            ] = data[
                "drivers"
            ][:split]


            data[
                "negative_drivers"
            ] = data[
                "drivers"
            ][split:]


    return assets