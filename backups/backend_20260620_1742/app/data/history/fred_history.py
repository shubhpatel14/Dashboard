import requests
from datetime import datetime


FRED_API_KEY = "6b153e4a6a232a0a4e535a801629752b"


def fetch_fred_history(
    series_id
):


    url = (
        "https://api.stlouisfed.org/fred/series/observations"
    )


    params = {

        "series_id": series_id,

        "api_key": FRED_API_KEY,

        "file_type": "json"

    }


    r = requests.get(
        url,
        params=params,
        timeout=20
    )


    data = r.json()


    rows = []


    for item in data.get(
        "observations",
        []
    ):


        value = item.get(
            "value"
        )


        if value == ".":

            continue


        rows.append(

            {

                "date":
                    datetime.strptime(
                        item["date"],
                        "%Y-%m-%d"
                    ),

                "value":
                    float(value)

            }

        )


    return rows
