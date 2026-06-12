import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, Gauge, LineChart, Table2 } from "lucide-react";
import { fetchApi, macroCategories } from "@/lib/api";
import { biasFromScore, clampScore, formatNumber, titleCase } from "@/lib/format";
import { ScoreLine } from "@/components/lazy-charts";
import { BiasPill, Panel, ScoreBar, SectionTitle, StatCard } from "@/components/ui";
import type { Indicator, MacroCategory } from "@/types/api";

export const dynamic = "force-dynamic";

type FoundIndicator = {
  category: string;
  categorySlug: string;
  indicator: Indicator;
};

function normalizeId(value: string) {
  return decodeURIComponent(value).toLowerCase().replace(/[\s-]+/g, "_");
}

function matches(indicator: Indicator, requested: string) {
  const candidates = [indicator.key, indicator.code, indicator.name]
    .filter(Boolean)
    .map((value) => normalizeId(String(value)));
  return candidates.includes(normalizeId(requested));
}

function fallbackCategory(slug: string): MacroCategory {
  return {
    success: false,
    data_status: "fallback",
    name: titleCase(slug),
    score: 50,
    bias: "Neutral",
    trend: "Stable",
    summary: "Category temporarily unavailable.",
    drivers: [],
    indicators: [],
    explanation: "Category temporarily unavailable.",
    history: [{ date: "Current", score: 50 }]
  };
}

async function findIndicator(id: string): Promise<FoundIndicator | null> {
  for (const [label, slug] of macroCategories) {
    const data = await fetchApi<MacroCategory>(`/macro/${slug}`, { fallback: fallbackCategory(slug), retries: 1 });
    const indicators = Array.isArray(data.indicators) ? data.indicators : [];
    const indicator = indicators.find((item) => matches(item, id));
    if (indicator) {
      return { category: label, categorySlug: slug, indicator };
    }
  }

  return null;
}

function marketImpactMatrix(score: number) {
  const weak = score <= 40;
  const strong = score >= 60;

  return [
    ["Stocks", strong ? "Positive" : weak ? "Negative" : "Neutral"],
    ["Gold", weak ? "Positive" : strong ? "Neutral" : "Neutral"],
    ["USD", weak ? "Positive" : strong ? "Neutral" : "Neutral"],
    ["Bonds", strong ? "Negative" : weak ? "Positive" : "Neutral"],
  ];
}

export default async function IndicatorPage({ params }: { params: { indicator: string } }) {
  const found = await findIndicator(params.indicator);

  if (!found) {
    notFound();
  }

  const { indicator, category, categorySlug } = found;
  const score = clampScore(indicator.score);
  const current = indicator.current_display ?? formatNumber(indicator.current);
  const previous = indicator.previous_display ?? formatNumber(indicator.previous);
  const historicalRows = [
    { date: "Previous", score: clampScore(indicator.previous, score), value: previous },
    { date: "Current", score, value: current },
  ];

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-end justify-between gap-4 border-b border-line pb-4">
        <div>
          <Link href={`/macro?category=${categorySlug}`} className="mb-3 inline-flex items-center gap-2 text-sm font-semibold text-muted hover:text-ink">
            <ArrowLeft className="h-4 w-4" aria-hidden="true" />
            {category}
          </Link>
          <div className="text-xs font-semibold uppercase text-muted">Indicator Analysis</div>
          <h1 className="mt-1 text-2xl font-semibold tracking-normal">{indicator.name}</h1>
        </div>
        <BiasPill value={indicator.bias || biasFromScore(score)} />
      </header>

      <section className="grid gap-3 md:grid-cols-4">
        <StatCard label="Current Value" value={current} />
        <StatCard label="Macro Signal" value={indicator.bias || biasFromScore(score)} />
        <StatCard label="Percentile" value={`${formatNumber(indicator.percentile ?? 50)}%`} />
        <StatCard label="Z-Score" value={formatNumber(indicator.z_score ?? 0)} />
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <Panel>
          <SectionTitle title="Historical Chart" action={<LineChart className="h-4 w-4 text-muted" />} />
          <ScoreLine data={historicalRows} name={`${indicator.name} Signal`} />
        </Panel>

        <Panel>
          <SectionTitle title="Current vs History" action={<Gauge className="h-4 w-4 text-muted" />} />
          <div className="space-y-4">
            {[
              ["Current", current],
              ["Average", previous],
              ["Percentile", `${formatNumber(indicator.percentile ?? 50)}%`],
              ["Z-score", formatNumber(indicator.z_score ?? 0)],
              ["Distance from average", formatNumber(indicator.distance_from_average ?? 0)]
            ].map(([label, value]) => (
              <div key={label} className="flex items-center justify-between border-b border-line pb-3 last:border-0">
                <span className="text-xs font-semibold uppercase text-muted">{label}</span>
                <span className="text-sm font-semibold text-ink">{value}</span>
              </div>
            ))}
            <ScoreBar score={score} height="h-3" />
          </div>
        </Panel>
      </section>

      <Panel>
        <SectionTitle title="Macro Explanation" />
        <p className="max-w-5xl text-sm leading-6 text-ink">
          {indicator.explanation || indicator.info || `${indicator.name} currently screens ${biasFromScore(score).toLowerCase()} for macro conditions.`}
        </p>
      </Panel>

      <section className="grid gap-4 xl:grid-cols-[0.8fr_1.2fr]">
        <Panel>
          <SectionTitle title="Market Impact Matrix" />
          <div className="space-y-2">
            {marketImpactMatrix(score).map(([asset, impact]) => (
              <div key={asset} className="flex items-center justify-between rounded-lg border border-line bg-canvas px-3 py-2">
                <span className="text-sm font-semibold text-ink">{asset}</span>
                <BiasPill value={impact} />
              </div>
            ))}
          </div>
        </Panel>

        <Panel>
          <SectionTitle title="Data Table" action={<Table2 className="h-4 w-4 text-muted" />} />
          <div className="overflow-x-auto terminal-scrollbar">
            <table className="w-full min-w-[540px] text-left text-sm">
              <thead className="border-b border-line text-xs uppercase text-muted">
                <tr>
                  <th className="py-2 pr-4">Date</th>
                  <th className="py-2 pr-4">Value</th>
                  <th className="py-2 pr-4">Change</th>
                  <th className="py-2 pr-4">Score</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-line">
                  <td className="py-3 pr-4">Previous</td>
                  <td className="py-3 pr-4">{previous}</td>
                  <td className="py-3 pr-4">N/A</td>
                  <td className="py-3 pr-4">{formatNumber(clampScore(indicator.previous, score))}</td>
                </tr>
                <tr>
                  <td className="py-3 pr-4">Current</td>
                  <td className="py-3 pr-4">{current}</td>
                  <td className="py-3 pr-4">{indicator.change_display ?? formatNumber(indicator.change)}</td>
                  <td className="py-3 pr-4">{formatNumber(score)}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </Panel>
      </section>
    </div>
  );
}
