from app.engines.macro.liquidity.scoring import build_liquidity_engine
from app.engines.macro.global_liquidity.scoring import build_global_liquidity_engine
from app.engines.macro.sentiment.scoring import build_sentiment_engine
from app.engines.macro.credit.scoring import build_credit_engine
from app.engines.macro.rates.scoring import build_rates_engine

from app.engines.helpers.asset_helpers import driver_row, weighted_asset_result


def build_bitcoin_engine():

    liquidity = build_liquidity_engine()
    global_liquidity = build_global_liquidity_engine()
    sentiment = build_sentiment_engine()
    credit = build_credit_engine()
    rates = build_rates_engine()

    # ------------------------------
    # Dollar Score
    # Higher dollar = bad for BTC
    # ------------------------------

    usd_score = global_liquidity["data"]["USD_INDEX"]["score"]

    # ------------------------------
    # Real Yield Score
    # Higher real yields = bad BTC
    # ------------------------------

    real_yield_score = rates["data"]["TEN_YEAR_REAL_YIELD_LEVEL"]["score"]

    return weighted_asset_result(
        [
            {"key": "LIQUIDITY", "weight": 30, **driver_row("Liquidity", liquidity["score"])},
            {"key": "GLOBAL_LIQUIDITY", "weight": 25, **driver_row("Global Liquidity", global_liquidity["score"])},
            {"key": "USD", "weight": 15, **driver_row("USD", usd_score, global_liquidity["data"]["USD_INDEX"])},
            {"key": "REAL_YIELD", "weight": 15, **driver_row("Real Yield", real_yield_score, rates["data"]["TEN_YEAR_REAL_YIELD_LEVEL"])},
            {"key": "SENTIMENT", "weight": 15, **driver_row("Sentiment", sentiment["score"], sentiment["data"]["VIX_LEVEL"])},
        ]
    )

