from app.database.connection import SessionLocal
from app.database.models import MacroSeries



def save_macro_history(
    indicator,
    rows,
    source="FRED"
):

    db = SessionLocal()


    try:

        for row in rows:


            exists = (
                db.query(MacroSeries)
                .filter(
                    MacroSeries.indicator == indicator,
                    MacroSeries.date == row["date"]
                )
                .first()
            )


            if exists:

                continue


            db.add(

                MacroSeries(

                    indicator=indicator,
                    date=row["date"],
                    value=row["value"],
                    source=source

                )

            )


        db.commit()


    finally:

        db.close()
