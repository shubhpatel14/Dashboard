from fastapi import APIRouter, HTTPException

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

        "asset_score": score,

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