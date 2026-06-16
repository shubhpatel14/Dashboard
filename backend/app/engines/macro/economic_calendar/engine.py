from datetime import date, timedelta, datetime


from app.data.economic_calendar import (
    build_economic_calendar as fetch_calendar,
)



def event_importance(name):

    high = [
        "CPI",
        "PCE",
        "Payroll",
        "FOMC",
        "GDP",
        "Powell",
        "PMI",
        "Retail",
        "Interest Rate",
        "Rate Decision"
    ]


    if any(
        x.lower() in str(name).lower()
        for x in high
    ):

        return "High"


    return "Medium"



def parse_date(x):

    try:

        return datetime.strptime(
            x.get("date"),
            "%d/%m/%Y"
        )

    except Exception:

        return datetime.max



def build_economic_calendar():


    today = date.today()


    calendar = fetch_calendar(
        today - timedelta(days=7),
        today + timedelta(days=30),
    )


    events = calendar.get(
        "events",
        []
    )


    upcoming = []

    released = []


    for e in events:


        name = (
            e.get("event")
            or e.get("name")
            or ""
        )


        row = {

            "date":
                e.get("date"),


            "time":
                e.get("time"),


            "event":
                name,


            "country":
                e.get(
                    "country"
                ),


            "importance":
                event_importance(
                    name
                ),


            "actual":
                e.get(
                    "actual"
                ),


            "forecast":
                e.get(
                    "forecast"
                ),


            "previous":
                e.get(
                    "previous"
                ),


            "source":
                e.get(
                    "source"
                ),

        }


        event_date = parse_date(
            row
        ).date()


        if (
            event_date >= today
            and row["actual"] in [
                None,
                "",
                "N/A",
                "Pending"
            ]
        ):

            upcoming.append(
                row
            )

        else:

            released.append(
                row
            )



    upcoming = sorted(
        upcoming,
        key=parse_date
    )


    released = sorted(
        released,
        key=parse_date,
        reverse=True
    )



    return {

        "upcoming_count":
            len(upcoming),


        "released_count":
            len(released),


        "upcoming":
            upcoming,


        "released":
            released,

    }
