
import json

from sqlalchemy import text

from app.database.connection import SessionLocal



# ===========================================
# TRISHULA INTELLIGENCE READER
# Database ? API
# ===========================================



def _parse(value):

    if value is None:
        return None


    if isinstance(value, dict):
        return value


    return json.loads(value)





def get_latest_macro():

    db = SessionLocal()


    try:

        result = db.execute(

            text("""

            SELECT data

            FROM macro_history

            ORDER BY created_at DESC

            LIMIT 1

            """)

        ).scalar()


        return _parse(
            result
        )


    finally:

        db.close()



def get_latest_category(category):

    db = SessionLocal()


    try:


        result=db.execute(

            text("""

            SELECT data

            FROM macro_scores

            WHERE category=:category

            ORDER BY created_at DESC

            LIMIT 1

            """),

            {
            "category":category
            }

        ).scalar()



        return _parse(result)



    finally:

        db.close()






def get_latest_asset(asset):

    db=SessionLocal()


    try:


        result=db.execute(

            text("""

            SELECT data

            FROM asset_scores

            WHERE asset=:asset

            ORDER BY created_at DESC

            LIMIT 1

            """),

            {
            "asset":asset
            }

        ).scalar()



        return _parse(result)



    finally:

        db.close()






def get_asset_history(asset):


    db=SessionLocal()


    try:


        rows=db.execute(

            text("""

            SELECT

            created_at,

            score

            FROM asset_scores

            WHERE asset=:asset

            ORDER BY created_at

            """),

            {
            "asset":asset
            }

        ).all()



        return [

        {

        "date":
        str(r[0]),


        "score":
        r[1]

        }

        for r in rows

        ]



    finally:

        db.close()

def get_all_assets():


    db = SessionLocal()


    try:


        rows = db.execute(

            text("""

            SELECT DISTINCT ON (asset)

                asset,
                data

            FROM asset_scores

            ORDER BY asset, created_at DESC

            """)

        ).all()



        result = {}



        for asset, data in rows:


            # convert JSONB/text into python dict

            parsed = _parse(
                data
            )


            result[
                asset.capitalize()
            ] = {


                "asset":

                    parsed.get(
                        "asset",
                        asset.capitalize()
                    ),



                "asset_score":

                    parsed.get(
                        "asset_score",
                        parsed.get(
                            "score",
                            50
                        )
                    ),



                "score":

                    parsed.get(
                        "score",
                        parsed.get(
                            "asset_score",
                            50
                        )
                    ),



                "outlook":

                    parsed.get(
                        "outlook",
                        "Neutral"
                    ),



                "bias":

                    parsed.get(
                        "outlook",
                        "Neutral"
                    ),



                "trend":

                    parsed.get(
                        "trend",
                        "Neutral"
                    ),



                "drivers":

                    parsed.get(
                        "drivers",
                        {}
                    ),



                "bullish_drivers":

                    parsed.get(
                        "bullish_drivers",
                        []
                    ),



                "bearish_drivers":

                    parsed.get(
                        "bearish_drivers",
                        []
                    ),



                "components":

                    parsed.get(
                        "components",
                        []
                    )

            }



        return result



    finally:


        db.close()


def get_macro_history(category):


    db = SessionLocal()


    try:


        rows = db.execute(

            text("""

            SELECT
                created_at,
                score

            FROM macro_scores

            WHERE LOWER(category)=LOWER(:category)

            ORDER BY created_at

            """),

            {
                "category":category
            }

        ).all()



        return [

            {

                "date":str(row[0]),

                "score":row[1]

            }

            for row in rows

        ]



    finally:

        db.close()

