import calendar
import re
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import requests


NEWS_API_KEY = "m2GaidmpOevVR8z1SQCL99iN9kdTMX5d"

FMP_ECONOMIC_CALENDAR_URL = (
    "https://financialmodelingprep.com/api/v3/economic_calendar"
)

HIGH_IMPACT_EVENTS = {
    "cpi mom": ("Inflation", "CPI MoM"),
    "cpi yoy": ("Inflation", "CPI YoY"),
    "core cpi mom": ("Inflation", "Core CPI MoM"),
    "core cpi yoy": ("Inflation", "Core CPI YoY"),
    "pce mom": ("Inflation", "PCE MoM"),
    "core pce mom": ("Inflation", "Core PCE MoM"),
    "ppi mom": ("Inflation", "PPI MoM"),
    "core ppi mom": ("Inflation", "Core PPI MoM"),
    "non farm payrolls": ("Labor", "Non Farm Payrolls"),
    "nonfarm payrolls": ("Labor", "Non Farm Payrolls"),
    "unemployment rate": ("Labor", "Unemployment Rate"),
    "average hourly earnings": ("Labor", "Average Hourly Earnings"),
    "initial jobless claims": ("Labor", "Initial Jobless Claims"),
    "continuing claims": ("Labor", "Continuing Claims"),
    "gdp qoq": ("Growth", "GDP QoQ"),
    "gdp yoy": ("Growth", "GDP YoY"),
    "retail sales": ("Growth", "Retail Sales"),
    "core retail sales": ("Growth", "Core Retail Sales"),
    "ism manufacturing pmi": ("Growth", "ISM Manufacturing PMI"),
    "ism services pmi": ("Growth", "ISM Services PMI"),
    "industrial production": ("Growth", "Industrial Production"),
    "housing starts": ("Housing", "Housing Starts"),
    "building permits": ("Housing", "Building Permits"),
    "new home sales": ("Housing", "New Home Sales"),
    "fomc rate decision": ("Federal Reserve", "FOMC Rate Decision"),
    "fomc statement": ("Federal Reserve", "FOMC Statement"),
    "powell speech": ("Federal Reserve", "Powell Speech"),
    "fomc minutes": ("Federal Reserve", "FOMC Minutes")
}

FOMC_DATES = {
    2026: [
        date(2026, 1, 28),
        date(2026, 3, 18),
        date(2026, 4, 29),
        date(2026, 6, 17),
        date(2026, 7, 29),
        date(2026, 9, 16),
        date(2026, 10, 28),
        date(2026, 12, 9)
    ]
}


def _clean_text(value):

    return re.sub(
        r"\s+",
        " ",
        str(value or "").strip()
    )


def _normalize_name(value):

    text = _clean_text(value).lower()
    text = text.replace("m/m", "mom")
    text = text.replace("y/y", "yoy")
    text = text.replace("month over month", "mom")
    text = text.replace("year over year", "yoy")
    text = re.sub(r"[^a-z0-9% ]+", " ", text)

    return re.sub(
        r"\s+",
        " ",
        text
    ).strip()


def _match_event(raw_name):

    normalized = _normalize_name(raw_name)

    for needle, result in HIGH_IMPACT_EVENTS.items():
        if needle in normalized:
            if needle == "retail sales" and "core retail sales" in normalized:
                continue

            return result

    return None


def _parse_datetime(value):

    if not value:
        return None

    text = str(value).replace("Z", "+00:00")

    try:
        return datetime.fromisoformat(text)
    except ValueError:
        pass

    for fmt in [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d"
    ]:
        try:
            return datetime.strptime(text[:len(fmt)], fmt)
        except ValueError:
            continue

    return None


def _event_time_parts(value):

    event_datetime = _parse_datetime(value)

    if event_datetime is None:
        return ("N/A", "N/A", None)

    if event_datetime.tzinfo is None:
        event_datetime = event_datetime.replace(
            tzinfo=ZoneInfo("America/New_York")
        )
    else:
        event_datetime = event_datetime.astimezone(
            ZoneInfo("America/New_York")
        )

    return (
        event_datetime.date().isoformat(),
        event_datetime.strftime("%H:%M"),
        event_datetime
    )


def _parse_number(value):

    if value in [None, "", "N/A", "Pending", "--"]:
        return None

    text = str(value).strip()
    multiplier = 1

    if text.endswith("%"):
        text = text[:-1]

    if text.endswith(("K", "k")):
        multiplier = 1_000
        text = text[:-1]
    elif text.endswith(("M", "m")):
        multiplier = 1_000_000
        text = text[:-1]
    elif text.endswith(("B", "b")):
        multiplier = 1_000_000_000
        text = text[:-1]

    text = text.replace(",", "")

    try:
        return float(text) * multiplier
    except ValueError:
        return None


def _format_value(value):

    if value in [None, "", "--"]:
        return "N/A"

    return str(value)


