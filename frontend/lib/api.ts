const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api";

export async function fetchApi<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${path}`);
  }

  return response.json() as Promise<T>;
}

export const assets = ["Gold", "Bitcoin", "SP500", "Nasdaq", "Dollar", "Bonds"];
export const assetSlugs = ["gold", "bitcoin", "sp500", "nasdaq", "dollar", "bonds"];

export const macroCategories = [
  ["Liquidity", "liquidity"],
  ["Global Liquidity", "global-liquidity"],
  ["Rates", "rates"],
  ["Inflation", "inflation"],
  ["Growth", "growth"],
  ["Labor", "labor"],
  ["Credit", "credit"],
  ["Sentiment", "sentiment"],
  ["Housing", "housing"],
  ["Recession", "recession"]
] as const;
