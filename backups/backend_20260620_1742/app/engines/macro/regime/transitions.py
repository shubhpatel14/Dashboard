def detect_transition(
    probabilities
):


    ordered = sorted(
        probabilities.items(),
        key=lambda x: x[1],
        reverse=True
    )


    current = ordered[0]

    next_regime = ordered[1]


    spread = (
        current[1]
        -
        next_regime[1]
    )



    if spread < 5:


        return {

            "state":
                "Transition",

            "from":
                current[0],

            "to":
                next_regime[0],

            "message":
                f"{current[0]} → {next_regime[0]} transition forming",

            "confidence_gap":
                round(
                    spread,
                    2
                )

        }



    return {


        "state":
            "Stable",


        "dominant":

            current[0],


        "message":

            f"{current[0]} regime stable",


        "confidence_gap":

            round(
                spread,
                2
            )


    }