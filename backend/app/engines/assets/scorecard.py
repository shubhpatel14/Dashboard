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




def classify(
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


    score = round(
        clamp(score),
        2
    )


    bullish = []

    bearish = []

    components = []

    radar = []



    for name,value in drivers.items():


        if isinstance(
            value,
            dict
        ):

            value = value.get(
                "score",
                50
            )


        value = round(
            value,
            2
        )


        item = {

            "name":
                name,


            "score":
                value,


            "value":
                value,


            "impact":
                round(
                    value-50,
                    2
                )

        }


        components.append(
            item
        )


        radar.append(

            {
                "indicator":
                    name,


                "value":
                    value
            }

        )



        if value >= 55:

            bullish.append(
                item
            )


        elif value <=45:

            bearish.append(
                item
            )





    return {


        "asset":
            asset,


        "score":
            score,


        "bias":
            classify(
                score
            ),


        "outlook":
            classify(
                score
            ),



        # original raw data

        "drivers":
            drivers,



        # frontend compatibility

        "bullish_drivers":
            bullish,


        "bearish_drivers":
            bearish,


        "components":
            components,


        "radar":
            radar,


        "trend":
            "Neutral",


        "history":[

            {
                "date":"Current",

                "score":score
            }

        ],


        "explanation":

            f"{asset} macro score is {score} with {classify(score)} outlook."

    }