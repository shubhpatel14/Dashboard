from __future__ import annotations

from typing import Any


# =====================================
# HELPERS
# =====================================

def clamp(value: float) -> float:
    """
    Keep asset score between 0-100
    """

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

    if score >= 60:
        return "Bullish"

    if score <= 40:
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
# MULTI FACTOR ASSET ALLOCATION ENGINE
# =====================================================

def macro_asset_impact(
    surprise: dict[str, Any],
    macro: dict[str, Any]
) -> dict[str, Any]:


    # ==========================
    # READ MACRO FACTORS
    # ==========================

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



    # ===================================
    # GOLD MODEL
    #
    # Bullish when:
    # - inflation stress
    # - weak growth
    # - risk-off
    # - dovish policy
    # ===================================

    gold_score = (

        (100 - inflation) * 0.25

        +

        (100 - sentiment) * 0.25

        +

        (100 - growth) * 0.20

        +

        (100 - surprise_score) * 0.20

        +

        (100 - monetary) * 0.10

    )


    assets["Gold"] = {

        "score": clamp(
            gold_score
        ),

        "drivers": [

            "Inflation pressure",

            "Risk aversion",

            "Policy expectations",

            "Macro uncertainty",
        ],
    }



    # ===================================
    # SP500 MODEL
    #
    # Bullish when:
    # - growth strong
    # - liquidity loose
    # - sentiment positive
    # ===================================

    sp500_score = (

        growth * 0.35

        +

        liquidity * 0.30

        +

        sentiment * 0.20

        +

        surprise_score * 0.15

    )


    assets["SP500"] = {

        "score": clamp(
            sp500_score
        ),

        "drivers": [

            "Economic growth",

            "Liquidity conditions",

            "Risk appetite",

            "Earnings environment",
        ],
    }



    # ===================================
    # NASDAQ MODEL
    #
    # More liquidity/rates sensitive
    # ===================================

    nasdaq_score = (

        liquidity * 0.45

        +

        growth * 0.20

        +

        sentiment * 0.20

        +

        surprise_score * 0.15

    )


    assets["Nasdaq"] = {

        "score": clamp(
            nasdaq_score
        ),

        "drivers": [

            "Liquidity",

            "Rate sensitivity",

            "Growth expectations",
        ],
    }



    # ===================================
    # BONDS MODEL
    #
    # Bullish when:
    # - inflation cooling
    # - growth slowing
    # ===================================

    bond_score = (

        (100 - inflation) * 0.35

        +

        (100 - growth) * 0.30

        +

        (100 - surprise_score) * 0.20

        +

        (100 - monetary) * 0.15

    )


    assets["Bonds"] = {

        "score": clamp(
            bond_score
        ),

        "drivers": [

            "Inflation trend",

            "Growth slowdown",

            "Fed policy expectations",
        ],
    }



    # ===================================
    # US DOLLAR MODEL
    #
    # Bullish when:
    # - tighter policy
    # - risk aversion
    # ===================================

    dollar_score = (

        monetary * 0.35

        +

        (100 - sentiment) * 0.30

        +

        (100 - liquidity) * 0.20

        +

        inflation * 0.15

    )


    assets["Dollar"] = {

        "score": clamp(
            dollar_score
        ),

        "drivers": [

            "Interest rate expectations",

            "Safe haven demand",

            "Liquidity environment",
        ],
    }



    # ===================================
    # BITCOIN MODEL
    #
    # Bullish when:
    # - liquidity expands
    # - risk appetite improves
    # ===================================

    bitcoin_score = (

        liquidity * 0.50

        +

        sentiment * 0.30

        +

        surprise_score * 0.20

    )


    assets["Bitcoin"] = {

        "score": clamp(
            bitcoin_score
        ),

        "drivers": [

            "Global liquidity",

            "Risk appetite",

            "Macro momentum",
        ],
    }



    # ==========================
    # ADD FINAL BIAS
    # ==========================

    for asset in assets:

        assets[asset]["bias"] = asset_bias(
            assets[asset]["score"]
        )


    return assets