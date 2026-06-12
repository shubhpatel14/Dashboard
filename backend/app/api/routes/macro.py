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

router = APIRouter(prefix="/macro", tags=["macro"])
logger = logging.getLogger(__name__)


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


def _safe_score(value: Any, default: float = 50) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _empty_category(slug: str, message: str = "") -> dict[str, Any]:
    name = MACRO_LABELS.get(slug, clean_label(slug).title())
    summary = message or f"{name} data is temporarily unavailable. Neutral fallback is being used."
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
        "history": [{"date": "Current", "score": 50}],
        "data": [],
    }


@router.post("/update-economic-data")
def update_economic_data():
    clear_cache()
    result = refresh_engine_cache()
    clear_cache()

    return {
        "status": "updated",
        "message": "Economic releases, macro scores, asset scores, and explanations were recalculated.",
        **result,
    }


@router.get("/dashboard", response_model=MacroDashboardResponse)
@cached("macro-dashboard")
def macro_dashboard():
    try:
        macro = get_macro_engine() or {}
        trend = get_trend_engine() or {}
        score = _safe_score(macro.get("score"), 50)
    except Exception as exc:
        logger.exception("Macro dashboard engine failed")
        return {
            "success": False,
            "data_status": "fallback",
            "error": str(exc),
            "macro_score": 50,
            "regime": "Neutral",
            "trend": "Stable",
            "recession_risk": "N/A",
            "risk_status": "Neutral",
            "summary": ["Macro API temporarily failed. Neutral cached fallback is being used."],
            "asset_outlooks": {},
            "category_scores": {},
            "history": [],
        }

    return {
        "success": True,
        "data_status": "connected",
        "macro_score": score,
        "regime": clean_label(macro_regime(score)),
        "trend": clean_label(trend.get("trend", "Neutral")),
        "recession_risk": clean_label(macro.get("outlooks", {}).get("Recession Risk Level", "N/A")),
        "risk_status": clean_label(macro.get("risk_status", "Neutral")),
        "summary": macro_summary(macro),
        "asset_outlooks": {
            "Gold": macro.get("gold_bias"),
            "SP500": macro.get("equity_bias"),
            "Dollar": macro.get("usd_bias"),
            "Bitcoin": macro.get("outlooks", {}).get("Bitcoin Outlook", "N/A"),
            "Nasdaq": macro.get("outlooks", {}).get("Nasdaq Outlook", "N/A"),
            "Bonds": macro.get("outlooks", {}).get("Bond Yield Outlook", "N/A"),
        },
        "category_scores": macro.get("scores", {}),
        "history": macro_category_history("trend", score),
    }


@router.get("/{category}", response_model=MacroCategoryResponse)
@cached("macro-category")
def macro_category(category: str):
    slug = category.lower().replace("-", "_")
    if slug not in MACRO_BUILDERS:
        raise HTTPException(status_code=404, detail="Macro category not found")

    try:
        engine = get_macro_category(slug) or {}
        score = _safe_score(engine.get("score"), 50)
        name = MACRO_LABELS.get(slug, clean_label(slug).title())
        bias = clean_label(engine.get("bias", "Neutral"))
        indicators = indicators_from_engine(engine)
        intelligence = macro_category_intelligence(name, score, bias, indicators)
    except Exception as exc:
        logger.exception("Macro category failed: %s", slug)
        return _empty_category(slug, str(exc))

    return {
        "success": True,
        "data_status": "connected",
        "name": name,
        "score": score,
        "bias": bias,
        "trend": intelligence["trend"],
        "summary": intelligence["summary"],
        "drivers": intelligence["drivers"],
        "indicators": indicators,
        "explanation": intelligence["summary"],
        "history": macro_category_history(slug, score),
        "data": indicators,
    }


