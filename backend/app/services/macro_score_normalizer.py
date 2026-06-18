from app.engines.macro.scoring_v3.engine import (
    macro_score
)




def normalize_macro_scores(
    engine
):


    if not isinstance(
        engine,
        dict
    ):

        return engine



    data = engine.get(
        "data"
    )


    if not isinstance(
        data,
        dict
    ):

        return engine



    category_scores = []





    for name,item in data.items():



        if not isinstance(
            item,
            dict
        ):

            continue



        current = item.get(
            "current",
            item.get(
                "actual"
            )
        )


        previous = item.get(
            "previous"
        )


        forecast = item.get(
            "forecast"
        )



        if (
            current is None
            or previous is None
        ):

            continue





        try:


            result = macro_score(

                name,
                current,
                previous,
                forecast

            )



        except Exception:


            continue






        # =====================
        # overwrite old scoring
        # =====================


        item["score"] = result[
            "score"
        ]



        item["bias"] = result[
            "bias"
        ]

        # ==========================
# HISTORICAL INTELLIGENCE V4
# ==========================

        item["percentile"] = result.get(
            "percentile",
            50
        )


        item["z_score"] = result.get(
            "z_score",
            0
        )


        item["historical_average"] = result.get(
            "historical_average",
            0
        )


        item["distance_avg"] = result.get(
            "distance_avg",
            0
        )



        item["level_score"] = result[
            "level"
        ]



        item["trend_score"] = result[
            "trend_score"
        ]



        item["momentum_score"] = result[
            "momentum"
        ]



        item["surprise_score"] = result[
            "surprise"
        ]




        if result["trend_score"] > 50:


            item["trend"] = "Improving"


        elif result["trend_score"] < 50:


            item["trend"] = "Weakening"


        else:


            item["trend"] = "Stable"




        category_scores.append(
            result["score"]
        )





    # update category score

    if category_scores:


        engine["score"] = round(

            sum(category_scores)

            /

            len(category_scores),

            2

        )




        engine["bias"] = (

            "Bullish"

            if engine["score"] >= 60

            else

            "Bearish"

            if engine["score"] <= 40

            else

            "Neutral"

        )





    return engine