def _format_surprise(actual, forecast):

    actual_value = _parse_number(actual)
    forecast_value = _parse_number(forecast)

    if actual_value is None or forecast_value is None:
        return "--"

    surprise = actual_value - forecast_value

    if abs(surprise) < 0.0001:
        return "0"

    return f"{surprise:.2f}".rstrip("0").rstrip(".")


def _surprise_tone(surprise):

    value = _parse_number(surprise)

    if value is None:
        return "Neutral"

    if value > 0:
        return "Positive"

    if value < 0:
        return "Negative"

    return "Neutral"


def _build_calendar_row(
    event,
    event_datetime,
    category,
    display_event,
    previous,
    forecast,
    actual,
    source="API"
):

    release_date, release_time, aware_datetime = _event_time_parts(
        event_datetime
    )
    actual_value = _format_value(actual)

    if actual_value == "N/A":
        actual_value = "Pending"

    status = "Released" if actual_value != "Pending" else "Upcoming"
    surprise = _format_surprise(
        actual_value,
        forecast
    )

    return {
        "date": release_date,
        "event": display_event or event,
        "time": release_time,
        "previous": _format_value(previous),
        "forecast": _format_value(forecast),
        "actual": actual_value,
        "surprise": surprise,
        "impact": "High",
        "status": status,
        "category": category,
        "currency": "USD",
        "surprise_tone": _surprise_tone(surprise),
        "event_datetime": aware_datetime,
        "source": source
    }


def _extract_api_value(row, *keys):

    for key in keys:
        if key in row and row[key] not in [None, ""]:
            return row[key]

    return None


def _normalize_api_row(row):

    raw_event = _extract_api_value(
        row,
        "event",
        "title",
        "name"
    )
    match = _match_event(raw_event)

    if not match:
        return None

    category, display_event = match
    country = _clean_text(
        _extract_api_value(
            row,
            "country",
            "countryName"
        )
    ).lower()
    currency = _clean_text(
        _extract_api_value(
            row,
            "currency"
        )
    ).upper()

    if country not in ["", "united states", "us", "usa"] and currency != "USD":
        return None

    return _build_calendar_row(
        raw_event,
        _extract_api_value(row, "date", "datetime", "time"),
        category,
        display_event,
        _extract_api_value(row, "previous", "prev"),
        _extract_api_value(row, "forecast", "estimate", "consensus"),
        _extract_api_value(row, "actual"),
        source="Financial Modeling Prep"
    )


def fetch_calendar_from_api(start_date, end_date):

    response = requests.get(
        FMP_ECONOMIC_CALENDAR_URL,
        params={
            "from": start_date.isoformat(),
            "to": end_date.isoformat(),
            "apikey": NEWS_API_KEY
        },
        timeout=20
    )
    response.raise_for_status()

    data = response.json()

    if isinstance(data, dict) and data.get("Error Message"):
        raise RuntimeError(data["Error Message"])

    rows = []

    for item in data if isinstance(data, list) else []:
        normalized = _normalize_api_row(item)

        if normalized:
            rows.append(normalized)

    return rows


def _fallback_event(
    release_date,
    release_time,
    category,
    event
):

    return _build_calendar_row(
        event,
        f"{release_date.isoformat()} {release_time}:00",
        category,
        event,
        "N/A",
        "N/A",
        None,
        source="Fallback Schedule"
    )


def _month_start(value):

    return date(value.year, value.month, 1)


def _add_months(value, months):

    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1

    return date(year, month, 1)


def _next_business_day(value):

    while value.weekday() >= 5:
        value += timedelta(days=1)

    return value


def _first_weekday(year, month, weekday):

    value = date(year, month, 1)

    while value.weekday() != weekday:
        value += timedelta(days=1)

    return value


def _business_day_number(year, month, number):

    value = date(year, month, 1)
    count = 0

    while value.month == month:
        if value.weekday() < 5:
            count += 1

            if count == number:
                return value

        value += timedelta(days=1)

    return _next_business_day(
        date(year, month, calendar.monthrange(year, month)[1])
    )


def _last_weekday(year, month, weekday):

    value = date(year, month, calendar.monthrange(year, month)[1])

    while value.weekday() != weekday:
        value -= timedelta(days=1)

    return value


