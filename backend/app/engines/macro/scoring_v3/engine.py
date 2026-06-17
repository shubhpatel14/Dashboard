from app.engines.macro.scoring_v3.rules import (
    INDICATOR_RULES
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
    forecast=None
):


    key = (

        str(name)

        .upper()

        .replace(
            " ",
            "_"
        )

    )




    rule = INDICATOR_RULES.get(
        key
    )




    if rule is None:


        return {

            "score":50,

            "bias":"Neutral",

            "level":50,

            "trend_score":50,

            "momentum":50,

            "surprise":50

        }





    current = float(
        current
    )


    previous = float(
        previous
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
        forecast,
        rule
    )






    final_score = (

        level * 0.4

        +

        trend * 0.3

        +

        momentum * 0.2

        +

        surprise * 0.1

    )




    final_score = round(
        final_score,
        2
    )





    return {


        "score":
            final_score,


        "bias":

            "Bullish"

            if final_score >= 60

            else

            "Bearish"

            if final_score <=40

            else

            "Neutral",



        "level":
            round(level,2),


        "trend_score":
            round(trend,2),


        "momentum":
            round(momentum,2),


        "surprise":
            round(surprise,2),

    }