from fastapi import APIRouter, HTTPException

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


@router.get("/dashboard")
@cached("macro-dashboard")
def macro_dashboard():
    macro = get_macro_engine()
    trend = get_trend_engine()

    return {
        "macro_score": macro["score"],
        "regime": clean_label(macro_regime(macro["score"])),
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
    }


@router.get("/{category}")
@cached("macro-category")
def macro_category(category: str):
    slug = category.lower()
    if slug not in MACRO_BUILDERS:
        raise HTTPException(status_code=404, detail="Macro category not found")

    engine = get_macro_category(slug)
    score = engine.get("score", 50)
    name = MACRO_LABELS[slug]
    bias = clean_label(engine.get("bias", "Neutral"))
    indicators = indicators_from_engine(engine)
    intelligence = macro_category_intelligence(name, score, bias, indicators)

    return {
        "name": name,
        "score": score,
        "bias": bias,
        "trend": intelligence["trend"],
        "summary": intelligence["summary"],
        "drivers": intelligence["drivers"],
        "indicators": indicators,
        "explanation": intelligence["summary"],
        "history": macro_category_history(slug, score),
    }


