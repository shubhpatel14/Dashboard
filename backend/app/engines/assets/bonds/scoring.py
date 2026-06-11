from app.engines.macro.growth.scoring import build_growth_engine
from app.engines.macro.inflation.scoring import build_inflation_engine
from app.engines.macro.rates.scoring import build_rates_engine
from app.engines.macro.recession.scoring import build_recession_engine

from app.engines.helpers.asset_helpers import driver_row, weighted_asset_result


def build_bonds_engine():

    rates = build_rates_engine()
    inflation = build_inflation_engine()
    growth = build_growth_engine()
    recession = build_recession_engine()
    recession_risk_score = 100 - recession["score"]
    slowing_growth_score = 100 - growth["score"]

    return weighted_asset_result(
        [
            {"key": "RATES", "weight": 35, **driver_row("Rates", rates["score"], rates["data"]["TEN_YEAR_YIELD_LEVEL"])},
            {"key": "INFLATION", "weight": 30, **driver_row("Inflation", inflation["score"], inflation["data"]["CPI_YOY"])},
            {"key": "RECESSION", "weight": 20, **driver_row("Recession Risk", recession_risk_score, recession["data"]["YIELD_CURVE"])},
            {"key": "GROWTH", "weight": 15, **driver_row("Growth Slowdown", slowing_growth_score, growth["data"]["GDP_QOQ_ANNUALIZED"])},
        ]
    )


