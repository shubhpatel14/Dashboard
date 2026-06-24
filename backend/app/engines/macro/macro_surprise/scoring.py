from __future__ import annotations

# ======================================
# CATEGORY CLASSIFIER
# ======================================

def classify_event(name):

    n = str(name).lower()


    mapping = {

        "inflation":[
            "cpi",
            "pce",
            "ppi",
            "inflation",
            "price"
        ],

        "growth":[
            "gdp",
            "retail",
            "sales",
            "pmi",
            "production",
            "durable"
        ],

        "labor":[
            "payroll",
            "employment",
            "unemployment",
            "jobless",
            "claims",
            "jolts"
        ],

        "rates":[
            "fed rate",
            "rate decision",
            "interest rate"
        ],

        "sentiment":[
            "sentiment",
            "confidence",
            "michigan"
        ],
    }


    for category, keys in mapping.items():

        if any(
            k in n
            for k in keys
        ):
            return category


    return "general"



import re
from datetime import date, datetime, timedelta
from functools import lru_cache
from typing import Any

from sqlalchemy import text

from app.data.economic_calendar import build_economic_calendar
from app.database.connection import SessionLocal

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

    "AVERAGE_HOURLY_EARNINGS_MOM": [
        "average hourly earnings"
    ],

    "JOLTS_JOB_OPENINGS": [
        "jolts job openings",
        "jolts"
    ],


    "CPI_YOY": [
        "cpi yoy",
        "consumer price index"
    ],

    "CPI_MOM": [
        "cpi mom"
    ],

    "CORE_CPI_YOY": [
        "core cpi yoy"
    ],

    "CORE_CPI_MOM": [
        "core cpi mom"
    ],

    "PPI_MOM": [
        "ppi",
        "producer price index"
    ],

    "CORE_PPI_MOM": [
        "core ppi"
    ],

    "PCE_MOM": [
        "pce price index",
        "pce price",
        "pce mom"
    ],

    "PCE_YOY": [
        "pce yoy"
    ],

    "CORE_PCE_MOM": [
        "core pce mom"
    ],

    "CORE_PCE_YOY": [
        "core pce yoy"
    ],

    "MICHIGAN_INFLATION_EXPECTATIONS": [
        "michigan 1 year inflation expectations",
        "michigan 5 year inflation expectations",
        "inflation expectations"
    ],


    "RETAIL_SALES_MOM": [
        "retail sales"
    ],

    "CORE_RETAIL_SALES_MOM": [
        "core retail sales"
    ],

    "ISM_MANUFACTURING_PMI": [
        "ism manufacturing pmi"
    ],

    "ISM_SERVICES_PMI": [
        "ism services pmi"
    ],

    "GDP_QOQ": [
        "gdp qoq",
        "gdp"
    ],

    "GDP_QOQ_ANNUALIZED": [
        "gdp qoq",
        "gdp"
    ],

    "INDUSTRIAL_PRODUCTION_MOM": [
        "industrial production"
    ],

    "DURABLE_GOODS_ORDERS_MOM": [
        "durable goods orders"
    ],

    "FACTORY_ORDERS_MOM": [
        "factory orders"
    ],

    "FED_RATE_DECISION": [
        "fed interest rate decision",
        "interest rate decision",
        "fed rate decision"
    ],

    "MICHIGAN_CONSUMER_SENTIMENT": [
        "michigan consumer sentiment"
    ],

    "CONSUMER_CONFIDENCE": [
        "consumer confidence"
    ],
}


DEFAULT_SCALE = {

    "labor": 100.0,

    "inflation": 0.2,

    "growth": 1.0,

    "rates": 0.25,

}


