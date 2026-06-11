from engines.helpers import (
    build_change_indicator,
    finalize_engine
)


CPI = "CPIAUCSL"
CORE_CPI = "CPILFESL"
PCE = "PCEPI"
CORE_PCE = "PCEPILFE"
PPI = "PPIACO"
CORE_PPI = "PPIFES"


def build_inflation_engine():

    indicators = {
        "CORE_CPI_MOM": {
            "code": CORE_CPI,
            "period": "mom",
            "weight": 25
        },
        "CPI_MOM": {
            "code": CPI,
            "period": "mom",
            "weight": 20
        },
        "CORE_PCE_MOM": {
            "code": CORE_PCE,
            "period": "mom",
            "weight": 20
        },
        "PCE_MOM": {
            "code": PCE,
            "period": "mom",
            "weight": 10
        },
        "PPI_MOM": {
            "code": PPI,
            "period": "mom",
            "weight": 5
        },
        "CORE_PPI_MOM": {
            "code": CORE_PPI,
            "period": "mom",
            "weight": 5
        },
        "CPI_YOY": {
            "code": CPI,
            "period": "yoy",
            "weight": 10
        },
        "CORE_CPI_YOY": {
            "code": CORE_CPI,
            "period": "yoy",
            "weight": 10
        },
        "PCE_YOY": {
            "code": PCE,
            "period": "yoy",
            "weight": 5
        },
        "CORE_PCE_YOY": {
            "code": CORE_PCE,
            "period": "yoy",
            "weight": 5
        }
    }

    output = {}
    weighted_scores = []

    for name, info in indicators.items():

        try:
            result = build_change_indicator(
                info["code"],
                info["period"],
                -1 if info["period"] == "mom" else 0,
                1 if info["period"] == "mom" else 8,
                lower_is_bullish=True
            )

            output[name] = result

            if info["weight"] > 0:
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
