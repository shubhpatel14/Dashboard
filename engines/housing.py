from engines.helpers import (
    build_change_indicator,
    build_level_indicator,
    finalize_engine
)


HOUSING_STARTS = "HOUST"
BUILDING_PERMITS = "PERMIT"
CASE_SHILLER = "CSUSHPISA"
MORTGAGE_RATE = "MORTGAGE30US"
NEW_HOME_SALES = "HSN1F"
EXISTING_HOME_SALES = "EXHOSLUSM495S"


def build_housing_engine():

    indicators = {
        "HOUSING_STARTS_MOM": {
            "code": HOUSING_STARTS,
            "weight": 25
        },
        "BUILDING_PERMITS_MOM": {
            "code": BUILDING_PERMITS,
            "weight": 25
        },
        "NEW_HOME_SALES_MOM": {
            "code": NEW_HOME_SALES,
            "weight": 15
        },
        "EXISTING_HOME_SALES_MOM": {
            "code": EXISTING_HOME_SALES,
            "weight": 15
        },
        "CASE_SHILLER_YOY": {
            "code": CASE_SHILLER,
            "weight": 10
        }
    }

    output = {}
    weighted_scores = []

    for name, info in indicators.items():

        try:
            period = "yoy" if name.endswith("_YOY") else "mom"
            result = build_change_indicator(
                info["code"],
                period,
                -10,
                10
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

    output["MORTGAGE_RATE_LEVEL"] = build_level_indicator(
        MORTGAGE_RATE,
        3,
        8,
        lower_is_bullish=True
    )
    weighted_scores.append(
        (
            output["MORTGAGE_RATE_LEVEL"]["score"],
            10
        )
    )

    return finalize_engine(
        weighted_scores,
        output
    )
