import io
import json
import zipfile
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import pandas as pd
import requests


CFTC_HISTORY_URL = "https://www.cftc.gov/files/dea/history/deacot{year}.zip"
CACHE_DIR = Path(".cot_cache")
CACHE_PATH = CACHE_DIR / "cot_legacy_futures.csv"
META_PATH = CACHE_DIR / "cot_meta.json"
CACHE_MAX_AGE_SECONDS = 60 * 60 * 12
HISTORY_YEARS = 6


ASSET_MARKETS = {
    "Gold": "GOLD - COMMODITY EXCHANGE INC.",
    "Bitcoin": "BITCOIN - CHICAGO MERCANTILE EXCHANGE",
    "SP500": "E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE",
    "Nasdaq": "NASDAQ MINI - CHICAGO MERCANTILE EXCHANGE",
    "Dollar": "USD INDEX - ICE FUTURES U.S.",
    "Bonds": "UST 10Y NOTE - CHICAGO BOARD OF TRADE"
}


LONG_COLUMN = "Noncommercial Positions-Long (All)"
SHORT_COLUMN = "Noncommercial Positions-Short (All)"
DATE_COLUMN = "As of Date in Form YYYY-MM-DD"
MARKET_COLUMN = "Market and Exchange Names"
REQUIRED_COLUMNS = [
    MARKET_COLUMN,
    DATE_COLUMN,
    LONG_COLUMN,
    SHORT_COLUMN
]


def calculate_bias(long_percent):

    if long_percent >= 75:
        return "Very Bullish", 90
    if long_percent >= 60:
        return "Bullish", 70
    if long_percent >= 40:
        return "Neutral", 50
    if long_percent >= 25:
        return "Bearish", 30
    return "Very Bearish", 10


def calculate_velocity(series, weeks=4):

    if len(series) <= weeks:
        return 0

    return int(series.iloc[-1] - series.iloc[-1 - weeks])


