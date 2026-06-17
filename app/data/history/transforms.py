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


        result.append(

            {

                "date":
                    rows[i]["date"],


                "value":
                    round(
                        (
                            (
                                current
                                /
                                previous
                            )
                            -
                            1
                        )
                        *
                        100,
                        2
                    )

            }

        )


    return result
