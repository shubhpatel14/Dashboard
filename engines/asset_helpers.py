from models.scoring import bias_from_score, weighted_average


def driver_row(name, score, source=None):

    row = {
        "name": name,
        "current": round(score, 2),
        "previous": round(score, 2),
        "change": 0,
        "score": round(score, 2),
        "bias": bias_from_score(score),
        "last_update": "N/A",
        "last_updated": "N/A"
    }

    if isinstance(source, dict):
        row["current"] = source.get("current", row["current"])
        row["previous"] = source.get("previous", row["previous"])
        row["change"] = source.get("change", row["change"])
        row["last_update"] = source.get("last_update", row["last_update"])
        row["last_updated"] = source.get("last_updated", row["last_updated"])

    return row


def weighted_asset_result(drivers):

    score = weighted_average(
        (driver["score"], driver["weight"])
        for driver in drivers
    )

    return {
        "score": round(score, 2),
        "outlook": bias_from_score(score),
        "data": {
            driver["key"]: {
                key: value
                for key, value in driver.items()
                if key not in {"key", "weight"}
            }
            for driver in drivers
        },
        "components": {
            driver["key"]: round(driver["score"], 2)
            for driver in drivers
        },
        "weights": {
            driver["key"]: driver["weight"]
            for driver in drivers
        }
    }
