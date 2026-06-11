from engines.liquidity import build_liquidity_engine
import sys

from engines.global_liquidity import build_global_liquidity_engine
from engines.rates import build_rates_engine
from engines.inflation import build_inflation_engine
from engines.growth import build_growth_engine
from engines.labor import build_labor_engine
from engines.credit import build_credit_engine
from engines.macro import build_macro_engine
from engines.recession import build_recession_engine
from engines.sentiment import build_sentiment_engine
from engines.housing import build_housing_engine
from engines.trend import build_trend_engine
from engines.gold import build_gold_engine
from engines.bitcoin import build_bitcoin_engine
from engines.sp500 import build_sp500_engine
from engines.nasdaq import build_nasdaq_engine
from engines.dollar import build_dollar_engine
from engines.bonds import build_bonds_engine

from models.status import (
    get_status,
    get_regime
)

from data.history import (
    save_dashboard_snapshot
)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def field(row, *keys, default="N/A"):

    for key in keys:
        if key in row:
            return row[key]

    return default

# ==================================================
# LOAD ENGINES
# ==================================================

liquidity = build_liquidity_engine()
global_liquidity = build_global_liquidity_engine()
rates = build_rates_engine()
inflation = build_inflation_engine()
growth = build_growth_engine()
labor = build_labor_engine()
credit = build_credit_engine()
recession = build_recession_engine()
sentiment = build_sentiment_engine()
housing = build_housing_engine()
gold = build_gold_engine()
bitcoin = build_bitcoin_engine()
sp500 = build_sp500_engine()
nasdaq = build_nasdaq_engine()
dollar = build_dollar_engine()
bonds = build_bonds_engine()
macro = build_macro_engine()
# ==================================================
# OVERALL SCORE
# ==================================================

overall_score = macro["score"]
# ==================================================
# SAVE SNAPSHOT
# ==================================================

save_dashboard_snapshot(
    liquidity["score"],
    rates["score"],
    inflation["score"],
    growth["score"],
    labor["score"],
    overall_score
)

# ==================================================
# TREND
# ==================================================

trend = build_trend_engine()

# ==================================================
# SCORECARD
# ==================================================

print()
print("=" * 70)
print("TRISHULA CAPITAL MACRO DASHBOARD")
print("=" * 70)

print()

print(f"💧 Liquidity          : {liquidity['score']:.2f} {get_status(liquidity['score'])}")
print(f"🌍 Global Liquidity   : {global_liquidity['score']:.2f} {get_status(global_liquidity['score'])}")
print(f"🏦 Rates              : {rates['score']:.2f} {get_status(rates['score'])}")
print(f"📈 Inflation          : {inflation['score']:.2f} {get_status(inflation['score'])}")
print(f"🏭 Growth             : {growth['score']:.2f} {get_status(growth['score'])}")
print(f"👷 Labor              : {labor['score']:.2f} {get_status(labor['score'])}")
print(f"💳 Credit             : {credit['score']:.2f} {get_status(credit['score'])}")
print(f"😎 Sentiment          : {sentiment['score']:.2f} {get_status(sentiment['score'])}")
print(f"🏠 Housing            : {housing['score']:.2f} {get_status(housing['score'])}")
print(f"🥇 Gold               : {gold['score']:.2f} {get_status(gold['score'])}")
print(f"₿ Bitcoin          : {bitcoin['score']:.2f} {get_status(bitcoin['score'])}")
print(f"📊 SP500             : {sp500['score']:.2f} {get_status(sp500['score'])}")
print(
    f"💻 Nasdaq            : "
    f"{nasdaq['score']:.2f} "
    f"{get_status(nasdaq['score'])}"
)
print(
    f"🏛 Bonds             : "
    f"{bonds['score']:.2f} "
    f"{get_status(bonds['score'])}"
)

print()
print("-" * 70)
print()

print(f"Macro Score          : {overall_score:.2f}")
print(f"Trend                : {trend['trend']}")
print(f"Daily Change         : {trend['change']:+.2f}")
print(f"Regime               : {get_regime(overall_score)}")

print()
print(f"🧠 Recession Score    : {recession['score']:.2f}")
print(f"📉 Recession Risk     : {recession['recession_probability']:.2f}%")
print(f"🥇 Gold Outlook       : {gold['outlook']}")
print(f"₿ Bitcoin Outlook    : {bitcoin['outlook']}")
print(f"📊 SP500 Outlook     : {sp500['outlook']}")
print(f"💻 Nasdaq Outlook    : {nasdaq['outlook']}")
print(f"💵 Dollar Outlook    : {dollar['outlook']}")
print(f"🏛 Bonds Outlook     : {bonds['outlook']}")
print("=" * 70)

# ==================================================
# LIQUIDITY
# ==================================================

print("\nLIQUIDITY\n")

for k, v in liquidity["data"].items():

    print(
        f"{k:<15}"
        f"{v['change']:>10}%"
        f"   Score: {v['score']}"
    )

# ==================================================
# GLOBAL LIQUIDITY
# ==================================================

