from app.data.fred_client import (
    get_current_date,
    get_current_value,
    get_previous_value,
    get_series
)

from app.engines.helpers.helpers import (
    build_level_indicator,
    finalize_engine,
    score_level
)

from app.models.scoring import indicator_result
from app.models.scoring import pct_change


FEDFUNDS = "FEDFUNDS"
DFII10 = "DFII10"
GS10 = "GS10"
DGS2 = "DGS2"


def build_yield_curve_indicator():

    ten_year = get_series(GS10)
    two_year = get_series(DGS2)

    current = get_current_value(ten_year) - get_current_value(two_year)
    previous = get_previous_value(ten_year) - get_previous_value(two_year)
    change = pct_change(current, previous) if previous != 0 else current - previous
    score = score_level(
        current,
        -1,
        2
    )

    return indicator_result(
        current,
        previous,
        change,
        score,
        last_update=get_current_date(ten_year).date().isoformat(),
        history={
            "type": "spread",
            "codes": [GS10, DGS2]
        }
    )


def build_rates_engine():

    output = {
        "FED_FUNDS_RATE_LEVEL": build_level_indicator(
            FEDFUNDS,
            0,
            6,
            lower_is_bullish=True
        ),
        "TEN_YEAR_YIELD_LEVEL": build_level_indicator(
            GS10,
            2,
            6,
            lower_is_bullish=True
        ),
        "TWO_YEAR_YIELD_LEVEL": build_level_indicator(
            DGS2,
            1,
            6,
            lower_is_bullish=True
        ),
        "TEN_YEAR_REAL_YIELD_LEVEL": build_level_indicator(
            DFII10,
            0,
            3,
            lower_is_bullish=True
        ),
        "YIELD_CURVE_10Y_2Y": build_yield_curve_indicator()
    }

    weighted_scores = [
        (
            output["FED_FUNDS_RATE_LEVEL"]["score"],
            25
        ),
        (
            output["TEN_YEAR_YIELD_LEVEL"]["score"],
            20
        ),
        (
            output["TWO_YEAR_YIELD_LEVEL"]["score"],
            15
        ),
        (
            output["TEN_YEAR_REAL_YIELD_LEVEL"]["score"],
            25
        ),
        (
            output["YIELD_CURVE_10Y_2Y"]["score"],
            15
        )
    ]

    return finalize_engine(
        weighted_scores,
        output
    )


