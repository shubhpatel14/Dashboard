from concurrent.futures import ThreadPoolExecutor

from data.fred_client import (
    get_12m_value,
    get_current_date,
    get_current_value,
    get_previous_value,
    get_series
)

from engines.helpers import (
    build_change_indicator,
    build_level_indicator,
    score_change_indicator,
    score_change,
    score_level
)

from models.scoring import (
    bias_from_score,
    clamp_score,
    indicator_result,
    pct_change,
    status_from_score,
    status_label_from_score,
    weighted_average
)


def _safe_indicator(builder):

    try:
        return builder()

    except Exception as error:
        return _unavailable_result(str(error))


def _unavailable_result(reason="Data unavailable from current provider"):

    return {
        "current": "N/A",
        "previous": "N/A",
        "change": "N/A",
        "consensus": "N/A",
        "surprise": "N/A",
        "last_update": "N/A",
        "score": 50,
        "bias": "Neutral",
        "status": "YELLOW",
        "status_label": "Neutral",
        "note": reason
    }


def _prefetch_macro_series():

    codes = [
        "CPIAUCSL",
        "CPILFESL",
        "PCEPI",
        "PCEPILFE",
        "PPIACO",
        "PPIFES",
        "PAYEMS",
        "UNRATE",
        "CES0500000003",
        "JTSJOL",
        "ICSA",
        "ADPMNUSNERSA",
        "GDPC1",
        "RSAFS",
        "RSFSXMV",
        "INDPRO",
        "DGORDER",
        "AMTMNO",
        "FEDFUNDS",
        "GS10",
        "DGS2",
        "DFII10",
        "WALCL",
        "M2SL",
        "RRPONTSYD",
        "TOTRESNS",
        "NFCI",
        "UMCSENT",
        "VIXCLS"
    ]

    def fetch(code):
        try:
            get_series(code)
        except Exception:
            pass

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(fetch, codes))


def _attach_forecast_fields(result, consensus=None):

    result = result.copy()
    result["consensus"] = consensus if consensus is not None else "N/A"
    result["surprise"] = "N/A"

    if consensus not in (None, 0, "N/A"):
        try:
            result["surprise"] = round(
                ((result["current"] - consensus) / abs(consensus)) * 100,
                2
            )
        except Exception:
            result["surprise"] = "N/A"

    result["status"] = status_from_score(result["score"])
    result["status_label"] = status_label_from_score(result["score"])

    return result


def _fred_change(code, period, low, high, lower_is_bullish=False):

    return _safe_indicator(
        lambda: _build_change_rate_indicator(
            code,
            period,
            low,
            high,
            lower_is_bullish=lower_is_bullish
        )
    )


def _fred_level(code, low, high, lower_is_bullish=False):

    return _safe_indicator(
        lambda: _attach_forecast_fields(
            build_level_indicator(
                code,
                low,
                high,
                lower_is_bullish=lower_is_bullish
            )
        )
    )


def _fred_abs_change(code, low, high, lower_is_bullish=False):

    return _safe_indicator(
        lambda: _build_absolute_change_indicator(
            code,
            low,
            high,
            lower_is_bullish=lower_is_bullish
        )
    )


def _build_change_rate_indicator(
    code,
    period,
    low,
    high,
    lower_is_bullish=False
):

    series = get_series(code)

    if period == "yoy":
        current_base_index = 12
        previous_base_index = 13
    else:
        current_base_index = 1
        previous_base_index = 2

    current = pct_change(
        series[0]["value"],
        series[current_base_index]["value"]
    )
    previous = pct_change(
        series[1]["value"],
        series[previous_base_index]["value"]
    )
    change = current - previous
    change_rate = pct_change(current, previous) if previous != 0 else change
    score = score_change_indicator(
        current,
        change_rate,
        low,
        high,
        lower_is_bullish=lower_is_bullish
    )

    return _attach_forecast_fields(
        indicator_result(
            current,
            previous,
            change,
            score,
            last_update=get_current_date(series).date().isoformat(),
            history={
                "type": "change",
                "code": code,
                "period": period,
                "percent_change": True,
                "label": "YoY %" if period == "yoy" else "MoM %"
            }
        )
    )


def _build_absolute_change_indicator(
    code,
    low,
    high,
    lower_is_bullish=False
):

    series = get_series(code)
    current = series[0]["value"] - series[1]["value"]
    previous = series[1]["value"] - series[2]["value"]
    change = current - previous
    change_rate = pct_change(current, previous) if previous != 0 else change
    score = score_change_indicator(
        current,
        change_rate,
        low,
        high,
        lower_is_bullish=lower_is_bullish
    )

    return _attach_forecast_fields(
        indicator_result(
            current,
            previous,
            change,
            score,
            last_update=get_current_date(series).date().isoformat(),
            history={
                "type": "change",
                "code": code,
                "period": "period",
                "percent_change": False
            }
        )
    )


