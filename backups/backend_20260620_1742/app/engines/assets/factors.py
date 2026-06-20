from __future__ import annotations

from typing import Any



def read_score(
    macro,
    name,
    default=50
):


    if not isinstance(
        macro,
        dict
    ):

        return default


    return float(

        macro
        .get(
            "scores",
            {}
        )
        .get(
            name,
            default
        )

    )



def build_asset_factors(
    macro: dict[str, Any],
    weights: dict[str, Any] | None = None
):

    inflation = read_score(
        macro,
        "Inflation"
    )


    growth = read_score(
        macro,
        "Economic Growth"
    )


    liquidity = read_score(
        macro,
        "Liquidity & Financial Conditions"
    )


    credit = read_score(
        macro,
        "Credit Conditions"
    )


    rates = read_score(
        macro,
        "Monetary Policy"
    )


    sentiment = read_score(
        macro,
        "Market Sentiment"
    )



    return {


        "liquidity":

            liquidity,


        "growth":

            growth,


        "credit":

            credit,


        "rates":

            rates,


        "inflation":

            inflation,


        "sentiment":

            sentiment,


        # GOLD
        "real_yield_support":

            100-rates,


        "dollar_weakness":

            100-rates,


        "inflation_hedge":

            inflation,


        "safe_haven":

            100-sentiment,


        # BTC
        "risk_appetite":

            sentiment,


        "macro_momentum":

            growth,

    }



def weighted_score(
    factors,
    weights=None
):


    # fallback equal weights
    if weights is None:

        weights = {

            key: 1

            for key
            in factors.keys()

        }



    score = 0

    total = 0



    for key, weight in weights.items():


        score += (

            factors.get(
                key,
                50
            )

            *

            weight

        )


        total += weight



    if total == 0:

        return 50



    return round(

        score / total,

        2

    )