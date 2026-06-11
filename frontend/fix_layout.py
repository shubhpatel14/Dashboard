from pathlib import Path

file = Path("app/layout.tsx")

text = file.read_text(encoding="utf-8")


# add fallback macro categories
insert = '''

const macroCategories = [
  ["Inflation", "inflation"],
  ["Labor", "labor"],
  ["Liquidity", "liquidity"],
  ["Global Liquidity", "global_liquidity"],
  ["Rates", "rates"],
  ["Growth", "growth"],
  ["Credit", "credit"],
  ["Housing", "housing"],
  ["Recession", "recession"],
  ["Sentiment", "sentiment"],
  ["Trend", "trend"],
];

'''


if "const macroCategories" not in text:

    idx = text.find("export default")

    text = (
        text[:idx]
        + insert
        + text[idx:]
    )


file.write_text(text,encoding="utf-8")

print("layout fixed")
