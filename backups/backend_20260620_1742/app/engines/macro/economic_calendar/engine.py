from datetime import datetime


from app.data.investing_calendar import (
    fetch_investing_calendar,
)



def parse_date(row):

    try:

        return datetime.strptime(
            row.get("date"),
            "%Y-%m-%d"
        )

    except Exception:

        return datetime.max




def build_economic_calendar():


    events = fetch_investing_calendar()


    calendar = []



    for e in events:


        calendar.append(

            {

                "date":
                    e.get("date"),


                "time":
                    e.get("time")
                    or "All Day",


                "event":
                    e.get("event"),


                "country":
                    e.get("country"),


                "importance":
                    e.get("importance"),


                "actual":
                    e.get("actual"),


                "forecast":
                    e.get("forecast"),


                "previous":
                    e.get("previous"),


                "source":
                    e.get("source"),

            }

        )




    # OLD → TODAY → FUTURE
    # 06 → 16 → 25

    calendar = sorted(

        calendar,

        key=lambda x: (

            parse_date(x),

            x.get("time") or ""

        )

    )




    return {


        # keep frontend compatibility

        "upcoming_count":
            len(calendar),


        "released_count":
            0,


        "upcoming":
            calendar,


        "released":
            [],

    }