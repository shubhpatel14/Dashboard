from app.data.history.fred_history import (
    fetch_fred_history
)

from app.database.repository import (
    save_macro_history
)

from app.data.history.transforms import (
    percent_change,
    difference
)



SERIES = {


    # =================================
    # INFLATION
    # =================================

    "CPI_MOM": ("CPIAUCSL", 1),

    "CORE_CPI_MOM": ("CPILFESL", 1),

    "CPI_YOY": ("CPIAUCSL", 12),

    "CORE_CPI_YOY": ("CPILFESL", 12),


    "PCE_MOM": ("PCEPI", 1),

    "CORE_PCE_MOM": ("PCEPILFE", 1),

    "PCE_YOY": ("PCEPI", 12),

    "CORE_PCE_YOY": ("PCEPILFE", 12),


    "PPI_MOM": ("PPIACO", 1),

    "CORE_PPI_MOM": ("WPSFD4131", 1),




    # =================================
    # LIQUIDITY
    # =================================

    "M2": ("M2SL", 12),

    "WALCL": ("WALCL", 52),

    "BANK_RESERVES": ("WRESBAL", 52),

    "RRP": ("RRPONTSYD", 252),




    # =================================
    # RATES
    # =================================

    "FEDFUNDS": ("FEDFUNDS", None),

    "REAL_YIELD": ("DFII10", None),

    "TEN_YEAR_YIELD": ("DGS10", None),

    "TWO_YEAR_YIELD": ("DGS2", None),

    "YIELD_CURVE": ("T10Y2Y", None),

    "MORTGAGE_RATE": ("MORTGAGE30US", None),




    # =================================
    # GROWTH
    # =================================

    "GDP_YOY": ("GDP", 4),

    "INDUSTRIAL_PRODUCTION": ("INDPRO", 12),

    "RETAIL_SALES": ("RSAFS", 12),

    "PMI": ("NAPM", None),

        # =================================
    # GROWTH
    # =================================

    "GDP_YOY": ("GDP", 4),

    "INDUSTRIAL_PRODUCTION": ("INDPRO", 12),

    "RETAIL_SALES": ("RSAFS", 12),

    "PMI": ("NAPM", None),


    "DURABLE_GOODS": (
        "DGORDER",
        12
    ),


    "FACTORY_ORDERS": (
        "AMTMNO",
        12
    ),




    # =================================
    # LABOR
    # =================================

    "UNEMPLOYMENT": ("UNRATE", None),

    "PAYROLLS": ("PAYEMS", "diff"),

    "JOBLESS_CLAIMS": ("ICSA", 52),

    "WAGES": ("CES0500000003", 12),

        "LABOR_PARTICIPATION":
        (
            "CIVPART",
            None
        ),


    "CONTINUING_CLAIMS":
        (
            "CCSA",
            52
        ),




    # =================================
    # CREDIT
    # =================================

    "HIGH_YIELD_SPREAD": ("BAMLH0A0HYM2", None),

    "INVESTMENT_GRADE_SPREAD": ("BAMLC0A0CM", None),

    "FINANCIAL_CONDITIONS": ("NFCI", None),

    "TED_SPREAD":
        (
            "TEDRATE",
            None
        ),   




    # =================================
    # HOUSING
    # =================================

    "HOME_PRICES": ("CSUSHPISA", 12),

    "HOUSING_STARTS": ("HOUST", 12),

    "BUILDING_PERMITS": ("PERMIT", 12),

    "NEW_HOME_SALES":
        (
            "HSN1F",
            12
        ),


    "EXISTING_HOME_SALES": (
    "EXHOSLUSM495N",
    None
),




    # =================================
    # SENTIMENT
    # =================================

    "CONSUMER_SENTIMENT": ("UMCSENT", None),



    # =================================
    # RECESSION
    # =================================

    "SAHM_RULE": ("SAHMCURRENT", None),

    "VIX":
        (
            "VIXCLS",
            None
        ),

        # =================================
    # MARKET
    # =================================


    "DXY":
        (
            "DTWEXBGS",
            None
        ),


    "SP500":
        (
            "SP500",
            None
        ),

}



for name, item in SERIES.items():


    code, transform = item


    print(
        "Loading",
        name
    )


    rows = fetch_fred_history(
        code
    )


    if transform == "diff":

        rows = difference(
            rows,
            1
        )


    elif transform:

        rows = percent_change(
            rows,
            transform
        )




    save_macro_history(
        name,
        rows
    )



print(
    "ALL MACRO HISTORY IMPORTED"
)