def _adp_change():

    series = get_series("ADPMNUSNERSA")
    current = series[0]["value"] - series[1]["value"]
    previous = series[1]["value"] - series[2]["value"]
    change = current - previous
    score = score_change(current, -150000, 350000)

    return _attach_forecast_fields(
        indicator_result(
            current,
            previous,
            change,
            score,
            last_update=get_current_date(series).date().isoformat(),
            history={
                "type": "change",
                "code": "ADPMNUSNERSA",
                "period": "period",
                "percent_change": False
            }
        )
    )


def _payroll_change():

    series = get_series("PAYEMS")
    current = series[0]["value"] - series[1]["value"]
    previous = series[1]["value"] - series[2]["value"]
    change = current - previous
    score = score_change(current, -100, 300)

    return _attach_forecast_fields(
        indicator_result(
            current,
            previous,
            change,
            score,
            last_update=get_current_date(series).date().isoformat(),
            history={
                "type": "change",
                "code": "PAYEMS",
                "period": "period",
                "percent_change": False
            }
        )
    )


def _gdp_qoq_annualized():

    series = get_series("GDPC1")
    current = pct_change(series[0]["value"], series[1]["value"]) * 4
    previous = pct_change(series[1]["value"], series[2]["value"]) * 4
    change = current - previous
    score = score_change(current, -2, 6)

    return _attach_forecast_fields(
        indicator_result(
            current,
            previous,
            change,
            score,
            last_update=get_current_date(series).date().isoformat(),
            history={
                "type": "change",
                "code": "GDPC1",
                "period": "period",
                "percent_change": True,
                "annualize": 4,
                "label": "QoQ Ann. %"
            }
        )
    )


def _industrial_production_yoy():

    series = get_series("INDPRO")
    current = pct_change(series[0]["value"], series[12]["value"])
    previous = pct_change(series[1]["value"], series[13]["value"])
    change = current - previous
    score = score_change(current, -5, 5)

    return _attach_forecast_fields(
        indicator_result(
            current,
            previous,
            change,
            score,
            last_update=get_current_date(series).date().isoformat(),
            history={
                "type": "change",
                "code": "INDPRO",
                "period": "yoy",
                "percent_change": True
            }
        )
    )


def _yield_curve_10y_2y():

    ten_year = get_series("GS10")
    two_year = get_series("DGS2")
    current = get_current_value(ten_year) - get_current_value(two_year)
    previous = get_previous_value(ten_year) - get_previous_value(two_year)
    change = current - previous
    score = score_level(current, -1, 2)

    return _attach_forecast_fields(
        indicator_result(
            current,
            previous,
            change,
            score,
            last_update=get_current_date(ten_year).date().isoformat(),
            history={
                "type": "spread",
                "codes": ["GS10", "DGS2"]
            }
        )
    )


def _fomc_rate_decision():

    series = get_series("FEDFUNDS")
    current = series[0]["value"] - series[1]["value"]
    previous = series[1]["value"] - series[2]["value"]
    change = current - previous
    score = score_change(
        change,
        -0.50,
        0.50,
        lower_is_bullish=True
    )

    return _attach_forecast_fields(
        indicator_result(
            current,
            previous,
            change,
            score,
            last_update=get_current_date(series).date().isoformat(),
            history={
                "type": "change",
                "code": "FEDFUNDS",
                "period": "period",
                "percent_change": False
            }
        )
    )


def _category_score(rows, weights):

    weighted_scores = []

    for key, weight in weights.items():
        row = rows.get(key)

        if (
            row
            and isinstance(row.get("score"), (int, float))
            and row.get("current") != "N/A"
            and "error" not in row
        ):
            weighted_scores.append((row["score"], weight))

    return weighted_average(weighted_scores)


def _risk_status(score):

    if score >= 60:
        return "Risk-On"

    if score <= 40:
        return "Risk-Off"

    return "Neutral"


def _recession_risk(score, labor_score, growth_score, liquidity_score):

    inverse = 100 - weighted_average(
        [
            (score, 40),
            (labor_score, 25),
            (growth_score, 25),
            (liquidity_score, 10)
        ]
    )

    if inverse >= 65:
        return "High"

    if inverse >= 40:
        return "Moderate"

    return "Low"


