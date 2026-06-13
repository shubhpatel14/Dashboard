from typing import Any
import requests


URL = "https://www.myfxbook.com/api/get-economic-calendar.json"


def fetch_myfxbook_calendar() -> list[dict[str, Any]]:

    response = requests.get(
        URL,
        headers={
            "User-Agent":"Mozilla/5.0"
        },
        timeout=20
    )


    response.raise_for_status()


    data=response.json()


    events=[]


    for item in data.get("events", []):


        if item.get("country") != "United States":
            continue


        if item.get("impact") != "High":
            continue


        events.append(
            {
                "date": item.get("date"),

                "event": item.get("name"),

                "actual": item.get("actual"),

                "forecast": item.get("consensus"),

                "previous": item.get("previous"),

                "impact": "High",

                "currency":"USD",

                "source":"Myfxbook"
            }
        )


    return events