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


router = APIRouter(
    prefix="/assets",
    tags=["Assets"]
)


@router.get("/{asset}")
@cached("asset")
def asset(asset: str):

    slug = asset.lower()

    if slug not in ASSET_BUILDERS:
        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )

    engine = get_asset_engine(slug)

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

        "asset_score": engine.get(
            "score",
            50
        ),


        "raw_score": engine.get(
            "raw_score"
        ),


        "macro_score": engine.get(
            "macro_score"
        ),


        "macro_drivers": engine.get(
            "macro_drivers",
            []
        ),

        "outlook": engine.get(
            "outlook",
            "Neutral"
        ),

        "drivers": drivers,

        "summary": asset_summary(
            name,
            score,
            drivers
        ),

        "history": asset_history(
            slug,
            score
        ),

    }