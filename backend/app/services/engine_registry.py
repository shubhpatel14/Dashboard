from functools import lru_cache


# ASSETS
from app.engines.assets.bitcoin.scoring import build_bitcoin_engine
from app.engines.assets.bonds.scoring import build_bonds_engine
from app.engines.assets.dollar.scoring import build_dollar_engine
from app.engines.assets.gold.scoring import build_gold_engine
from app.engines.assets.nasdaq.scoring import build_nasdaq_engine
from app.engines.assets.sp500.scoring import build_sp500_engine


# MACRO
from app.engines.macro.credit.scoring import build_credit_engine
from app.engines.macro.global_liquidity.scoring import build_global_liquidity_engine
from app.engines.macro.growth.scoring import build_growth_engine
from app.engines.macro.housing.scoring import build_housing_engine
from app.engines.macro.inflation.scoring import build_inflation_engine
from app.engines.macro.labor.scoring import build_labor_engine
from app.engines.macro.liquidity.scoring import build_liquidity_engine
from app.engines.macro.macro.scoring import build_macro_engine
from app.engines.macro.rates.scoring import build_rates_engine
from app.engines.macro.recession.scoring import build_recession_engine
from app.engines.macro.sentiment.scoring import build_sentiment_engine
from app.engines.macro.trend.scoring import build_trend_engine
from app.engines.macro.macro_surprise.scoring import build_macro_surprise
from app.services.macro_score_normalizer import (
    normalize_macro_scores
)



@lru_cache()
def get_engines():

    return {

        # assets
        "bitcoin": build_bitcoin_engine,
        "bonds": build_bonds_engine,
        "dollar": build_dollar_engine,
        "gold": build_gold_engine,
        "nasdaq": build_nasdaq_engine,
        "sp500": build_sp500_engine,


        # macro
        "credit": build_credit_engine,
        "global_liquidity": build_global_liquidity_engine,
        "growth": build_growth_engine,
        "housing": build_housing_engine,
        "inflation": build_inflation_engine,
        "labor": build_labor_engine,
        "liquidity": build_liquidity_engine,
        "macro": build_macro_engine,
        "rates": build_rates_engine,
        "recession": build_recession_engine,
        "sentiment": build_sentiment_engine,
        "trend": build_trend_engine,

    }


def get_engine(name):

    return get_engines().get(name)



# ==================================================
# Compatibility exports for API routes
# ==================================================


MACRO_BUILDERS = {

    "credit": build_credit_engine,
    "global_liquidity": build_global_liquidity_engine,
    "growth": build_growth_engine,
    "housing": build_housing_engine,
    "inflation": build_inflation_engine,
    "labor": build_labor_engine,
    "liquidity": build_liquidity_engine,
    "macro": build_macro_engine,
    "rates": build_rates_engine,
    "recession": build_recession_engine,
    "sentiment": build_sentiment_engine,
    "trend": build_trend_engine,
    "macro_surprise": build_macro_surprise,

}


ASSET_BUILDERS = {

    "bitcoin": build_bitcoin_engine,
    "bonds": build_bonds_engine,
    "dollar": build_dollar_engine,
    "gold": build_gold_engine,
    "nasdaq": build_nasdaq_engine,
    "sp500": build_sp500_engine,

}



def get_institutional_engine():

    return {
        "status": "available",
        "message": "Institutional engine placeholder"
    }

# ==================================================
# API COMPATIBILITY FUNCTIONS
# ==================================================


def _run(builder):

    result = builder()


    return normalize_macro_scores(
        result
    )

    if result is None:
        return {}

    return result



def get_macro_category(name: str):

    builder = MACRO_BUILDERS.get(name)

    if builder is None:
        return {}

    return _run(builder)



def get_asset_engine(name: str):

    builder = ASSET_BUILDERS.get(name)

    if builder is None:
        return {}

    return _run(builder)



def get_macro_engine():

    return get_macro_category("macro")



def get_trend_engine():

    return get_macro_category("trend")



def macro_regime(score):

    if score >= 65:
        return "Expansion"

    if score <= 35:
        return "Contraction"

    return "Neutral"



def refresh_engine_cache():

    get_engines.cache_clear()

    return {
        "status": "success",
        "message": "engine cache refreshed"
    }



def get_institutional_engine():

    # temporary bridge until institutional engine migration

    assets = {}

    for key,builder in ASSET_BUILDERS.items():

        name = key.capitalize()

        assets[name] = {

            "long_percent": 0,
            "short_percent": 0,
            "net_position": 0,
            "weekly_change": 0,
            "velocity_4w": 0,
            "bias": "Neutral",
            "score": 50,
            "position_percentile": 50,
            "trend": []

        }

    return {
        "assets": assets
    }