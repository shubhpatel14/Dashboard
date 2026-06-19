def clamp(val: float) -> int:
    return max(0, min(100, int(round(val))))


def calculate_risks(macro_scores: dict, probabilities: dict) -> dict:
    """
    Calculate risk metrics based on macro scores and regime probabilities.
    All returned component scores and overall score are integers between 0 and 100.
    """
    # Safe extraction of inputs with default values
    growth = float(macro_scores.get("growth", 50.0))
    credit = float(macro_scores.get("credit", 50.0))
    inflation = float(macro_scores.get("inflation", 50.0))
    rates = float(macro_scores.get("rates", 50.0))
    liquidity = float(macro_scores.get("liquidity", 50.0))

    recession_prob = float(probabilities.get("Recession", 25.0))

    # 1. Recession Risk: higher when growth and credit are weak (low), and recession probability is high
    recession_risk = clamp(0.40 * (100.0 - growth) + 0.35 * (100.0 - credit) + 0.25 * recession_prob)

    # 2. Inflation Risk: higher when inflation pressure is high (inflation score is low), and policy is easy (rates score is high)
    inflation_risk = clamp(0.60 * (100.0 - inflation) + 0.40 * rates)

    # 3. Liquidity Stress: higher when liquidity is low, and credit is low
    liquidity_stress = clamp(0.50 * (100.0 - liquidity) + 0.50 * (100.0 - credit))

    # 4. Credit Stress: higher when credit score is weak (low)
    credit_stress = clamp(100.0 - credit)

    # 5. Market Overheating Risk: higher when growth is strong, liquidity is easy (high), and inflation pressure is high (low inflation score)
    market_overheating = clamp(0.40 * growth + 0.30 * liquidity + 0.30 * (100.0 - inflation))

    components = {
        "recession_risk": recession_risk,
        "inflation_risk": inflation_risk,
        "liquidity_stress": liquidity_stress,
        "credit_stress": credit_stress,
        "market_overheating": market_overheating
    }

    # Overall score is the simple average of all components
    overall_score = clamp(sum(components.values()) / len(components))

    # Determine qualitative risk state
    if overall_score < 35:
        state = "Low Risk"
    elif overall_score >= 60:
        state = "High Risk"
    else:
        state = "Moderate Risk"

    return {
        "overall_score": overall_score,
        "state": state,
        "components": components
    }
