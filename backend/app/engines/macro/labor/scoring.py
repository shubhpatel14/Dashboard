from app.data.fred_client import (
    get_current_date,
    get_current_value,
    get_previous_value,
    get_series
)

from app.engines.helpers.helpers import (
    build_change_indicator,
    build_level_indicator,
    finalize_engine,
    score_change,
    score_level
)

from app.models.scoring import (
    indicator_result,
    pct_change
)


UNRATE = "UNRATE"
PAYEMS = "PAYEMS"
ICSA = "ICSA"
CCSA = "CCSA"
CIVPART = "CIVPART"


def build_payroll_change_indicator():

    series = get_series(PAYEMS)
    current = get_current_value(series) - get_previous_value(series)
    previous = get_previous_value(series) - series[2]["value"]
    change = pct_change(current, previous) if previous != 0 else current - previous
    score = score_change(
        current,
        -100,
        300
    )

    return indicator_result(
        current,
        previous,
        change,
        score,
        last_update=get_current_date(series).date().isoformat()
    )


def build_labor_engine():

    output = {}
    weighted_scores = []

    output["NON_FARM_PAYROLL_CHANGE"] = build_payroll_change_indicator()
    weighted_scores.append(
        (
            output["NON_FARM_PAYROLL_CHANGE"]["score"],
            30
        )
    )

    weekly_indicators = {
        "INITIAL_CLAIMS_WEEKLY_CHANGE": {
            "code": ICSA,
            "weight": 25
        },
        "CONTINUING_CLAIMS_WEEKLY_CHANGE": {
            "code": CCSA,
            "weight": 15
        }
    }

    for name, info in weekly_indicators.items():

        result = build_change_indicator(
            info["code"],
            "mom",
            -15,
            15,
            lower_is_bullish=True
        )
        output[name] = result
        weighted_scores.append(
            (
                result["score"],
                info["weight"]
            )
        )

    output["UNEMPLOYMENT_RATE"] = build_level_indicator(
        UNRATE,
        3.5,
        7,
        lower_is_bullish=True
    )
    weighted_scores.append(
        (
            output["UNEMPLOYMENT_RATE"]["score"],
            20
        )
    )

    output["LABOR_PARTICIPATION_RATE"] = build_level_indicator(
        CIVPART,
        60,
        64
    )
    weighted_scores.append(
        (
            output["LABOR_PARTICIPATION_RATE"]["score"],
            10
        )
    )

    return finalize_engine(
        weighted_scores,
        output
    )