TRACKED_EVENTS = [
    ("CPI_MOM", "CPI MoM", "inflation", True, 18),
    ("CPI_YOY", "CPI YoY", "inflation", True, 12),
    ("CORE_CPI_MOM", "Core CPI MoM", "inflation", True, 18),
    ("CORE_CPI_YOY", "Core CPI YoY", "inflation", True, 12),
    ("PCE_MOM", "PCE MoM", "inflation", True, 10),
    ("PCE_YOY", "PCE YoY", "inflation", True, 6),
    ("CORE_PCE_MOM", "Core PCE MoM", "inflation", True, 10),
    ("CORE_PCE_YOY", "Core PCE YoY", "inflation", True, 6),
    ("PPI_MOM", "PPI MoM", "inflaption", True, 6),
    ("CORE_PPI_MOM", "Core PPI MoM", "inflation", True, 2),
    ("GDP_QOQ_ANNUALIZED", "GDP QoQ Annualized", "growth", False, 25),
    ("GDP_QOQ", "GDP QoQ", "growth", False, 15),
    ("RETAIL_SALES_MOM", "Retail Sales MoM", "growth", False, 25),
    ("CORE_RETAIL_SALES_MOM", "Core Retail Sales MoM", "growth", False, 10),
    ("ISM_MANUFACTURING_PMI", "ISM Manufacturing PMI", "growth", False, 15),
    ("ISM_SERVICES_PMI", "ISM Services PMI", "growth", False, 10),
    ("NON_FARM_PAYROLL_CHANGE", "Non Farm Payrolls", "labor", False, 30),
    ("INITIAL_CLAIMS_WEEKLY_CHANGE", "Initial Jobless Claims", "labor", True, 20),
    ("CONTINUING_CLAIMS_WEEKLY_CHANGE", "Continuing Claims", "labor", True, 10),
    ("UNEMPLOYMENT_RATE", "Unemployment Rate", "labor", True, 25),
    ("FED_RATE_DECISION", "FOMC Rate Decision", "rates", True, 100),
    ("CONSUMER_CONFIDENCE", "Consumer Confidence", "sentiment", False, 45),
    ("MICHIGAN_CONSUMER_SENTIMENT", "Michigan Consumer Sentiment", "sentiment", False, 55),
]


