import sys
from functools import lru_cache

from app.core.config import get_settings

root = str(get_settings().project_root)
if root not in sys.path:
    sys.path.insert(0, root)

from engines.bitcoin import build_bitcoin_engine
from engines.bonds import build_bonds_engine
from engines.credit import build_credit_engine
from engines.dollar import build_dollar_engine
from engines.global_liquidity import build_global_liquidity_engine
from engines.gold import build_gold_engine
from engines.growth import build_growth_engine
from engines.housing import build_housing_engine
from engines.institutional import build_institutional_engine
from engines.inflation import build_inflation_engine
from engines.labor import build_labor_engine
from engines.liquidity import build_liquidity_engine
from engines.macro import build_macro_engine
from engines.nasdaq import build_nasdaq_engine
from engines.rates import build_rates_engine
from engines.recession import build_recession_engine
from engines.sentiment import build_sentiment_engine
from engines.sp500 import build_sp500_engine
from engines.trend import build_trend_engine
from models.status import get_regime
from data.fred_client import clear_fred_memory_cache
from engines.macro_surprise import clear_release_cache


MACRO_BUILDERS = {
    "liquidity": build_liquidity_engine,
    "global-liquidity": build_global_liquidity_engine,
    "rates": build_rates_engine,
    "inflation": build_inflation_engine,
    "growth": build_growth_engine,
    "labor": build_labor_engine,
    "credit": build_credit_engine,
    "sentiment": build_sentiment_engine,
    "housing": build_housing_engine,
    "recession": build_recession_engine,
}

ASSET_BUILDERS = {
    "gold": build_gold_engine,
    "bitcoin": build_bitcoin_engine,
    "sp500": build_sp500_engine,
    "nasdaq": build_nasdaq_engine,
    "dollar": build_dollar_engine,
    "bonds": build_bonds_engine,
}


@lru_cache(maxsize=1)
def get_macro_engine():
    return build_macro_engine()


@lru_cache(maxsize=1)
def get_trend_engine():
    return build_trend_engine()


@lru_cache(maxsize=32)
def get_macro_category(slug: str):
    return MACRO_BUILDERS[slug]()


@lru_cache(maxsize=32)
def get_asset_engine(slug: str):
    return ASSET_BUILDERS[slug]()


@lru_cache(maxsize=1)
def get_institutional_engine():
    return build_institutional_engine()


def macro_regime(score: float):
    return get_regime(score)


def refresh_engine_cache():
    clear_fred_memory_cache()
    clear_release_cache()
    get_macro_engine.cache_clear()
    get_trend_engine.cache_clear()
    get_macro_category.cache_clear()
    get_asset_engine.cache_clear()
    get_institutional_engine.cache_clear()

    macro = get_macro_engine()
    assets = {
        slug: get_asset_engine(slug)
        for slug in ASSET_BUILDERS
    }

    return {
        "macro_score": macro.get("score", 50),
        "category_scores": macro.get("scores", {}),
        "asset_scores": {
            slug: engine.get("score", 50)
            for slug, engine in assets.items()
        },
    }
