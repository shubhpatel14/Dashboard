import os

folders = [
    "data",
    "engines",
    "models",
    "dashboards",
    "charts",
    "assets",
    "assets/icons",
    "tests"
]

files = [
    "main.py",
    "config.py",
    "requirements.txt",

    "data/fred_client.py",
    "data/cache.py",
    "data/data_manager.py",

    "engines/liquidity.py",
    "engines/rates.py",
    "engines/inflation.py",
    "engines/growth.py",
    "engines/labor.py",
    "engines/credit.py",
    "engines/internals.py",
    "engines/sentiment.py",
    "engines/global_liquidity.py",
    "engines/gold.py",
    "engines/bitcoin.py",
    "engines/housing.py",
    "engines/recession.py",

    "models/scoring.py",
    "models/regime.py",
    "models/weights.py",

    "dashboards/liquidity_dashboard.py",
    "dashboards/macro_dashboard.py",
    "dashboards/gold_dashboard.py",
    "dashboards/bitcoin_dashboard.py",
    "dashboards/housing_dashboard.py",

    "charts/line_chart.py",
    "charts/gauge_chart.py",
    "charts/heatmap.py",

    "tests/test_liquidity.py",
    "tests/test_rates.py",
    "tests/test_growth.py"
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

for file in files:
    if not os.path.exists(file):
        open(file, "w").close()

print("✅ Trishula Dashboard project structure created successfully!")