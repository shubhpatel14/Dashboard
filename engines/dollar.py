from engines.growth import build_growth_engine
from engines.inflation import build_inflation_engine
from engines.labor import build_labor_engine
from engines.rates import build_rates_engine
from engines.sentiment import build_sentiment_engine

from engines.asset_helpers import driver_row, weighted_asset_result


def build_dollar_engine():

    rates = build_rates_engine()
    inflation = build_inflation_engine()
    growth = build_growth_engine()
    labor = build_labor_engine()
    sentiment = build_sentiment_engine()
    rate_differential_score = 100 - rates["score"]
    inflation_score = 100 - inflation["score"]
    sentiment_score = 100 - sentiment["score"]

    return weighted_asset_result(
        [
            {"key": "RATES", "weight": 35, **driver_row("Rates", rate_differential_score, rates["data"]["TEN_YEAR_YIELD_LEVEL"])},
            {"key": "GROWTH", "weight": 25, **driver_row("Growth", growth["score"])},
            {"key": "INFLATION", "weight": 15, **driver_row("Inflation", inflation_score, inflation["data"]["CPI_YOY"])},
            {"key": "LABOR", "weight": 15, **driver_row("Labor", labor["score"])},
            {"key": "SENTIMENT", "weight": 10, **driver_row("Sentiment", sentiment_score, sentiment["data"]["VIX_LEVEL"])},
        ]
    )
