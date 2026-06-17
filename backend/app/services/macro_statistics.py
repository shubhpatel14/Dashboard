import numpy as np


from app.database.connection import (
    SessionLocal
)


from app.database.models import (
    MacroSeries
)



def macro_statistics(
    indicator,
    current
):


    db = SessionLocal()


    try:


        rows = (
            db.query(
                MacroSeries.value
            )
            .filter(
                MacroSeries.indicator
                ==
                indicator
            )
            .all()
        )



        values = [
            r[0]
            for r in rows
            if r[0] is not None
        ]



        if len(values) < 10:

            return {

                "percentile":50,

                "z_score":0,

                "average":current,

                "distance_avg":0,

                "samples":len(values)

            }



        arr = np.array(
            values
        )



        average = float(
            np.mean(arr)
        )



        std = float(
            np.std(arr)
        )



        percentile = (

            np.sum(
                arr <= current
            )

            /

            len(arr)

            *

            100

        )



        z = (

            (current-average)

            /

            std

            if std != 0

            else 0

        )



        return {

            "percentile":
                round(
                    percentile,
                    2
                ),


            "z_score":
                round(
                    z,
                    2
                ),


            "average":
                round(
                    average,
                    2
                ),


            "distance_avg":
                round(
                    current-average,
                    2
                ),


            "samples":
                len(values)

        }



    finally:

        db.close()
