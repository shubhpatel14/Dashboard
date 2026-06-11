import csv
import os
from datetime import datetime


FILE_NAME = "dashboard_history.csv"


def save_dashboard_snapshot(
    liquidity,
    rates,
    inflation,
    growth,
    labor,
    overall
):

    file_exists = os.path.exists(
        FILE_NAME
    )

    with open(
        FILE_NAME,
        "a",
        newline=""
    ) as file:

        writer = csv.writer(
            file
        )

        if not file_exists:

            writer.writerow([
                "date",
                "liquidity",
                "rates",
                "inflation",
                "growth",
                "labor",
                "overall"
            ])

        writer.writerow([
            datetime.now().strftime(
                "%Y-%m-%d"
            ),
            liquidity,
            rates,
            inflation,
            growth,
            labor,
            overall
        ])