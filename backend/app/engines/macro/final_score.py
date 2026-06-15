from typing import Dict, Any


def build_final_macro_score(
    macro: Dict[str, Any],
    surprise: Dict[str, Any],
):

    """
    Final institutional macro score.

    Existing macro model = 90%
    Economic surprise = 10%

    Keeps core macro stable but reacts
    to fresh economic releases.
    """


    base_score = macro.get(
        "score",
        50
    )


    surprise_score = surprise.get(
        "score",
        50
    )


    final = (
        base_score * 0.70
        +
        surprise_score * 0.30
    )


    return {

        "score": round(final,2),

        "base_macro_score": round(
            base_score,
            2
        ),

        "surprise_score": round(
            surprise_score,
            2
        ),

        "weights": {
            "macro_model":70,
            "economic_surprise":30,
        }
    }

