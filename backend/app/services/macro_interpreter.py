from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class IndicatorMeta:
    name: str
    source: str
    measures: str
    impact: str
    positive_trend: str
    negative_trend: str
    neutral_trend: str
    positive_condition: str
    negative_condition: str
    asset_positive: str
    asset_negative: str
    unit: str = "%"
    period: str = ""
    lower_is_bullish: bool = False
    weight: float = 10


META: dict[str, IndicatorMeta] = {
    "M2": IndicatorMeta("Money Supply Growth", "FRED M2SL", "Amount of money circulating in the economy.", "Higher liquidity generally supports equities, crypto and commodities.", "Improving Liquidity", "Tightening Liquidity", "Stable Liquidity", "expanded", "contracted", "Supports risk assets", "Pressures risk assets", "%", "YoY", False, 40),
    "WALCL": IndicatorMeta("Federal Reserve Balance Sheet", "FRED WALCL", "Size of the Federal Reserve balance sheet.", "Balance sheet expansion adds system liquidity; contraction drains liquidity.", "Expanding Liquidity", "Contracting Liquidity", "Stable Balance Sheet", "expanded", "contracted", "Supports risk assets", "Tightens financial liquidity", "%", "YoY", False, 30),
    "BANK_RESERVES": IndicatorMeta("Bank Reserves", "FRED TOTRESNS", "Reserve balances held by banks.", "Rising reserves improve banking-system liquidity.", "Increasing Reserves", "Falling Reserves", "Stable Reserves", "increased", "fell", "Supports credit and risk assets", "Restricts credit creation", "%", "YoY", False, 10),
    "RRP": IndicatorMeta("Reverse Repo Liquidity", "FRED RRPONTSYD", "Cash parked at the Fed reverse repo facility.", "Falling reverse repo balances release liquidity back into markets.", "Falling Cash Drain", "Rising Cash Drain", "Stable Cash Drain", "fell", "increased", "Supports liquidity and risk assets", "Pulls liquidity away from markets", "%", "YoY", True, 20),
    "USD_INDEX": IndicatorMeta("Dollar Liquidity Pressure", "FRED DTWEXBGS", "Trade-weighted U.S. dollar pressure.", "A weaker dollar usually eases global liquidity conditions.", "Dollar Pressure Easing", "Dollar Pressure Rising", "Stable Dollar Pressure", "eased", "tightened", "Supports global risk assets", "Pressures global liquidity", "%", "YoY", True, 20),
    "FED_FUNDS_RATE_LEVEL": IndicatorMeta("Fed Policy Rate", "FRED FEDFUNDS", "Effective federal funds policy rate.", "Higher policy rates tighten financial conditions and pressure risk assets.", "Less Restrictive Policy", "More Restrictive Policy", "Restrictive Policy", "eased", "tightened", "Supports rate-sensitive assets", "Pressures risk assets", "%", "", True, 25),
    "TEN_YEAR_YIELD_LEVEL": IndicatorMeta("10-Year Treasury Yield", "FRED GS10", "Long-term U.S. Treasury yield.", "Higher long yields raise discount rates for equities and housing.", "Yield Pressure Easing", "Yield Pressure Rising", "Stable Yield Pressure", "fell", "rose", "Supports bonds and growth equities", "Pressures equities and housing", "%", "", True, 20),
    "TWO_YEAR_YIELD_LEVEL": IndicatorMeta("2-Year Treasury Yield", "FRED DGS2", "Short-term Treasury yield sensitive to Fed expectations.", "Rising 2-year yields imply tighter expected policy.", "Policy Pressure Easing", "Policy Pressure Rising", "Stable Policy Pressure", "fell", "rose", "Supports risk appetite", "Pressures risk assets", "%", "", True, 15),
    "TEN_YEAR_REAL_YIELD_LEVEL": IndicatorMeta("10-Year Real Yield", "FRED DFII10", "Inflation-adjusted Treasury yield.", "Higher real yields compete with risk assets and gold.", "Real Yield Pressure Easing", "Real Yield Pressure Rising", "Stable Real Yield Pressure", "fell", "rose", "Supports gold and growth assets", "Pressures gold and long-duration assets", "%", "", True, 25),
    "YIELD_CURVE_10Y_2Y": IndicatorMeta("Yield Curve", "FRED GS10/DGS2", "Spread between 10-year and 2-year Treasury yields.", "A steeper curve usually signals improving growth expectations.", "Curve Steepening", "Curve Flattening", "Stable Curve", "steepened", "flattened", "Supports cyclicals and banks", "Raises recession concern", "%", "", False, 15),
    "YIELD_CURVE": IndicatorMeta("Yield Curve", "FRED T10Y2Y", "10-year minus 2-year Treasury spread.", "A deeply inverted curve is a classic recession warning.", "Recession Signal Easing", "Recession Signal Worsening", "Stable Recession Signal", "improved", "deteriorated", "Reduces recession risk", "Raises recession risk", "%", "", False, 35),
    "CPI_MOM": IndicatorMeta("Consumer Inflation", "FRED CPIAUCSL", "Monthly change in consumer prices.", "Cooling inflation supports Fed easing expectations.", "Cooling", "Heating Up", "Sticky Inflation", "cooled", "accelerated", "Supports Fed rate cuts", "Pressures bonds and risk assets", "%", "MoM", True, 20),
    "CORE_CPI_MOM": IndicatorMeta("Core Consumer Inflation", "FRED CPILFESL", "Monthly CPI excluding food and energy.", "Core inflation drives Fed policy more than volatile headline prices.", "Cooling", "Heating Up", "Sticky Core Inflation", "cooled", "accelerated", "Supports Fed rate cuts", "Keeps Fed policy restrictive", "%", "MoM", True, 25),
    "PCE_MOM": IndicatorMeta("PCE Inflation", "FRED PCEPI", "Monthly change in personal consumption prices.", "PCE is the Fed's preferred inflation gauge.", "Cooling", "Heating Up", "Sticky PCE Inflation", "cooled", "accelerated", "Supports Fed rate cuts", "Keeps policy tight", "%", "MoM", True, 10),
    "CORE_PCE_MOM": IndicatorMeta("Core PCE Inflation", "FRED PCEPILFE", "Monthly PCE excluding food and energy.", "Core PCE is the Fed's preferred underlying inflation measure.", "Cooling", "Heating Up", "Sticky Core PCE", "cooled", "accelerated", "Supports Fed rate cuts", "Keeps policy restrictive", "%", "MoM", True, 20),
    "PPI_MOM": IndicatorMeta("Producer Inflation", "FRED PPIACO", "Monthly producer-price pressure.", "Producer prices can feed into consumer inflation and margins.", "Cooling", "Heating Up", "Stable Producer Prices", "cooled", "accelerated", "Supports margins and rate cuts", "Pressures margins and policy", "%", "MoM", True, 5),
    "CORE_PPI_MOM": IndicatorMeta("Core Producer Inflation", "FRED PPIFES", "Monthly core producer-price pressure.", "Core producer prices show underlying pipeline inflation.", "Cooling", "Heating Up", "Stable Pipeline Inflation", "cooled", "accelerated", "Supports margins", "Pressures inflation expectations", "%", "MoM", True, 5),
    "CPI_YOY": IndicatorMeta("Consumer Inflation", "FRED CPIAUCSL", "Year-over-year consumer price inflation.", "Cooling inflation supports Fed easing expectations.", "Cooling", "Heating Up", "Sticky Inflation", "cooled", "accelerated", "Supports Fed rate cuts", "Pressures bonds and risk assets", "%", "YoY", True, 10),
    "CORE_CPI_YOY": IndicatorMeta("Core Consumer Inflation", "FRED CPILFESL", "Year-over-year CPI excluding food and energy.", "Core inflation drives Fed policy expectations.", "Cooling", "Heating Up", "Sticky Core Inflation", "cooled", "accelerated", "Supports Fed rate cuts", "Keeps Fed policy restrictive", "%", "YoY", True, 10),
    "PCE_YOY": IndicatorMeta("PCE Inflation", "FRED PCEPI", "Year-over-year PCE inflation.", "PCE is the Fed's preferred inflation gauge.", "Cooling", "Heating Up", "Sticky PCE Inflation", "cooled", "accelerated", "Supports Fed rate cuts", "Keeps policy tight", "%", "YoY", True, 5),
    "CORE_PCE_YOY": IndicatorMeta("Core PCE Inflation", "FRED PCEPILFE", "Year-over-year core PCE inflation.", "Core PCE shows underlying inflation pressure.", "Cooling", "Heating Up", "Sticky Core PCE", "cooled", "accelerated", "Supports Fed rate cuts", "Keeps policy restrictive", "%", "YoY", True, 5),
    "GDP_QOQ_ANNUALIZED": IndicatorMeta("Real GDP Growth", "FRED GDPC1", "Quarterly real GDP growth annualized.", "Stronger growth supports earnings and cyclical assets.", "Growth Improving", "Growth Slowing", "Stable Growth", "improved", "slowed", "Supports equities and cyclicals", "Raises slowdown risk", "%", "QoQ annualized", False, 30),
    "GDP_YOY": IndicatorMeta("Real GDP Growth", "FRED GDPC1", "Year-over-year real GDP growth.", "Real growth anchors earnings and risk appetite.", "Growth Improving", "Growth Slowing", "Stable Growth", "improved", "slowed", "Supports equities", "Raises slowdown risk", "%", "YoY", False, 10),
    "RETAIL_SALES_MOM": IndicatorMeta("Retail Sales", "FRED RSAFS", "Monthly retail spending growth.", "Retail sales show consumer demand momentum.", "Demand Improving", "Demand Weakening", "Stable Demand", "improved", "weakened", "Supports consumer equities", "Pressures growth expectations", "%", "MoM", False, 20),
    "INDUSTRIAL_PRODUCTION_MOM": IndicatorMeta("Industrial Production", "FRED INDPRO", "Monthly industrial output growth.", "Industrial production tracks real-economy momentum.", "Production Improving", "Production Weakening", "Stable Production", "improved", "weakened", "Supports cyclicals", "Pressures cyclicals", "%", "MoM", False, 15),
    "DURABLE_GOODS_ORDERS_MOM": IndicatorMeta("Durable Goods Orders", "FRED DGORDER", "Monthly durable-goods order growth.", "Durables show business and consumer demand for big-ticket items.", "Orders Improving", "Orders Weakening", "Stable Orders", "improved", "weakened", "Supports cyclicals", "Pressures cyclicals", "%", "MoM", False, 15),
    "FACTORY_ORDERS_MOM": IndicatorMeta("Factory Orders", "FRED AMTMNO", "Monthly factory-order growth.", "Factory orders show manufacturing demand.", "Orders Improving", "Orders Weakening", "Stable Orders", "improved", "weakened", "Supports industrials", "Pressures industrials", "%", "MoM", False, 10),
    "NON_FARM_PAYROLL_CHANGE": IndicatorMeta("Job Creation", "FRED PAYEMS", "Monthly change in nonfarm payroll employment.", "Healthy job creation supports income and spending.", "Healthy Labor Market", "Labor Cooling", "Stable Hiring", "increased", "slowed", "Supports consumption", "Raises slowdown concern", "K jobs", "", False, 30),
    "INITIAL_CLAIMS_WEEKLY_CHANGE": IndicatorMeta("Initial Jobless Claims", "FRED ICSA", "Weekly change in new unemployment claims.", "Falling claims signal labor-market resilience.", "Claims Falling", "Claims Rising", "Stable Claims", "fell", "rose", "Supports confidence and equities", "Raises labor-market stress", "%", "MoM", True, 25),
    "CONTINUING_CLAIMS_WEEKLY_CHANGE": IndicatorMeta("Continuing Jobless Claims", "FRED CCSA", "Change in ongoing unemployment claims.", "Rising continuing claims can signal hiring weakness.", "Claims Falling", "Claims Rising", "Stable Claims", "fell", "rose", "Supports confidence", "Signals labor stress", "%", "MoM", True, 15),
    "UNEMPLOYMENT_RATE": IndicatorMeta("Unemployment Rate", "FRED UNRATE", "Share of labor force unemployed.", "A low unemployment rate supports incomes but can influence Fed policy.", "Labor Stress Easing", "Labor Stress Rising", "Stable Labor Market", "fell", "rose", "Supports consumption", "Raises recession concern", "%", "", True, 20),
    "LABOR_PARTICIPATION_RATE": IndicatorMeta("Labor Participation Rate", "FRED CIVPART", "Share of working-age population in the labor force.", "Higher participation expands labor supply and supports growth.", "Participation Improving", "Participation Weakening", "Stable Participation", "rose", "fell", "Supports growth", "Constrains labor supply", "%", "", False, 10),
    "HY_SPREAD_LEVEL": IndicatorMeta("High Yield Credit Spreads", "FRED BAMLH0A0HYM2", "Yield premium demanded for high-yield bonds.", "Wider spreads signal credit stress and tighter financing.", "Credit Stress Easing", "Credit Stress Rising", "Stable Credit Stress", "tightened", "widened", "Supports risk credit and equities", "Pressures risk assets", "%", "", True, 50),
    "IG_SPREAD_LEVEL": IndicatorMeta("Investment Grade Spreads", "FRED BAMLC0A0CM", "Yield premium demanded for investment-grade bonds.", "Wider spreads show financing stress in higher-quality credit.", "Credit Stress Easing", "Credit Stress Rising", "Stable Credit Stress", "tightened", "widened", "Supports credit markets", "Signals tighter financing", "%", "", True, 30),
    "TED_SPREAD_LEVEL": IndicatorMeta("Bank Funding Stress", "FRED TEDRATE", "Spread between bank funding and Treasury rates.", "Higher TED spreads indicate funding stress.", "Funding Stress Easing", "Funding Stress Rising", "Stable Funding Stress", "eased", "worsened", "Supports financial conditions", "Pressures liquidity", "%", "", True, 20),
    "VIX_LEVEL": IndicatorMeta("Equity Volatility", "FRED VIXCLS", "S&P 500 implied volatility.", "Lower volatility usually supports risk appetite.", "Volatility Easing", "Volatility Rising", "Stable Volatility", "eased", "rose", "Supports equities", "Pressures risk appetite", "", "", True, 40),
    "CONSUMER_SENTIMENT_LEVEL": IndicatorMeta("Consumer Sentiment", "FRED UMCSENT", "University of Michigan consumer sentiment.", "Stronger sentiment supports consumption and earnings.", "Sentiment Improving", "Sentiment Weakening", "Stable Sentiment", "improved", "weakened", "Supports consumer demand", "Pressures consumption", "", "", False, 35),
    "FINANCIAL_CONDITIONS_INDEX_LEVEL": IndicatorMeta("Financial Conditions", "FRED NFCI", "Chicago Fed National Financial Conditions Index.", "Looser financial conditions support credit and risk assets.", "Conditions Easing", "Conditions Tightening", "Stable Conditions", "eased", "tightened", "Supports risk assets", "Pressures risk assets", "", "", True, 25),
    "HOUSING_STARTS_MOM": IndicatorMeta("Housing Starts", "FRED HOUST", "Monthly growth in new home construction starts.", "Housing starts show construction and housing demand momentum.", "Housing Activity Improving", "Housing Activity Weakening", "Stable Housing Activity", "improved", "weakened", "Supports housing and cyclicals", "Pressures housing-linked assets", "%", "MoM", False, 25),
    "BUILDING_PERMITS_MOM": IndicatorMeta("Building Permits", "FRED PERMIT", "Monthly growth in authorized building permits.", "Permits are a forward-looking housing activity signal.", "Forward Demand Improving", "Forward Demand Weakening", "Stable Forward Demand", "improved", "weakened", "Supports housing activity", "Signals housing slowdown", "%", "MoM", False, 25),
    "NEW_HOME_SALES_MOM": IndicatorMeta("New Home Sales", "FRED HSN1F", "Monthly growth in new single-family home sales.", "New home sales track housing demand and construction momentum.", "Demand Improving", "Demand Weakening", "Stable Demand", "improved", "weakened", "Supports homebuilders", "Pressures homebuilders", "%", "MoM", False, 15),
    "EXISTING_HOME_SALES_MOM": IndicatorMeta("Existing Home Sales", "FRED EXHOSLUSM495S", "Monthly growth in existing home sales.", "Existing sales show housing-market transaction activity.", "Activity Improving", "Activity Weakening", "Stable Activity", "improved", "weakened", "Supports housing turnover", "Signals housing weakness", "%", "MoM", False, 15),
    "CASE_SHILLER_YOY": IndicatorMeta("Home Price Growth", "FRED CSUSHPISA", "Year-over-year national home price growth.", "Home price growth reflects household wealth and affordability pressure.", "Prices Firming", "Prices Cooling", "Stable Home Prices", "improved", "cooled", "Supports household wealth", "Eases inflation but may signal weak demand", "%", "YoY", False, 10),
    "MORTGAGE_RATE_LEVEL": IndicatorMeta("Mortgage Rate", "FRED MORTGAGE30US", "30-year fixed mortgage rate.", "Higher mortgage rates pressure affordability and housing demand.", "Affordability Improving", "Affordability Worsening", "Stable Affordability", "fell", "rose", "Supports housing demand", "Pressures housing demand", "%", "", True, 10),
}


