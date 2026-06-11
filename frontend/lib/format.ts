export function toneClass(value: string | number) {
  const text = String(value).toLowerCase();
  const numeric = typeof value === "number" ? value : Number.NaN;

  if (text.includes("bull") || text.includes("risk-on") || numeric >= 60) {
    return "text-positive";
  }
  if (text.includes("bear") || text.includes("risk-off") || numeric <= 40) {
    return "text-negative";
  }
  return "text-neutral";
}

export function formatNumber(value: string | number | undefined) {
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
