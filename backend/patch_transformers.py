from pathlib import Path

file = Path("app/services/transformers.py")

text = file.read_text(encoding="utf-8")

start = text.index("def indicators_from_engine")

# find next function after drivers_from_asset
end_marker = "\ndef "
pos = text.index("def drivers_from_asset")
end = text.find(end_marker, pos + 5)

if end == -1:
    end = len(text)


new_code = r'''

def indicators_from_engine(engine):

    indicators = []

    data = engine.get("data", {})

    for key, item in data.items():

        indicators.append({
            "id": key,
            "name": item.get("name", key),
            "current": item.get("current"),
            "previous": item.get("previous"),
            "change": item.get("change"),
            "score": item.get("score", 50),
            "bias": item.get("bias", "Neutral"),
            "last_updated": item.get(
                "last_updated",
                item.get("last_update", "N/A")
            )
        })

    return indicators



def drivers_from_asset(engine):

    drivers = []

    for item in indicators_from_engine(engine):

        score = item.get("score", 50)

        drivers.append({

            "name": item["name"],

            "score": score,

            "bias": item["bias"],

            "impact":
                "Positive"
                if score > 55
                else "Negative"
                if score < 45
                else "Neutral",

            "current": item["current"],

            "change": item["change"],

            "last_updated": item["last_updated"],

        })

    return drivers

'''


text = text[:start] + new_code + text[end:]

file.write_text(text,encoding="utf-8")

print("transformers patched ??")