def _fallback_meta(key: str) -> IndicatorMeta:
    label = key.replace("_", " ").title()
    return IndicatorMeta(
        label,
        "FRED",
        f"{label} macro input.",
        "Used as part of the macro score.",
        "Improving",
        "Worsening",
        "Stable",
        "improved",
        "weakened",
        "Supports risk appetite",
        "Pressures risk appetite",
    )


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _direction(values: dict[str, Any], meta: IndicatorMeta) -> str:
    current = _as_float(values.get("current"))
    previous = _as_float(values.get("previous"))
    delta = current - previous

    if abs(delta) < 0.01:
        return "neutral"

    improving = delta < 0 if meta.lower_is_bullish else delta > 0
    return "positive" if improving else "negative"


def _format_value(value: Any, meta: IndicatorMeta) -> str:
    if value in (None, "N/A"):
        return "N/A"

    number = _as_float(value)
    sign = "+" if number > 0 and meta.unit in {"%", "K jobs"} else ""
    suffix = f" {meta.period}" if meta.period else ""

    if meta.unit == "K jobs":
        return f"{sign}{number:,.0f}K"
    if meta.unit == "%":
        return f"{sign}{number:,.2f}%{suffix}"
    if meta.unit:
        return f"{sign}{number:,.2f} {meta.unit}{suffix}"
    return f"{sign}{number:,.2f}{suffix}"