TRACKED_EVENT_BY_NAME = {
    name: {
        "key": key,
        "category": category,
        "lower_is_bullish": lower,
        "weight": weight,
    }
    for key, name, category, lower, weight in TRACKED_EVENTS
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


def _release_numbers(event):

    actual = parse_macro_number(
        event.get("actual")
    )

    forecast = parse_macro_number(
        event.get("forecast")
    )

    previous = parse_macro_number(
        event.get("previous")
    )

    return actual, forecast, previous


def _has_actual_and_forecast(event) -> bool:

    actual, forecast, _ = _release_numbers(
        event
    )

    return (
        actual is not None
        and
        forecast is not None
    )




def _has_numeric_release(event) -> bool:

    actual, forecast, previous = _release_numbers(
        event
    )

    return (
        actual is not None
        and forecast is not None
        and previous is not None
    )


def _event_release_date(event):

    value = (
        event.get("date")
        or event.get("release_date")
    )

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if not value:
        return None

    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _ensure_surprise_table(db):

    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS economic_surprises(
                id SERIAL PRIMARY KEY,
                category TEXT NOT NULL,
                event_name TEXT NOT NULL,
                actual FLOAT NOT NULL,
                forecast FLOAT NOT NULL,
                previous FLOAT NOT NULL,
                surprise FLOAT NOT NULL,
                score FLOAT NOT NULL,
                bias TEXT NOT NULL,
                release_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                CONSTRAINT uq_economic_surprises_release
                    UNIQUE(category,event_name,release_date)
            )
            """
        )
    )

    db.execute(
        text(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS ux_economic_surprises_release
            ON economic_surprises(category,event_name,release_date)
            """
        )
    )

    db.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS ix_economic_surprises_latest
            ON economic_surprises(category,event_name,release_date DESC)
            """
        )
    )


def _save_surprise(row):

    release_date = row.get("release_date")

    if not release_date:
        return

    db = SessionLocal()

    try:
        _ensure_surprise_table(db)

        db.execute(
            text(
                """
                INSERT INTO economic_surprises
                (
                    category,
                    event_name,
                    actual,
                    forecast,
                    previous,
                    surprise,
                    score,
                    bias,
                    release_date
                )
                VALUES
                (
                    :category,
                    :event_name,
                    :actual,
                    :forecast,
                    :previous,
                    :surprise,
                    :score,
                    :bias,
                    :release_date
                )
                ON CONFLICT(category,event_name,release_date)
                DO UPDATE SET
                    actual = EXCLUDED.actual,
                    forecast = EXCLUDED.forecast,
                    previous = EXCLUDED.previous,
                    surprise = EXCLUDED.surprise,
                    score = EXCLUDED.score,
                    bias = EXCLUDED.bias
                """
            ),
            {
                "category": row.get("category"),
                "event_name": row.get("name"),
                "actual": row.get("actual"),
                "forecast": row.get("forecast"),
                "previous": row.get("previous"),
                "surprise": row.get("surprise"),
                "score": row.get("score"),
                "bias": row.get("bias"),
                "release_date": release_date,
            }
        )

        db.commit()

    finally:
        db.close()


def _load_latest_saved_surprises():

    db = SessionLocal()

    try:
        _ensure_surprise_table(db)

        rows = (
            db.execute(
                text(
                    """
                    SELECT DISTINCT ON(category,event_name)
                        category,
                        event_name,
                        actual,
                        forecast,
                        previous,
                        release_date
                    FROM economic_surprises
                    ORDER BY category,event_name,release_date DESC
                    """
                )
            )
            .mappings()
            .all()
        )

    finally:
        db.close()

    events = []

    for item in rows:
        meta = TRACKED_EVENT_BY_NAME.get(
            item["event_name"],
            {}
        )
        category = item["category"]
        lower = meta.get(
            "lower_is_bullish",
            False
        )

        row = release_score(
            name=item["event_name"],
            actual=float(item["actual"]),
            forecast=float(item["forecast"]),
            previous=float(item["previous"]),
            category=category,
            lower_is_bullish=lower,
        )

        row["category"] = category
        row["weight"] = meta.get(
            "weight",
            1
        )

        release_date = item["release_date"]

        if hasattr(release_date, "isoformat"):
            release_date = release_date.isoformat()

        row["release_date"] = str(release_date)

        events.append(row)

    return events


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


    for event in _recent_calendar_events():


        name=_normalize_text(
            event.get(
                "event"
            )
        )

        if key in ["CPI_MOM", "CPI_YOY"] and "core cpi" in name:
            continue

        if key == "PPI_MOM" and "core ppi" in name:
            continue

        if key in ["PCE_MOM", "PCE_YOY"] and "core pce" in name:
            continue

        if key == "RETAIL_SALES_MOM" and "core retail" in name:
            continue


        if any(
            a in name
            for a in aliases
        ):


            if _has_actual_and_forecast(event):

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
    lower_is_bullish=False,
    require_previous=False
):


    event=latest_release_event(
        key
    )


    if not event:
        return None

    actual, forecast, previous = _release_numbers(
        event
    )

    if actual is None or forecast is None:
        return None

    if require_previous and previous is None:
        return None

    if previous is None:
        previous = forecast


    row = release_score(
        name=name,

        actual=actual,

        forecast=forecast,

        previous=previous,

        category=category,

        lower_is_bullish=lower_is_bullish,
    )

    release_date = _event_release_date(
        event
    )

    if release_date:
        row["release_date"] = release_date.isoformat()

    return row





def build_macro_surprise():


    current_events=[]

    _recent_calendar_events.cache_clear()


    for key,name,category,lower,weight in TRACKED_EVENTS:


        row=release_from_calendar(
            key=key,
            name=name,
            category=category,
            lower_is_bullish=lower,
            require_previous=True,
        )


        if row:

            row["weight"]=weight

            row["category"]=category

            current_events.append(row)

            try:

                _save_surprise(row)

            except Exception:

                pass


    try:

        events = _load_latest_saved_surprises()

    except Exception:

        events = current_events



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