def _trading_outlooks(overall, scores):

    inflation = scores["Inflation"]
    labor = scores["Labor Market"]
    growth = scores["Economic Growth"]
    monetary = scores["Monetary Policy"]
    liquidity = scores["Liquidity & Financial Conditions"]
    sentiment = scores["Market Sentiment"]

    usd_score = weighted_average(
        [
            (100 - inflation, 30),
            (100 - monetary, 25),
            (growth, 20),
            (labor, 15),
            (100 - sentiment, 10)
        ]
    )
    gold_score = weighted_average(
        [
            (100 - inflation, 25),
            (monetary, 25),
            (liquidity, 20),
            (100 - growth, 15),
            (100 - sentiment, 15)
        ]
    )
    equity_score = weighted_average(
        [
            (overall, 40),
            (growth, 25),
            (liquidity, 20),
            (sentiment, 15)
        ]
    )
    bond_yield_score = weighted_average(
        [
            (100 - inflation, 30),
            (100 - monetary, 30),
            (growth, 20),
            (100 - liquidity, 20)
        ]
    )

    return {
        "USD Outlook": bias_from_score(usd_score),
        "Gold Outlook (XAUUSD)": bias_from_score(gold_score),
        "S&P 500 Outlook": bias_from_score(equity_score),
        "Nasdaq Outlook": bias_from_score(
            weighted_average(
                [
                    (equity_score, 70),
                    (liquidity, 30)
                ]
            )
        ),
        "Bond Yield Outlook": bias_from_score(bond_yield_score),
        "Recession Risk Level": _recession_risk(
            overall,
            labor,
            growth,
            liquidity
        )
    }


