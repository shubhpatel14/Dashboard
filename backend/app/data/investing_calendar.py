from typing import Any
from datetime import datetime, timedelta

import investpy


def fetch_investing_calendar() -> list[dict[str, Any]]:

    start = (
        datetime.now() - timedelta(days=30)
    ).strftime("%d/%m/%Y")


    end = (
        datetime.now()
    ).strftime("%d/%m/%Y")


    df = investpy.economic_calendar(
        from_date=start,
        to_date=end,
        countries=["united states"],
        importances=["high"]
    )


    events=[]


    for _,row in df.iterrows():


        events.append(
            {
                "date": row.get("date"),

                "event": row.get("event"),

                "actual": row.get("actual"),

                "forecast": row.get("forecast"),

                "previous": row.get("previous"),

                "impact":"High",

                "currency":"USD",

                "source":"Investing.com"
            }
        )


    return events