from datetime import datetime
from typing import Any

import requests
import xml.etree.ElementTree as ET


URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"


def clean(value):

    if value is None:
        return "N/A"

    value = str(value).strip()

    return value if value else "N/A"



def fetch_forex_factory_calendar() -> list[dict[str, Any]]:

    response = requests.get(
        URL,
        timeout=20
    )

    response.raise_for_status()


    root = ET.fromstring(
        response.content
    )


    events = []


    for item in root.findall(
        "event"
    ):

        currency = clean(
            item.findtext("country")
        )


        if currency != "USD":
            continue


        impact = clean(
            item.findtext("impact")
        )


        if impact != "High":
            continue


        events.append(
            {
                "date": clean(
                    item.findtext("date")
                ),

                "time": clean(
                    item.findtext("time")
                ),

                "event": clean(
                    item.findtext("title")
                ),

                "actual": clean(
                    item.findtext("actual")
                ),

                "forecast": clean(
                    item.findtext("forecast")
                ),

                "previous": clean(
                    item.findtext("previous")
                ),

                "impact": impact,

                "currency": "USD",

                "source": "Forex Factory XML",
            }
        )


    return events