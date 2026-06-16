from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from app.engines.macro.category_final_score import (
    build_category_final_score,
)
from app.core.cache import cached, clear_cache

from app.services.engine_registry import (
    MACRO_BUILDERS,
    get_macro_category,
    get_macro_engine,
    get_trend_engine,
    macro_regime,
    refresh_engine_cache,
)

from app.services.transformers import (
    MACRO_LABELS,
    clean_label,
    indicators_from_engine,
    macro_category_intelligence,
    macro_category_history,
    macro_summary,
)

from app.engines.macro.macro_surprise.scoring import (
    build_macro_surprise,
)

from app.engines.assets.macro_impact import (
    macro_asset_impact,
)

from app.engines.assets.allocation import (
    build_allocation,
)

from app.engines.macro.regime.engine import (
    build_macro_regime,
)

from app.engines.macro.final_score import (
    build_final_macro_score,
)

from app.engines.macro.regime.history import (
    update_regime_history,
)


router = APIRouter(prefix="/macro", tags=["macro"])

logger = logging.getLogger(__name__)


# ================================
# MODELS
# ================================

class MacroDashboardResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    success: bool = True
    data_status: str = "connected"

    macro_score: float = 50
    regime: str = "Neutral"
    regime_detail: dict[str, Any] = {}
    regime_history: dict[str, Any] = {}
    trend: str = "Neutral"

    recession_risk: str = "N/A"
    risk_status: str = "Neutral"

    summary: list[str] = []

    asset_outlooks: dict[str, Any] = {}

    portfolio_allocation: dict[str, Any] = {}

    macro_surprises: list[dict[str, Any]] = []

    category_scores: dict[str, Any] = {}

    history: list[dict[str, Any]] = []


class MacroCategoryResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    success: bool = True
    data_status: str = "connected"

    name: str = "Macro"

    score: float = 50
    bias: str = "Neutral"

    core_score: Optional[float] = None

    surprise_score: Optional[float] = None

    surprise_events: list[Any] = []

    trend: str = "Stable"

    summary: str = ""

    drivers: list[dict[str, Any]] = []

    indicators: list[dict[str, Any]] = []

    explanation: str = ""

    history: list[dict[str, Any]] = []

    data: list[dict[str, Any]] = []



# ================================
# HELPERS
# ================================

def _safe_score(value, default=50):

    try:
        return float(value)

    except Exception:
        return default



def _empty_category(slug, message=""):

    name = MACRO_LABELS.get(
        slug,
        clean_label(slug).title()
    )


    return {

        "success": True,

        "data_status": "fallback",

        "name": name,

        "score": 50,

        "bias": "Neutral",

        "trend": "Stable",

        "summary": message,

        "drivers": [],

        "indicators": [],

        "explanation": message,

        "history":[
            {
                "date":"Current",
                "score":50
            }
        ],

        "data": [],
    }



# ================================
# UPDATE
# ================================

@router.post("/update-economic-data")
def update_economic_data():

    clear_cache()

    result = refresh_engine_cache()

    clear_cache()


    return {

        "status":"updated",

        "message":
        "Economic data recalculated",

        **result,
    }



# ================================
# DASHBOARD
# ================================

@router.get(
    "/dashboard",
    response_model=MacroDashboardResponse
)
def macro_dashboard():

    try:

        macro = get_macro_engine() or {}

        trend = get_trend_engine() or {}


        surprise = build_macro_surprise()


        final_macro = build_final_macro_score(
            macro,
            surprise
        )


        score = final_macro[
            "score"
        ]


        asset_scores = macro_asset_impact(
            surprise,
            macro
        )

        regime_detail = build_macro_regime(
             macro
        )


        regime_history = update_regime_history(
            regime_detail
        )

        portfolio = build_allocation(
            asset_scores,
            regime_detail
        )


        print(portfolio)


    except Exception as exc:


        logger.exception(exc)


        return {

            "success": False,

            "data_status": "fallback",

            "macro_score":50,

            "regime":"Neutral",

            "trend":"Neutral",

            "asset_outlooks": {},

            "category_scores": {},

            "history": [],
        }



    return {

        "success": True,
        
        "data_status": "connected",


        "macro_score": score,


        "regime":
         regime_detail["regime"],


        "trend":
            clean_label(
                trend.get(
                    "trend",
                    "Neutral"
                )
            ),


        "recession_risk":
            clean_label(
                macro
                .get("outlooks",{})
                .get(
                    "Recession Risk Level",
                    "N/A"
                )
            ),


        "risk_status":
            clean_label(
                macro.get(
                    "risk_status",
                    "Neutral"
                )
            ),

        "regime_detail":
            regime_detail,

        
        "regime_history":
            regime_history,


        "summary":
            macro_summary(
                macro
            ),


        # 🔥 NEW SMART ASSET ENGINE
        "asset_outlooks":
            asset_scores,

        "portfolio_allocation":
            portfolio,


        # ?? ECONOMIC RELEASE SURPRISE MONITOR
        "macro_surprises":
            surprise.get(
                "events",
                []
            ),

        "category_scores": {

            **macro.get(
                "scores",
                {}
            ),

            "macro_surprise":
                surprise.get(
                    "score"
                ),
        },


        "history":
            macro_category_history(
                "trend",
                score
            ),
    }



# ================================
# CATEGORY ROUTE
# KEEP LAST
# ================================

@router.get(
    "/{category}",
    response_model=MacroCategoryResponse
)
def macro_category(category:str):


    slug = (
        category
        .lower()
        .replace("-","_")
    )


    if slug not in MACRO_BUILDERS:

        raise HTTPException(
            status_code=404,
            detail="Macro category not found"
        )


    try:


        engine = (
            get_macro_category(slug)
            or {}
        )

        surprise = build_macro_surprise()


        engine = build_category_final_score(
            slug,
            engine,
            surprise
        )

        score = _safe_score(
            engine.get("score")
        )


        name = MACRO_LABELS.get(
            slug,
            clean_label(slug).title()
        )


        bias = clean_label(
            engine.get(
                "bias",
                "Neutral"
            )
        )


        indicators = indicators_from_engine(
            engine
        )


        intelligence = macro_category_intelligence(
            name,
            score,
            bias,
            indicators,
        )


    except Exception as exc:


        return _empty_category(
            slug,
            str(exc)
        )



    return {

        "success": True,

        "data_status":"connected",

        "name": name,

        "score": score,
                
        "core_score":
            engine.get(
                "core_score"
            ),


        "surprise_score":
            engine.get(
                "surprise_score"
            ),


        "surprise_events":
            engine.get(
                "surprise_events",
                []
            ),

        "bias": bias,


        "trend":
            intelligence["trend"],


        "summary":
            intelligence["summary"],


        "drivers":
            intelligence["drivers"],


        "indicators":
            indicators,


        "explanation":
            intelligence["summary"],


        "history":
            macro_category_history(
                slug,
                score
            ),


        "data":
            indicators,
    }