def _read_meta():

    if not META_PATH.exists():
        return {}

    try:
        return json.loads(META_PATH.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _write_meta(meta):

    CACHE_DIR.mkdir(exist_ok=True)
    META_PATH.write_text(json.dumps(meta, indent=2))


def _cache_is_fresh():

    meta = _read_meta()
    fetched_at = meta.get("fetched_at")

    if not CACHE_PATH.exists() or not fetched_at:
        return False

    if meta.get("history_years") != HISTORY_YEARS:
        return False

    try:
        age = datetime.utcnow() - datetime.fromisoformat(fetched_at)
    except ValueError:
        return False

    return age.total_seconds() < CACHE_MAX_AGE_SECONDS


def _download_year(year):

    response = requests.get(
        CFTC_HISTORY_URL.format(year=year),
        timeout=30
    )

    if response.status_code == 404:
        return pd.DataFrame()

    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        text_files = [
            name
            for name in archive.namelist()
            if name.lower().endswith(".txt")
        ]

        if not text_files:
            return pd.DataFrame()

        with archive.open(text_files[0]) as file:
            return pd.read_csv(file, usecols=REQUIRED_COLUMNS)


def _read_cached_cot_csv():

    return pd.read_csv(
        CACHE_PATH,
        usecols=REQUIRED_COLUMNS,
        parse_dates=[DATE_COLUMN],
        low_memory=False
    )


def fetch_latest_cot_data(force=False):

    if not force and _cache_is_fresh():
        return _read_cached_cot_csv()

    current_year = datetime.utcnow().year
    frames = []
    downloaded_years = []

    for year in range(current_year, current_year - HISTORY_YEARS, -1):
        frame = _download_year(year)

        if not frame.empty:
            frames.append(frame)
            downloaded_years.append(year)

    if not frames:
        if CACHE_PATH.exists():
            return _read_cached_cot_csv()
        raise RuntimeError("No CFTC COT data could be downloaded.")

    data = pd.concat(frames, ignore_index=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    data = data.drop_duplicates(
        subset=[MARKET_COLUMN, DATE_COLUMN],
        keep="last"
    ).sort_values([MARKET_COLUMN, DATE_COLUMN])

    CACHE_DIR.mkdir(exist_ok=True)
    data.to_csv(CACHE_PATH, index=False)
    _write_meta(
        {
            "fetched_at": datetime.utcnow().isoformat(),
            "source": CFTC_HISTORY_URL.format(year=current_year),
            "years": downloaded_years,
            "history_years": HISTORY_YEARS,
            "latest_report": str(data[DATE_COLUMN].max().date())
        }
    )

    return data


@lru_cache(maxsize=1)
def _cached_latest_cot_data():

    return fetch_latest_cot_data(force=False)


def _market_rows(asset, force=False, data=None):

    market = ASSET_MARKETS[asset]
    if data is None:
        data = fetch_latest_cot_data(force=force) if force else _cached_latest_cot_data()

    rows = data[data[MARKET_COLUMN] == market].copy()

    if rows.empty:
        raise ValueError(f"CFTC market not found for {asset}: {market}")

    rows[LONG_COLUMN] = pd.to_numeric(rows[LONG_COLUMN], errors="coerce").fillna(0)
    rows[SHORT_COLUMN] = pd.to_numeric(rows[SHORT_COLUMN], errors="coerce").fillna(0)
    rows = rows.sort_values(DATE_COLUMN)
    rows["net_position"] = rows[LONG_COLUMN] - rows[SHORT_COLUMN]
    total_position = rows[LONG_COLUMN] + rows[SHORT_COLUMN]
    rows["long_percent"] = (rows[LONG_COLUMN] / total_position.replace(0, pd.NA)) * 100
    rows["short_percent"] = 100 - rows["long_percent"]
    rows["weekly_change"] = rows["net_position"].diff().fillna(0)
    rows["velocity_4w"] = rows["net_position"] - rows["net_position"].shift(4)
    rows["position_percentile"] = rows["net_position"].rank(pct=True) * 100

    bias_data = rows["long_percent"].apply(calculate_bias)
    rows["bias"] = bias_data.apply(lambda item: item[0])
    rows["score"] = bias_data.apply(lambda item: item[1])

    return rows


def get_cot_data(asset, force=False, data=None):

    rows = _market_rows(asset, force=force, data=data)
    latest = rows.iloc[-1]
    long_percent = float(latest["long_percent"])
    bias = latest["bias"]
    score = int(latest["score"])
    net_series = rows["net_position"].astype(float).reset_index(drop=True)
    velocity = calculate_velocity(net_series)
    percentile = float(latest["position_percentile"])

    return {
        "asset": asset,
        "market": ASSET_MARKETS[asset],
        "last_updated": str(latest[DATE_COLUMN].date()),
        "long_contracts": int(latest[LONG_COLUMN]),
        "short_contracts": int(latest[SHORT_COLUMN]),
        "net_position": int(latest["net_position"]),
        "long_percent": round(long_percent, 2),
        "short_percent": round(float(latest["short_percent"]), 2),
        "weekly_change": int(latest["weekly_change"]),
        "velocity_4w": int(velocity),
        "position_percentile": round(percentile, 2),
        "bias": bias,
        "score": score,
        "trend": [
            {
                "Date": str(row[DATE_COLUMN].date()),
                "Net Position": int(row["net_position"]),
                "Long Exposure": round(float(row["long_percent"]), 2),
                "Short Exposure": round(float(row["short_percent"]), 2),
                "Weekly Change": int(row["weekly_change"]),
                "4W Velocity": int(row["velocity_4w"]) if pd.notna(row["velocity_4w"]) else 0,
                "Position Percentile": round(float(row["position_percentile"]), 2),
                "Bias": row["bias"],
                "Score": int(row["score"])
            }
            for _, row in rows.iterrows()
        ]
    }


def build_institutional_engine(force=False):

    assets = {}
    data = fetch_latest_cot_data(force=True) if force else _cached_latest_cot_data()

    for asset in ASSET_MARKETS:
        assets[asset] = get_cot_data(asset, force=force, data=data)

    latest_report = max(item["last_updated"] for item in assets.values())

    return {
        "score": round(sum(item["score"] for item in assets.values()) / len(assets), 2),
        "last_updated": latest_report,
        "assets": assets
    }
