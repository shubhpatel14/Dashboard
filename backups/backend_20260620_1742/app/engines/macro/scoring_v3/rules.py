INDICATOR_RULES = {


    # =====================
    # INFLATION
    # =====================

    "CPI_MOM": {
        "type": "lower_better",
        "target": 0.2,
        "danger": 0.8
    },

    "CORE_CPI_MOM": {
        "type": "lower_better",
        "target": 0.2,
        "danger": 0.8
    },


    "CPI_YOY": {
        "type": "lower_better",
        "target": 2,
        "danger": 6
    },


    "CORE_CPI_YOY": {
        "type": "lower_better",
        "target": 2,
        "danger": 6
    },


    "PCE_YOY": {
        "type": "lower_better",
        "target": 2,
        "danger": 5
    },


    "CORE_PCE_YOY": {
        "type": "lower_better",
        "target": 2,
        "danger": 5
    },



    # =====================
    # LIQUIDITY
    # =====================


    "M2": {
        "type": "higher_better",
        "target": 6,
        "danger": -5
    },


    "WALCL": {
        "type": "higher_better",
        "target": 5,
        "danger": -10
    },


    "BANK_RESERVES": {
        "type": "higher_better",
        "target": 10,
        "danger": -20
    },


    "RRP": {
        "type": "lower_better",
        "target": -50,
        "danger": 50
    },



    # =====================
    # GROWTH
    # =====================


    "GDP_YOY": {
        "type": "higher_better",
        "target": 3,
        "danger": 0
    },


    "GDP_QOQ_ANNUALIZED": {
        "type": "higher_better",
        "target": 3,
        "danger": 0
    },



    # =====================
    # RATES
    # =====================


    "FEDFUNDS": {
        "type": "lower_better",
        "target": 2,
        "danger": 6
    },


    "REAL_YIELD": {
        "type": "lower_better",
        "target": 1,
        "danger": 3
    },


}