def _format_change(values: dict[str, Any], meta: IndicatorMeta) -> str:
    current = _as_float(values.get("current"))
    previous = _as_float(values.get("previous"))
    delta = current - previous
    arrow = "->" if abs(delta) < 0.01 else "up" if delta > 0 else "down"
    sign = "+" if delta > 0 else ""
    suffix = "%" if meta.unit == "%" else ""
    if meta.unit == "K jobs":
        suffix = "K"
    return f"{arrow} {sign}{delta:,.2f}{suffix}"


def _format_delta(value: Any, meta: IndicatorMeta) -> str:
    if value in (None, "N/A"):
        return "N/A"

    number = _as_float(value)
    sign = "+" if number > 0 else ""
    suffix = "%" if meta.unit == "%" else ""
    if meta.unit == "K jobs":
        suffix = "K"
    return f"{sign}{number:,.2f}{suffix}"


def _bias(score: float) -> str:
    if score >= 80:
        return "Very Bullish"
    if score >= 65:
        return "Bullish"
    if score >= 45:
        return "Neutral"
    if score >= 25:
        return "Bearish"
    return "Very Bearish"


def interpret_indicator(key: str, values: dict[str, Any]) -> dict[str, Any]:
    meta = META.get(key, _fallback_meta(key))
    score = round(_as_float(values.get("score"), 50.0), 2)

    if values.get("release_type") == "economic_release":
        surprise_score = round(_as_float(values.get("surprise_score"), 50.0), 2)
        trend_score = round(_as_float(values.get("trend_score"), 50.0), 2)
        trend_state = values.get("trend_state") or (
            "positive" if score >= 60 else "negative" if score <= 40 else "neutral"
        )
        market_surprise = values.get("market_surprise") or "In line with expectations"
        trend = values.get("trend") or "Trend unavailable"

        return {
            "key": key,
            "name": values.get("name") or meta.name,
            "code": _fred_code(values, meta),
            "source": values.get("source") or "Economic Calendar",
            "measures": meta.measures,
            "current": values.get("actual", values.get("current", "N/A")),
            "previous": values.get("previous", "N/A"),
            "change": values.get("trend_change", values.get("change", "N/A")),
            "actual": values.get("actual", "N/A"),
            "forecast": values.get("forecast", "N/A"),
            "surprise": values.get("surprise", "N/A"),
            "trend_change": values.get("trend_change", "N/A"),
            "surprise_score": surprise_score,
            "trend_score": trend_score,
            "final_score": score,
            "current_display": _format_value(values.get("actual", values.get("current")), meta),
            "previous_display": _format_value(values.get("previous"), meta),
            "change_display": _format_delta(values.get("trend_change", values.get("change")), meta),
            "actual_display": _format_value(values.get("actual"), meta),
            "forecast_display": _format_value(values.get("forecast"), meta),
            "surprise_display": _format_delta(values.get("surprise"), meta),
            "trend": trend,
            "market_surprise": market_surprise,
            "trend_state": trend_state,
            "impact": market_surprise,
            "market_impact": meta.impact,
            "score": score,
            "bias": values.get("bias") or _bias(score),
            "last_update": values.get("last_updated") or values.get("last_update", "N/A"),
            "explanation": values.get("explanation") or f"{meta.name} scored {score:.0f}/100 after surprise and trend scoring.",
            "info": f"Source: {values.get('source') or 'Economic Calendar'}\n\nMeasures: {meta.measures}\n\nMarket Impact: {meta.impact}",
            "weight": meta.weight,
            "contribution": round((score / 100) * meta.weight, 2),
            "release_type": "economic_release",
        }

    direction = _direction(values, meta)
    action = {
        "positive": meta.positive_condition,
        "negative": meta.negative_condition,
        "neutral": "was little changed",
    }[direction]
    trend = {
        "positive": meta.positive_trend,
        "negative": meta.negative_trend,
        "neutral": meta.neutral_trend,
    }[direction]
    impact = meta.asset_positive if direction != "negative" else meta.asset_negative

    return {
        "key": key,
        "name": meta.name,
        "code": _fred_code(values, meta),
        "source": meta.source,
        "measures": meta.measures,
        "current": values.get("current", "N/A"),
        "previous": values.get("previous", "N/A"),
        "change": values.get("change", "N/A"),
        "direction_score": values.get("direction_score"),
        "momentum_score": values.get("momentum_score"),
        "final_score": values.get("final_score", score),
        "current_display": _format_value(values.get("current"), meta),
        "previous_display": _format_value(values.get("previous"), meta),
        "change_display": _format_change(values, meta),
        "trend": trend,
        "trend_state": direction,
        "impact": impact,
        "market_impact": meta.impact,
        "score": score,
        "bias": values.get("bias") or _bias(score),
        "last_update": values.get("last_updated") or values.get("last_update", "N/A"),
        "explanation": f"{meta.name} {action} to {_format_value(values.get('current'), meta)}, making conditions {trend.lower()}.",
        "info": f"Source: {meta.source}\n\nMeasures: {meta.measures}\n\nMarket Impact: {meta.impact}",
        "weight": meta.weight,
        "contribution": round((score / 100) * meta.weight, 2),
    }


