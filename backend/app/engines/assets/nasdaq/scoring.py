from app.engines.macro.liquidity.scoring import build_liquidity_engine
from app.engines.macro.global_liquidity.scoring import build_global_liquidity_engine
from app.engines.macro.rates.scoring import build_rates_engine
from app.engines.macro.sentiment.scoring import build_sentiment_engine
from app.engines.macro.credit.scoring import build_credit_engine
from app.engines.macro.growth.scoring import build_growth_engine
from app.engines.macro.inflation.scoring import build_inflation_engine

from app.engines.helpers.asset_helpers import driver_row, weighted_asset_result


def build_nasdaq_engine():

    liquidity = build_liquidity_engine()
    global_liquidity = build_global_liquidity_engine()
    rates = build_rates_engine()
    sentiment = build_sentiment_engine()
    credit = build_credit_engine()
    growth = build_growth_engine()
    inflation = build_inflation_engine()
    real_yield_score = rates["data"]["TEN_YEAR_REAL_YIELD_LEVEL"]["score"]
    return weighted_asset_result(
        [
            {"key": "LIQUIDITY", "weight": 25, **driver_row("Liquidity", liquidity["score"])},
            {"key": "REAL_YIELD", "weight": 25, **driver_row("Real Yield", real_yield_score, rates["data"]["TEN_YEAR_REAL_YIELD_LEVEL"])},
            {"key": "GROWTH", "weight": 15, **driver_row("Growth", growth["score"])},
            {"key": "SENTIMENT", "weight": 15, **driver_row("Sentiment", sentiment["score"])},
            {"key": "CREDIT", "weight": 10, **driver_row("Credit", credit["score"])},
            {"key": "INFLATION", "weight": 10, **driver_row("Inflation", inflation["score"])},
        ]
    )

