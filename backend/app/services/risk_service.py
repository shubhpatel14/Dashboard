from app.services.regime_service import build_regime_engine
from app.engines.risk.engine import calculate_risks


def get_risk_analysis() -> dict:
    """
    Combines Regime Engine outputs and calculates the macroeconomic risks.
    """
    # 1. Get macro scores and regime probabilities
    regime_data = build_regime_engine()

    macro_scores = regime_data.get("macro", {})
    probabilities = regime_data.get("probabilities", {})

    # 2. Pass them to the risk engine
    risks = calculate_risks(macro_scores, probabilities)

    # 3. Format the return structure
    regime_val = regime_data.get("regime", {})
    if isinstance(regime_val, dict):
        regime_str = regime_val.get("regime", "Neutral")
    else:
        regime_str = str(regime_val)

    transition_val = regime_data.get("transition", {})
    if isinstance(transition_val, dict):
        transition_str = transition_val.get("message", "Neutral regime stable")
    else:
        transition_str = str(transition_val)

    return {
        "regime": regime_str,
        "transition": transition_str,
        "risks": risks
    }
