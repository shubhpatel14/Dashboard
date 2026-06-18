INDICATOR_RULES = {


    # =====================
    # INFLATION
    # =====================

    "CPI_MOM": {
        "lower_is_bullish": True,
        "neutral":0.2,
        "range":0.6
    },

    "CORE_CPI_MOM": {
        "lower_is_bullish": True,
        "neutral":0.2,
        "range":0.6
    },

    "CPI_YOY": {
        "lower_is_bullish": True,
        "neutral":2,
        "range":5
    },

    "CORE_CPI_YOY": {
        "lower_is_bullish": True,
        "neutral":2,
        "range":5
    },


    "PCE_MOM": {
        "lower_is_bullish": True,
        "neutral":0.2,
        "range":0.6
    },

    "CORE_PCE_MOM": {
        "lower_is_bullish": True,
        "neutral":0.2,
        "range":0.6
    },

    "PCE_YOY": {
        "lower_is_bullish": True,
        "neutral":2,
        "range":5
    },

    "CORE_PCE_YOY": {
        "lower_is_bullish": True,
        "neutral":2,
        "range":5
    },

    "PPI_MOM": {
        "lower_is_bullish": True,
        "neutral":0.2,
        "range":1
    },




    # =====================
    # LIQUIDITY
    # =====================

    "M2": {
        "lower_is_bullish": False,
        "neutral":5,
        "range":10
    },


    "WALCL": {
        "lower_is_bullish": False,
        "neutral":0,
        "range":20
    },


    "BANK_RESERVES": {
        "lower_is_bullish": False,
        "neutral":0,
        "range":20
    },


    "RRP": {
        "lower_is_bullish": True,
        "neutral":0,
        "range":50
    },




    # =====================
    # RATES
    # =====================

    "FEDFUNDS": {
        "lower_is_bullish": True,
        "neutral":3,
        "range":5
    },


    "REAL_YIELD": {
        "lower_is_bullish": True,
        "neutral":1,
        "range":3
    },


    "TEN_YEAR_YIELD": {
        "lower_is_bullish": True,
        "neutral":3.5,
        "range":4
    },


    "TWO_YEAR_YIELD": {
        "lower_is_bullish": True,
        "neutral":3.5,
        "range":4
    },


    "YIELD_CURVE": {
        "lower_is_bullish": False,
        "neutral":0,
        "range":2
    },




    # =====================
    # GROWTH
    # =====================

    "GDP_YOY": {
        "lower_is_bullish": False,
        "neutral":2,
        "range":5
    },


    "INDUSTRIAL_PRODUCTION": {
        "lower_is_bullish": False,
        "neutral":2,
        "range":10
    },


    "RETAIL_SALES": {
        "lower_is_bullish": False,
        "neutral":3,
        "range":10
    },




    # =====================
    # LABOR
    # =====================

    "UNEMPLOYMENT": {
        "lower_is_bullish": True,
        "neutral":5,
        "range":5
    },


    "PAYROLLS": {
        "lower_is_bullish": False,
        "neutral":2,
        "range":5
    },


    "JOBLESS_CLAIMS": {
        "lower_is_bullish": True,
        "neutral":250000,
        "range":300000
    },




    # =====================
    # CREDIT
    # =====================

    "HIGH_YIELD_SPREAD": {
        "lower_is_bullish": True,
        "neutral":4,
        "range":6
    },


    "FINANCIAL_CONDITIONS": {
        "lower_is_bullish": True,
        "neutral":0,
        "range":2
    },




    # =====================
    # HOUSING
    # =====================

    "HOME_PRICES": {
        "lower_is_bullish": False,
        "neutral":3,
        "range":10
    },


    "HOUSING_STARTS": {
        "lower_is_bullish": False,
        "neutral":0,
        "range":20
    },




    # =====================
    # SENTIMENT
    # =====================

    "CONSUMER_SENTIMENT": {
        "lower_is_bullish": False,
        "neutral":80,
        "range":40
    }

}