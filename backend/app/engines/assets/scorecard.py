def clamp(
    value,
    minimum=0,
    maximum=100
):

    return max(
        minimum,
        min(
            value,
            maximum
        )
    )





def classify_asset(
    score
):


    if score >= 70:

        return "Strong Bullish"


    if score >= 60:

        return "Bullish"


    if score <= 30:

        return "Strong Bearish"


    if score <= 40:

        return "Bearish"



    return "Neutral"






def build_scorecard(
    asset,
    score,
    drivers
):


    score = clamp(
        score
    )



    return {


        "asset":

            asset,


        "score":

            round(
                score,
                2
            ),


        "bias":

            classify_asset(
                score
            ),


        "drivers":

            drivers

    }