from __future__ import annotations


# categories where economic calendar surprise exists
EVENT_BASED_CATEGORIES = {
    "inflation",
    "growth",
    "labor",
    "rates",
    "housing",
    "sentiment",
}


def get_category_surprise(
    category,
    surprise
):

    events = surprise.get(
        "events",
        []
    )


    filtered = [

        e for e in events

        if e.get(
            "category"
        ) == category

    ]


    if not filtered:

        return {

            "score": None,
            "events":[]

        }


    total = 0
    weight = 0


    for e in filtered:


        w = float(
            e.get(
                "weight",
                1
            )
        )


        total += (
            float(
                e.get(
                    "score",
                    50
                )
            )
            *
            w
        )


        weight += w



    return {

        "score": round(
            total / weight,
            2
        ),

        "events": filtered

    }





def build_category_final_score(
    category: str,
    engine: dict,
    surprise: dict
):


    if not engine:

        return engine



    result = dict(
        engine
    )



    core_score = float(

        result.get(

            "core_score",

            result.get(
                "score",
                50
            )

        )

    )



    category_surprise = get_category_surprise(
        category,
        surprise
    )


    surprise_score = category_surprise.get(
        "score"
    )



    # ====================================
    # EVENT BASED MACROS
    # ====================================

    if (
        category in EVENT_BASED_CATEGORIES
        and
        surprise_score is not None
    ):


        final_score = (

            core_score * 0.85

            +

            float(
                surprise_score
            ) * 0.15

        )



    # ====================================
    # MARKET CONDITION MACROS
    # liquidity / credit / recession etc
    # ====================================

    else:


        final_score = core_score

        surprise_score = None




    result[
        "core_score"
    ] = round(
        core_score,
        2
    )



    result[
        "surprise_score"
    ] = (
        round(
            surprise_score,
            2
        )

        if surprise_score is not None

        else None
    )



    result[
        "score"
    ] = round(
        final_score,
        2
    )



    result[
        "surprise_events"
    ] = category_surprise.get(
        "events",
        []
    )



    if final_score >= 60:

        result[
            "bias"
        ] = "Bullish"


    elif final_score <= 40:


        result[
            "bias"
        ] = "Bearish"



    else:


        result[
            "bias"
        ] = "Neutral"



    return result