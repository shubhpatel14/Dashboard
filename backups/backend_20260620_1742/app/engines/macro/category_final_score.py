from typing import Dict, Any


CATEGORY_EVENTS = {

    "inflation": [
        "CPI",
        "PPI",
        "PCE"
    ],

    "labor": [
        "Payroll",
        "Claims",
        "Unemployment"
    ],

    "economic_growth": [
        "GDP",
        "Retail",
        "PMI"
    ],

    "monetary_policy": [
        "Fed",
        "Rate"
    ],
}



def build_category_final_score(
    category:str,
    engine:Dict[str,Any],
    surprise:Dict[str,Any],
):


    base = engine.get(
        "score",
        50
    )


    events = surprise.get(
        "events",
        []
    )


    matched=[]


    for e in events:

        name = (
            e.get("name","")
            .lower()
        )


        for key in CATEGORY_EVENTS.get(category, []):

            if key.lower() in name:

                matched.append(
                    e
                )



    if matched:

        surprise_score = sum(
            e.get("score",50)
            for e in matched
        ) / len(matched)


    else:

        surprise_score = 50



    final = (
        base * 0.70
        +
        surprise_score * 0.30
    )


    result = engine.copy()


    result["core_score"] = round(
        base,
        2
    )


    result["surprise_score"] = round(
        surprise_score,
        2
    )


    result["score"] = round(
        final,
        2
    )


    result["surprise_events"] = matched


    return result
