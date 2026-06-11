from data.fred_client import (
    get_current_value,
    get_current_date,
    get_previous_value,
    get_series,
    get_12m_value
)

from engines.helpers import (
    build_change_indicator,
    finalize_engine,
    score_change
)

from models.scoring import (
    indicator_result,
    pct_change
)


GDP = "GDPC1"
INDPRO = "INDPRO"
RETAIL = "RSAFS"
DURABLE_GOODS = "DGORDER"
FACTORY_ORDERS = "AMTMNO"


def build_gdp_qoq_indicator():

    series = get_series(GDP)
    current = pct_change(get_current_value(series), get_previous_value(series)) * 4
    previous = pct_change(get_previous_value(series), series[2]["value"]) * 4
    change = pct_change(current, previous) if previous != 0 else current - previous
    score = score_change(
        current,
        -2,
        6
    )

    return indicator_result(
        current,
        previous,
        change,
        score,
        last_update=get_current_date(series).date().isoformat()
    )


def build_gdp_yoy_indicator():

    series = get_series(GDP)
    current = pct_change(get_current_value(series), get_12m_value(series))
    previous = pct_change(get_previous_value(series), series[13]["value"])
    change = pct_change(current, previous) if previous != 0 else current - previous
    score = score_change(
        current,
        -2,
        5
    )

    return indicator_result(
        current,
        previous,
        change,
        score,
        last_update=get_current_date(series).date().isoformat()
    )


def build_growth_engine():

    output = {}
    weighted_scores = []

    output["GDP_QOQ_ANNUALIZED"] = build_gdp_qoq_indicator()
    weighted_scores.append(
        (
            output["GDP_QOQ_ANNUALIZED"]["score"],
            30
        )
    )

    output["GDP_YOY"] = build_gdp_yoy_indicator()
    weighted_scores.append(
        (
            output["GDP_YOY"]["score"],
            10
        )
    )

    indicators = {
        "RETAIL_SALES_MOM": {
            "code": RETAIL,
            "weight": 20
        },
        "INDUSTRIAL_PRODUCTION_MOM": {
            "code": INDPRO,
            "weight": 15
        },
        "DURABLE_GOODS_ORDERS_MOM": {
            "code": DURABLE_GOODS,
            "weight": 15
        },
        "FACTORY_ORDERS_MOM": {
            "code": FACTORY_ORDERS,
            "weight": 10
        }
    }

    for name, info in indicators.items():

        try:
            result = build_change_indicator(
                info["code"],
                "mom",
                -3,
                3
            )

            output[name] = result
            weighted_scores.append(
                (
                    result["score"],
                    info["weight"]
                )
            )

        except Exception as e:
            output[name] = {
                "error": str(e)
            }

    return finalize_engine(
        weighted_scores,
        output
    )
