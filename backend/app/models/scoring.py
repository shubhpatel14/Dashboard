def pct_change(current, previous):

    if previous == 0:
        return 0

    return ((current - previous) / previous) * 100


def score_positive(change):

    if change >= 10:
        return 100

    elif change >= 5:
        return 75

    elif change >= 0:
        return 50

    elif change >= -5:
        return 25

    return 0


def score_negative(change):

    if change <= -10:
        return 100

    elif change <= -5:
        return 75

    elif change <= 0:
        return 50

    elif change <= 5:
        return 25

    return 0


def weighted_average(values):

    total_score = 0
    total_weight = 0

    for score, weight in values:
        if not isinstance(score, (int, float)):
            continue

        if not isinstance(weight, (int, float)) or weight <= 0:
            continue

        total_score += clamp_score(score) * weight
        total_weight += weight

    if total_weight == 0:
        return 50

    return round(
        total_score / total_weight,
        2
    )


def normalize(
    value,
    minimum,
    maximum
):
    if maximum == minimum:
        return 50

    if value <= minimum:
        return 0

    if value >= maximum:
        return 100

    return round(
        (
            (value - minimum)
            /
            (maximum - minimum)
        ) * 100,
        2
    )


def bias_from_score(score):

    if score >= 80:
        return "Very Bullish"

    if score >= 65:
        return "Bullish"

    if score >= 45:
        return "Neutral"

    if score >= 25:
        return "Bearish"

    return "Very Bearish"


def clamp_score(score):

    return round(
        max(
            0,
            min(
                100,
                score
            )
        ),
        2
    )


def status_from_score(score):

    if score >= 60:
        return "GREEN"

    if score <= 40:
        return "RED"

    return "YELLOW"


def status_label_from_score(score):

    if score >= 60:
        return "Bullish / Risk-On"

    if score <= 40:
        return "Bearish / Risk-Off"

    return "Neutral"


def indicator_result(
    current,
    previous,
    change,
    score,
    name=None,
    last_update=None,
    last_updated=None,
    consensus=None,
    surprise=None,
    status=None,
    status_label=None,
    **extra
):

    score = clamp_score(score)

    updated_at = last_updated or last_update

    result = {
        "current": round(current, 2),
        "previous": round(previous, 2),
        "change": round(change, 2),
        "consensus": consensus,
        "surprise": surprise,
        "last_update": updated_at,
        "last_updated": updated_at,
        "score": score,
        "bias": bias_from_score(score),
        "status": status or status_from_score(score),
        "status_label": status_label or status_label_from_score(score)
    }

    if name:
        result["name"] = name

    result.update(extra)

    return result


def engine_result(
    score,
    data,
    **extra
):

    score = round(score, 2)

    result = {
        "score": score,
        "bias": bias_from_score(score),
        "data": data
    }

    result.update(extra)

    return result

