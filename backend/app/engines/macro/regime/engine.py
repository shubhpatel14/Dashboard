from __future__ import annotations

from typing import Any


# =====================================================
# HELPERS
# =====================================================

def get_score(
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



def regime_confidence(
    *values
) -> float:
    """
    Measures how far macro factors are from neutral.
    Higher = clearer regime
    """

    confidence = sum(
        abs(
            value - 50
        )
        for value in values
    )

    return min(
        100,
        round(
            confidence / 2,
            2
        )
    )



# =====================================================
# MACRO REGIME ENGINE
# =====================================================

def build_macro_regime(
    macro: dict[str, Any]
) -> dict[str, Any]:


    # ----------------------------
    # INPUT FACTORS
    # ----------------------------

    inflation = get_score(
        macro,
        "Inflation"
    )


    growth = get_score(
        macro,
        "Economic Growth"
    )


    liquidity = get_score(
        macro,
        "Liquidity & Financial Conditions"
    )


    policy = get_score(
        macro,
        "Monetary Policy"
    )


    sentiment = get_score(
        macro,
        "Market Sentiment"
    )



    # =================================================
    # REGIME CLASSIFICATION
    # =================================================


    # 🟢 GOLDILOCKS
    # Growth strong
    # Inflation controlled
    # Liquidity supportive

    if (
        growth >= 60
        and inflation >= 45
        and inflation <= 60
        and liquidity >= 55
        and sentiment >= 50
    ):

        regime = "Goldilocks"

        description = (
            "Healthy growth, stable inflation, and supportive liquidity."
        )


        assets = [
            "Stocks",
            "Nasdaq",
            "Bitcoin"
        ]


        risks = [
            "Inflation acceleration"
        ]



    # 🔥 REFLATION
    # Recovery + liquidity expansion

    elif (
        growth >= 55
        and inflation >= 55
        and liquidity >= 50
    ):

        regime = "Reflation"


        description = (
            "Growth is improving with rising inflation and expanding liquidity."
        )


        assets = [
            "Stocks",
            "Commodities",
            "Bitcoin"
        ]


        risks = [
            "Inflation overheating",
            "Central bank tightening"
        ]



    # 🟠 LATE CYCLE
    # Growth ok but financial stress rising

    elif (
        growth >= 50
        and liquidity <= 50
        and sentiment <= 45
    ):

        regime = "Late Cycle Slowdown"


        description = (
            "Growth remains positive but liquidity is tightening and risk appetite is weak."
        )


        assets = [
            "Gold",
            "Quality Stocks",
            "Cash"
        ]


        risks = [
            "Growth slowdown",
            "Market volatility"
        ]



    # 🔴 STAGFLATION
    # Weak growth + inflation

    elif (
        growth <= 45
        and inflation >= 55
    ):

        regime = "Stagflation"


        description = (
            "Weak economic growth with persistent inflation pressure."
        )


        assets = [
            "Gold",
            "Commodities",
            "Cash"
        ]


        risks = [
            "Equity weakness",
            "Policy mistakes"
        ]



    # 🔵 DEFLATION / RECESSION

    elif (
        growth <= 45
        and inflation <= 45
    ):

        regime = "Deflationary Slowdown"


        description = (
            "Growth weakness with falling inflation pressure."
        )


        assets = [
            "Bonds",
            "Dollar",
            "Cash"
        ]


        risks = [
            "Recession risk",
            "Earnings contraction"
        ]



    # ⚠️ LIQUIDITY CRUNCH

    elif (
        liquidity <= 40
        and sentiment <= 40
    ):

        regime = "Liquidity Stress"


        description = (
            "Financial conditions are tight and investors are reducing risk."
        )


        assets = [
            "Gold",
            "Dollar",
            "Cash"
        ]


        risks = [
            "Market volatility",
            "Risk asset drawdowns"
        ]



    # ⚪ MIXED

    else:

        regime = "Neutral"


        description = (
            "Mixed macro environment with no dominant economic trend."
        )


        assets = [
            "Balanced Portfolio"
        ]


        risks = [
            "Unclear macro direction"
        ]



    # =================================================
    # OUTPUT
    # =================================================

    return {

        "regime": regime,


        "confidence":
            regime_confidence(
                inflation,
                growth,
                liquidity,
                sentiment
            ),


        "description":
            description,


        "favored_assets":
            assets,


        "risks":
            risks,


        "inputs": {

            "growth":
                growth,


            "inflation":
                inflation,


            "liquidity":
                liquidity,
    

            "policy":
                policy,


            "sentiment":
                sentiment,

        }

    }