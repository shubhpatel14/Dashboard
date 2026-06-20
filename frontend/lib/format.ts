export function toneClass(value: string | number) {
  const text = String(value).toLowerCase();
  const numeric = typeof value === "number" ? value : Number.NaN;

  if (text.includes("bull") || text.includes("risk on") || text.includes("risk-on") || text.includes("positive") || numeric >= 65) {
    return "text-positive";
  }
  if (text.includes("bear") || text.includes("risk off") || text.includes("risk-off") || text.includes("negative") || numeric <= 35) {
    return "text-negative";
  }
  return "text-neutral";
}

export function formatNumber(value: string | number | null | undefined) {
  if (value === undefined || value === null || value === "N/A") {
    return "N/A";
  }

  const numeric = Number(value);
  if (!Number.isFinite(numeric)) {
    return String(value);
  }

  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 2
  }).format(numeric);
}

export function toNumber(value: unknown, fallback = 0) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : fallback;
}

export function clampScore(value: unknown, fallback = 50) {
  return Math.max(0, Math.min(100, toNumber(value, fallback)));
}

export function asArray<T>(value: T[] | T | null | undefined): T[] {
  if (Array.isArray(value)) {
    return value;
  }
  if (value === undefined || value === null) {
    return [];
  }
  return [value];
}

const LABEL_SPECIAL_CASES: Record<string, string> = {
  "n/a": "N/A",
  "s&p": "S&P",
  sp500: "SP500",
  nasdaq: "NASDAQ",
  usd: "USD",
  cpi: "CPI",
  pce: "PCE",
  gdp: "GDP",
  fed: "FED"
};

export function formatLabel(value?: string) {
  if (!value) {
    return "N/A";
  }

  return value
    .replaceAll("_", " ")
    .split(" ")
    .filter(Boolean)
    .map((word) => {
      const normalized = word.toLowerCase();

      if (LABEL_SPECIAL_CASES[normalized]) {
        return LABEL_SPECIAL_CASES[normalized];
      }

      if (/^[A-Z0-9]+$/.test(word)) {
        return word;
      }

      return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    })
    .join(" ");
}

export function titleCase(value: string) {
  return formatLabel(value);
}

export function regimeFromScore(score: unknown) {
  const numeric = clampScore(score);
  if (numeric < 35) {
    return "Risk Off";
  }
  if (numeric > 65) {
    return "Risk On";
  }
  return "Neutral";
}

export function biasFromScore(score: unknown) {
  const numeric = clampScore(score);
  if (numeric < 40) {
    return "Bearish";
  }
  if (numeric > 60) {
    return "Bullish";
  }
  return "Neutral";
}
