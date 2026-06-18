import numpy as np


from app.database.connection import (
    SessionLocal
)


from app.database.models import (
    MacroSeries
)

SERIES_ALIASES = {


    # ==================
    # RATES
    # ==================

    "FED_FUNDS_RATE_LEVEL":
        "FEDFUNDS",

    "TEN_YEAR_YIELD_LEVEL":
        "TEN_YEAR_YIELD",

    "TWO_YEAR_YIELD_LEVEL":
        "TWO_YEAR_YIELD",

    "TEN_YEAR_REAL_YIELD_LEVEL":
        "REAL_YIELD",

    "YIELD_CURVE_10Y_2Y":
        "YIELD_CURVE",




    # ==================
    # GROWTH
    # ==================

    "GDP_QOQ_ANNUALIZED":
        "GDP_YOY",

    "RETAIL_SALES_MOM":
        "RETAIL_SALES",

    "INDUSTRIAL_PRODUCTION_MOM":
        "INDUSTRIAL_PRODUCTION",

    
    "DURABLE_GOODS_ORDERS_MOM":
        "DURABLE_GOODS",


    "FACTORY_ORDERS_MOM":
        "FACTORY_ORDERS",


    # ==================
    # LABOR
    # ==================

    "NON_FARM_PAYROLL_CHANGE":
        "PAYROLLS",

    "INITIAL_CLAIMS_WEEKLY_CHANGE":
        "JOBLESS_CLAIMS",

    "CONTINUING_CLAIMS_WEEKLY_CHANGE":
        "JOBLESS_CLAIMS",

    "UNEMPLOYMENT_RATE":
        "UNEMPLOYMENT",




    # ==================
    # CREDIT
    # ==================

    "HY_SPREAD_LEVEL":
        "HIGH_YIELD_SPREAD",

    "IG_SPREAD_LEVEL":
        "INVESTMENT_GRADE_SPREAD",




    # ==================
    # HOUSING
    # ==================

    "HOUSING_STARTS_MOM":
        "HOUSING_STARTS",

    "BUILDING_PERMITS_MOM":
        "BUILDING_PERMITS",

    "CASE_SHILLER_YOY":
        "HOME_PRICES",

    "MORTGAGE_RATE_LEVEL":
        "MORTGAGE_RATE",




    # ==================
    # SENTIMENT
    # ==================

    "CONSUMER_SENTIMENT_LEVEL":
        "CONSUMER_SENTIMENT",

    "FINANCIAL_CONDITIONS_INDEX_LEVEL":
        "FINANCIAL_CONDITIONS",


        # ==================
    # GROWTH EXTRA
    # ==================

    "DURABLE_GOODS_ORDERS_MOM":
        "DURABLE_GOODS",

    "FACTORY_ORDERS_MOM":
        "FACTORY_ORDERS",



    # ==================
    # LABOR EXTRA
    # ==================

    "LABOR_PARTICIPATION_RATE":
        "LABOR_PARTICIPATION",

    "CONTINUING_CLAIMS_WEEKLY_CHANGE":
        "CONTINUING_CLAIMS",



    # ==================
    # CREDIT EXTRA
    # ==================

    "TED_SPREAD_LEVEL":
        "TED_SPREAD",



    # ==================
    # HOUSING EXTRA
    # ==================

    "NEW_HOME_SALES_MOM":
        "NEW_HOME_SALES",

    "EXISTING_HOME_SALES_MOM":
        "EXISTING_HOME_SALES",



    # ==================
    # SENTIMENT EXTRA
    # ==================

    "VIX_LEVEL":
        "VIX",

}


def macro_statistics(
    indicator,
    current
):


    original_indicator = indicator


    indicator = SERIES_ALIASES.get(
        indicator,
        indicator
    )


    if original_indicator == "NON_FARM_PAYROLL_CHANGE":
        current = current / 1000

    db = SessionLocal()


    try:


        rows = (
            db.query(
                MacroSeries.value
            )
            .filter(
                MacroSeries.indicator
                ==
                indicator
            )
            .all()
        )



        values = [
            r[0]
            for r in rows
            if r[0] is not None
        ]



        if len(values) < 10:

            return {

                "percentile":50,

                "z_score":0,

                "average":current,

                "distance_avg":0,

                "samples":len(values)

            }



        arr = np.array(
            values
        )



        average = float(
            np.mean(arr)
        )



        std = float(
            np.std(arr)
        )



        percentile = (

            np.sum(
                arr <= current
            )

            /

            len(arr)

            *

            100

        )



        z = (

            (current-average)

            /

            std

            if std != 0

            else 0

        )



        return {

            "percentile":
                round(
                    percentile,
                    2
                ),


            "z_score":
                round(
                    z,
                    2
                ),


            "average":
                round(
                    average,
                    2
                ),


            "distance_avg":
                round(
                    current-average,
                    2
                ),


            "samples":
                len(values)

        }



    finally:

        db.close()
