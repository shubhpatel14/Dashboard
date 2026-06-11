import pandas as pd
import streamlit as st
import altair as alt
from pathlib import Path
from datetime import datetime
from html import escape
from math import cos, pi, sin
from textwrap import dedent

from engines.bitcoin import build_bitcoin_engine
from engines.bonds import build_bonds_engine
from engines.credit import build_credit_engine
from engines.dollar import build_dollar_engine
from engines.global_liquidity import build_global_liquidity_engine
from engines.gold import build_gold_engine
from engines.growth import build_growth_engine
from engines.housing import build_housing_engine
from engines.institutional import build_institutional_engine
from engines.inflation import build_inflation_engine
from engines.labor import build_labor_engine
from engines.liquidity import build_liquidity_engine
from engines.macro import build_macro_engine
from engines.macro_surprise import clear_release_cache
from engines.nasdaq import build_nasdaq_engine
from engines.rates import build_rates_engine
from engines.recession import build_recession_engine
from engines.sentiment import build_sentiment_engine
from engines.sp500 import build_sp500_engine
from engines.trend import build_trend_engine

from data.fred_client import clear_fred_memory_cache, get_series
from models.scoring import pct_change
from models.status import get_regime


st.set_page_config(
    page_title="Trishula Capital",
    page_icon="TC",
    layout="wide"
)

try:
    with open("styles.css") as file:
        st.markdown(
            f"<style>{file.read()}</style>",
            unsafe_allow_html=True
        )
except Exception:
    pass


def render_html(markup, target=st):

    html = "\n".join(
        line.strip()
        for line in dedent(markup).strip().splitlines()
        if line.strip()
    )

    if hasattr(target, "html"):
        target.html(html)
        return

    target.markdown(
        html,
        unsafe_allow_html=True
    )


def render_unsafe_html(markup, target=st):

    html = "\n".join(
        line.strip()
        for line in dedent(markup).strip().splitlines()
        if line.strip()
    )
    target.markdown(html, unsafe_allow_html=True)


ENGINE_CACHE_VERSION = 4
HISTORY_PATH = Path("dashboard_history.csv")


def refresh_economic_data():

    clear_fred_memory_cache()
    clear_release_cache()
    load_all_engines.clear()


def get_engine_cache_key():

    files = [
        Path("dashboard.py"),
        *Path("engines").glob("*.py"),
        *Path("models").glob("*.py"),
        *Path("data").glob("*.py")
    ]

    return (
        ENGINE_CACHE_VERSION,
        tuple(
            file.stat().st_mtime
            for file in files
            if file.exists()
        )
    )


@st.cache_data(ttl=900)
def load_all_engines(cache_key):

    return {
        "liquidity": build_liquidity_engine(),
        "global_liquidity": build_global_liquidity_engine(),
        "rates": build_rates_engine(),
        "inflation": build_inflation_engine(),
        "growth": build_growth_engine(),
        "labor": build_labor_engine(),
        "credit": build_credit_engine(),
        "sentiment": build_sentiment_engine(),
        "housing": build_housing_engine(),
        "institutional": build_institutional_engine(),
        "macro": build_macro_engine(),
        "gold": build_gold_engine(),
        "bitcoin": build_bitcoin_engine(),
        "sp500": build_sp500_engine(),
        "nasdaq": build_nasdaq_engine(),
        "dollar": build_dollar_engine(),
        "bonds": build_bonds_engine(),
        "recession": build_recession_engine(),
        "trend": build_trend_engine()
    }


engines = load_all_engines(get_engine_cache_key())

macro = engines["macro"]
macro_score = macro["score"]
bitcoin = engines["bitcoin"]
gold = engines["gold"]
sp500 = engines["sp500"]
nasdaq = engines["nasdaq"]
dollar = engines["dollar"]
bonds = engines["bonds"]


def current_history_snapshot():

    return {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "liquidity": engines["liquidity"]["score"],
        "rates": engines["rates"]["score"],
        "inflation": engines["inflation"]["score"],
        "growth": engines["growth"]["score"],
        "labor": engines["labor"]["score"],
        "overall": macro_score
    }


