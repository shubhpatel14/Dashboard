from datetime import date
from typing import Any

import requests


def fetch_econdb_calendar() -> list[dict[str, Any]]:

    url = "https://www.econdb.com/api/series/"


    indicators = {
        "CPI YoY": "CPIUS",
        "Unemployment Rate": "URATEUS",
        "GDP": "GDPUS",
        "Interest Rate": "POLIRUS",
    }


    events = []


    for name, ticker in indicators.items():

        r = requests.get(
            f"{url}{ticker}/?format=json",
            timeout=20
        )


        r.raise_for_status()


        data = r.json()


        values = data.get(
            "data",
            {}
        )


        dates = values.get(
            "dates",
            []
        )


        nums = values.get(
            "values",
            []
        )


        if len(nums) < 2:
            continue


        current = nums[-1]
        previous = nums[-2]


        events.append(
            {
                "date": dates[-1],

                "event": name,

                "actual": current,

                "previous": previous,

                # temporary until consensus provider
                "forecast": previous,

                "currency": "USD",

                "impact": "High",

                "source": "EconDB",
            }
        )


    return events