from app.services.macro_statistics import (
    macro_statistics
)



def normalize_macro_scores(
    engine
):


    if (
        not engine
        or
        "data" not in engine
    ):

        return engine




    for name,item in engine["data"].items():



        current = item.get(
            "current",
            item.get(
                "value",
                0
            )
        )



        stats = macro_statistics(
            name,
            current
        )



        item[
            "percentile"
        ] = stats[
            "percentile"
        ]



        item[
            "z_score"
        ] = stats[
            "z_score"
        ]



        item[
            "average"
        ] = stats[
            "average"
        ]



        item[
            "distance_avg"
        ] = stats[
            "distance_avg"
        ]



        item[
            "samples"
        ] = stats[
            "samples"
        ]



    return engine