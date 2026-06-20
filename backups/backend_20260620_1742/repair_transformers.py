from pathlib import Path

path = Path("app/services/transformers.py")

txt = path.read_text(encoding="utf-8")


append = r'''


# ==================================================
# Compatibility functions
# ==================================================

def macro_category_intelligence(name, score, bias, indicators):

    drivers = []

    for i in indicators:
        if isinstance(i, dict):
            drivers.append(
                i.get("name", "Unknown")
            )

    return {
        "trend": bias,
        "summary": f"{name} is currently {bias} with score {score}.",
        "drivers": drivers,
    }



def macro_category_history(slug, score):

    return [
        {
            "period": "current",
            "score": score
        }
    ]



def macro_summary(macro):

    score = macro.get(
        "score",
        50
    )

    return (
        f"Macro environment score is {score}"
    )

'''


if "def macro_category_intelligence" not in txt:
    txt += append


path.write_text(
    txt,
    encoding="utf-8"
)


print("transformers compatibility restored")
