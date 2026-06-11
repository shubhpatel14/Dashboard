from fastapi import APIRouter, HTTPException

from app.core.cache import cached
from app.services.engine_registry import get_institutional_engine
from app.services.transformers import DISPLAY_NAMES

router = APIRouter(prefix="/institutional", tags=["institutional"])


@router.get("/{asset}")
@cached("institutional")
def institutional(asset: str):
    slug = asset.lower()
    if slug not in DISPLAY_NAMES:
        raise HTTPException(status_code=404, detail="Asset not found")

    name = DISPLAY_NAMES[slug]
    data = get_institutional_engine()["assets"][name]

    return {
        "asset": name,
        "long_percentage": data["long_percent"],
        "short_percentage": data["short_percent"],
        "net_position": data["net_position"],
        "weekly_change": data["weekly_change"],
        "four_week_velocity": data["velocity_4w"],
        "bias": data["bias"],
        "score": data["score"],
        "position_percentile": data["position_percentile"],
        "history": data["trend"],
    }

