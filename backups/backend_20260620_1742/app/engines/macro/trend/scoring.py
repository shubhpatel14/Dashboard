import csv
import os

FILE_NAME = "dashboard_history.csv"


def build_trend_engine():

    if not os.path.exists(FILE_NAME):

        return {
            "trend": "NO DATA",
            "change": 0
        }

    rows = []

    with open(FILE_NAME, "r") as file:

        reader = csv.DictReader(file)

        for row in reader:
            rows.append(row)

    if len(rows) < 2:

        return {
            "trend": "NO DATA",
            "change": 0
        }

    latest = float(rows[-1]["overall"])

    previous = float(rows[-2]["overall"])

    change = round(
        latest - previous,
        2
    )

    if change > 1:

        trend = "🟢 IMPROVING"

    elif change < -1:

        trend = "🔴 DETERIORATING"

    else:

        trend = "🟡 STABLE"

    return {
        "trend": trend,
        "change": change
    }