def record_dashboard_snapshot_if_changed():

    snapshot = current_history_snapshot()
    def to_number(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    score_columns = [
        "liquidity",
        "rates",
        "inflation",
        "growth",
        "labor",
        "overall"
    ]

    if HISTORY_PATH.exists():
        history = pd.read_csv(HISTORY_PATH)
    else:
        history = pd.DataFrame(columns=["date", *score_columns])

    if not history.empty:
        latest = history.iloc[-1]
        unchanged = all(
            abs(to_number(latest.get(column)) - snapshot[column]) < 0.005
            if to_number(latest.get(column)) is not None
            else False
            for column in score_columns
        )

        if unchanged:
            return

    pd.concat(
        [
            history,
            pd.DataFrame([snapshot])
        ],
        ignore_index=True
    ).to_csv(HISTORY_PATH, index=False)


record_dashboard_snapshot_if_changed()
trend = build_trend_engine()


def build_component_table(asset):

    rows = []

    def add_row(component, values):

        if isinstance(values, dict):
            change = values.get(
                "change",
                values.get("difference")
            )
            rows.append(
                {
                    "Metric": component,
                    "Current": values.get("current", ""),
                    "Previous": values.get("previous", values.get("old", "")),
                    "Change": change if change is not None else "",
                    "Score": values.get("score", ""),
                    "Bias": values.get("bias", "")
                }
            )
        else:
            rows.append(
                {
                    "Metric": component,
                    "Current": "",
                    "Previous": "",
                    "Change": "",
                    "Score": values,
                    "Bias": ""
                }
            )

    def add_dataset(name, dataset):

        if isinstance(dataset, dict):
            if any(
                key in dataset
                for key in [
                    "current",
                    "previous",
                    "old",
                    "change",
                    "difference",
                    "score"
                ]
            ):
                add_row(name, dataset)
            else:
                for item_name, item_data in dataset.items():
                    add_dataset(f"{name} - {item_name}", item_data)
        else:
            add_row(name, dataset)

    if "data" in asset:
        for name, dataset in asset["data"].items():
            add_dataset(name, dataset)

    if not rows and "components" in asset:
        for component, score in asset["components"].items():
            add_row(component, score)

    table = pd.DataFrame(
        rows,
        columns=["Metric", "Current", "Previous", "Change", "Score", "Bias"]
    )

    if table.empty:
        return table

    return table.drop_duplicates(
        subset=["Metric"],
        keep="first"
    )


def build_macro_indicator_table(rows):

    output = []

    for name, values in rows.items():
        if values.get("release_type") == "economic_release":
            output.append(
                {
                    "Indicator": name,
                    "Actual": values.get("actual", "N/A"),
                    "Forecast": values.get("forecast", "N/A"),
                    "Previous": values.get("previous", "N/A"),
                    "Market Surprise": values.get("market_surprise", "N/A"),
                    "Trend": values.get("trend", "N/A"),
                    "Score": values.get("score", "N/A"),
                    "Bias": values.get("bias", "Neutral"),
                    "Explanation": values.get("explanation", "N/A")
                }
            )
        else:
            output.append(
                {
                    "Indicator": name,
                    "Current": values.get("current", "N/A"),
                    "Previous": values.get("previous", "N/A"),
                    "Change": values.get("change", "N/A"),
                    "Direction Score": values.get("direction_score", values.get("score", "N/A")),
                    "Momentum Score": values.get("momentum_score", "N/A"),
                    "Score": values.get("final_score", values.get("score", "N/A")),
                    "Bias": values.get("bias", "Neutral"),
                    "Trend": values.get("explanation", values.get("status_label", "Neutral"))
                }
            )

    return pd.DataFrame(output).astype(str)


def style_macro_table(table):

    def status_color(value):
        if value == "GREEN":
            return "background-color: #14532D; color: #DCFCE7; font-weight: 800;"
        if value == "RED":
            return "background-color: #7F1D1D; color: #FEE2E2; font-weight: 800;"
        return "background-color: #713F12; color: #FEF3C7; font-weight: 800;"

    if "Status Indicator" in table.columns:
        return table.style.map(
            status_color,
            subset=["Status Indicator"]
        )

    return table.style


def show_macro_category(category_name):

    score = macro["scores"][category_name]

    st.subheader(f"{category_name} Score: {score:.2f}")
    st.dataframe(
        style_macro_table(
            build_macro_indicator_table(
                macro["categories"][category_name]
            )
        ),
        width="stretch",
        hide_index=True
    )


def show_asset_metrics():

    st.subheader("Asset Intelligence")

    row1 = st.columns(3)
    row1[0].metric("Bitcoin", f"{bitcoin['score']:.2f}", bitcoin["outlook"])
    row1[1].metric("S&P 500", f"{sp500['score']:.2f}", sp500["outlook"])
    row1[2].metric("Nasdaq", f"{nasdaq['score']:.2f}", nasdaq["outlook"])

    row2 = st.columns(3)
    row2[0].metric("Gold", f"{gold['score']:.2f}", gold["outlook"])
    row2[1].metric("Dollar", f"{dollar['score']:.2f}", dollar["outlook"])
    row2[2].metric("Bonds", f"{bonds['score']:.2f}", bonds["outlook"])
    
def style_calendar_table(table):

    def status_color(value):
        if value == "Released":
            return "background-color: #14532D; color: #DCFCE7; font-weight: 800;"
        return "background-color: #713F12; color: #FEF3C7; font-weight: 800;"

    return table.style.map(
        status_color,
        subset=["Status"]
    )


def score_to_signal(score):

    if score >= 75:
        return "Very Bullish"
    if score >= 60:
        return "Bullish"
    if score >= 45:
        return "Neutral"
    if score >= 30:
        return "Bearish"
    return "Very Bearish"


def score_to_edgefinder(score):

    return round(
        ((score - 50) / 10),
        1
    )


def signal_class(signal):

    signal = str(signal)

    if signal == "Very Bullish":
        return "score-very-bullish"
    if "Bullish" in signal:
        return "score-bullish"
    if signal == "Very Bearish":
        return "score-very-bearish"
    if "Bearish" in signal:
        return "score-bearish"
    return "score-neutral"


def clean_outlook(outlook):

    outlook = str(outlook)

    for signal in [
        "Very Bullish",
        "Bullish",
        "Neutral",
        "Bearish",
        "Very Bearish"
    ]:
        if signal.upper() in outlook.upper():
            return signal

    return outlook


ASSET_MODELS = {
    "Gold": [
        ("Real Yield", 28),
        ("Liquidity", 24),
        ("USD", 16),
        ("Inflation", 8),
        ("Risk Sentiment", 4),
        ("Institutional", 20)
    ],
    "Bitcoin": [
        ("Liquidity", 21),
        ("Global Liquidity", 18),
        ("USD", 10),
        ("Real Yield", 10),
        ("Sentiment", 11),
        ("Institutional", 30)
    ],
    "SP500": [
        ("Growth", 21),
        ("Liquidity", 17),
        ("Labor", 12),
        ("Credit", 13),
        ("Inflation", 8),
        ("Housing", 4),
        ("Retail Sentiment", 10),
        ("Institutional", 15)
    ],
    "Nasdaq": [
        ("Liquidity", 22),
        ("Real Yield", 22),
        ("Growth", 13),
        ("Credit", 9),
        ("Inflation", 9),
        ("Retail Sentiment", 10),
        ("Institutional", 15)
    ],
    "Dollar": [
        ("Rates", 28),
        ("Growth", 20),
        ("Inflation", 12),
        ("Labor", 12),
        ("Sentiment", 8),
        ("Institutional", 20)
    ],
    "Bonds": [
        ("Rates", 28),
        ("Inflation", 24),
        ("Recession", 16),
        ("Growth", 12),
        ("Institutional", 20)
    ]
}


TOOLTIP_LIBRARY = {
    "Liquidity": {
        "what_it_is": "Tracks money supply, central-bank balance-sheet liquidity, reserves, and funding conditions.",
        "why_it_matters": "More liquidity usually makes capital easier to deploy into financial assets.",
        "asset_impact": "Expanding liquidity is generally supportive for risk assets, Gold, and Bitcoin."
    },
    "Global Liquidity": {
        "what_it_is": "Combines broad money, Federal Reserve liquidity, and dollar pressure.",
        "why_it_matters": "Global liquidity shapes the amount of capital available for speculative assets.",
        "asset_impact": "Improving global liquidity is typically bullish for Bitcoin and growth assets."
    },
    "USD": {
        "what_it_is": "Measures the strength of the US Dollar against major currencies.",
        "why_it_matters": "A stronger dollar tightens global financial conditions.",
        "asset_impact": "Dollar weakness is usually supportive for Gold, Bitcoin, and risk assets."
    },
    "Inflation": {
        "what_it_is": "Measures changes in consumer and producer prices.",
        "why_it_matters": "Inflation affects purchasing power, margins, policy expectations, and real returns.",
        "asset_impact": "Lower inflation supports equities and bonds, while higher inflation can support Gold."
    },
    "Real Yield": {
        "what_it_is": "Inflation-adjusted return on US Treasury bonds.",
        "why_it_matters": "Higher real yields increase the appeal of holding bonds over non-yielding assets.",
        "asset_impact": "Falling real yields are generally bullish for Gold, Bitcoin, and Nasdaq."
    },
    "Risk Sentiment": {
        "what_it_is": "Measures market risk appetite using volatility and financial-condition inputs.",
        "why_it_matters": "Risk appetite changes how much investors pay for defensive or speculative assets.",
        "asset_impact": "Calmer risk conditions support cyclical assets; stress can support defensive Gold demand."
    },
    "Institutional": {
        "what_it_is": "Tracks noncommercial futures positioning from the CFTC Commitment of Traders report.",
        "why_it_matters": "Large speculative positioning shows whether institutions are accumulating or distributing exposure.",
        "asset_impact": "Higher long exposure is treated as more supportive for the selected asset."
    },
    "Retail Sentiment": {
        "what_it_is": "Measures risk appetite using sentiment and volatility inputs.",
        "why_it_matters": "Retail and market sentiment can amplify or soften institutional positioning.",
        "asset_impact": "Stronger sentiment is generally supportive for equity-index assets."
    },
    "Sentiment": {
        "what_it_is": "Measures market risk appetite using volatility and confidence indicators.",
        "why_it_matters": "Investor confidence affects positioning, liquidity demand, and valuation multiples.",
        "asset_impact": "Better sentiment is generally supportive for Bitcoin, equities, and Nasdaq."
    },
    "Growth": {
        "what_it_is": "Measures the pace of economic activity and demand.",
        "why_it_matters": "Stronger growth usually improves revenue, earnings, and credit quality.",
        "asset_impact": "Stronger growth supports equities and the Dollar; weaker growth supports bonds."
    },
    "Labor": {
        "what_it_is": "Measures employment, unemployment, claims, and labor-market participation.",
        "why_it_matters": "Labor strength signals household income, demand, and recession risk.",
        "asset_impact": "A resilient labor market generally supports equities and the Dollar."
    },
    "Credit": {
        "what_it_is": "Measures stress in corporate borrowing markets.",
        "why_it_matters": "Credit spreads show how easily companies can borrow and refinance.",
        "asset_impact": "Tighter credit spreads are usually bullish for equities and Nasdaq."
    },
    "Housing": {
        "what_it_is": "Measures construction activity, home sales, prices, and mortgage pressure.",
        "why_it_matters": "Housing is a major transmission channel for rates and consumer wealth.",
        "asset_impact": "A healthier housing market generally supports the SP500."
    },
    "Rates": {
        "what_it_is": "Tracks policy rates, Treasury yields, real yields, and curve shape.",
        "why_it_matters": "Rates influence discount rates, financing costs, and currency carry.",
        "asset_impact": "Lower rates support bonds; higher relative rates can support the Dollar."
    },
    "Recession": {
        "what_it_is": "Measures recession pressure through curve, labor, claims, and credit stress.",
        "why_it_matters": "Recession risk changes demand for safety and duration.",
        "asset_impact": "Rising recession risk is generally supportive for high-quality bonds."
    },
    "M2": {
        "what_it_is": "Measures total money circulating throughout the economy.",
        "why_it_matters": "Higher liquidity generally supports asset prices.",
        "asset_impact": "Expanding money supply is typically supportive for liquidity-sensitive assets."
    },
    "WALCL": {
        "what_it_is": "Measures the size of the Federal Reserve balance sheet.",
        "why_it_matters": "A larger balance sheet usually increases system liquidity.",
        "asset_impact": "Expansion is generally supportive for financial assets."
    },
    "Bank Reserves": {
        "what_it_is": "Measures bank reserve balances held at the Federal Reserve.",
        "why_it_matters": "Higher reserves can improve funding conditions.",
        "asset_impact": "Rising reserves are generally supportive for liquidity-sensitive assets."
    },
    "Reverse Repo": {
        "what_it_is": "Measures cash parked at the Fed reverse repo facility.",
        "why_it_matters": "Falling reverse repo can release liquidity into markets.",
        "asset_impact": "Declining usage is typically supportive for risk assets."
    },
    "CPI MoM": {
        "what_it_is": "Measures monthly inflation experienced by consumers.",
        "why_it_matters": "Monthly inflation helps shape near-term Fed expectations.",
        "asset_impact": "Higher inflation may support Gold but pressure equities and bonds."
    },
    "Core CPI MoM": {
        "what_it_is": "Measures monthly consumer inflation excluding food and energy.",
        "why_it_matters": "Core inflation is closely watched for policy persistence.",
        "asset_impact": "Cooling core inflation supports equities and bonds."
    },
    "PCE MoM": {
        "what_it_is": "Measures monthly inflation in consumer expenditures.",
        "why_it_matters": "PCE is a preferred Federal Reserve inflation gauge.",
        "asset_impact": "Cooling PCE usually supports duration and risk assets."
    },
    "Core PCE MoM": {
        "what_it_is": "Measures monthly PCE inflation excluding food and energy.",
        "why_it_matters": "Core PCE helps assess persistent inflation pressure.",
        "asset_impact": "Lower core PCE is generally supportive for equities and bonds."
    },
    "GDP QoQ Annualized": {
        "what_it_is": "Measures quarterly economic growth at an annualized rate.",
        "why_it_matters": "Growth drives earnings, employment, and policy expectations.",
        "asset_impact": "Stronger growth generally supports corporate earnings."
    },
    "Non-Farm Payroll Change": {
        "what_it_is": "Measures monthly job creation in the US economy.",
        "why_it_matters": "Payrolls show labor-market momentum and household income support.",
        "asset_impact": "Strong labor markets typically support economic growth."
    },
    "USD Index": {
        "what_it_is": "Measures the strength of the US Dollar against major currencies.",
        "why_it_matters": "Dollar strength affects liquidity, commodities, and global funding.",
        "asset_impact": "A stronger dollar usually pressures Gold and Bitcoin."
    },
    "10Y Real Yield": {
        "what_it_is": "Inflation-adjusted return on 10-year US Treasury bonds.",
        "why_it_matters": "Higher real yields raise the opportunity cost of non-yielding assets.",
        "asset_impact": "Rising real yields are generally bearish for Gold and Nasdaq."
    },
    "VIX": {
        "what_it_is": "Measures expected equity-market volatility.",
        "why_it_matters": "Higher volatility usually signals investor stress.",
        "asset_impact": "Lower volatility is typically supportive for risk assets."
    }
}


INDICATOR_LABELS = {
    "USD": "USD",
    "SP500": "S&P 500",
    "CFTC_POSITIONING": "CFTC Positioning",
    "BANK_RESERVES": "Bank Reserves",
    "RRP": "Reverse Repo",
    "USD_INDEX": "USD Index",
    "TEN_YEAR_REAL_YIELD_LEVEL": "10Y Real Yield",
    "FED_FUNDS_RATE_LEVEL": "Fed Funds Rate",
    "TEN_YEAR_YIELD_LEVEL": "10Y Treasury Yield",
    "TWO_YEAR_YIELD_LEVEL": "2Y Treasury Yield",
    "YIELD_CURVE_10Y_2Y": "10Y-2Y Yield Curve",
    "CORE_CPI_MOM": "Core CPI MoM",
    "CPI_MOM": "CPI MoM",
    "CORE_PCE_MOM": "Core PCE MoM",
    "PCE_MOM": "PCE MoM",
    "PPI_MOM": "PPI MoM",
    "CORE_PPI_MOM": "Core PPI MoM",
    "CPI_YOY": "CPI YoY",
    "CORE_CPI_YOY": "Core CPI YoY",
    "GDP_QOQ_ANNUALIZED": "GDP QoQ Annualized",
    "GDP_YOY": "GDP YoY",
    "RETAIL_SALES_MOM": "Retail Sales MoM",
    "INDUSTRIAL_PRODUCTION_MOM": "Industrial Production MoM",
    "DURABLE_GOODS_ORDERS_MOM": "Durable Goods Orders MoM",
    "FACTORY_ORDERS_MOM": "Factory Orders MoM",
    "NON_FARM_PAYROLL_CHANGE": "Non-Farm Payroll Change",
    "INITIAL_CLAIMS_WEEKLY_CHANGE": "Initial Claims Weekly Change",
    "CONTINUING_CLAIMS_WEEKLY_CHANGE": "Continuing Claims Weekly Change",
    "UNEMPLOYMENT_RATE": "Unemployment Rate",
    "LABOR_PARTICIPATION_RATE": "Labor Participation Rate",
    "HY_SPREAD_LEVEL": "High Yield Spread",
    "IG_SPREAD_LEVEL": "Investment Grade Spread",
    "TED_SPREAD_LEVEL": "TED Spread",
    "VIX_LEVEL": "VIX",
    "CONSUMER_SENTIMENT_LEVEL": "Consumer Sentiment",
    "FINANCIAL_CONDITIONS_INDEX_LEVEL": "Financial Conditions Index",
    "HOUSING_STARTS_MOM": "Housing Starts MoM",
    "BUILDING_PERMITS_MOM": "Building Permits MoM",
    "NEW_HOME_SALES_MOM": "New Home Sales MoM",
    "EXISTING_HOME_SALES_MOM": "Existing Home Sales MoM",
    "CASE_SHILLER_YOY": "Case-Shiller YoY",
    "MORTGAGE_RATE_LEVEL": "Mortgage Rate",
    "YIELD_CURVE": "Yield Curve"
}


def humanize_indicator_name(name):

    if name in INDICATOR_LABELS:
        return INDICATOR_LABELS[name]

    return str(name).replace("_", " ").title()


def tooltip_label(name):

    label = humanize_indicator_name(name)
    tooltip = TOOLTIP_LIBRARY.get(
        label,
        TOOLTIP_LIBRARY.get(name, {})
    )

    if not tooltip:
        tooltip = {
            "what_it_is": f"Measures the {label.lower()} macro signal.",
            "why_it_matters": "It helps explain the current asset score.",
            "asset_impact": "Stronger scores are interpreted as more supportive for the selected asset."
        }

    return f"""
    <span class="tc-tooltip-wrap">
        <span>{escape(label)}</span>
        <span class="tc-info-icon">&#9432;</span>
        <span class="tc-tooltip">
            <b>What it is:</b> {escape(tooltip["what_it_is"])}<br>
            <b>Why it matters:</b> {escape(tooltip["why_it_matters"])}<br>
            <b>Asset impact:</b> {escape(tooltip["asset_impact"])}
        </span>
    </span>
    """


def format_value(value):

    if value in [None, ""]:
        return ""

    if isinstance(value, float):
        return f"{value:.2f}"

    return str(value)


def invert_score(score):

    return round(100 - score, 2)


def get_driver_score(asset_name, driver):

    score_map = {
        "Liquidity": engines["liquidity"]["score"],
        "Global Liquidity": engines["global_liquidity"]["score"],
        "USD": engines["global_liquidity"]["data"]["USD_INDEX"]["score"],
        "Real Yield": engines["rates"]["data"]["TEN_YEAR_REAL_YIELD_LEVEL"]["score"],
        "Risk Sentiment": engines["sentiment"]["score"],
        "Sentiment": engines["sentiment"]["score"],
        "Retail Sentiment": engines["sentiment"]["score"],
        "Growth": engines["growth"]["score"],
        "Labor": engines["labor"]["score"],
        "Credit": engines["credit"]["score"],
        "Housing": engines["housing"]["score"],
        "Rates": engines["rates"]["score"],
        "Inflation": engines["inflation"]["score"],
        "Recession": engines["recession"]["score"],
        "Institutional": engines["institutional"]["assets"][asset_name]["score"]
    }

    score = score_map[driver]

    if asset_name == "Gold" and driver == "Inflation":
        return invert_score(score)
    if asset_name == "Dollar" and driver in ["Rates", "Inflation", "Sentiment"]:
        return invert_score(score)
    if asset_name == "Bonds" and driver in ["Growth", "Recession"]:
        return invert_score(score)

    return round(score, 2)


def build_asset_driver_frame(asset_name):

    rows = []

    for driver, weight in ASSET_MODELS[asset_name]:
        score = get_driver_score(asset_name, driver)
        rows.append(
            {
                "Driver": driver,
                "Weight": weight,
                "Score": score,
                "Bias": score_to_signal(score),
                "Contribution": round(score * weight / 100, 2)
            }
        )

    return pd.DataFrame(rows)


def build_asset_model(asset_name):

    drivers = build_asset_driver_frame(asset_name)
    final_score = round(drivers["Contribution"].sum(), 2)
    outlook = score_to_signal(final_score)

    return {
        "drivers": drivers,
        "score": final_score,
        "outlook": outlook,
        "positive": drivers.sort_values("Contribution", ascending=False).iloc[0],
        "negative": drivers.assign(
            Drag=lambda table: table["Weight"] * (100 - table["Score"]) / 100
        ).sort_values("Drag", ascending=False).iloc[0],
        "least": drivers.sort_values("Contribution").iloc[0]
    }


def signed_number(value, decimals=1):

    return f"{value:+.{decimals}f}"


def format_contracts(value, signed=True):

    value = int(value)
    sign = "+" if signed and value > 0 else "-" if value < 0 else ""
    absolute = abs(value)

    if absolute >= 1_000_000:
        return f"{sign}{absolute / 1_000_000:.1f}M Contracts"
    if absolute >= 1_000:
        return f"{sign}{absolute / 1_000:.0f}K Contracts"
    return f"{sign}{absolute} Contracts"


def driver_tone(score):

    if score >= 60:
        return "supportive"
    if score <= 40:
        return "a headwind"
    return "neutral"


def score_direction_sentence(subject, previous_score, current_score):

    if previous_score is None:
        return f"{subject} is currently at {current_score:.2f} with no prior comparable score in the saved history."

    delta = current_score - previous_score

    if delta > 0.01:
        return f"{subject} improved from {previous_score:.2f} to {current_score:.2f}, a {delta:+.2f} point move."
    if delta < -0.01:
        return f"{subject} weakened from {previous_score:.2f} to {current_score:.2f}, a {delta:+.2f} point move."

    return f"{subject} is essentially unchanged at {current_score:.2f} versus {previous_score:.2f} previously."


def change_direction_phrase(change):

    if change > 0.01:
        return f"rose {change:+.2f}"
    if change < -0.01:
        return f"fell {change:+.2f}"
    return f"changed {change:+.2f}"


def contribution_card_class(score):

    if score >= 60:
        return "positive"
    if score <= 40:
        return "negative"
    return "neutral"


def row_class_from_bias(bias):

    return signal_class(bias).replace("score-", "tc-row-")


def render_html_table(rows, columns, classes="tc-table"):

    header = "".join(f"<th>{column}</th>" for column in columns)
    body = []

    for row in rows:
        row_class = row.get("_class", "")
        cells = "".join(f"<td>{row.get(column, '')}</td>" for column in columns)
        body.append(f"<tr class='{row_class}'>{cells}</tr>")

    render_html(
        f"""
        <div class="tc-table-wrap">
            <table class="{classes}">
                <thead><tr>{header}</tr></thead>
                <tbody>{''.join(body)}</tbody>
            </table>
        </div>
        """
    )


def render_driver_cards(drivers):

    cards = []

    for _, row in drivers.iterrows():
        bias = row["Bias"]
        cards.append(
            f"""
            <div class="tc-driver-card">
                <div class="tc-driver-name">{tooltip_label(row["Driver"])}</div>
                <div class="tc-driver-score">{row["Score"]:.0f}</div>
                <div class="{signal_class(bias)} tc-driver-badge">{escape(str(bias))}</div>
            </div>
            """
        )

    render_html(
        f"""
        <div class="tc-driver-grid">
            {''.join(cards)}
        </div>
        """
    )


def render_asset_header(asset_name, model):

    score = model["score"]
    outlook = model["outlook"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    render_html(
        f"""
        <div class="tc-asset-hero">
            <div>
                <div class="tc-kicker">Asset Intelligence</div>
                <h1>{escape(asset_name.upper())} INTELLIGENCE</h1>
                <div class="tc-hero-subtitle">Major macro drivers, weighted contribution, and explainable score logic.</div>
            </div>
            <div class="tc-score-tile">
                <div class="tc-score-topline">
                    <span>Asset Score</span>
                    <span class="{signal_class(outlook)} tc-outlook-pill">{outlook}</span>
                </div>
                <div class="tc-score-big">{score:.0f}</div>
                <div class="tc-score-meta">
                    <span>Outlook: <b>{escape(outlook)}</b></span>
                    <span>Last Updated: <b>{timestamp}</b></span>
                </div>
            </div>
        </div>
        """
    )


def render_contribution_analysis(model):

    drivers = model["drivers"]
    rows = []

    for _, row in drivers.iterrows():
        rows.append(
            {
                "_class": row_class_from_bias(row["Bias"]),
                "Driver": tooltip_label(row["Driver"]),
                "Weight": f"{row['Weight']:.0f}%",
                "Score": f"{row['Score']:.0f}",
                "Contribution": f"{row['Contribution']:.1f}"
            }
        )

    render_html_table(
        rows,
        ["Driver", "Weight", "Score", "Contribution"]
    )

    positive = model["positive"]
    negative = model["negative"]
    least = model["least"]
    driver_count = len(drivers)
    supportive_count = len(drivers[drivers["Score"] >= 60])
    headwind_count = len(drivers[drivers["Score"] <= 40])
    negative_drag = negative["Weight"] * (100 - negative["Score"]) / 100
    least_tone = driver_tone(least["Score"])
    positive_tone = driver_tone(positive["Score"])
    supportive_label = "supportive driver" if supportive_count == 1 else "supportive drivers"
    headwind_label = "headwind driver" if headwind_count == 1 else "headwind drivers"
    final_detail = (
        f"{supportive_count} {supportive_label} and {headwind_count} "
        f"{headwind_label} across {driver_count} inputs"
    )

    render_html(
        f"""
        <div class="tc-contributor-grid">
            <div class="tc-contributor-card {contribution_card_class(model["score"])}">
                <div>Final Asset Score</div>
                <strong>{model["score"]:.1f}</strong>
                <span>{escape(final_detail)}</span>
            </div>
            <div class="tc-contributor-card {contribution_card_class(positive["Score"])}">
                <div>Largest Score Contributor</div>
                <strong>{escape(positive["Driver"])} {signed_number(positive["Contribution"])}</strong>
                <span>{positive["Weight"]:.0f}% weight, {positive["Score"]:.0f} score, currently {escape(positive_tone)}</span>
            </div>
            <div class="tc-contributor-card {contribution_card_class(negative["Score"])}">
                <div>Largest Headwind</div>
                <strong>{escape(negative["Driver"])}</strong>
                <span>{negative["Score"]:.0f} score creates {negative_drag:.1f} points of weighted drag</span>
            </div>
            <div class="tc-contributor-card {contribution_card_class(least["Score"])}">
                <div>Smallest Contribution</div>
                <strong>{escape(least["Driver"])} {signed_number(least["Contribution"])}</strong>
                <span>{least["Weight"]:.0f}% weight and {least["Score"]:.0f} score, currently {escape(least_tone)}</span>
            </div>
        </div>
        """
    )


def generate_executive_summary(asset_name, model):

    drivers = model["drivers"].sort_values("Contribution", ascending=False)
    supportive = drivers[drivers["Score"] >= 60]["Driver"].tolist()
    headwinds = drivers[drivers["Score"] < 45]["Driver"].tolist()
    top = model["positive"]["Driver"]
    negative = model["negative"]["Driver"]
    outlook_phrase = {
        "Very Bullish": "strongly supportive",
        "Bullish": "supportive",
        "Neutral": "balanced",
        "Bearish": "challenging",
        "Very Bearish": "strongly challenging"
    }.get(model["outlook"], "balanced")

    support_text = (
        f"{asset_name} is receiving support from {', '.join(supportive[:2])}."
        if supportive else
        f"{asset_name} has limited outright supportive macro drivers at the moment."
    )
    headwind_text = (
        f"However, {', '.join(headwinds[:2])} continue to create headwinds."
        if headwinds else
        f"The model is not showing a major bearish driver cluster right now."
    )
    total_text = (
        f"Overall macro conditions are {outlook_phrase} with {top} contributing most and {negative} acting as the key drag."
    )

    return [support_text, headwind_text, total_text]


def render_executive_summary(asset_name, model):

    lines = generate_executive_summary(asset_name, model)
    render_html(
        f"""
        <div class="tc-summary-box">
            <p>{escape(lines[0])}</p>
            <p>{escape(lines[1])}</p>
            <p>{escape(lines[2])}</p>
        </div>
        """
    )


def render_radar_chart(drivers):

    size = 360
    center = size / 2
    radius = 128
    labels = drivers["Driver"].tolist()
    scores = drivers["Score"].tolist()
    count = len(labels)

    def point(index, value):
        angle = (2 * pi * index / count) - (pi / 2)
        scaled = radius * (value / 100)
        return (
            center + cos(angle) * scaled,
            center + sin(angle) * scaled
        )

    rings = []
    for value in [25, 50, 75, 100]:
        points = " ".join(f"{x:.1f},{y:.1f}" for x, y in [point(i, value) for i in range(count)])
        rings.append(f"<polygon points='{points}' class='tc-radar-ring' />")

    axes = []
    label_nodes = []
    for index, label in enumerate(labels):
        x, y = point(index, 100)
        axes.append(f"<line x1='{center}' y1='{center}' x2='{x:.1f}' y2='{y:.1f}' class='tc-radar-axis' />")
        lx, ly = point(index, 116)
        label_nodes.append(
            f"<text x='{lx:.1f}' y='{ly:.1f}' text-anchor='middle' class='tc-radar-label'>{escape(label)}</text>"
        )

    score_points = " ".join(f"{x:.1f},{y:.1f}" for x, y in [point(i, scores[i]) for i in range(count)])

    render_unsafe_html(
        f"""
        <div class="tc-chart-panel">
            <svg viewBox="0 0 {size} {size}" class="tc-radar">
                {''.join(rings)}
                {''.join(axes)}
                <polygon points="{score_points}" class="tc-radar-score" />
                {''.join(label_nodes)}
            </svg>
        </div>
        """
    )


def build_asset_score_history(asset_name, model):

    if not HISTORY_PATH.exists():
        return pd.DataFrame(
            {
                "Date": [datetime.now()],
                "Score": [model["score"]]
            }
        ).set_index("Date")

    history = pd.read_csv(HISTORY_PATH)

    if "date" not in history.columns:
        return pd.DataFrame(
            {
                "Date": [datetime.now()],
                "Score": [model["score"]]
            }
        ).set_index("Date")

    model_map = {
        "Liquidity": "liquidity",
        "Rates": "rates",
        "Inflation": "inflation",
        "Growth": "growth",
        "Labor": "labor"
    }
    rows = []

    for _, item in history.tail(40).iterrows():
        total = 0
        for driver, weight in ASSET_MODELS[asset_name]:
            column = model_map.get(driver)
            if column and column in history.columns:
                score = adjust_asset_driver_score(
                    asset_name,
                    driver,
                    numeric_or_none(item[column])
                )
            else:
                score = get_driver_score(asset_name, driver)
            if score is None:
                score = get_driver_score(asset_name, driver)
            total += score * weight / 100
        rows.append({"Date": item["date"], "Score": round(total, 2)})

    frame = pd.DataFrame(rows)
    frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce")
    frame["Score"] = pd.to_numeric(frame["Score"], errors="coerce")
    frame = frame.dropna(subset=["Date", "Score"])

    if frame.empty:
        frame = pd.DataFrame(
            {
                "Date": [datetime.now()],
                "Score": [model["score"]]
            }
        )
    else:
        frame = pd.concat(
            [
                frame,
                pd.DataFrame(
                    [
                        {
                            "Date": datetime.now(),
                            "Score": model["score"]
                        }
                    ]
                )
            ],
            ignore_index=True
        )

    return frame.drop_duplicates(subset=["Date"], keep="last").set_index("Date")


def get_raw_driver_data(asset_name, driver):

    source_map = {
        "Liquidity": engines["liquidity"]["data"],
        "Global Liquidity": engines["global_liquidity"]["data"],
        "USD": {"USD_INDEX": engines["global_liquidity"]["data"]["USD_INDEX"]},
        "Real Yield": {"TEN_YEAR_REAL_YIELD_LEVEL": engines["rates"]["data"]["TEN_YEAR_REAL_YIELD_LEVEL"]},
        "Risk Sentiment": engines["sentiment"]["data"],
        "Sentiment": engines["sentiment"]["data"],
        "Retail Sentiment": engines["sentiment"]["data"],
        "Growth": engines["growth"]["data"],
        "Labor": engines["labor"]["data"],
        "Credit": engines["credit"]["data"],
        "Housing": engines["housing"]["data"],
        "Rates": engines["rates"]["data"],
        "Inflation": engines["inflation"]["data"],
        "Recession": engines["recession"]["data"],
        "Institutional": {
            "CFTC_POSITIONING": {
                "current": engines["institutional"]["assets"][asset_name]["net_position"],
                "previous": (
                    engines["institutional"]["assets"][asset_name]["net_position"]
                    - engines["institutional"]["assets"][asset_name]["weekly_change"]
                ),
                "change": engines["institutional"]["assets"][asset_name]["weekly_change"],
                "score": engines["institutional"]["assets"][asset_name]["score"],
                "bias": engines["institutional"]["assets"][asset_name]["bias"],
                "last_update": engines["institutional"]["assets"][asset_name]["last_updated"]
            }
        }
    }

    rows = []

    for indicator, values in source_map.get(driver, {}).items():
        if not isinstance(values, dict):
            continue

        rows.append(
            {
                "Indicator": humanize_indicator_name(indicator),
                "Current": format_value(values.get("current", "N/A")),
                "Previous": format_value(values.get("previous", values.get("old", "N/A"))),
                "Change": format_value(values.get("change", values.get("difference", "N/A"))),
                "Score": format_value(values.get("score", "N/A")),
                "Bias": clean_outlook(values.get("bias", "Neutral")),
                "_class": row_class_from_bias(clean_outlook(values.get("bias", "Neutral")))
            }
        )

    return rows


def asset_history_driver_column(driver):

    return {
        "Liquidity": "liquidity",
        "Rates": "rates",
        "Inflation": "inflation",
        "Growth": "growth",
        "Labor": "labor"
    }.get(driver)


def adjust_asset_driver_score(asset_name, driver, score):

    if score is None:
        return None

    if asset_name == "Gold" and driver == "Inflation":
        return 100 - score
    if asset_name == "Dollar" and driver in ["Rates", "Inflation", "Sentiment"]:
        return 100 - score
    if asset_name == "Bonds" and driver in ["Growth", "Recession"]:
        return 100 - score

    return score


def asset_score_from_history_row(asset_name, item):

    total = 0

    for driver, weight in ASSET_MODELS[asset_name]:
        column = asset_history_driver_column(driver)
        score = None

        if column and column in item:
            score = numeric_or_none(item[column])
            score = adjust_asset_driver_score(asset_name, driver, score)

        if score is None:
            score = get_driver_score(asset_name, driver)

        total += score * weight / 100

    return round(total, 2)


def get_previous_asset_score(asset_name, current_score):

    path = Path("dashboard_history.csv")

    if not path.exists():
        return None

    history = pd.read_csv(path)

    if history.empty:
        return None

    scores = [
        asset_score_from_history_row(asset_name, row)
        for _, row in history.iterrows()
    ]

    return latest_different_score(scores, current_score)


def find_asset_previous_driver_scores(asset_name):

    path = Path("dashboard_history.csv")

    if not path.exists():
        return {}

    history = pd.read_csv(path)

    if history.empty:
        return {}

    latest = history.iloc[-1]
    previous_scores = {}

    for driver, _ in ASSET_MODELS[asset_name]:
        column = asset_history_driver_column(driver)

        if not column or column not in history.columns:
            continue

        current_driver_score = get_driver_score(asset_name, driver)
        history_score = None

        for _, row in history.iloc[::-1].iterrows():
            candidate = numeric_or_none(row.get(column))
            candidate = adjust_asset_driver_score(asset_name, driver, candidate)

            if candidate is None:
                continue

            if abs(candidate - current_driver_score) > 0.005:
                history_score = candidate
                break

        if history_score is None:
            candidate = numeric_or_none(latest.get(column))
            history_score = adjust_asset_driver_score(asset_name, driver, candidate)

        if history_score is not None:
            previous_scores[driver] = history_score

    return previous_scores


def describe_asset_score_moves(asset_name, drivers, limit=3):

    previous_driver_scores = find_asset_previous_driver_scores(asset_name)
    moves = []

    for _, row in drivers.iterrows():
        driver = row["Driver"]
        previous_score = previous_driver_scores.get(driver)

        if previous_score is None:
            continue

        contribution_change = (
            row["Score"] - previous_score
        ) * row["Weight"] / 100
        moves.append(
            {
                "indicator": f"{driver} contribution",
                "change": contribution_change,
                "score": row["Score"]
            }
        )

    moves = sorted(
        moves,
        key=lambda item: abs(item["change"]),
        reverse=True
    )

    if moves:
        return moves[:limit]

    current_data_moves = []

    for driver in drivers["Driver"]:
        current_data_moves.extend(describe_indicator_moves(get_raw_driver_data(asset_name, driver), 1))

    return sorted(
        current_data_moves,
        key=lambda item: abs(item["change"]),
        reverse=True
    )[:limit]


def render_asset_change_explanation(asset_name, model):

    previous_score = get_previous_asset_score(asset_name, model["score"])
    moves = describe_asset_score_moves(asset_name, model["drivers"])
    score_sentence = score_direction_sentence(
        f"{asset_name} score",
        previous_score,
        model["score"]
    )

    if moves:
        top_move = moves[0]
        if "contribution" in top_move["indicator"].lower():
            move_phrase = change_direction_phrase(top_move["change"])
            summary = (
                f"{score_sentence} The biggest weighted score change was "
                f"{top_move['indicator']}, which {move_phrase} points in the final model."
            )
        else:
            move_phrase = change_direction_phrase(top_move["change"])
            summary = (
                f"{score_sentence} Comparable driver history is limited, "
                f"so the block highlights the biggest changed input: {top_move['indicator']} "
                f"{move_phrase}."
            )
    else:
        top_driver = model["positive"]
        top_tone = driver_tone(top_driver["Score"])
        summary = (
            f"{score_sentence} The strongest current driver is "
            f"{top_driver['Driver']} with a {top_driver['Score']:.1f} score, making it "
            f"{top_tone}; prior comparable driver history is limited."
        )

    render_score_change_block(
        f"{asset_name} Score",
        previous_score,
        model["score"],
        summary,
        moves
    )


def render_underlying_data(asset_name, drivers):

    for _, row in drivers.iterrows():
        driver = row["Driver"]
        with st.expander(f"{driver} Details", expanded=False):
            rows = get_raw_driver_data(asset_name, driver)
            if rows:
                render_html_table(
                    rows,
                    ["Indicator", "Current", "Previous", "Change", "Score", "Bias"]
                )
            else:
                st.caption("No raw indicator details available for this driver.")


def render_recent_change(asset_name, drivers):

    changes = []

    for driver in drivers["Driver"]:
        for row in get_raw_driver_data(asset_name, driver):
            try:
                change = float(row["Change"])
            except (TypeError, ValueError):
                continue
            changes.append((abs(change), row["Indicator"], change, driver))

    if not changes:
        st.caption("Recent change details are unavailable for the current feed.")
        return

    _, indicator, change, driver = sorted(changes, reverse=True)[0]

    render_html(
        f"""
        <div class="tc-change-card">
            <div class="tc-section-label">What Changed Recently</div>
            <div>{indicator}</div>
            <strong>{change:+.2f}</strong>
            <span>Largest absolute move inside the {escape(driver)} driver basket.</span>
        </div>
        """
    )


def cot_metric_label(label, description):

    return f"""
    <span class="tc-tooltip-wrap">
        <span>{escape(label)}</span>
        <span class="tc-info-icon">&#9432;</span>
        <span class="tc-tooltip">{escape(description)}</span>
    </span>
    """


def cot_bias_class(bias):

    return {
        "Very Bullish": "very-bullish",
        "Bullish": "bullish",
        "Neutral": "neutral",
        "Bearish": "bearish",
        "Very Bearish": "very-bearish"
    }.get(bias, "neutral")


def cot_interpretation(asset_name, cot):

    direction = "increasing" if cot["weekly_change"] > 0 else "reducing" if cot["weekly_change"] < 0 else "holding"
    exposure = "long exposure" if cot["long_percent"] >= cot["short_percent"] else "short exposure"
    velocity = cot["velocity_4w"]

    if velocity > 0:
        velocity_text = (
            f"Net positioning has increased by {format_contracts(velocity)} over four weeks, "
            "indicating sustained institutional accumulation."
        )
    elif velocity < 0:
        velocity_text = (
            f"Net positioning has decreased by {format_contracts(abs(velocity), signed=False)} over four weeks, "
            "indicating institutional distribution."
        )
    else:
        velocity_text = "Four-week positioning velocity is flat, indicating no clear accumulation or distribution trend."

    return (
        f"Institutions are {direction} {exposure} in {asset_name} futures. "
        f"The latest CFTC report shows {cot['long_percent']:.0f}% long exposure versus "
        f"{cot['short_percent']:.0f}% short exposure, producing a {cot['bias'].lower()} institutional bias. "
        f"{velocity_text}"
    )


def render_institutional_positioning(asset_name):

    cot = engines["institutional"]["assets"][asset_name]

    st.markdown("### Institutional Positioning")

    if st.session_state.pop("cot_updated_success", False):
        st.success("COT data updated successfully.")

    if st.button("Fetch Latest Data", key=f"cot_refresh_{asset_name}", type="secondary"):
        try:
            engines["institutional"] = build_institutional_engine(force=True)
            load_all_engines.clear()
            st.session_state.cot_updated_success = True
            st.rerun()
        except Exception as error:
            st.error(f"COT data refresh failed: {error}")

    bias_class = cot_bias_class(cot["bias"])
    long_width = max(0, min(100, cot["long_percent"]))
    short_width = max(0, min(100, cot["short_percent"]))

    render_html(
        f"""
        <div class="tc-cot-panel">
            <div class="tc-cot-head">
                <div>
                    <div class="tc-section-label">Institutional Positioning</div>
                    <h3>CFTC Commitment of Traders</h3>
                    <span>Last Updated: {escape(cot["last_updated"])}</span>
                </div>
                <div class="tc-cot-bias {bias_class}">{escape(cot["bias"])}</div>
            </div>
            <div class="tc-cot-metrics">
                <div>
                    <span>{cot_metric_label("Long Contracts", "Number of noncommercial long futures contracts reported by the CFTC.")}</span>
                    <strong>{format_contracts(cot["long_contracts"], signed=False)}</strong>
                </div>
                <div>
                    <span>{cot_metric_label("Short Contracts", "Number of noncommercial short futures contracts reported by the CFTC.")}</span>
                    <strong>{format_contracts(cot["short_contracts"], signed=False)}</strong>
                </div>
                <div>
                    <span>{cot_metric_label("Long Exposure", "Share of noncommercial futures positioning held long.")}</span>
                    <strong>{cot["long_percent"]:.0f}%</strong>
                </div>
                <div>
                    <span>{cot_metric_label("Short Exposure", "Share of noncommercial futures positioning held short.")}</span>
                    <strong>{cot["short_percent"]:.0f}%</strong>
                </div>
                <div>
                    <span>{cot_metric_label("Net Position", "Difference between institutional long and short futures positions. Positive values indicate bullish positioning.")}</span>
                    <strong>{format_contracts(cot["net_position"])}</strong>
                </div>
                <div>
                    <span>{cot_metric_label("Weekly Change", "Current net position minus the previous week's net position.")}</span>
                    <strong>{format_contracts(cot["weekly_change"])}</strong>
                </div>
                <div>
                    <span>{cot_metric_label("4 Week Velocity", "Measures how quickly institutions are increasing or decreasing exposure. Positive velocity indicates accumulation.")}</span>
                    <strong>{format_contracts(cot["velocity_4w"])}</strong>
                </div>
            </div>
            <div class="tc-cot-gauge">
                <div style="width: {long_width:.2f}%;">Long {cot["long_percent"]:.0f}%</div>
                <div style="width: {short_width:.2f}%;">Short {cot["short_percent"]:.0f}%</div>
            </div>
            <p>{escape(cot_interpretation(asset_name, cot))}</p>
        </div>
        """
    )

    trend = pd.DataFrame(cot["trend"])
    trend["Date"] = pd.to_datetime(trend["Date"])

    left, right = st.columns([1, 1])

    with left:
        st.markdown("#### Net Position Trend")
        st.line_chart(
            trend.set_index("Date")["Net Position"],
            width="stretch"
        )

    with right:
        st.markdown("#### 4 Week Velocity")
        chart = (
            alt.Chart(trend)
            .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
            .encode(
                x=alt.X("Date:T", title=None),
                y=alt.Y("4W Velocity:Q", title="Contracts"),
                color=alt.condition(
                    alt.datum["4W Velocity"] >= 0,
                    alt.value("#6DB982"),
                    alt.value("#E07A72")
                ),
                tooltip=["Date:T", "4W Velocity:Q", "Weekly Change:Q"]
            )
            .properties(height=260)
        )
        st.altair_chart(chart, use_container_width=True)


def institutional_metric_card(title, value, explanation, bias):

    return f"""
    <div class="tc-inst-metric-card">
        <div class="tc-inst-card-title">{escape(title)}</div>
        <div class="tc-inst-card-value {cot_bias_class(bias)}">{escape(str(value))}</div>
        <div class="tc-inst-card-note">{escape(explanation)}</div>
    </div>
    """


def institutional_trend_frame(asset_name, timeframe):

    trend = pd.DataFrame(engines["institutional"]["assets"][asset_name]["trend"])
    trend["Date"] = pd.to_datetime(trend["Date"])

    windows = {
        "1M": 31,
        "3M": 93,
        "6M": 186,
        "1Y": 366
    }

    if timeframe in windows and not trend.empty:
        cutoff = trend["Date"].max() - pd.Timedelta(days=windows[timeframe])
        trend = trend[trend["Date"] >= cutoff]

    return trend


def institutional_bias_color_expr():

    return alt.Scale(
        domain=["Very Bullish", "Bullish", "Neutral", "Bearish", "Very Bearish"],
        range=["#14532D", "#4D8F61", "#D4A04C", "#C95F5A", "#7F1D1D"]
    )


def render_institutional_heatmap():

    rows = []

    for asset_name in ASSET_ICONS:
        cot = engines["institutional"]["assets"][asset_name]
        rows.append(
            f"""
            <div class="tc-inst-heat-row">
                <span>{ASSET_ICONS[asset_name]} {escape(asset_name)}</span>
                <b class="tc-cot-bias {cot_bias_class(cot["bias"])}">{escape(cot["bias"])}</b>
                <strong>{format_contracts(cot["weekly_change"])}</strong>
            </div>
            """
        )

    render_html(
        f"""
        <div class="tc-inst-heatmap">
            <div class="tc-inst-heat-head">
                <span>Asset</span>
                <span>Bias</span>
                <span>Weekly Change</span>
            </div>
            {''.join(rows)}
        </div>
        """
    )


def render_position_percentile(cot):

    percentile = cot["position_percentile"]
    marker = max(0, min(100, percentile))

    if percentile >= 80:
        text = "Positioning is near the upper historical range."
    elif percentile <= 20:
        text = "Positioning is near the lower historical range."
    else:
        text = "Positioning is within the middle historical range."

    render_html(
        f"""
        <div class="tc-inst-percentile">
            <div>
                <span>Position Percentile</span>
                <strong>{percentile:.0f}%</strong>
                <p>{escape(text)}</p>
            </div>
            <div class="tc-inst-percentile-track">
                <i style="left: {marker:.2f}%;"></i>
            </div>
        </div>
        """
    )


def render_long_short_gauge(cot):

    long_width = max(0, min(100, cot["long_percent"]))
    short_width = max(0, min(100, cot["short_percent"]))

    render_html(
        f"""
        <div class="tc-inst-gauge-panel">
            <div class="tc-section-label">Long / Short Gauge</div>
            <div class="tc-cot-gauge">
                <div style="width: {long_width:.2f}%;">Long {cot["long_percent"]:.0f}%</div>
                <div style="width: {short_width:.2f}%;">Short {cot["short_percent"]:.0f}%</div>
            </div>
        </div>
        """
    )


def render_institutional_charts(asset_name, timeframe):

    trend = institutional_trend_frame(asset_name, timeframe)

    if trend.empty:
        st.caption("No COT trend data is available for the selected asset.")
        return

    net_chart = (
        alt.Chart(trend)
        .mark_line(color="#8FA3E8", strokeWidth=2)
        .encode(
            x=alt.X("Date:T", title=None),
            y=alt.Y("Net Position:Q", title="Contracts"),
            tooltip=["Date:T", "Net Position:Q", "Position Percentile:Q"]
        )
        .properties(height=260)
    )

    exposure = trend.melt(
        id_vars=["Date"],
        value_vars=["Long Exposure", "Short Exposure"],
        var_name="Side",
        value_name="Exposure"
    )
    exposure_chart = (
        alt.Chart(exposure)
        .mark_area(opacity=0.78)
        .encode(
            x=alt.X("Date:T", title=None),
            y=alt.Y("Exposure:Q", stack="normalize", title="Exposure"),
            color=alt.Color("Side:N", scale=alt.Scale(range=["#6DB982", "#E07A72"])),
            tooltip=["Date:T", "Side:N", "Exposure:Q"]
        )
        .properties(height=260)
    )

    bias_chart = (
        alt.Chart(trend)
        .mark_bar()
        .encode(
            x=alt.X("Date:T", title=None),
            y=alt.Y("Score:Q", title="Institutional Score"),
            color=alt.Color("Bias:N", scale=institutional_bias_color_expr()),
            tooltip=["Date:T", "Bias:N", "Score:Q"]
        )
        .properties(height=220)
    )

    change_chart = (
        alt.Chart(trend)
        .mark_bar()
        .encode(
            x=alt.X("Date:T", title=None),
            y=alt.Y("Weekly Change:Q", title="Contracts"),
            color=alt.condition(
                alt.datum["Weekly Change"] >= 0,
                alt.value("#6DB982"),
                alt.value("#E07A72")
            ),
            tooltip=["Date:T", "Weekly Change:Q"]
        )
        .properties(height=220)
    )

    velocity_chart = (
        alt.Chart(trend)
        .mark_line(color="#70B7FF", strokeWidth=2)
        .encode(
            x=alt.X("Date:T", title=None),
            y=alt.Y("4W Velocity:Q", title="Contracts"),
            tooltip=["Date:T", "4W Velocity:Q"]
        )
        .properties(height=220)
    )

    top_left, top_right = st.columns(2)

    with top_left:
        st.markdown("#### Net Position Trend")
        st.altair_chart(net_chart, use_container_width=True)

    with top_right:
        st.markdown("#### Long vs Short Exposure")
        st.altair_chart(exposure_chart, use_container_width=True)

    mid_left, mid_right = st.columns(2)

    with mid_left:
        st.markdown("#### Institutional Bias History")
        st.altair_chart(bias_chart, use_container_width=True)

    with mid_right:
        st.markdown("#### Weekly Position Change")
        st.altair_chart(change_chart, use_container_width=True)

    low_left, low_right = st.columns([1.1, 0.9])

    with low_left:
        st.markdown("#### 4 Week Velocity")
        st.altair_chart(velocity_chart, use_container_width=True)

    with low_right:
        st.markdown("#### Extremes")
        render_long_short_gauge(engines["institutional"]["assets"][asset_name])
        render_position_percentile(engines["institutional"]["assets"][asset_name])


def render_institutional_positioning_page():

    if st.session_state.pop("cot_updated_success", False):
        st.success("COT data updated successfully.")

    asset_names = list(ASSET_ICONS.keys())
    selected_asset = st.selectbox(
        "Select Asset",
        asset_names,
        index=asset_names.index(st.session_state.institutional_asset),
        format_func=lambda item: f"{ASSET_ICONS[item]} {item}"
    )
    st.session_state.institutional_asset = selected_asset

    cot = engines["institutional"]["assets"][selected_asset]
    updated = datetime.strptime(cot["last_updated"], "%Y-%m-%d").strftime("%b %d %Y")

    header_left, header_right = st.columns([1, 0.28])

    with header_left:
        render_html(
            f"""
            <div class="tc-inst-page-header">
                <div>
                    <div class="tc-section-label">Institutional Positioning</div>
                    <h1>{ASSET_ICONS[selected_asset]} {escape(selected_asset.upper())} INSTITUTIONAL POSITIONING</h1>
                    <span>Last Updated: {escape(updated)}</span>
                </div>
                <div class="tc-cot-bias {cot_bias_class(cot["bias"])}">{escape(cot["bias"])}</div>
            </div>
            """
        )

    with header_right:
        if st.button("Fetch Latest Data", key="cot_page_refresh", type="primary", width="stretch"):
            try:
                engines["institutional"] = build_institutional_engine(force=True)
                load_all_engines.clear()
                st.session_state.cot_updated_success = True
                st.rerun()
            except Exception as error:
                st.error(f"COT data refresh failed: {error}")

    metric_data = [
        (
            "Long Exposure %",
            f"{cot['long_percent']:.0f}%",
            "Share of institutional futures exposure held long.",
            cot["bias"]
        ),
        (
            "Short Exposure %",
            f"{cot['short_percent']:.0f}%",
            "Share of institutional futures exposure held short.",
            "Bearish" if cot["short_percent"] >= 60 else "Neutral"
        ),
        (
            "Net Position",
            format_contracts(cot["net_position"]),
            "Institutional long contracts minus short contracts.",
            cot["bias"]
        ),
        (
            "Weekly Change",
            format_contracts(cot["weekly_change"]),
            "Change in net positioning from the prior CFTC report.",
            "Bullish" if cot["weekly_change"] > 0 else "Bearish" if cot["weekly_change"] < 0 else "Neutral"
        ),
        (
            "4 Week Velocity",
            format_contracts(cot["velocity_4w"]),
            "Four-week change in institutional net positioning.",
            "Bullish" if cot["velocity_4w"] > 0 else "Bearish" if cot["velocity_4w"] < 0 else "Neutral"
        ),
        (
            "Institutional Score",
            f"{cot['score']}",
            "Bias score derived from long exposure percentage.",
            cot["bias"]
        )
    ]

    render_html(
        f"""
        <div class="tc-inst-metric-grid">
            {''.join(institutional_metric_card(*item) for item in metric_data)}
        </div>
        """
    )

    render_html(
        f"""
        <div class="tc-inst-commentary">
            {escape(cot_interpretation(selected_asset, cot))}
        </div>
        """
    )

    st.markdown("### Positioning Heatmap")
    render_institutional_heatmap()

    st.markdown("### Historical Positioning")
    timeframe = st.radio(
        "Timeframe",
        ["1M", "3M", "6M", "1Y", "ALL"],
        horizontal=True,
        index=["1M", "3M", "6M", "1Y", "ALL"].index(st.session_state.institutional_timeframe)
    )
    st.session_state.institutional_timeframe = timeframe
    render_institutional_charts(selected_asset, timeframe)


def render_asset_intelligence(asset_name, asset):

    model = build_asset_model(asset_name)

    render_asset_header(asset_name, model)
    render_asset_change_explanation(asset_name, model)

    st.markdown("### Key Drivers")
    render_driver_cards(model["drivers"])

    st.markdown("### Contribution Analysis")
    render_contribution_analysis(model)

    visual_left, visual_right = st.columns([1, 1])

    with visual_left:
        st.markdown("### Radar Chart")
        render_radar_chart(model["drivers"])

    with visual_right:
        st.markdown("### Score History")
        render_score_history_chart(
            build_asset_score_history(asset_name, model),
            f"{asset_name} Score"
        )
        render_recent_change(asset_name, model["drivers"])

    st.markdown("### Executive Summary")
    render_executive_summary(asset_name, model)

    st.markdown("### Underlying Data")
    st.caption("Raw FRED and macro inputs are available for audit, but the primary view remains driver-first.")
    render_underlying_data(asset_name, model["drivers"])


MACRO_NAV_ITEMS = (
    ("Liquidity", "Liquidity", "liquidity"),
    ("Global Liquidity", "Global Liquidity", "global_liquidity"),
    ("Rates", "Rates", "rates"),
    ("Inflation", "Inflation", "inflation"),
    ("Growth", "Growth", "growth"),
    ("Labor Market", "Labor Market", "labor"),
    ("Credit", "Credit", "credit"),
    ("Sentiment", "Sentiment", "sentiment"),
    ("Housing", "Housing", "housing"),
    ("Recession", "Recession", "recession")
)


ASSET_NAV_ITEMS = (
    ("Gold", "Gold"),
    ("Bitcoin", "Bitcoin"),
    ("SP500", "SP500"),
    ("Nasdaq", "Nasdaq"),
    ("Dollar", "Dollar"),
    ("Bonds", "Bonds")
)


ASSET_ICONS = {
    "Gold": "XAU",
    "Bitcoin": "BTC",
    "SP500": "SPX",
    "Nasdaq": "NDX",
    "Dollar": "USD",
    "Bonds": "UST"
}


MACRO_ENGINE_KEYS = {
    view_name: engine_key
    for _, view_name, engine_key in MACRO_NAV_ITEMS
}


MACRO_HISTORY_COLUMNS = {
    "Liquidity": "liquidity",
    "Rates": "rates",
    "Inflation": "inflation",
    "Growth": "growth",
    "Labor Market": "labor",
    "Macro Intelligence": "overall"
}


def build_macro_score_frame():

    rows = []

    for _, view_name, _ in MACRO_NAV_ITEMS:
        key = MACRO_ENGINE_KEYS[view_name]
        score = engines[key].get("score")

        if score is None:
            continue

        rows.append(
            {
                "Driver": view_name,
                "Score": round(score, 2),
                "Signal": score_to_signal(score)
            }
        )

    return pd.DataFrame(rows)


def build_macro_history_frame(view_name, score):

    if not HISTORY_PATH.exists():
        return pd.DataFrame(
            {
                "Date": [datetime.now()],
                "Score": [score]
            }
        ).set_index("Date")

    history = pd.read_csv(HISTORY_PATH)
    column = MACRO_HISTORY_COLUMNS.get(view_name, "overall")

    if "date" not in history.columns or column not in history.columns:
        return pd.DataFrame(
            {
                "Date": [datetime.now()],
                "Score": [score]
            }
        ).set_index("Date")

    frame = history[["date", column]].tail(40).copy()
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.dropna(subset=["date", column])

    if frame.empty:
        frame = pd.DataFrame(
            {
                "date": [datetime.now()],
                column: [score]
            }
        )
    else:
        frame = pd.concat(
            [
                frame,
                pd.DataFrame(
                    [
                        {
                            "date": datetime.now(),
                            column: score
                        }
                    ]
                )
            ],
            ignore_index=True
        )

    frame = frame.drop_duplicates(subset=["date"], keep="last")
    frame = frame.set_index("date")

    return frame.rename(columns={column: "Score"})


def render_score_history_chart(frame, label="Score"):

    chart_frame = frame.reset_index().copy()
    date_column = chart_frame.columns[0]
    chart_frame = chart_frame.rename(columns={date_column: "Date"})
    chart_frame["Date"] = pd.to_datetime(chart_frame["Date"], errors="coerce")
    chart_frame["Score"] = pd.to_numeric(chart_frame["Score"], errors="coerce")
    chart_frame = chart_frame.dropna(subset=["Date", "Score"]).tail(40)

    if chart_frame.empty:
        st.caption("No score history is available yet.")
        return

    score_min = chart_frame["Score"].min()
    score_max = chart_frame["Score"].max()
    padding = max(4, (score_max - score_min) * 0.28)
    y_min = max(0, score_min - padding)
    y_max = min(100, score_max + padding)

    if y_max - y_min < 10:
        midpoint = (y_min + y_max) / 2
        y_min = max(0, midpoint - 5)
        y_max = min(100, midpoint + 5)

    chart_frame["Point"] = "History"
    chart_frame.loc[chart_frame.index[-1], "Point"] = "Latest"

    base = alt.Chart(chart_frame).encode(
        x=alt.X(
            "Date:T",
            title=None,
            axis=alt.Axis(
                labelColor="#C6D0DF",
                labelOverlap=True,
                grid=False
            )
        ),
        y=alt.Y(
            "Score:Q",
            title=None,
            scale=alt.Scale(domain=[y_min, y_max]),
            axis=alt.Axis(
                labelColor="#C6D0DF",
                gridColor="rgba(148, 163, 184, 0.18)"
            )
        )
    )

    area = base.mark_area(
        interpolate="monotone",
        opacity=0.18,
        color="#65B7FF"
    )
    line = base.mark_line(
        interpolate="monotone",
        strokeWidth=3,
        color="#73C4FF"
    )
    points = base.mark_circle(size=70).encode(
        color=alt.Color(
            "Point:N",
            scale=alt.Scale(
                domain=["History", "Latest"],
                range=["#73C4FF", "#F7D774"]
            ),
            legend=None
        ),
        tooltip=[
            alt.Tooltip("Date:T", title="Time", format="%b %d, %Y %I:%M %p"),
            alt.Tooltip("Score:Q", title=label, format=".2f")
        ]
    )

    latest = chart_frame.iloc[-1]
    rule = alt.Chart(pd.DataFrame([latest])).mark_rule(
        color="#F7D774",
        strokeDash=[4, 4],
        opacity=0.65
    ).encode(y="Score:Q")

    chart = (
        (area + line + points + rule)
        .properties(height=260)
        .configure_view(stroke="rgba(148, 163, 184, 0.34)")
        .configure_axis(domain=False, tickColor="rgba(148, 163, 184, 0.32)")
    )

    st.altair_chart(chart, use_container_width=True)


def numeric_or_none(value):

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def format_score_move(previous, current):

    if previous is None:
        return {
            "previous": "N/A",
            "current": f"{current:.2f}",
            "delta": "N/A",
            "direction": "No prior score",
            "class": "tc-score-move-flat"
        }

    delta = current - previous

    if delta > 0.01:
        direction = "Score improved"
        class_name = "tc-score-move-up"
    elif delta < -0.01:
        direction = "Score weakened"
        class_name = "tc-score-move-down"
    else:
        direction = "Score unchanged"
        class_name = "tc-score-move-flat"

    return {
        "previous": f"{previous:.2f}",
        "current": f"{current:.2f}",
        "delta": f"{delta:+.2f}",
        "direction": direction,
        "class": class_name
    }


def latest_different_score(values, current):

    numeric_values = [
        value
        for value in (numeric_or_none(item) for item in values)
        if value is not None
    ]

    if not numeric_values:
        return None

    for value in reversed(numeric_values):
        if abs(value - current) > 0.005:
            return value

    return numeric_values[-1]


def get_previous_macro_score(view_name, current_score):

    path = Path("dashboard_history.csv")

    if not path.exists():
        return None

    history = pd.read_csv(path)
    column = MACRO_HISTORY_COLUMNS.get(view_name, "overall")

    if column not in history.columns:
        return None

    return latest_different_score(history[column].tolist(), current_score)


def describe_indicator_moves(rows, limit=3):

    changes = []

    for row in rows:
        change = numeric_or_none(row.get("Change"))
        score = numeric_or_none(row.get("Score"))

        if change is None:
            continue

        changes.append(
            {
                "indicator": str(row.get("Indicator", "Unknown")),
                "change": change,
                "score": score
            }
        )

    changes = sorted(
        changes,
        key=lambda item: abs(item["change"]),
        reverse=True
    )

    if not changes:
        return []

    return changes[:limit]


def render_score_change_block(title, previous_score, current_score, summary, moves):

    score_move = format_score_move(previous_score, current_score)
    move_items = []

    for move in moves:
        score_text = (
            "N/A"
            if move.get("score") is None
            else f"{move['score']:.1f}"
        )
        move_items.append(
            f"""
            <div class="tc-change-explain-item">
                <span>{escape(move["indicator"])}</span>
                <strong>{move["change"]:+.2f}</strong>
                <em>Input score {escape(score_text)}</em>
            </div>
            """
        )

    if not move_items:
        move_items.append(
            """
            <div class="tc-change-explain-item">
                <span>No release-level changes available</span>
                <strong>N/A</strong>
                <em>Current feed did not expose comparable input changes.</em>
            </div>
            """
        )

    render_html(
        f"""
        <div class="tc-change-explain-block">
            <div class="tc-change-explain-head">
                <div>
                    <div class="tc-section-label">Why The Score Changed</div>
                    <h3>{escape(title)}</h3>
                </div>
                <div class="{score_move["class"]} tc-score-move-pill">{score_move["delta"]}</div>
            </div>
            <div class="tc-score-change-line">
                <span>Previous {score_move["previous"]}</span>
                <strong>{score_move["current"]}</strong>
                <span>{escape(score_move["direction"])}</span>
            </div>
            <p>{escape(summary)}</p>
            <div class="tc-change-explain-grid">{''.join(move_items)}</div>
        </div>
        """
    )


def build_macro_indicator_rows(table):

    rows = []

    for _, row in table.iterrows():
        bias = clean_outlook(row.get("Bias", "Neutral"))
        rows.append(
            {
                "Indicator": humanize_indicator_name(row.get("Metric", "")),
                "Current": format_value(row.get("Current", "")),
                "Previous": format_value(row.get("Previous", "")),
                "Change": format_value(row.get("Change", "")),
                "Score": format_value(row.get("Score", "")),
                "Bias": bias,
                "_class": row_class_from_bias(bias)
            }
        )

    return rows


def render_macro_change_explanation(view_name, table, score):

    rows = build_macro_indicator_rows(table)
    previous_score = get_previous_macro_score(view_name, score)
    moves = describe_indicator_moves(rows)
    score_sentence = score_direction_sentence(
        f"{view_name} score",
        previous_score,
        score
    )

    if moves:
        top_move = moves[0]
        move_phrase = change_direction_phrase(top_move["change"])
        summary = (
            f"{score_sentence} The largest changed input was "
            f"{top_move['indicator']}, which {move_phrase}; "
            "the block below ranks the biggest current data changes feeding this score."
        )
    else:
        summary = (
            f"{score_sentence} The current feed does not expose release-level input "
            "changes for this model, so only the score comparison is shown."
        )

    render_score_change_block(
        f"{view_name} Score",
        previous_score,
        score,
        summary,
        moves
    )


def build_macro_indicator_chart_frame(table):

    rows = []

    for _, row in table.iterrows():
        score = numeric_or_none(row.get("Score"))

        if score is None:
            continue

        rows.append(
            {
                "Indicator": humanize_indicator_name(row.get("Metric", "")),
                "Score": round(score, 2)
            }
        )

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows).set_index("Indicator")


def build_release_history_frame(values):

    history = values.get("history", {})
    history_type = history.get("type")

    try:
        if history_type == "spread":
            first = get_series(history["codes"][0], limit=40)
            second = get_series(history["codes"][1], limit=40)
            rows = []

            for left, right in zip(first, second):
                if left["date"] != right["date"]:
                    continue
                rows.append(
                    {
                        "Date": left["date"],
                        "Value": round(left["value"] - right["value"], 2)
                    }
                )
                if len(rows) >= 10:
                    break
        else:
            code = history.get("code")
            if not code:
                return pd.DataFrame()

            series = get_series(code, limit=80)
            rows = []

            for index, item in enumerate(series):
                if history_type == "change":
                    period = history.get("period", "mom")
                    base_index = index + (12 if period == "yoy" else 1)

                    if base_index >= len(series):
                        continue

                    previous = series[base_index]["value"]
                    if history.get("percent_change", True):
                        value = pct_change(item["value"], previous)
                    else:
                        value = item["value"] - previous
                else:
                    value = item["value"]

                rows.append(
                    {
                        "Date": item["date"],
                        "Value": round(value, 2)
                    }
                )

                if len(rows) >= 10:
                    break
    except Exception:
        return pd.DataFrame()

    frame = pd.DataFrame(rows)

    if frame.empty:
        return frame

    frame["Date"] = pd.to_datetime(frame["Date"])
    return frame.sort_values("Date")


def render_release_history_card(indicator, values):

    frame = build_release_history_frame(values)

    if frame.empty:
        return

    label = values.get("history", {}).get("label", "Value")
    latest_value = frame.iloc[-1]["Value"]
    previous_value = frame.iloc[-2]["Value"] if len(frame) > 1 else latest_value
    change = latest_value - previous_value
    badge_class = "tc-history-up" if change >= 0 else "tc-history-down"
    latest_date = frame.iloc[-1]["Date"].date().isoformat()

    render_html(
        f"""
        <div class="tc-history-card-head">
            <div>
                <span>Last 10 FRED releases</span>
                <strong>{escape(humanize_indicator_name(indicator))}</strong>
            </div>
            <em class="{badge_class}">{latest_value:.2f}</em>
        </div>
        """
    )

    base = alt.Chart(frame).encode(
        x=alt.X(
            "Date:T",
            axis=alt.Axis(
                title=None,
                labelAngle=0,
                labelColor="#AAB4C0",
                labelFontSize=10,
                format="%b %d"
            )
        ),
        y=alt.Y(
            "Value:Q",
            axis=alt.Axis(
                title=label,
                titleColor="#AAB4C0",
                labelColor="#AAB4C0",
                gridColor="#465566",
                labelFontSize=10,
                titleFontSize=10
            )
        )
    )
    bars = base.mark_bar(
        color="#6EA0D0",
        opacity=0.78,
        size=20
    )
    line = base.mark_line(
        color="#F2C572",
        strokeWidth=2.5,
        interpolate="monotone"
    )
    points = base.mark_circle(
        color="#F2C572",
        stroke="#1F2733",
        strokeWidth=1.3,
        size=42
    )

    chart = (bars + line + points).properties(height=150).configure_view(
        stroke=None
    ).configure_axis(
        domain=False
    )

    st.altair_chart(chart, use_container_width=True)

    render_html(
        f"""
        <div class="tc-history-meta">
            <span>Latest: {latest_date}</span>
            <span>Change: {change:+.2f}</span>
        </div>
        """
    )


def render_fred_release_history(engine):

    history_items = [
        (indicator, values)
        for indicator, values in engine.get("data", {}).items()
        if isinstance(values, dict) and values.get("history")
    ]

    if not history_items:
        st.caption("No FRED release history is available for this model.")
        return

    columns = st.columns(2)

    for index, (indicator, values) in enumerate(history_items):
        with columns[index % 2]:
            render_release_history_card(indicator, values)


def macro_signal_sentence(view_name, signal, score):

    return f"{view_name} is {signal.lower()} with a {score:.1f} score."


def render_macro_score_ring(view_name, score, signal):

    radius = 54
    circumference = 2 * pi * radius
    filled = circumference * max(0, min(score, 100)) / 100
    empty = circumference - filled

    render_unsafe_html(
        f"""
        <div class="tc-macro-ring-panel">
            <svg viewBox="0 0 150 150" class="tc-macro-ring">
                <circle cx="75" cy="75" r="{radius}" class="tc-macro-ring-bg" />
                <circle cx="75" cy="75" r="{radius}" class="tc-macro-ring-fill"
                    stroke-dasharray="{filled:.2f} {empty:.2f}" />
                <text x="75" y="72" text-anchor="middle" class="tc-macro-ring-score">{score:.0f}</text>
                <text x="75" y="93" text-anchor="middle" class="tc-macro-ring-label">score</text>
            </svg>
            <div>
                <div class="tc-section-label">Macro Diagram</div>
                <h3>{escape(view_name)}</h3>
                <p>{escape(macro_signal_sentence(view_name, signal, score))}</p>
                <span class="{signal_class(signal)} tc-macro-status-pill">{escape(signal)}</span>
            </div>
        </div>
        """
    )


def render_macro_category_cards():

    frame = build_macro_score_frame()

    if frame.empty:
        return

    cards = []

    for _, row in frame.iterrows():
        cards.append(
            f"""
            <div class="tc-driver-card tc-macro-card">
                <div class="tc-driver-name">{escape(row["Driver"])}</div>
                <div class="tc-driver-score">{row["Score"]:.0f}</div>
                <div class="{signal_class(row["Signal"])} tc-driver-badge">{escape(row["Signal"])}</div>
            </div>
            """
        )

    render_html(
        f"""
        <div class="tc-driver-grid tc-macro-card-grid">
            {''.join(cards)}
        </div>
        """
    )


def render_macro_indicator_bars(table):

    rows = []

    for _, row in table.iterrows():
        score = numeric_or_none(row.get("Score"))

        if score is None:
            continue

        label = humanize_indicator_name(row.get("Metric", ""))
        signal = score_to_signal(score)
        rows.append(
            f"""
            <div class="tc-indicator-bar-row">
                <div class="tc-indicator-bar-label">{escape(label)}</div>
                <div class="tc-indicator-bar-track"><div style="width:{max(0, min(score, 100)):.0f}%;"></div></div>
                <div class="{signal_class(signal)} tc-indicator-bar-score">{score:.0f}</div>
            </div>
            """
        )

    if not rows:
        st.caption("No scored indicator bars are available for this view.")
        return

    render_html(
        f"<div class='tc-indicator-bar-panel'>{''.join(rows)}</div>",
    )


def render_macro_insight_panel(view_name, table, score, signal):

    chart_frame = build_macro_indicator_chart_frame(table)
    change_rows = []

    for _, row in table.iterrows():
        change = numeric_or_none(row.get("Change"))

        if change is not None:
            change_rows.append(
                (
                    abs(change),
                    humanize_indicator_name(row.get("Metric", "")),
                    change
                )
            )

    if chart_frame.empty:
        strongest = "No ranked indicator"
        weakest = "No ranked indicator"
    else:
        strongest = chart_frame["Score"].idxmax()
        weakest = chart_frame["Score"].idxmin()

    if change_rows:
        _, mover, change = sorted(change_rows, reverse=True)[0]
        mover_text = f"{mover} moved {change:+.2f}"
    else:
        mover_text = "Recent move data unavailable"

    render_html(
        f"""
        <div class="tc-macro-insight-panel">
            <div class="tc-section-label">Read Through</div>
            <p>{escape(macro_signal_sentence(view_name, signal, score))}</p>
            <div class="tc-macro-insight-grid">
                <div><span>Strongest input</span><strong>{escape(strongest)}</strong></div>
                <div><span>Weakest input</span><strong>{escape(weakest)}</strong></div>
                <div><span>Largest recent move</span><strong>{escape(mover_text)}</strong></div>
            </div>
        </div>
        """
    )


def render_macro_driver_diagram(selected):

    frame = build_macro_score_frame()

    if frame.empty:
        return

    drivers = frame.rename(columns={"Driver": "Driver", "Score": "Score"})

    st.markdown("### Macro Driver Radar")
    render_radar_chart(drivers)
    st.caption(
        f"{selected} is plotted against the rest of the macro stack to show whether this category is leading or lagging the regime."
    )


def render_page_header(title, subtitle):

    render_html(
        f"""
        <div class="tc-page-header">
            <div>
                <div class="tc-page-title">{escape(title)}</div>
                <div class="tc-page-subtitle">{escape(subtitle)}</div>
            </div>
            <div class="tc-page-mark">TC</div>
        </div>
        """
    )


def render_dashboard_hero():

    score_width = max(0, min(100, macro_score))
    regime = get_regime(macro_score)

    render_html(
        f"""
        <div class="tc-dashboard-hero">
            <div>
                <div class="tc-dashboard-eyebrow">Trishula Capital</div>
                <div class="tc-dashboard-title">Macro Intelligence Command Center</div>
                <div class="tc-dashboard-copy">
                    Real-time regime, liquidity, inflation, growth, and asset-bias signals
                    summarized into one operating view.
                </div>
                <div class="tc-dashboard-strip">
                    <div>
                        <span>Regime</span>
                        <strong>{escape(str(regime))}</strong>
                    </div>
                    <div>
                        <span>Risk Mode</span>
                        <strong>{escape(str(macro["risk_status"]))}</strong>
                    </div>
                    <div>
                        <span>Trend</span>
                        <strong>{escape(str(trend["trend"]))}</strong>
                    </div>
                </div>
            </div>
            <div class="tc-dashboard-score">
                <div class="tc-dashboard-score-label">Overall Macro Score</div>
                <div class="tc-dashboard-score-value">{macro_score:.2f}</div>
                <div class="tc-dashboard-score-bar">
                    <div style="width: {score_width:.0f}%;"></div>
                </div>
            </div>
        </div>
        """
    )


def render_sidebar_nav():

    render_html(
        """
        <div class="sidebar-brand">
            <div class="brand-mark">TC</div>
            <div>
                <div class="brand-name">TRISHULA CAPITAL</div>
                <div class="brand-caption">Macro Intelligence Platform</div>
            </div>
        </div>
        """,
        target=st.sidebar
    )

    st.sidebar.button(
        "Dashboard",
        key="nav_Dashboard",
        width="stretch",
        type="primary" if st.session_state.page == "Dashboard" else "secondary",
        on_click=set_page,
        args=("Dashboard",)
    )
    render_html('<div class="sidebar-divider"></div>', target=st.sidebar)
    render_html(
        '<div class="sidebar-section-label">Macro Intelligence</div>',
        target=st.sidebar
    )

    for label, view_name, _ in MACRO_NAV_ITEMS:
        is_active = (
            st.session_state.page == "Macro Intelligence"
            and st.session_state.macro_view == view_name
        )
        st.sidebar.button(
            label,
            key=f"macro_nav_{view_name}",
            width="stretch",
            type="primary" if is_active else "secondary",
            on_click=set_macro_view,
            args=(view_name,)
        )

    render_html('<div class="sidebar-divider"></div>', target=st.sidebar)
    render_html(
        '<div class="sidebar-section-label">Asset Intelligence</div>',
        target=st.sidebar
    )

    for label, asset_name in ASSET_NAV_ITEMS:
        is_active = (
            st.session_state.page == "Asset Intelligence"
            and st.session_state.asset_view == asset_name
        )
        st.sidebar.button(
            label,
            key=f"asset_nav_{asset_name}",
            width="stretch",
            type="primary" if is_active else "secondary",
            on_click=set_asset_view,
            args=(asset_name,)
        )

    render_html('<div class="sidebar-divider"></div>', target=st.sidebar)
    st.sidebar.button(
        "Institutional Positioning",
        key="nav_Institutional_Positioning",
        width="stretch",
        type="primary" if st.session_state.page == "Institutional Positioning" else "secondary",
        on_click=set_page,
        args=("Institutional Positioning",)
    )

    render_html(
        f"""
        <div class="sidebar-footer">
            <div class="footer-label">Current Regime</div>
            <div class="footer-value">{escape(str(get_regime(macro_score)))}</div>
        </div>
        """,
        target=st.sidebar
    )


def show_macro_engine_view(view_name):

    key = MACRO_ENGINE_KEYS.get(view_name, "macro")
    engine = engines[key]
    score = engine.get("score", macro_score)
    signal = score_to_signal(score)
    table = build_component_table(engine)

    top_left, top_right = st.columns([0.95, 1.35])

    with top_left:
        render_macro_score_ring(view_name, score, signal)
        render_macro_insight_panel(view_name, table, score, signal)
        render_macro_change_explanation(view_name, table, score)

    with top_right:
        st.markdown("### Latest FRED Release History")
        render_fred_release_history(engine)

    st.markdown("### Score History")
    render_score_history_chart(
        build_macro_history_frame(view_name, score),
        f"{view_name} Score"
    )

    st.markdown("### Input Scores")
    render_html_table(
        build_macro_indicator_rows(table),
        ["Indicator", "Current", "Previous", "Change", "Score", "Bias"]
    )

    render_macro_driver_diagram(view_name)


def render_bias_bar(label, signal, value=None):

    value_text = "" if value is None else f"<span>{value}</span>"

    render_html(
        f"""
        <div class="asset-bias-row">
            <div>{escape(label)}</div>
            <div class="{signal_class(signal)}">{escape(signal)}</div>
            {value_text}
        </div>
        """
    )


def style_asset_factor_table(table):

    def bias_color(value):
        if isinstance(value, str) and "Bullish" in value:
            return "background-color: #3646D9; color: #FFFFFF; font-weight: 800;"
        if isinstance(value, str) and "Bearish" in value:
            return "background-color: #EF5B5B; color: #FFFFFF; font-weight: 800;"
        return "background-color: #4B4B55; color: #F3F4F6; font-weight: 800;"

    columns = [
        column
        for column in ["Bias", "Signal", "Status"]
        if column in table.columns
    ]

    if not columns:
        return table.style

    return table.style.map(
        bias_color,
        subset=columns
    )


def build_macro_factor_table(category_name, indicators):

    rows = []
    category = macro["categories"][category_name]

    for indicator in indicators:
        values = category.get(indicator, {})
        rows.append(
            {
                "Indicator": indicator,
                "Bias": values.get("bias", "Neutral"),
                "Current": values.get("current", "N/A"),
                "Previous": values.get("previous", "N/A")
            }
        )

    return pd.DataFrame(rows).astype(str)


def build_asset_factor_table(asset):

    table = build_component_table(asset)

    if table.empty:
        return table

    return table.rename(
        columns={
            "Metric": "Driver"
        }
    )[["Driver", "Current", "Previous", "Change", "Score", "Bias"]].astype(str)


def build_asset_history_frame(asset_name, asset):

    path = Path("dashboard_history.csv")

    if not path.exists():
        return pd.DataFrame(
            {
                "Score": [asset["score"]]
            }
        )

    history = pd.read_csv(path)

    if "date" not in history.columns or "overall" not in history.columns:
        return pd.DataFrame(
            {
                "Score": [asset["score"]]
            }
        )

    history = history.tail(20).copy()
    history["date"] = pd.to_datetime(history["date"])
    history = history.drop_duplicates(
        subset=["date"],
        keep="last"
    )
    history = history.set_index("date")

    return history[["overall"]].rename(
        columns={
            "overall": f"{asset_name} Score Proxy"
        }
    )


def render_asset_scorecard(asset_name, asset):

    score = asset["score"]
    signal = score_to_signal(score)
    edge_score = score_to_edgefinder(score)
    macro_growth_signal = score_to_signal(macro["scores"]["Economic Growth"])
    inflation_signal = score_to_signal(macro["scores"]["Inflation"])
    labor_signal = score_to_signal(macro["scores"]["Labor Market"])
    liquidity_signal = score_to_signal(
        macro["scores"]["Liquidity & Financial Conditions"]
    )
    sentiment_signal = score_to_signal(macro["scores"]["Market Sentiment"])

    render_html(
        f"""
        <div class="asset-scorecard-header">
            <div>
                <div class="asset-scorecard-title">Asset Scorecard</div>
                <div class="asset-scorecard-subtitle">Symbol: {asset_name.upper()}</div>
            </div>
            <div class="{signal_class(signal)} asset-scorecard-headline">{signal}</div>
        </div>
        """
    )

    left, right = st.columns([0.9, 1.9])

    with left:
        render_html(
            f"""
            <div class="asset-score-panel">
                <div class="asset-symbol-row">
                    <span>Symbol: {asset_name.upper()}</span>
                    <span>{asset['outlook']}</span>
                </div>
                <div class="asset-score-number">{edge_score:+.1f}</div>
                <div class="asset-score-label">{signal}</div>
                <div class="asset-score-meter">
                    <div style="width:{score}%;"></div>
                </div>
                <div class="asset-score-grid">
                    <span>EdgeFinder score</span><b>{edge_score:+.1f}</b>
                    <span>Technical score</span><b>0.0</b>
                    <span>Sentiment score</span><b>{score_to_edgefinder(macro['scores']['Market Sentiment']):+.1f}</b>
                    <span>Fundamentals score</span><b>{score_to_edgefinder(score):+.1f}</b>
                </div>
            </div>
            """
        )

        st.markdown("#### Score over time")
        st.line_chart(
            build_asset_history_frame(
                asset_name,
                asset
            ),
            width="stretch"
        )

        target_rows = pd.DataFrame(
            [
                {"Target": "Target 1", "Value": "N/A"},
                {"Target": "Target 2", "Value": "N/A"},
                {"Target": "Target 3", "Value": "N/A"}
            ]
        )
        st.dataframe(
            target_rows,
            width="stretch",
            hide_index=True
        )

    with right:
        top_left, top_right = st.columns([1.1, 0.9])

        with top_left:
            st.markdown("#### Technical Bias")
            render_bias_bar("4H / Daily Chart Trend", "Neutral")
            render_bias_bar("Seasonality Trend", "Neutral")

        with top_right:
            st.markdown("#### Crowd Sentiment Signal")
            render_bias_bar("Crowd sentiment", sentiment_signal)
            st.caption(
                "Signal uses VIX and macro sentiment inputs until a dedicated positioning feed is connected."
            )

        st.markdown("#### Institutional Activity Bias")
        inst_cols = st.columns(3)
        inst_cols[0].metric("Bias", liquidity_signal)
        inst_cols[1].metric("Long %", "N/A")
        inst_cols[2].metric("Short %", "N/A")

        growth_table = build_macro_factor_table(
            "Economic Growth",
            [
                "GDP QoQ Annualized",
                "ISM Manufacturing PMI",
                "ISM Services PMI",
                "Retail Sales MoM",
                "Core Retail Sales MoM"
            ]
        )
        st.markdown(f"#### Economic Growth Bias: {macro_growth_signal}")
        st.dataframe(
            style_asset_factor_table(growth_table),
            width="stretch",
            hide_index=True
        )

        inflation_table = build_macro_factor_table(
            "Inflation",
            [
                "CPI YoY",
                "Core CPI YoY",
                "PPI YoY",
                "PCE YoY",
                "Core PCE YoY"
            ]
        )
        st.markdown(f"#### Inflation Bias: {inflation_signal}")
        st.dataframe(
            style_asset_factor_table(inflation_table),
            width="stretch",
            hide_index=True
        )

        labor_table = build_macro_factor_table(
            "Labor Market",
            [
                "Non-Farm Payrolls (NFP)",
                "Unemployment Rate",
                "Initial Jobless Claims",
                "ADP Employment Change",
                "JOLTS Job Openings"
            ]
        )
        st.markdown(f"#### Jobs Market Bias: {labor_signal}")
        st.dataframe(
            style_asset_factor_table(labor_table),
            width="stretch",
            hide_index=True
        )

        st.markdown("#### Asset Driver Breakdown")
        st.dataframe(
            style_asset_factor_table(
                build_asset_factor_table(asset)
            ),
            width="stretch",
            hide_index=True
        )


if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "macro_view" not in st.session_state:
    st.session_state.macro_view = "Liquidity"

if "asset_view" not in st.session_state:
    st.session_state.asset_view = "Gold"

if "institutional_asset" not in st.session_state:
    st.session_state.institutional_asset = "Gold"

if "institutional_timeframe" not in st.session_state:
    st.session_state.institutional_timeframe = "6M"

macro_view_options = [view_name for _, view_name, _ in MACRO_NAV_ITEMS]
asset_view_options = [asset_name for _, asset_name in ASSET_NAV_ITEMS]

if st.session_state.macro_view not in macro_view_options:
    st.session_state.macro_view = macro_view_options[0]

if st.session_state.asset_view not in asset_view_options:
    st.session_state.asset_view = asset_view_options[0]

if st.session_state.institutional_asset not in asset_view_options:
    st.session_state.institutional_asset = asset_view_options[0]

if st.session_state.institutional_timeframe not in ["1M", "3M", "6M", "1Y", "ALL"]:
    st.session_state.institutional_timeframe = "6M"


def set_page(page_name):

    st.session_state.page = page_name


def set_macro_view(view_name):

    st.session_state.page = "Macro Intelligence"
    st.session_state.macro_view = view_name


def set_asset_view(asset_name):

    st.session_state.page = "Asset Intelligence"
    st.session_state.asset_view = asset_name


render_sidebar_nav()

page = st.session_state.page


if page == "Dashboard":
    render_dashboard_hero()

    if st.button("🔄 Update Economic Data", key="update_economic_data_dashboard", type="secondary"):
        refresh_economic_data()
        st.success("Economic data updated. Macro scores, asset scores, and explanations were recalculated.")
        st.rerun()

    st.divider()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Overall Macro Score", f"{macro_score:.2f}")
    c2.metric("Risk-On / Risk-Off", macro["risk_status"])
    c3.metric("USD Bias", macro["usd_bias"])
    c4.metric("Gold Bias", macro["gold_bias"])
    c5.metric("Equity Market Bias", macro["equity_bias"])

    st.divider()

    st.subheader("Category Scores")
    render_macro_category_cards()

    st.divider()

    st.subheader("Trading Interpretation")
    outlook_columns = st.columns(3)

    for index, (label, value) in enumerate(macro["outlooks"].items()):
        outlook_columns[index % 3].metric(label, value)

    st.divider()

    middle = st.columns(3)
    with middle[0]:
        show_macro_category("Inflation")
    with middle[1]:
        show_macro_category("Labor Market")
    with middle[2]:
        show_macro_category("Economic Growth")

    st.divider()

    bottom = st.columns(3)
    with bottom[0]:
        show_macro_category("Monetary Policy")
    with bottom[1]:
        show_macro_category("Liquidity & Financial Conditions")
    with bottom[2]:
        show_macro_category("Market Sentiment")

    st.divider()
    show_asset_metrics()

elif page == "Macro Intelligence":
    render_page_header(
        "MACRO INTELLIGENCE",
        "Category-level macro conditions and regime context"
    )

    if st.button("🔄 Update Economic Data", key="update_economic_data_macro", type="secondary"):
        refresh_economic_data()
        st.success("Economic data updated. Macro scores, asset scores, and explanations were recalculated.")
        st.rerun()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall Macro Score", f"{macro_score:.2f}")
    c2.metric("Risk Status", macro["risk_status"])
    c3.metric("Regime", get_regime(macro_score))
    c4.metric("Trend", trend["trend"])

    selected = st.selectbox(
        "Select Macro Category",
        macro_view_options,
        index=macro_view_options.index(st.session_state.macro_view)
    )
    st.session_state.macro_view = selected

    show_macro_engine_view(selected)

elif page == "Asset Intelligence":
    render_page_header(
        "ASSET INTELLIGENCE",
        "Weighted asset scorecards and macro-driver explanations"
    )

    selected = st.selectbox(
        "Select Asset",
        asset_view_options,
        index=asset_view_options.index(st.session_state.asset_view)
    )
    st.session_state.asset_view = selected

    asset_map = {
        "Gold": gold,
        "Bitcoin": bitcoin,
        "SP500": sp500,
        "Nasdaq": nasdaq,
        "Dollar": dollar,
        "Bonds": bonds
    }

    asset = asset_map[selected]

    render_asset_intelligence(selected, asset)

elif page == "Institutional Positioning":
    render_institutional_positioning_page()
