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





def regime_probabilities(
    inflation,
    growth,
    liquidity,
    rates,
    credit
):


    # ==========================
    # EXPANSION SCORE
    # ==========================

    expansion = (

        growth * 0.35

        +

        liquidity * 0.30

        +

        credit * 0.25

        +

        rates * 0.10

    )




    # ==========================
    # RECOVERY SCORE
    # ==========================

    recovery = (

        liquidity * 0.40

        +

        growth * 0.30

        +

        (100 - rates) * 0.15

        +

        credit * 0.15

    )




    # ==========================
    # SLOWDOWN SCORE
    # ==========================

    slowdown = (

        (100-growth) * 0.40

        +

        (100-liquidity) * 0.25

        +

        (100-credit) * 0.25

        +

        rates * 0.10

    )




    # ==========================
    # RECESSION SCORE
    # ==========================

    recession = (

        (100-growth) * 0.35

        +

        (100-credit) * 0.35

        +

        (100-liquidity) * 0.20

        +

        (100-rates) * 0.10

    )





    raw = {


        "Expansion":
            clamp(
                expansion
            ),


        "Recovery":
            clamp(
                recovery
            ),


        "Slowdown":
            clamp(
                slowdown
            ),


        "Recession":
            clamp(
                recession
            )

    }




    total = sum(
        raw.values()
    )



    return {


        key:

            round(
                value
                /
                total
                *
                100,
                2
            )


        for key,value in raw.items()

    }