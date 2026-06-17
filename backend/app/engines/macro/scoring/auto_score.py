from app.engines.macro.scoring.rules import (
    INDICATOR_RULES
)


def auto_score_indicator(
    name,
    values
):


    current = float(values[-1])
    previous = float(values[-2])


    change = (
        current
        -
        previous
    )


    key = (
        name
        .upper()
        .replace(" ","_")
    )


    higher_good = INDICATOR_RULES.get(
        key,
        True
    )


    if higher_good:


        improving = current > previous


    else:


        improving = current < previous




    strength = min(

        abs(change / previous)
        * 100,

        50

    )




    if improving:


        score = 50 + strength


    else:


        score = 50 - strength





    score = round(
        score,
        2
    )




    return {


        "current":
            current,


        "previous":
            previous,


        "change":
            round(
                change,
                2
            ),


        "score":
            score,


        "trend":

            "Improving"

            if improving

            else

            "Weakening",



        "bias":

            "Bullish"

            if score >= 55

            else

            "Bearish"

            if score <=45

            else

            "Neutral"

    }