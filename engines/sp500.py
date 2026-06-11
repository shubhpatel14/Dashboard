from engines.credit import build_credit_engine
from engines.growth import build_growth_engine
from engines.housing import build_housing_engine
from engines.inflation import build_inflation_engine
from engines.labor import build_labor_engine
from engines.liquidity import build_liquidity_engine
from engines.sentiment import build_sentiment_engine

from engines.asset_helpers import driver_row, weighted_asset_result


def build_sp500_engine():

    liquidity = build_liquidity_engine()
    inflation = build_inflation_engine()
    growth = build_growth_engine()
    labor = build_labor_engine()
    credit = build_credit_engine()
    sentiment = build_sentiment_engine()
    housing = build_housing_engine()
    return weighted_asset_result(
        [
            {"key": "GROWTH", "weight": 25, **driver_row("Growth", growth["score"])},
            {"key": "LIQUIDITY", "weight": 20, **driver_row("Liquidity", liquidity["score"])},
            {"key": "LABOR", "weight": 15, **driver_row("Labor", labor["score"])},
            {"key": "CREDIT", "weight": 15, **driver_row("Credit", credit["score"])},
            {"key": "INFLATION", "weight": 10, **driver_row("Inflation", inflation["score"])},
            {"key": "SENTIMENT", "weight": 10, **driver_row("Sentiment", sentiment["score"])},
            {"key": "HOUSING", "weight": 5, **driver_row("Housing", housing["score"])},
        ]
    )
