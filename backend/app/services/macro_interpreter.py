# ==================================================
# TRISHULA MACRO INTERPRETER
# Central explanation engine
# ==================================================


def _safe_float(value, default=50):

    try:
        return float(value)

    except Exception:
        return default



# ==================================================
# SCORE STATE HELPERS
# ==================================================


def score_bias(score):

    score = _safe_float(
        score
    )


    if score >= 70:

        return "Very Bullish"


    if score >= 60:

        return "Bullish"


    if score <= 30:

        return "Very Bearish"


    if score <= 40:

        return "Bearish"


    return "Neutral"




def tone_state(score):

    bias = score_bias(
        score
    )


    if "Bullish" in bias:

        return "positive"


    if "Bearish" in bias:

        return "negative"


    return "neutral"





# ==================================================
# MAIN MACRO PAGE INTERPRETATION
# ==================================================


def build_macro_interpretation(
    category,
    score,
    drivers=None
):

    drivers = drivers or {}


    positive=[]
    negative=[]


    for name,data in drivers.items():

        s = _safe_float(
            data.get(
                "score",
                50
            )
        )


        if s >= 60:

            positive.append(name)


        elif s <= 40:

            negative.append(name)



    category = (
        str(category)
        .replace("_"," ")
        .title()
    )


    bias = score_bias(
        score
    )


    text = (
        f"{category} is currently {bias.lower()} "
        "based on current macro conditions."
    )


    if positive:

        text += (
            " Strength comes from "
            +
            ", ".join(positive[:3])
            +
            "."
        )


    if negative:

        text += (
            " Pressure comes from "
            +
            ", ".join(negative[:3])
            +
            "."
        )


    return text





# ==================================================
# TREND ENGINE COMPATIBILITY
# ==================================================


def describe_trend(
    current=None,
    previous=None,
    *args,
    **kwargs
):

    try:

        change = (
            float(current)
            -
            float(previous)
        )


        if change > 0:

            return "Improving"


        if change < 0:

            return "Weakening"


    except Exception:

        pass


    return "Stable"





def explain_trend(
    name,
    score=50,
    *args,
    **kwargs
):

    return (

        f"{name} trend is "
        f"{score_bias(score).lower()}."

    )






# ==================================================
# SURPRISE ENGINE COMPATIBILITY
# ==================================================


def describe_surprise(
    name,
    actual=None,
    forecast=None,
    previous=None,
    score=50,
    *args,
    **kwargs
):


    try:

        diff = (
            float(actual)
            -
            float(forecast)
        )


        if diff > 0:

            result="beat expectations"


        elif diff < 0:

            result="missed expectations"


        else:

            result="matched expectations"



    except Exception:

        result="generated a surprise"



    return (

        f"{name} {result}. "
        f"Signal is {score_bias(score)}."

    )





def explain_release(
    name,
    actual=None,
    forecast=None,
    previous=None,
    score=50,
    *args,
    **kwargs
):


    return describe_surprise(

        name,
        actual,
        forecast,
        previous,
        score

    )





# ==================================================
# EXTRA LEGACY ALIASES
# protects old engines
# ==================================================


def explain_macro(
    *args,
    **kwargs
):

    return build_macro_interpretation(
        *args,
        **kwargs
    )



def market_tone(
    score
):

    return tone_state(
        score
    )