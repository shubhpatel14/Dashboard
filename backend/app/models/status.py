def get_status(score):

    if score >= 65:
        return "🟢"

    elif score >= 50:
        return "🟡"

    elif score >= 35:
        return "🟠"

    else:
        return "🔴"


def get_regime(score):

    if score >= 75:
        return "🚀 STRONG RISK ON"

    elif score >= 60:
        return "🟢 MILDLY BULLISH"

    elif score >= 45:
        return "🟡 NEUTRAL"

    elif score >= 30:
        return "🟠 BEARISH"

    else:
        return "🔴 RISK OFF"

