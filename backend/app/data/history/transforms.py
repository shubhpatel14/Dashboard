def percent_change(
    rows,
    periods
):


    result = []


    for i in range(
        periods,
        len(rows)
    ):


        previous = rows[i-periods]["value"]

        current = rows[i]["value"]


        if previous == 0:

            continue


        change = (
            (
                current
                /
                previous
            )
            -
            1
        ) * 100



        result.append(

            {

                "date":
                    rows[i]["date"],

                "value":
                    round(
                        change,
                        2
                    )

            }

        )


    return result
