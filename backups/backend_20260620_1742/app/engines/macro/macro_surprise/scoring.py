from __future__ import annotations

import re
from datetime import date, timedelta
from functools import lru_cache
from typing import Any

from app.data.economic_calendar import build_economic_calendar

from app.services.macro_interpreter import (
    describe_surprise,
    describe_trend,
    explain_release,
    score_bias,
    tone_state,
)

from app.models.scoring import (
    clamp_score,
    weighted_average,
)


RELEASE_ALIASES = {

    "INITIAL_CLAIMS_WEEKLY_CHANGE": [
        "initial jobless claims"
    ],

    "CONTINUING_CLAIMS_WEEKLY_CHANGE": [
        "continuing claims"
    ],

    "UNEMPLOYMENT_RATE": [
        "unemployment rate"
    ],

    "NON_FARM_PAYROLL_CHANGE": [
        "non farm payroll",
        "nonfarm payroll",
        "payrolls"
    ],


    "CPI_YOY": [
        "cpi yoy",
        "consumer price index"
    ],

    "CORE_CPI_YOY": [
        "core cpi yoy"
    ],


    "RETAIL_SALES_MOM": [
        "retail sales"
    ],

    "ISM_MANUFACTURING_PMI": [
        "ism manufacturing pmi"
    ],
}


DEFAULT_SCALE = {

    "labor": 100.0,

    "inflation": 0.2,

    "growth": 1.0,

    "rates": 0.25,

}



def _event_scale(
    name: str,
    category: str
) -> float:

    n = name.lower()


    if "claims" in n:
        return 25.0


    if "unemployment" in n:
        return 0.2


    if "payroll" in n:
        return 75.0


    if "cpi" in n:
        return 0.2


    if "retail" in n:
        return 0.5


    return DEFAULT_SCALE.get(
        category,
        1
    )




def _normalize_text(value):

    text = str(
        value or ""
    ).lower()


    text = (
        text
        .replace("m/m","mom")
        .replace("y/y","yoy")
    )


    text = re.sub(
        r"[^a-z0-9 ]+",
        " ",
        text
    )


    return " ".join(
        text.split()
    )




def parse_macro_number(value):

    if value in [
        None,
        "",
        "N/A",
        "--"
    ]:
        return None


    text=str(value)

    text=text.replace(
        ",",
        ""
    )


    multiplier=1


    if text.endswith("%"):
        text=text[:-1]


    if text.endswith(("K","k")):

        text=text[:-1]


    elif text.endswith(("M","m")):

        multiplier=1000

        text=text[:-1]



    try:

        return float(text)*multiplier


    except:

        return None




def _score_delta(
    delta,
    scale,
    lower_is_bullish
):


    if scale <= 0:
        scale=1


    if lower_is_bullish:

        delta = -delta



    score = (
        50
        +
        max(
            -40,
            min(
                40,
                delta/scale*40
            )
        )
    )


    return clamp_score(score)




def release_score(
    name,
    actual,
    forecast,
    previous,
    category,
    lower_is_bullish=False
):


    surprise = (
        actual - forecast
    )


    trend_change = (
        actual - previous
    )


    scale=_event_scale(
        name,
        category
    )


    surprise_score=_score_delta(
        surprise,
        scale,
        lower_is_bullish
    )


    trend_score=_score_delta(
        trend_change,
        scale,
        lower_is_bullish
    )



    final_score = weighted_average(
        [
            (
                surprise_score,
                70
            ),

            (
                trend_score,
                30
            )
        ]
    )



    row={

        "name":name,

        "actual":actual,

        "forecast":forecast,

        "previous":previous,


        "surprise":round(
            surprise,
            4
        ),


        "trend_change":round(
            trend_change,
            4
        ),


        "surprise_score":surprise_score,


        "trend_score":trend_score,


        "score":final_score,


        "bias":score_bias(
            final_score
        ),


        "lower_is_bullish":
            lower_is_bullish,


        "trend_state":
            tone_state(final_score),

    }


    row["market_surprise"] = describe_surprise(
        name,
        surprise,
        surprise_score,
        lower_is_bullish
    )


    row["trend"] = describe_trend(
        name,
        trend_change,
        trend_score,
        lower_is_bullish
    )


    row["explanation"] = explain_release(
        row
    )


    return row




@lru_cache(maxsize=1)
def _recent_calendar_events():

    today=date.today()


    calendar = build_economic_calendar(
        start_date=today-timedelta(days=45),
        end_date=today,
        horizon_days=0,
        lookback_days=45,
    )


    return tuple(
        calendar.get(
            "events",
            []
        )
    )




def latest_release_event(key):


    aliases = RELEASE_ALIASES.get(
        key,
        []
    )


    matches=[]


    for e in _recent_calendar_events():
        print(e.get("event"))   


    for event in _recent_calendar_events():


        name=_normalize_text(
            event.get(
                "event"
            )
        )


        if any(
            a in name
            for a in aliases
        ):


            if (
                parse_macro_number(event.get("actual")) is not None
                and
                parse_macro_number(event.get("forecast")) is not None
                and
                parse_macro_number(event.get("previous")) is not None
            ):

                matches.append(
                    event
                )



    if not matches:

        return None


    return matches[-1]




def release_from_calendar(
    key,
    name,
    category,
    lower_is_bullish=False
):


    event=latest_release_event(
        key
    )


    if not event:
        return None



    return release_score(
        name=name,

        actual=parse_macro_number(
            event["actual"]
        ),

        forecast=parse_macro_number(
            event["forecast"]
        ),

        previous=parse_macro_number(
            event["previous"]
        ),

        category=category,

        lower_is_bullish=lower_is_bullish,
    )





def build_macro_surprise():


    tracked_events=[

        (
            "INITIAL_CLAIMS_WEEKLY_CHANGE",
            "Initial Jobless Claims",
            "labor",
            True,
            25
        ),

        (
            "UNEMPLOYMENT_RATE",
            "Unemployment Rate",
            "labor",
            True,
            20
        ),

        (
            "CPI_YOY",
            "CPI YoY",
            "inflation",
            True,
            25
        ),

        (
            "RETAIL_SALES_MOM",
            "Retail Sales",
            "growth",
            False,
            30
        ),

    ]


    events=[]


    for key,name,category,lower,weight in tracked_events:


        row=release_from_calendar(
            key=key,
            name=name,
            category=category,
            lower_is_bullish=lower,
        )


        if row:

            row["weight"]=weight

            events.append(row)



    if not events:

        return {

            "success":True,

            "score":50,

            "bias":"Neutral",

            "events":[]

        }



    score=weighted_average(
        [
            (
                e["score"],
                e["weight"]
            )
            for e in events
        ]
    )



    return {

        "success":True,

        "score":score,

        "bias":score_bias(score),

        "events":events,

    }