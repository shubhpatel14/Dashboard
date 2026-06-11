from app.engines.macro.global_liquidity.scoring import build_global_liquidity_engine
from app.engines.macro.inflation.scoring import build_inflation_engine
from app.engines.macro.liquidity.scoring import build_liquidity_engine
from app.engines.macro.rates.scoring import build_rates_engine
from app.engines.macro.sentiment.scoring import build_sentiment_engine

from app.engines.helpers.asset_helpers import driver_row, weighted_asset_result


def build_gold_engine():

    liquidity = build_liquidity_engine()
    global_liquidity = build_global_liquidity_engine()
    inflation = build_inflation_engine()
    rates = build_rates_engine()
    sentiment = build_sentiment_engine()

    usd = global_liquidity["data"]["USD_INDEX"]
    real_yield = rates["data"]["TEN_YEAR_REAL_YIELD_LEVEL"]
    inflation_pressure_score = 100 - inflation["score"]
    risk_score = 100 - sentiment["score"]

    return weighted_asset_result(
        [
            {"key": "REAL_YIELD", "weight": 35, **driver_row("Real Yield", real_yield["score"], real_yield)},
            {"key": "LIQUIDITY", "weight": 30, **driver_row("Liquidity", liquidity["score"])},
            {"key": "USD", "weight": 20, **driver_row("USD", usd["score"], usd)},
            {"key": "INFLATION", "weight": 10, **driver_row("Inflation Pressure", inflation_pressure_score, inflation["data"]["CPI_YOY"])},
            {"key": "RISK", "weight": 5, **driver_row("Risk", risk_score, sentiment["data"]["VIX_LEVEL"])},
        ]
    )

