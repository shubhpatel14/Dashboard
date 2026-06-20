def classify_regime(score):

    if score >= 85:
        return "🚀 STRONG RISK ON"

    if score >= 70:
        return "🟢 BULLISH"

    if score >= 50:
        return "🟡 NEUTRAL"

    if score >= 30:
        return "🟠 BEARISH"

    return "🔴 RISK OFF"


