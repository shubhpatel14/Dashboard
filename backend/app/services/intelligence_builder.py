from __future__ import annotations

import json

from sqlalchemy import text

from app.database.connection import SessionLocal


from app.services.engine_registry import (
    MACRO_BUILDERS,
    ASSET_BUILDERS,
)

from app.engines.macro.category_final_score import (
    build_category_final_score,
)

from app.engines.macro.macro_surprise.scoring import (
    build_macro_surprise,
)

from app.services.intelligence_store import (
    save_macro_category,
    save_asset,
)


# ==========================================
# SAVE HELPERS
# ==========================================

def save_macro_category(
    category,
    data
):

    db = SessionLocal()

    try:

        db.execute(

            text("""

            INSERT INTO macro_scores
            (
                category,
                score,
                bias,
                data
            )

            VALUES
            (
                :category,
                :score,
                :bias,
                :data
            )

            """),

            {

                "category": category,

                "score":
                    data.get(
                        "score",
                        50
                    ),

                "bias":
                    data.get(
                        "bias",
                        "Neutral"
                    ),

                "data":
                    json.dumps(
                        data
                    )

            }

        )


        db.commit()


    finally:

        db.close()



def save_asset(
    asset,
    data
):

    db = SessionLocal()


    try:

        db.execute(

            text("""

            INSERT INTO asset_scores
            (
                asset,
                score,
                data
            )

            VALUES
            (
                :asset,
                :score,
                :data
            )

            """),

            {

                "asset":asset,


                "score":

                    data.get(
                        "score",
                        data.get(
                            "asset_score",
                            50
                        )
                    ),


                "data":

                    json.dumps(
                        data
                    )

            }

        )


        db.commit()


    finally:

        db.close()



# ==========================================
# MAIN REBUILD
# ==========================================

def rebuild_intelligence():


    print(
        "Building Trishula Intelligence..."
    )


    # -------------------------------
    # MACRO CATEGORIES
    # -------------------------------

    surprise = build_macro_surprise()

    for slug,builder in MACRO_BUILDERS.items():


        if slug in [
            "macro_surprise"
        ]:

            continue


        try:


            print(
                "Saving macro:",
                slug
            )


            result = builder()

            result = build_category_final_score(
                slug,
                result,
                surprise
            )


            save_macro_category(
                slug,
                result
            )


        except Exception as e:


            print(
                "FAILED MACRO",
                slug,
                e
            )




    # -------------------------------
    # ASSETS
    # -------------------------------


    for slug,builder in ASSET_BUILDERS.items():


        try:


            print(
                "Saving asset:",
                slug
            )


            result = builder()


            save_asset(
                slug,
                result
            )



        except Exception as e:


            print(
                "FAILED ASSET",
                slug,
                e
            )




    return {

        "status":"success"

    }
