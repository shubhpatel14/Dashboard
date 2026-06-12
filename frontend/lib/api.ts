export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

const staleCache = new Map<string, unknown>();

type FetchOptions<T> = {
  fallback?: T;
  retries?: number;
};

export async function fetchApi<T>(
  path: string,
  options: FetchOptions<T> = {}
): Promise<T> {
  const retries = options.retries ?? 2;
  let lastError: unknown;

  for (let attempt = 0; attempt <= retries; attempt += 1) {
    try {
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

      const data = await response.json() as T;
      staleCache.set(path, data);
      return data;
    } catch (error) {
      lastError = error;
      if (attempt < retries) {
        await new Promise((resolve) => setTimeout(resolve, 150 * (attempt + 1)));
      }
    }
  }

  if (staleCache.has(path)) {
    return staleCache.get(path) as T;
  }

  if (options.fallback !== undefined) {
    return options.fallback;
  }

  throw lastError instanceof Error ? lastError : new Error(`API request failed: ${API_URL}${path}`);
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

