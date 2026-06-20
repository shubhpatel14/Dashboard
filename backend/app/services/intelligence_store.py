
import json


from sqlalchemy import text




from app.database.connection import SessionLocal



# ============================================
# TRISHULA INTELLIGENCE STORE
# ============================================






# ==========================================
# AUTO ENRICH MACRO INDICATORS WITH STATS
# ==========================================

def enrich_indicator_statistics(category_data):


    data = (
        category_data.get("data")
        or
        category_data.get("indicators")
        or
        {}
    )


    if isinstance(data, dict):


        for key,value in data.items():


            try:


                stats = get_indicator_statistics(
                    key,
                    value.get("current")
                )


                value["percentile"] = stats.get(
                    "percentile",
                    50
                )


                value["z_score"] = stats.get(
                    "z_score",
                    0
                )


                value["average"] = stats.get(
                    "average",
                    0
                )


                value["distance_average"] = stats.get(
                    "distance_average",
                    0
                )



            except Exception:


                value["percentile"] = 50

                value["z_score"] = 0

                value["distance_average"] = 0



    return category_data


def save_macro_category(
    category,
    result
):


    # ==================================
    # ADD HISTORICAL STATISTICS
    # ==================================

    payload = data


    indicators = (
        payload.get("data")
        or
        payload.get("indicators")
        or
        {}
    )


    if isinstance(indicators, dict):


        for name,item in indicators.items():


            try:


                stats=get_indicator_statistics(
                    name,
                    item.get("current")
                )


                item.update(stats)


            except Exception:


                pass



    db = SessionLocal()

    try:

        db.execute(
        text("""
        INSERT INTO macro_scores
        (
        category,
        score,
        bias,
        trend,
        data
        )

        VALUES
        (
        :category,
        :score,
        :bias,
        :trend,
        :data
        )

        """),

        {

        "category":
        category,


        "score":
        result.get(
        "score"
        ),


        "bias":
        result.get(
        "bias"
        ),


        "trend":
        result.get(
        "trend"
        ),


        "data":
        json.dumps(
        result
        )

        })


        db.commit()


    finally:

        db.close()





def save_macro_dashboard(data):

    db=SessionLocal()

    try:

        scores=data.get(
        "category_scores",
        {}
        )


        db.execute(

        text("""

        INSERT INTO macro_history
        (

        macro_score,

        regime,

        liquidity_score,

        inflation_score,

        growth_score,

        rates_score,

        labor_score,

        credit_score,

        sentiment_score,

        data

        )

        VALUES

        (

        :macro_score,

        :regime,

        :liquidity,

        :inflation,

        :growth,

        :rates,

        :labor,

        :credit,

        :sentiment,

        :data

        )

        """),


        {


        "macro_score":
        data.get(
        "macro_score"
        ),


        "regime":
        str(
        data.get(
        "regime"
        )),


        "liquidity":
        scores.get(
        "liquidity"
        ),


        "inflation":
        scores.get(
        "inflation"
        ),


        "growth":
        scores.get(
        "growth"
        ),


        "rates":
        scores.get(
        "rates"
        ),


        "labor":
        scores.get(
        "labor"
        ),


        "credit":
        scores.get(
        "credit"
        ),


        "sentiment":
        scores.get(
        "sentiment"
        ),


        "data":
        json.dumps(enrich_indicator_statistics(data))

        })


        db.commit()


    finally:

        db.close()





def save_asset(
    asset,
    result
):

    db=SessionLocal()

    try:

        db.execute(

        text("""

        INSERT INTO asset_scores
        (
        asset,
        score,
        outlook,
        bullish_drivers,
        bearish_drivers,
        data
        )

        VALUES
        (
        :asset,
        :score,
        :outlook,
        :bull,
        :bear,
        :data
        )

        """),


        {

        "asset":asset,


        "score":
        result.get(
        "asset_score"
        ),


        "outlook":
        result.get(
        "outlook"
        ),


        "bull":
        json.dumps(
        result.get(
        "bullish_drivers",
        []
        )),


        "bear":
        json.dumps(
        result.get(
        "bearish_drivers",
        []
        )),


        "data":
        json.dumps(result)

        })


        db.commit()


    finally:

        db.close()


