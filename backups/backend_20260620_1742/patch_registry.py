from pathlib import Path

path = Path("app/services/engine_registry.py")

text = path.read_text(encoding="utf-8")


patch = r'''


# ==================================================
# API COMPATIBILITY LAYER
# ==================================================


def _run_engine(builder):

    result = builder()

    if result is None:
        return {}

    return result



def get_macro_category(name: str):

    builder = MACRO_BUILDERS.get(name)

    if builder is None:
        return {}

    return _run_engine(builder)



def get_asset_engine(name: str):

    builder = ASSET_BUILDERS.get(name)

    if builder is None:
        return {}

    return _run_engine(builder)



def get_macro_engine():

    return get_macro_category("macro")



def get_trend_engine():

    return get_macro_category("trend")



def macro_regime(score):

    if score >= 65:
        return "Expansion"

    if score <= 35:
        return "Contraction"

    return "Neutral"



def refresh_engine_cache():

    get_engines.cache_clear()

    return {
        "status":"refreshed"
    }



def get_institutional_engine():

    assets = {}

    for key in ASSET_BUILDERS:

        assets[key.capitalize()] = {

            "long_percent":0,
            "short_percent":0,
            "net_position":0,
            "weekly_change":0,
            "velocity_4w":0,
            "bias":"Neutral",
            "score":50,
            "position_percentile":50,
            "trend":[]

        }


    return {
        "assets":assets
    }


'''


if "def get_asset_engine" not in text:
    text += patch


path.write_text(text,encoding="utf-8")


print("engine_registry patched")