def _fred_code(values: dict[str, Any], meta: IndicatorMeta) -> str:
    history = values.get("history") or {}
    if isinstance(history, dict):
        if history.get("code"):
            return str(history["code"])
        if history.get("codes"):
            return "/".join(str(code) for code in history["codes"])
    return meta.source.replace("FRED ", "")


def interpret_category(name: str, score: float, bias: str, indicators: list[dict[str, Any]]) -> dict[str, Any]:
    improving = [item for item in indicators if item["trend_state"] == "positive"]
    worsening = [item for item in indicators if item["trend_state"] == "negative"]
    top_positive = sorted(improving, key=lambda item: item["weight"], reverse=True)[:2]
    top_negative = sorted(worsening, key=lambda item: item["weight"], reverse=True)[:2]

    if top_positive and top_negative:
        summary = (
            f"{name} conditions are mixed: "
            f"{', '.join(item['name'].lower() for item in top_positive)} improved, "
            f"while {', '.join(item['name'].lower() for item in top_negative)} weakened."
        )
    elif top_positive:
        summary = (
            f"{name} conditions improved as "
            f"{', '.join(item['name'].lower() for item in top_positive)} moved in a market-supportive direction."
        )
    elif top_negative:
        summary = (
            f"{name} conditions worsened as "
            f"{', '.join(item['name'].lower() for item in top_negative)} moved against risk appetite."
        )
    else:
        summary = f"{name} conditions were broadly stable, with no major driver changing direction."

    trend = "Improving" if score >= 60 else "Worsening" if score <= 40 else "Neutral"

    drivers = [
        {
            "name": item["name"],
            "trend": item["trend"],
            "trend_state": item["trend_state"],
            "value": item["current_display"],
            "score": item["score"],
            "contribution": item["contribution"],
            "weight": item["weight"],
        }
        for item in sorted(indicators, key=lambda row: row["weight"], reverse=True)
    ]

    return {
        "summary": summary,
        "trend": trend,
        "bias": bias,
        "score": score,
        "drivers": drivers,
    }
