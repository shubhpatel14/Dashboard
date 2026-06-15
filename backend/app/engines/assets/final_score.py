from typing import Dict, Any


def blend_macro_score(
    asset_result: Dict[str, Any],
    macro_asset: Dict[str, Any],
    macro_weight: float = 0.30
):

    """
    Blends asset specific model with macro regime impact.

    Example:
    Gold model = 70%
    Macro regime = 30%
    """


    base_score = asset_result.get(
        "score",
        50
    )


    macro_score = macro_asset.get(
        "score",
        50
    )


    final_score = (
        base_score * (1 - macro_weight)
        +
        macro_score * macro_weight
    )


    result = asset_result.copy()


    result["raw_score"] = round(
        base_score,
        2
    )


    result["macro_score"] = round(
        macro_score,
        2
    )


    result["score"] = round(
        final_score,
        2
    )


    if final_score >= 60:

        result["bias"] = "Bullish"

    elif final_score <= 40:

        result["bias"] = "Bearish"

    else:

        result["bias"] = "Neutral"



    result["macro_drivers"] = (
        macro_asset.get(
            "drivers",
            []
        )
    )


    return result