def _monthly_fallback_events(month):

    year = month.year
    month_number = month.month
    nfp_date = _first_weekday(year, month_number, 4)
    cpi_date = _next_business_day(date(year, month_number, 10))
    ppi_date = _next_business_day(cpi_date + timedelta(days=1))
    retail_date = _next_business_day(date(year, month_number, 15))
    housing_date = _next_business_day(date(year, month_number, 17))
    pce_date = _last_weekday(year, month_number, 4)

    events = [
        _fallback_event(cpi_date, "08:30", "Inflation", "CPI MoM"),
        _fallback_event(cpi_date, "08:30", "Inflation", "CPI YoY"),
        _fallback_event(cpi_date, "08:30", "Inflation", "Core CPI MoM"),
        _fallback_event(cpi_date, "08:30", "Inflation", "Core CPI YoY"),
        _fallback_event(ppi_date, "08:30", "Inflation", "PPI MoM"),
        _fallback_event(ppi_date, "08:30", "Inflation", "Core PPI MoM"),
        _fallback_event(pce_date, "08:30", "Inflation", "PCE MoM"),
        _fallback_event(pce_date, "08:30", "Inflation", "Core PCE MoM"),
        _fallback_event(nfp_date, "08:30", "Labor", "Non Farm Payrolls"),
        _fallback_event(nfp_date, "08:30", "Labor", "Unemployment Rate"),
        _fallback_event(nfp_date, "08:30", "Labor", "Average Hourly Earnings"),
        _fallback_event(_business_day_number(year, month_number, 1), "10:00", "Growth", "ISM Manufacturing PMI"),
        _fallback_event(_business_day_number(year, month_number, 3), "10:00", "Growth", "ISM Services PMI"),
        _fallback_event(retail_date, "08:30", "Growth", "Retail Sales"),
        _fallback_event(retail_date, "08:30", "Growth", "Core Retail Sales"),
        _fallback_event(_next_business_day(retail_date), "09:15", "Growth", "Industrial Production"),
        _fallback_event(housing_date, "08:30", "Housing", "Housing Starts"),
        _fallback_event(housing_date, "08:30", "Housing", "Building Permits"),
        _fallback_event(_next_business_day(date(year, month_number, 25)), "10:00", "Housing", "New Home Sales")
    ]

    if month_number in [1, 4, 7, 10]:
        gdp_date = _last_weekday(year, month_number, 3)
        events.extend(
            [
                _fallback_event(gdp_date, "08:30", "Growth", "GDP QoQ"),
                _fallback_event(gdp_date, "08:30", "Growth", "GDP YoY")
            ]
        )

    return events


def _weekly_fallback_events(start_date, end_date):

    events = []
    value = start_date

    while value <= end_date:
        if value.weekday() == 3:
            events.extend(
                [
                    _fallback_event(value, "08:30", "Labor", "Initial Jobless Claims"),
                    _fallback_event(value, "08:30", "Labor", "Continuing Claims")
                ]
            )

        value += timedelta(days=1)

    return events


def _fed_fallback_events(start_date, end_date):

    events = []

    for year in range(start_date.year, end_date.year + 1):
        for fomc_date in FOMC_DATES.get(year, []):
            if start_date <= fomc_date <= end_date:
                events.extend(
                    [
                        _fallback_event(fomc_date, "14:00", "Federal Reserve", "FOMC Rate Decision"),
                        _fallback_event(fomc_date, "14:00", "Federal Reserve", "FOMC Statement"),
                        _fallback_event(fomc_date + timedelta(days=21), "14:00", "Federal Reserve", "FOMC Minutes")
                    ]
                )

    return events


def build_fallback_calendar(start_date, end_date):

    events = []
    month = _month_start(start_date)

    while month <= _month_start(end_date):
        events.extend(_monthly_fallback_events(month))
        month = _add_months(month, 1)

    events.extend(_weekly_fallback_events(start_date, end_date))
    events.extend(_fed_fallback_events(start_date, end_date))

    deduped = {
        (event["date"], event["time"], event["event"]): event
        for event in events
        if start_date.isoformat() <= event["date"] <= end_date.isoformat()
    }

    return sorted(
        deduped.values(),
        key=lambda item: (item["date"], item["time"], item["event"])
    )


def build_economic_calendar(
    start_date=None,
    end_date=None,
    horizon_days=90,
    lookback_days=7
):

    today = date.today()
    start_date = start_date or today - timedelta(days=lookback_days)
    end_date = end_date or today + timedelta(days=horizon_days)

    try:
        rows = fetch_calendar_from_api(start_date, end_date)
        source = "Financial Modeling Prep"
    except Exception as error:
        rows = build_fallback_calendar(start_date, end_date)
        source = f"Fallback Schedule: {error}"

    return {
        "source": source,
        "events": sorted(
            rows,
            key=lambda item: (
                item["date"],
                item["time"],
                item["event"]
            )
        )
    }


def get_next_major_event(events):

    now = datetime.now(ZoneInfo("America/New_York"))

    upcoming = [
        event
        for event in events
        if event.get("status") == "Upcoming"
        and event.get("event_datetime") is not None
        and event["event_datetime"] >= now
    ]

    if not upcoming:
        return None

    return sorted(
        upcoming,
        key=lambda item: item["event_datetime"]
    )[0]


def format_countdown(event):

    if not event or event.get("event_datetime") is None:
        return "N/A"

    now = datetime.now(ZoneInfo("America/New_York"))
    remaining = event["event_datetime"] - now

    if remaining.total_seconds() <= 0:
        return "Released"

    days = remaining.days
    hours = remaining.seconds // 3600
    minutes = (remaining.seconds % 3600) // 60

    if days > 0:
        return f"{days}d {hours:02d}h {minutes:02d}m"

    return f"{hours:02d}h {minutes:02d}m"


def build_high_impact_calendar(*args, **kwargs):

    return build_economic_calendar()["events"]


