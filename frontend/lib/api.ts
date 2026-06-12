export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";


export async function fetchApi<T>(
  path: string
): Promise<T> {

  const response = await fetch(
    `${API_URL}${path}`,
    {
      cache: "no-store",
    }
  );


  if (!response.ok) {
    throw new Error(
      `API request failed: ${response.status} ${API_URL}${path}`
    );
  }


  return response.json() as Promise<T>;
}


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

export const assetLabels: Record<string, string> = {
  gold: "Gold",
  bitcoin: "Bitcoin",
  sp500: "SP500",
  nasdaq: "Nasdaq",
  dollar: "Dollar",
  bonds: "Bonds",
};

export const assets = assetSlugs.map((slug) => assetLabels[slug]);

