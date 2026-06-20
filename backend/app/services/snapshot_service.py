
import json

from sqlalchemy import text

from app.database.connection import SessionLocal



# ==================================
# TRISHULA SNAPSHOT SERVICE
# ==================================



def save_macro_snapshot(data):

    db = SessionLocal()


    try:


        db.execute(

        text("""

        INSERT INTO macro_snapshots
        (
        macro_score,
        regime,
        data
        )

        VALUES

        (
        :score,
        :regime,
        :data
        )

        """),

        {

        "score":
        data.get(
            "macro_score"
        ),


        "regime":
        str(
        data.get(
            "regime"
        )),


        "data":
        json.dumps(
            data
        )

        }

        )


        db.commit()


    finally:

        db.close()





def get_latest_macro_snapshot():


    db = SessionLocal()


    try:


        result = db.execute(

        text("""

        SELECT data

        FROM macro_snapshots

        ORDER BY created_at DESC

        LIMIT 1

        """)

        ).scalar()



        if result:

            return result


        return None



    finally:

        db.close()



def save_asset_snapshot(
    asset,
    data
):

    db = SessionLocal()


    try:


        db.execute(

        text("""

        INSERT INTO asset_snapshots
        (
        asset,
        score,
        outlook,
        data
        )

        VALUES

        (
        :asset,
        :score,
        :outlook,
        :data
        )

        """),

        {


        "asset":
        asset,


        "score":
        data.get(
        "score"
        ),


        "outlook":
        data.get(
        "outlook"
        ),


        "data":
        json.dumps(data)


        }

        )


        db.commit()



    finally:

        db.close()

