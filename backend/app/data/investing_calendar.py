from typing import Any
from datetime import datetime, timedelta

import cloudscraper
from bs4 import BeautifulSoup



def clean(x):

    if not x:
        return None

    value = x.get_text(
        " ",
        strip=True
    )

    if value in [
        "",
        "&nbsp;"
    ]:
        return None

    return value





def fetch_investing_calendar() -> list[dict[str, Any]]:


    scraper = cloudscraper.create_scraper()


    url = (
        "https://www.investing.com/economic-calendar/"
        "Service/getCalendarFilteredData"
    )


    start = (
        datetime.now()
        - timedelta(days=30)
    ).strftime(
        "%Y-%m-%d"
    )


    end = (
        datetime.now()
        + timedelta(days=60)
    ).strftime(
        "%Y-%m-%d"
    )


    payload = {

        "dateFrom":
            start,

        "dateTo":
            end,

        "timeZone":
            "55",

        "timeFilter":
            "timeRemain",

        "limit_from":
            "0",

        "country[]":
            [
                "5"
            ],

        "importance[]":
            [
                "1",
                "2",
                "3"
            ],

    }


    r = scraper.post(

        url,

        data=payload,

        headers={

            "User-Agent":
                "Mozilla/5.0",

            "X-Requested-With":
                "XMLHttpRequest",

            "Referer":
                "https://www.investing.com/economic-calendar/",

        }

    )


    data = r.json()


    html = data.get(
        "data",
        ""
    )


    soup = BeautifulSoup(
        html,
        "html.parser"
    )


    events = []


    current_date = None



    for row in soup.find_all("tr"):


        # date separator

        if "theDay" in row.get(
            "class",
            []
        ):

            current_date = row.get_text(
                strip=True
            )

            continue



        if not row.get(
            "id",
            ""
        ).startswith(
            "eventRowId"
        ):

            continue



        time = clean(
            row.find(
                "td",
                class_="time"
            )
        )



        currency = clean(
            row.find(
                "td",
                class_="flagCur"
            )
        )



        event = clean(
            row.find(
                "td",
                class_="event"
            )
        )



        actual = clean(
            row.find(
                "td",
                class_="act"
            )
        )


        forecast = clean(
            row.find(
                "td",
                class_="fore"
            )
        )


        previous = clean(
            row.find(
                "td",
                class_="prev"
            )
        )



        events.append(

            {

                "date":
                    current_date,

                "time":
                    time,

                "country":
                    "United States",

                "currency":
                    currency,

                "event":
                    event,

                "actual":
                    actual,

                "forecast":
                    forecast,

                "previous":
                    previous,

                "impact":
                    "High",

                "source":
                    "Investing.com",

            }

        )



    return events