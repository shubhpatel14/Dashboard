from fastapi import APIRouter, HTTPException
from app.engines.assets.final_score import (
    blend_macro_score,
)

from app.engines.assets.macro_impact import (
    macro_asset_impact,
)

from app.engines.macro.macro_surprise.scoring import (
    build_macro_surprise,
)

from app.services.engine_registry import (
    get_macro_engine,
)

from app.core.cache import cached

from app.services.engine_registry import (
    ASSET_BUILDERS,
    get_asset_engine,
)

from app.services.transformers import (
    DISPLAY_NAMES,
    asset_history,
    asset_summary,
    drivers_from_asset,
)

from app.services.intelligence_reader import (
    get_latest_asset
)


router = APIRouter(
    prefix="/assets",
    tags=["Assets"]
)


@router.get("/{asset}")
@cached("asset")
def asset(asset: str):


    slug = asset.lower()

        # =============================
    # DATABASE FAST PATH
    # =============================

    stored = get_latest_asset(
        slug
    )


    if stored:


        return {


            "asset":

                stored.get(
                    "asset",
                    asset
                ),


            "asset_score":

                stored.get(
                    "score",
                    50
                ),


            "score":

                stored.get(
                    "score",
                    50
                ),


            "outlook":

                stored.get(
                    "outlook",
                    "Neutral"
                ),


            "bias":

                stored.get(
                    "bias",
                    "Neutral"
                ),


            "trend":

                stored.get(
                    "trend",
                    "Neutral"
                ),


            "drivers":

                stored.get(
                    "drivers",
                    {}
                ),


            "bullish_drivers":

                stored.get(
                    "bullish_drivers",
                    []
                ),


            "bearish_drivers":

                stored.get(
                    "bearish_drivers",
                    []
                ),


            "components":

                stored.get(
                    "components",
                    []
                ),


            "radar":

                stored.get(
                    "radar",
                    []
                ),


            "history":

                stored.get(
                    "history",
                    []
                ),


            "explanation":

                stored.get(
                    "explanation",
                    ""

                )

        }


    if slug not in ASSET_BUILDERS:

        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )



    # ===================================
    # FAST PATH
    # DATABASE FIRST
    # ===================================

    stored = get_latest_asset(
        slug
    )


    if stored:


        return stored




    # ===================================
    # FALLBACK
    # ENGINE CALCULATION
    # ===================================


    engine = get_asset_engine(
        slug
    )


    macro = get_macro_engine()


    surprise = build_macro_surprise()



    macro_assets = macro_asset_impact(
        surprise,
        macro
    )


    asset_key = DISPLAY_NAMES.get(
        slug,
        slug.upper()
    )


    if asset_key in macro_assets:


        engine = blend_macro_score(
            engine,
            macro_assets[asset_key],
            0.30
        )



    score = engine.get(
        "score",
        50
    )



    drivers = drivers_from_asset(
        engine
    )



    name = DISPLAY_NAMES.get(
        slug,
        slug.upper()
    )



    return {

    "asset": name,


    "asset_score":
        engine.get(
            "score",
            50
        ),


    "score":
        engine.get(
            "score",
            50
        ),


    "raw_score":
        engine.get(
            "raw_score"
        ),


    "macro_score":
        engine.get(
            "macro_score"
        ),


    "bias":
        engine.get(
            "bias",
            "Neutral"
        ),


    "trend":
        engine.get(
            "trend",
            "Neutral"
        ),


    "outlook":
        engine.get(
            "outlook",
            "Neutral"
        ),


    "drivers":
        drivers,


    "bullish_drivers":
        engine.get(
            "bullish_drivers",
            []
        ),


    "bearish_drivers":
        engine.get(
            "bearish_drivers",
            []
        ),


    "components":
        engine.get(
            "components",
            []
        ),


    "summary":
        asset_summary(
            name,
            score,
            drivers
        ),


    "history":
        asset_history(
            slug,
            score
        ),

}