from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict

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
    release_from_calendar,
)


router = APIRouter(prefix="/macro", tags=["macro"])
logger = logging.getLogger(__name__)


# =====================================================
# MODELS
# =====================================================

class MacroDashboardResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    success: bool = True
    data_status: str = "connected"

    macro_score: float = 50
    regime: str = "Neutral"
    trend: str = "Neutral"

    recession_risk: str = "N/A"
    risk_status: str = "Neutral"

    summary: list[str] = []

    asset_outlooks: dict[str, Any] = {}
    category_scores: dict[str, Any] = {}

    history: list[dict[str, Any]] = []



class MacroCategoryResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    success: bool = True
    data_status: str = "connected"

    name: str = "Macro"

    score: float = 50
    bias: str = "Neutral"
    trend: str = "Stable"

    summary: str = ""

    drivers: list[dict[str, Any]] = []
    indicators: list[dict[str, Any]] = []

    explanation: str = ""

    history: list[dict[str, Any]] = []
    data: list[dict[str, Any]] = []



class MacroSurpriseResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    success: bool = True

    score: float = 50
    bias: str = "Neutral"

    events: list[dict[str, Any]] = []



# =====================================================
# HELPERS
# =====================================================

def _safe_score(
    value: Any,
    default: float = 50
) -> float:

    try:
        return float(value)

    except (TypeError, ValueError):
        return default



def _empty_category(
    slug: str,
    message: str = ""
):

    name = (
        MACRO_LABELS.get(
            slug,
            clean_label(slug).title()
        )
    )


    summary = (
        message
        or
        f"{name} unavailable. Neutral fallback used."
    )


    return {

        "success": True,
        "data_status": "fallback",

        "name": name,

        "score": 50,
        "bias": "Neutral",
        "trend": "Stable",

        "summary": summary,

        "drivers": [],
        "indicators": [],

        "explanation": summary,

        "history":[
            {
                "date":"Current",
                "score":50
            }
        ],

        "data":[]

    }



# =====================================================
# UPDATE DATA
# =====================================================

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



# =====================================================
# DASHBOARD
# =====================================================

@router.get(
    "/dashboard",
    response_model=MacroDashboardResponse
)
@cached("macro-dashboard")
def macro_dashboard():

    try:

        macro = get_macro_engine() or {}

        trend = get_trend_engine() or {}

        score = _safe_score(
            macro.get("score"),
            50
        )


    except Exception as exc:

        logger.exception(
            "Macro dashboard failed"
        )


        return {

            "success":False,

            "data_status":"fallback",

            "error":str(exc),

            "macro_score":50,

            "regime":"Neutral",

            "trend":"Stable",

            "summary":[
                "Macro engine unavailable"
            ],

            "asset_outlooks":{},

            "category_scores":{},

            "history":[],

        }



    return {

        "success":True,

        "data_status":"connected",

        "macro_score":score,

        "regime":
            clean_label(
                macro_regime(score)
            ),

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


        "summary":
            macro_summary(macro),


        "asset_outlooks":{

            "Gold":
            macro.get("gold_bias"),

            "SP500":
            macro.get("equity_bias"),

            "Dollar":
            macro.get("usd_bias"),

            "Bitcoin":
            macro.get("outlooks",{})
            .get(
                "Bitcoin Outlook",
                "N/A"
            ),

            "Nasdaq":
            macro.get("outlooks",{})
            .get(
                "Nasdaq Outlook",
                "N/A"
            ),

            "Bonds":
            macro.get("outlooks",{})
            .get(
                "Bond Yield Outlook",
                "N/A"
            ),

        },


        "category_scores":
            macro.get(
                "scores",
                {}
            ),


        "history":
            macro_category_history(
                "trend",
                score
            ),

    }



# =====================================================
# MACRO SURPRISE ENGINE
# =====================================================

@router.get(
    "/surprise",
    response_model=MacroSurpriseResponse
)
@cached("macro-surprise")
def macro_surprise():


    releases = [

        (
            "CPI_YOY",
            "CPI YoY",
            "inflation"
        ),

        (
            "CORE_CPI_YOY",
            "Core CPI YoY",
            "inflation"
        ),

        (
            "NON_FARM_PAYROLL_CHANGE",
            "Non Farm Payrolls",
            "labor"
        ),

        (
            "UNEMPLOYMENT_RATE",
            "Unemployment Rate",
            "labor"
        ),

        (
            "GDP_QOQ_ANNUALIZED",
            "GDP Growth",
            "growth"
        ),

        (
            "FED_RATE_DECISION",
            "Fed Rate Decision",
            "rates"
        ),

    ]



    events=[]


    for key,name,category in releases:


        item = release_from_calendar(
            key,
            name,
            category
        )


        if item:

            item["category"] = category

            events.append(item)



    if events:

        score = round(

            sum(
                x["score"]
                for x in events
            )

            /

            len(events),

            2

        )

    else:

        score=50



    if score >=60:

        bias="Bullish"


    elif score <=40:

        bias="Bearish"


    else:

        bias="Neutral"



    return {

        "success":True,

        "score":score,

        "bias":bias,

        "events":events,

    }



# =====================================================
# CATEGORY (KEEP LAST)
# =====================================================

class MacroSurpriseResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    success: bool = True
    score: float = 50
    bias: str = "Neutral"
    events: list[dict[str, Any]] = []


from app.engines.macro.macro_surprise.scoring import release_from_calendar


@router.get("/surprise", response_model=MacroSurpriseResponse)
@cached("macro-surprise")
def macro_surprise():

    releases = [
        ("CPI_YOY", "CPI YoY", "inflation"),
        ("CORE_CPI_YOY", "Core CPI YoY", "inflation"),
        ("NON_FARM_PAYROLL_CHANGE", "Non Farm Payrolls", "labor"),
        ("UNEMPLOYMENT_RATE", "Unemployment Rate", "labor"),
        ("GDP_QOQ_ANNUALIZED", "GDP Growth", "growth"),
        ("FED_RATE_DECISION", "Fed Rate Decision", "rates"),
    ]

    events = []

    for key, name, category in releases:

        item = release_from_calendar(
            key,
            name,
            category,
        )

        if item:
            item["category"] = category
            events.append(item)


    if events:
        score = round(
            sum(x["score"] for x in events)
            /
            len(events),
            2,
        )

    else:
        score = 50


    if score >= 60:
        bias = "Bullish"

    elif score <= 40:
        bias = "Bearish"

    else:
        bias = "Neutral"


    return {
        "success": True,
        "score": score,
        "bias": bias,
        "events": events,
    }

@router.get(
    "/{category}",
    response_model=MacroCategoryResponse
)
@cached("macro-category")
def macro_category(
    category:str
):

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


        score = _safe_score(
            engine.get("score"),
            50
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


        indicators = (
            indicators_from_engine(
                engine
            )
        )


        intelligence = (
            macro_category_intelligence(
                name,
                score,
                bias,
                indicators
            )
        )


    except Exception as exc:

        logger.exception(
            "Macro category failed"
        )


        return _empty_category(
            slug,
            str(exc)
        )



    return {

        "success":True,

        "data_status":"connected",

        "name":name,

        "score":score,

        "bias":bias,

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