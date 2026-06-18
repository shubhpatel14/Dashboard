from app.engines.macro.scoring_v3.rules import (
    INDICATOR_RULES
)

from app.services.macro_statistics import (
    macro_statistics
)



def clamp(
    value,
    low=0,
    high=100
):

    return max(
        low,
        min(
            high,
            value
        )
    )





def calculate_level_score(
    current,
    rule
):


    target = rule.get(
        "target"
    )


    danger = rule.get(
        "danger"
    )



    if target == danger:

        return 50



    if rule.get("type") == "lower_better":


        score = (

            100

            -

            (
                (current - target)

                /

                (danger-target)

                *

                100
            )

        )


    else:


        score = (

            (
                current-danger
            )

            /

            (
                target-danger
            )

            *

            100

        )



    return clamp(
        score
    )







def calculate_trend_score(
    current,
    previous,
    rule
):


    if current == previous:

        return 50




    if rule.get("type") == "lower_better":


        improving = current < previous


    else:


        improving = current > previous





    return (

        75

        if improving

        else

        25

    )








def calculate_momentum_score(
    current,
    previous
):


    try:

        move = abs(

            (
                current-previous
            )

            /

            previous

        )



        return clamp(
            50 + move*50
        )


    except Exception:


        return 50







def calculate_surprise_score(
    current,
    forecast,
    rule
):


    if forecast is None:

        return 50



    try:


        if rule.get("type") == "lower_better":


            good = current < forecast


        else:


            good = current > forecast




        return (

            75

            if good

            else

            25

        )


    except Exception:


        return 50








def macro_score(
    name,
    current,
    previous,
    consensus=None
):


    rule = INDICATOR_RULES.get(
        name,
        {}
    )


    level = calculate_level_score(
        current,
        rule
    )


    trend = calculate_trend_score(
        current,
        previous,
        rule
    )


    momentum = calculate_momentum_score(
        current,
        previous
    )


    surprise = calculate_surprise_score(
        current,
        consensus,
        rule
    )


    # ==============================
    # HISTORICAL DATABASE INTELLIGENCE
    # ==============================


    stats = macro_statistics(
        name,
        current
    )


    percentile = stats.get(
        "percentile",
        50
    )


    z_score = stats.get(
        "z_score",
        0
    )


    if rule.get(
        "lower_is_bullish"
    ):


        percentile_score = (
            100
            -
            percentile
        )


    else:


        percentile_score = percentile



    z_score_factor = max(

        0,

        100
        -
        abs(
            z_score
        )
        *
        20

    )



    final = (

        level * 0.25

        +

        trend * 0.20

        +

        momentum * 0.15

        +

        surprise * 0.10

        +

        percentile_score * 0.20

        +

        z_score_factor * 0.10

    )



    if final >= 60:

        bias = "Bullish"


    elif final <= 40:

        bias = "Bearish"


    else:

        bias = "Neutral"



    return {


        "score":
            round(
                final,
                2
            ),


        "bias":
            bias,


        "level":
            level,


        "trend_score":
            trend,


        "momentum":
            momentum,


        "surprise":
            surprise,


        # V4 DATA

        "percentile":
            percentile,


        "z_score":
            z_score,


        "historical_average":
            stats.get(
                "average",
                0
            ),


        "distance_avg":
            stats.get(
                "distance_avg",
                0
            ),

    }