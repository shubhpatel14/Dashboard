import json
import requests
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from time import time


from config import API_KEY

BASE_URL = (
    "https://api.stlouisfed.org/fred/"
    "series/observations"
)
DEFAULT_LIMIT = 1000
SESSION = requests.Session()
CACHE_DIR = Path(".fred_cache")
CACHE_TTL_SECONDS = 30 * 60


# ==================================================
# HELPERS
# ==================================================

def safe_float(value):

    try:
        return float(value)

    except:
        return None


def _cache_path(series_id, limit):

    safe_id = "".join(
        character
        for character in str(series_id)
        if character.isalnum() or character in ("_", "-")
    )

    return CACHE_DIR / f"{safe_id}_{limit}.json"


def _read_disk_cache(series_id, limit, max_age_seconds=CACHE_TTL_SECONDS):

    path = _cache_path(series_id, limit)

    try:
        if not path.exists():
            return None

        if (
            max_age_seconds is not None
            and time() - path.stat().st_mtime > max_age_seconds
        ):
            return None

        with path.open("r", encoding="utf-8") as file:
            rows = json.load(file)

        return [
            {
                "date": datetime.strptime(row["date"], "%Y-%m-%d"),
                "value": row["value"]
            }
            for row in rows
        ]
    except Exception:
        return None


def _read_stale_disk_cache(series_id, limit):

    return _read_disk_cache(
        series_id,
        limit,
        max_age_seconds=None
    )


def _write_disk_cache(series_id, limit, rows):

    try:
        CACHE_DIR.mkdir(exist_ok=True)
        payload = [
            {
                "date": row["date"].strftime("%Y-%m-%d"),
                "value": row["value"]
            }
            for row in rows
        ]

        with _cache_path(series_id, limit).open("w", encoding="utf-8") as file:
            json.dump(payload, file)
    except Exception:
        pass


# ==================================================
# FETCH SERIES
# ==================================================

@lru_cache(maxsize=512)
def _fetch_series(
    series_id,
    limit=DEFAULT_LIMIT
):

    cached = _read_disk_cache(series_id, limit)
    if cached is not None:
        return cached

    params = {

        "series_id": series_id,

        "api_key": API_KEY,

        "file_type": "json",

        "sort_order": "desc",

        "limit": limit

    }

    try:
        response = SESSION.get(
            BASE_URL,
            params=params,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        if "observations" not in data:
            raise RuntimeError(data)

    except (requests.RequestException, RuntimeError, ValueError) as error:
        stale = _read_stale_disk_cache(series_id, limit)
        if stale is not None:
            return stale

        raise RuntimeError(
            f"Unable to fetch FRED series {series_id}; no cached data is available."
        ) from error

    cleaned = []

    for row in data["observations"]:

        value = safe_float(
            row["value"]
        )

        if value is None:
            continue

        cleaned.append({

            "date": datetime.strptime(
                row["date"],
                "%Y-%m-%d"
            ),

            "value": value

        })

    _write_disk_cache(series_id, limit, cleaned)

    return cleaned


def get_series(
    series_id,
    limit=DEFAULT_LIMIT
):

    if limit <= DEFAULT_LIMIT:
        return _fetch_series(series_id, DEFAULT_LIMIT)[:limit]

    return _fetch_series(series_id, limit)


def clear_fred_memory_cache():

    _fetch_series.cache_clear()


# ==================================================
# INTERNAL CONVERTER
# ==================================================

def _normalize(series):

    return series


# ==================================================
# LOOKBACK FUNCTIONS
# ==================================================

def get_current_value(series):

    series = _normalize(series)

    return series[0]["value"]


def get_previous_value(series):

    series = _normalize(series)

    if len(series) < 2:
        return series[0]["value"]

    return series[1]["value"]


def get_previous_date(series):

    series = _normalize(series)

    if len(series) < 2:
        return series[0]["date"]

    return series[1]["date"]


def get_current_date(series):

    series = _normalize(series)

    return series[0]["date"]


def get_value_months_ago(
    series,
    months_back
):

    series = _normalize(series)

    current_date = get_current_date(
        series
    )

    target_year = current_date.year

    target_month = (
        current_date.month -
        months_back
    )

    while target_month <= 0:

        target_month += 12

        target_year -= 1

    target_date = datetime(
        target_year,
        target_month,
        1
    )

    closest = min(

        series,

        key=lambda x:

        abs(
            (
                x["date"] -
                target_date
            ).days
        )

    )

    return closest["value"]


# ==================================================
# COMMON LOOKBACKS
# ==================================================

def get_3m_value(series):

    return get_value_months_ago(
        series,
        3
    )


def get_6m_value(series):

    return get_value_months_ago(
        series,
        6
    )


def get_12m_value(series):

    return get_value_months_ago(
        series,
        12
    )