print("\nGLOBAL LIQUIDITY\n")

for k, v in global_liquidity["data"].items():

    print(
        f"{k:<15}"
        f"{v['change']:>10}%"
        f"   Score: {v['score']}"
    )

# ==================================================
# RATES
# ==================================================

print("\nRATES\n")

for k, v in rates["data"].items():

    print(
        f"{k:<15}"
        f"Current: {v['current']:<8}"
        f" Old: {field(v, 'old', 'previous'):<8}"
        f" Diff: {field(v, 'difference', 'change'):<8}"
        f" Score: {v['score']}"
    )

# ==================================================
# INFLATION
# ==================================================

print("\nINFLATION\n")

for k, v in inflation["data"].items():

    print(
        f"{k:<15}"
        f"Current: {v['current']:<8}"
        f" Old: {field(v, 'old', 'previous'):<8}"
        f" Change: {v['change']:<8}%"
        f" Score: {v['score']}"
    )

# ==================================================
# GROWTH
# ==================================================

print("\nGROWTH\n")

for k, v in growth["data"].items():

    print(
        f"{k:<15}"
        f"Current: {v['current']:<8}"
        f" Old: {field(v, 'old', 'previous'):<8}"
        f" Change: {v['change']:<8}%"
        f" Score: {v['score']}"
    )

# ==================================================
# LABOR MARKET
# ==================================================

print("\nLABOR MARKET\n")

for k, v in labor["data"].items():

    print(
        f"{k:<15}"
        f"Current: {v['current']:<8}"
        f" Old: {field(v, 'old', 'previous'):<8}"
        f" Change: {v['change']:<8}%"
        f" Score: {v['score']}"
    )

# ==================================================
# CREDIT MARKET
# ==================================================

print("\nCREDIT MARKET\n")

for k, v in credit["data"].items():

    print(
        f"{k:<15}"
        f"Current: {v['current']:<8}"
        f" Old: {field(v, 'old', 'previous'):<8}"
        f" Diff: {field(v, 'difference', 'change'):<8}"
        f" Score: {v['score']}"
    )

# ==================================================
# HOUSING MARKET
# ==================================================

print("\nHOUSING MARKET\n")

for k, v in housing["data"].items():

    print(
        f"{k:<18}"
        f"Current: {v['current']:<8}"
        f" Old: {field(v, 'old', 'previous'):<8}"
        f" Change: {v['change']:<8}%"
        f" Score: {v['score']}"
    )

# ==================================================
# SENTIMENT
# ==================================================

print("\nSENTIMENT\n")

for k, v in sentiment["data"].items():

    print(
        f"{k:<22}"
        f"Current: {v['current']:<8}"
        f" Change: {v['change']:<8}%"
        f" Score: {v['score']}"
    )

# ==================================================
# RECESSION MODEL
# ==================================================

print("\nRECESSION MODEL\n")

for k, v in recession["data"].items():

    if k == "YIELD_CURVE":

        print(
            f"{k:<15}"
            f"Current: {v['current']:<8}"
            f" Score: {v['score']}"
        )

    elif k == "UNRATE":

        print(
            f"{k:<15}"
            f"Change: {v['change']:<8}%"
            f" Score: {v['score']}"
        )

    elif k == "HY_SPREAD":

        print(
            f"{k:<15}"
            f"Diff: {v['difference']:<8}"
            f" Score: {v['score']}"
        )

    elif k == "CLAIMS":

        print(
            f"{k:<15}"
            f"Change: {v['change']:<8}%"
            f" Score: {v['score']}"
        )

# ==================================================
# GOLD MODEL
# ==================================================

print("\nGOLD MODEL\n")

for k, v in gold["data"].items():

    print(
        f"{k:<15}"
        f"Current: {v['current']:<8}"
        f" Old: {field(v, 'old', 'previous'):<8}"
        f" Change: {v['change']:<8}%"
        f" Score: {v['score']}"
    )

# ==================================================
# BITCOIN MODEL
# ==================================================

print("\nBITCOIN MODEL\n")

for k, v in bitcoin["data"].items():

    print(
        f"{k:<20}"
        f"Score: {v}"
    )

print()

# ==================================================
# SP500 MODEL
# ==================================================

print("\nSP500 MODEL\n")

for k, v in sp500["data"].items():

    print(
        f"{k:<15}"
        f"Score: {v}"
    )

# ==================================================
# NASDAQ MODEL
# ==================================================

print("\nNASDAQ MODEL\n")

for k, v in nasdaq["data"].items():

    print(
        f"{k:<20}"
        f"Score: {v}"
    )


# ==================================================
# DOLLAR MODEL
# ==================================================

print("\nDOLLAR MODEL\n")

for k, v in dollar["data"].items():

    print(
        f"{k:<20}"
        f"Score: {v}"
    )

# ==================================================
# BONDS MODEL
# ==================================================

print("\nBONDS MODEL\n")

for k, v in bonds["data"].items():

    print(
        f"{k:<20}"
        f"Score: {v}"
    )


print("=" * 70)
