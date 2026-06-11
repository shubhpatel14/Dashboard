from pathlib import Path

file = Path("lib/api.ts")

text = file.read_text(encoding="utf-8")


add = r'''


export const macroCategories = [
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


export const assetSlugs = [
  "gold",
  "bitcoin",
  "sp500",
  "nasdaq",
  "dollar",
  "bonds",
];

'''


if "export const macroCategories" not in text:
    text += add


file.write_text(
    text,
    encoding="utf-8"
)


print("api exports fixed")
