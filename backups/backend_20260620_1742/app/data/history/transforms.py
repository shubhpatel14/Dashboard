def percent_change(
    rows,
    periods
):

    result = []


    for i in range(
        periods,
        len(rows)
    ):


        current = rows[i]["value"]

        previous = rows[i-periods]["value"]


        if (
            current is None
            or
            previous is None
            or
            previous == 0
        ):

            continue


        result.append(
            {
                "date":
                    rows[i]["date"],

                "value":
                    (
                        (
                            current
                            -
                            previous
                        )
                        /
                        previous
                    )
                    *
                    100
            }
        )


    return result




def difference(
    rows,
    periods=1
):

    result = []


    for i in range(
        periods,
        len(rows)
    ):


        current = rows[i]["value"]

        previous = rows[i-periods]["value"]


        if (
            current is None
            or
            previous is None
        ):

            continue


        result.append(
            {
                "date":
                    rows[i]["date"],

                "value":
                    current
                    -
                    previous
            }
        )


    return result