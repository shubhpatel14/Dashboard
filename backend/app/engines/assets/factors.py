def clamp(
    value,
    low=0,
    high=100
):

    return max(
        low,
        min(
            high,
            value
        )
    )




def weighted_score(
    factors
):

    score = 0


    for item in factors.values():

        score += (
            item["score"]
            *
            item["weight"]
        )


    return round(
        clamp(score),
        2
    )




def build_asset_factors(
    asset,
    macro
):


    asset = asset.lower()



    # =========================
    # SP500
    # =========================

    if asset == "sp500":

        return {

            "earnings_growth":{

                "score": macro["growth"],

                "weight":0.30

            },


            "liquidity":{

                "score": macro["liquidity"],

                "weight":0.25

            },


            "valuation":{

                "score":45,

                "weight":0.20

            },


            "credit_conditions":{

                "score":macro["credit"],

                "weight":0.15

            },


            "momentum":{

                "score":55,

                "weight":0.10

            }

        }





    # =========================
    # NASDAQ
    # =========================

    if asset == "nasdaq":

        return {


            "liquidity":{

                "score":macro["liquidity"],

                "weight":0.35

            },


            "real_rates":{

                "score":100-macro["rates"],

                "weight":0.25

            },


            "growth":{

                "score":macro["growth"],

                "weight":0.20

            },


            "valuation":{

                "score":40,

                "weight":0.10

            },


            "momentum":{

                "score":60,

                "weight":0.10

            }

        }







    # =========================
    # GOLD
    # =========================

    if asset == "gold":

        return {


            "real_yield_support":{

                "score":100-macro["rates"],

                "weight":0.35

            },


            "dollar_weakness":{

                "score":50,

                "weight":0.25

            },


            "inflation_hedge":{

                "score":macro["inflation"],

                "weight":0.20

            },


            "safe_haven":{

                "score":100-macro["credit"],

                "weight":0.15

            },


            "liquidity":{

                "score":macro["liquidity"],

                "weight":0.05

            }

        }






    # =========================
    # BITCOIN
    # =========================

    if asset == "bitcoin":

        return {


            "global_liquidity":{

                "score":macro["liquidity"],

                "weight":0.40

            },


            "real_rates":{

                "score":100-macro["rates"],

                "weight":0.25

            },


            "risk_appetite":{

                "score":macro["growth"],

                "weight":0.20

            },


            "momentum":{

                "score":55,

                "weight":0.15

            }

        }







    # =========================
    # BONDS
    # =========================

    if asset == "bonds":

        return {


            "inflation_cooling":{

                "score":100-macro["inflation"],

                "weight":0.30

            },


            "growth_slowdown":{

                "score":100-macro["growth"],

                "weight":0.25

            },


            "fed_policy":{

                "score":100-macro["rates"],

                "weight":0.25

            },


            "safe_haven":{

                "score":100-macro["credit"],

                "weight":0.20

            }

        }







    # =========================
    # DOLLAR
    # =========================

    if asset == "dollar":

        return {


            "rate_advantage":{

                "score":macro["rates"],

                "weight":0.35

            },


            "safe_haven":{

                "score":100-macro["credit"],

                "weight":0.30

            },


            "liquidity_tightness":{

                "score":100-macro["liquidity"],

                "weight":0.20

            },


            "growth_divergence":{

                "score":50,

                "weight":0.15

            }

        }



    return {}