def build_macro_engine():

    _prefetch_macro_series()

    categories = {
        "Inflation": {
            "CPI MoM": _fred_change("CPIAUCSL", "mom", -1, 1, True),
            "CPI YoY": _fred_change("CPIAUCSL", "yoy", -1, 6, True),
            "Core CPI MoM": _fred_change("CPILFESL", "mom", -1, 1, True),
            "Core CPI YoY": _fred_change("CPILFESL", "yoy", -1, 6, True),
            "PCE MoM": _fred_change("PCEPI", "mom", -1, 1, True),
            "PCE YoY": _fred_change("PCEPI", "yoy", -1, 6, True),
            "Core PCE MoM": _fred_change("PCEPILFE", "mom", -1, 1, True),
            "Core PCE YoY": _fred_change("PCEPILFE", "yoy", -1, 6, True),
            "PPI MoM": _fred_change("PPIACO", "mom", -2, 2, True),
            "PPI YoY": _fred_change("PPIACO", "yoy", -3, 8, True),
            "Core PPI MoM": _fred_change("PPIFES", "mom", -2, 2, True),
            "Core PPI YoY": _fred_change("PPIFES", "yoy", -3, 8, True)
        },
        "Labor Market": {
            "Non-Farm Payrolls (NFP)": _safe_indicator(_payroll_change),
            "Unemployment Rate": _fred_level("UNRATE", 3.5, 7, True),
            "Average Hourly Earnings MoM": _fred_change(
                "CES0500000003",
                "mom",
                -1,
                1
            ),
            "Average Hourly Earnings YoY": _fred_change(
                "CES0500000003",
                "yoy",
                -1,
                6
            ),
            "JOLTS Job Openings": _fred_level("JTSJOL", 5000, 12000),
            "Initial Jobless Claims": _fred_abs_change(
                "ICSA",
                -50000,
                50000,
                True
            ),
            "ADP Employment Change": _safe_indicator(_adp_change)
        },
        "Economic Growth": {
            "GDP QoQ Annualized": _safe_indicator(_gdp_qoq_annualized),
            "Retail Sales MoM": _fred_change("RSAFS", "mom", -3, 3),
            "Core Retail Sales MoM": _fred_change("RSFSXMV", "mom", -3, 3),
            "ISM Manufacturing PMI": _unavailable_result(
                "ISM PMI is not available from the current FRED-only provider"
            ),
            "ISM Services PMI": _unavailable_result(
                "ISM Services PMI is not available from the current FRED-only provider"
            ),
            "Industrial Production MoM": _fred_change("INDPRO", "mom", -3, 3),
            "Industrial Production YoY": _safe_indicator(
                _industrial_production_yoy
            ),
            "Durable Goods Orders MoM": _fred_change("DGORDER", "mom", -5, 5),
            "Factory Orders MoM": _fred_change("AMTMNO", "mom", -5, 5)
        },
        "Monetary Policy": {
            "Fed Funds Rate": _fred_level("FEDFUNDS", 0, 6, True),
            "FOMC Rate Decision": _safe_indicator(_fomc_rate_decision),
            "FOMC Statement": _unavailable_result(
                "Text sentiment requires a news/FOMC text provider"
            ),
            "Powell Speech Sentiment": _unavailable_result(
                "Speech sentiment requires a news/transcript provider"
            ),
            "Fed Balance Sheet (WALCL)": _fred_change("WALCL", "yoy", -10, 10)
        },
        "Liquidity & Financial Conditions": {
            "M2 Money Supply (M2SL)": _fred_change("M2SL", "yoy", -10, 10),
            "10-Year Real Yield (DFII10)": _fred_level("DFII10", 0, 3, True),
            "10-Year Treasury Yield": _fred_level("GS10", 2, 6, True),
            "2-Year Treasury Yield": _fred_level("DGS2", 1, 6, True),
            "Yield Curve Spread (10Y - 2Y)": _safe_indicator(
                _yield_curve_10y_2y
            ),
            "Financial Conditions Index": _fred_level("NFCI", -1, 1, True)
        },
        "Market Sentiment": {
            "University of Michigan Consumer Sentiment": _fred_level(
                "UMCSENT",
                50,
                100
            ),
            "Consumer Confidence Index": _unavailable_result(
                "Conference Board CCI is not available from the current FRED-only provider"
            ),
            "VIX Index": _fred_level("VIXCLS", 12, 35, True),
            "Put/Call Ratio": _unavailable_result(
                "Put/call ratio requires an options market data provider"
            )
        }
    }

    scores = {
        "Inflation": _category_score(
            categories["Inflation"],
            {
                "CPI MoM": 14,
                "CPI YoY": 8,
                "Core CPI MoM": 18,
                "Core CPI YoY": 12,
                "PCE MoM": 10,
                "PCE YoY": 6,
                "Core PCE MoM": 14,
                "Core PCE YoY": 10,
                "PPI MoM": 4,
                "PPI YoY": 2,
                "Core PPI MoM": 1,
                "Core PPI YoY": 1
            }
        ),
        "Labor Market": _category_score(
            categories["Labor Market"],
            {
                "Non-Farm Payrolls (NFP)": 25,
                "Unemployment Rate": 20,
                "Average Hourly Earnings MoM": 10,
                "Average Hourly Earnings YoY": 10,
                "JOLTS Job Openings": 15,
                "Initial Jobless Claims": 15,
                "ADP Employment Change": 5
            }
        ),
        "Economic Growth": _category_score(
            categories["Economic Growth"],
            {
                "GDP QoQ Annualized": 25,
                "Retail Sales MoM": 20,
                "Core Retail Sales MoM": 15,
                "ISM Manufacturing PMI": 10,
                "ISM Services PMI": 10,
                "Industrial Production MoM": 8,
                "Industrial Production YoY": 4,
                "Durable Goods Orders MoM": 5,
                "Factory Orders MoM": 3
            }
        ),
        "Monetary Policy": _category_score(
            categories["Monetary Policy"],
            {
                "Fed Funds Rate": 30,
                "FOMC Rate Decision": 25,
                "FOMC Statement": 15,
                "Powell Speech Sentiment": 10,
                "Fed Balance Sheet (WALCL)": 20
            }
        ),
        "Liquidity & Financial Conditions": _category_score(
            categories["Liquidity & Financial Conditions"],
            {
                "M2 Money Supply (M2SL)": 20,
                "10-Year Real Yield (DFII10)": 25,
                "10-Year Treasury Yield": 15,
                "2-Year Treasury Yield": 15,
                "Yield Curve Spread (10Y - 2Y)": 15,
                "Financial Conditions Index": 10
            }
        ),
        "Market Sentiment": _category_score(
            categories["Market Sentiment"],
            {
                "University of Michigan Consumer Sentiment": 35,
                "Consumer Confidence Index": 20,
                "VIX Index": 35,
                "Put/Call Ratio": 10
            }
        )
    }

    overall_score = weighted_average(
        [
            (scores["Inflation"], 20),
            (scores["Labor Market"], 18),
            (scores["Economic Growth"], 22),
            (scores["Monetary Policy"], 15),
            (scores["Liquidity & Financial Conditions"], 15),
            (scores["Market Sentiment"], 10)
        ]
    )
    overall_score = clamp_score(overall_score)
    outlooks = _trading_outlooks(overall_score, scores)

    return {
        "score": overall_score,
        "bias": bias_from_score(overall_score),
        "risk_status": _risk_status(overall_score),
        "scores": scores,
        "categories": categories,
        "outlooks": outlooks,
        "usd_bias": outlooks["USD Outlook"],
        "gold_bias": outlooks["Gold Outlook (XAUUSD)"],
        "equity_bias": outlooks["S&P 500 Outlook"]
    }
