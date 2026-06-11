import Link from "next/link";
import { Activity, BarChart3, Database, Minus, TrendingDown, TrendingUp } from "lucide-react";
import { fetchApi, macroCategories } from "@/lib/api";
import { formatNumber } from "@/lib/format";
import { IndicatorTrendChart, ScoreLine } from "@/components/lazy-charts";
import { BiasPill, InfoHint, Panel, SectionTitle, StatCard } from "@/components/ui";
import type { Indicator, MacroCategory, MacroDriver } from "@/types/api";

export const dynamic = "force-dynamic";

function trendTone(state: string) {
  if (state === "positive") {
    return "border-positive text-positive";
  }
  if (state === "negative") {
    return "border-negative text-negative";
  }
  return "border-neutral text-neutral";
}

function trendBg(state: string) {
  if (state === "positive") {
    return "bg-positive";
  }
  if (state === "negative") {
    return "bg-negative";
  }
  return "bg-neutral";
}

function TrendIcon({ state }: { state: string }) {
  if (state === "positive") {
    return <TrendingUp className="h-4 w-4" aria-hidden="true" />;
  }
  if (state === "negative") {
    return <TrendingDown className="h-4 w-4" aria-hidden="true" />;
  }
  return <Minus className="h-4 w-4" aria-hidden="true" />;
}

function DriverRow({ driver }: { driver: MacroDriver }) {
  return (
    <div className="grid grid-cols-[1fr_auto] items-center gap-3 border-b border-line py-3 last:border-b-0">
      <div className="min-w-0">
        <div className="flex min-w-0 items-center gap-2">
          <span className={trendTone(driver.trend_state)}>
            <TrendIcon state={driver.trend_state} />
          </span>
          <div className="truncate text-sm font-semibold text-ink">{driver.name}</div>
        </div>
        <div className="mt-1 text-xs text-muted">{driver.trend}</div>
      </div>
      <div className="text-right">
        <div className="text-sm font-semibold text-ink">{driver.value}</div>
        <div className="text-xs text-muted">{formatNumber(driver.score)}/100</div>
      </div>
    </div>
  );
}

function trendStateFromScore(score: number) {
  if (score >= 60) {
    return "positive";
  }
  if (score <= 40) {
    return "negative";
  }
  return "neutral";
}

function trendLabel(state: string) {
  if (state === "positive") {
    return "Improving";
  }
  if (state === "negative") {
    return "Worsening";
  }
  return "Neutral";
}

function normalizedWeight(value: unknown) {
  const number = Number(value);
  return Number.isFinite(number) && number > 0 ? number : 10;
}

function normalizeIndicators(indicators: Indicator[]): Indicator[] {
  return indicators.map((indicator, index) => {
    const score = Number.isFinite(Number(indicator.score)) ? Number(indicator.score) : 50;
    const trend_state = indicator.trend_state ?? trendStateFromScore(score);
    const trend = indicator.trend ?? trendLabel(trend_state);
    const weight = normalizedWeight(indicator.weight);
    const current_display = indicator.current_display ?? formatNumber(indicator.current);
    const previous_display = indicator.previous_display ?? formatNumber(indicator.previous);
    const change_display = indicator.change_display ?? formatNumber(indicator.change);

    return {
      ...indicator,
      key: indicator.key ?? `${indicator.name ?? "indicator"}-${index}`,
      name: indicator.name ?? `Indicator ${index + 1}`,
      code: indicator.code ?? "N/A",
      source: indicator.source ?? "N/A",
      measures: indicator.measures ?? "Macro input.",
      score,
      bias: indicator.bias ?? "Neutral",
      current: indicator.current ?? "N/A",
      previous: indicator.previous ?? "N/A",
      change: indicator.change ?? "N/A",
      current_display,
      previous_display,
      change_display,
      trend,
      trend_state,
      impact: indicator.impact ?? trend,
      market_impact: indicator.market_impact ?? "Used as part of the macro score.",
      last_update: indicator.last_update ?? "N/A",
      explanation: indicator.explanation || `${indicator.name ?? "This indicator"} is currently ${trend.toLowerCase()}.`,
      info: indicator.info ?? `Source: ${indicator.source ?? "N/A"}`,
      weight,
      contribution: indicator.contribution ?? roundContribution(score, weight)
    };
  });
}

function roundContribution(score: number, weight: number) {
  return Math.round((score / 100) * weight * 100) / 100;
}

function ContributionBars({ drivers }: { drivers: MacroDriver[] }) {
  const maxWeight = Math.max(...drivers.map((driver) => normalizedWeight(driver.weight)), 1);

  return (
    <div className="space-y-3">
      {drivers.map((driver) => (
        <div key={driver.name} className="grid gap-2 sm:grid-cols-[170px_1fr_64px] sm:items-center">
          <div className="truncate text-sm text-ink">{driver.name}</div>
          <div className="h-2 overflow-hidden bg-canvas">
            <div
              className={`h-full ${trendBg(driver.trend_state)}`}
              style={{ width: `${Math.max(6, (normalizedWeight(driver.weight) / maxWeight) * 100)}%` }}
            />
          </div>
          <div className="text-xs font-semibold text-muted sm:text-right">{formatNumber(driver.weight)}%</div>
        </div>
      ))}
    </div>
  );
}

function driversFromIndicators(indicators: Indicator[]): MacroDriver[] {
  return indicators.map((indicator) => ({
    name: indicator.name,
    trend: indicator.trend,
    trend_state: indicator.trend_state,
    value: indicator.current_display,
    score: indicator.score,
    contribution: indicator.contribution,
    weight: indicator.weight
  }));
}

function normalizeDrivers(drivers: MacroDriver[] | undefined, indicators: Indicator[]): MacroDriver[] {
  if (!Array.isArray(drivers) || drivers.length === 0) {
    return driversFromIndicators(indicators);
  }

  return drivers.map((driver, index) => {
    const indicator = indicators[index];
    const score = Number.isFinite(Number(driver.score)) ? Number(driver.score) : indicator?.score ?? 50;
    const trend_state = driver.trend_state ?? indicator?.trend_state ?? trendStateFromScore(score);
    const weight = normalizedWeight(driver.weight ?? indicator?.weight);

    return {
      name: driver.name ?? indicator?.name ?? `Driver ${index + 1}`,
      trend: driver.trend ?? indicator?.trend ?? trendLabel(trend_state),
      trend_state,
      value: driver.value ?? indicator?.current_display ?? "N/A",
      score,
      contribution: driver.contribution ?? indicator?.contribution ?? roundContribution(score, weight),
      weight
    };
  });
}

function IndicatorCard({ indicator }: { indicator: Indicator }) {
  return (
    <article className={`border bg-surface p-4 shadow-terminal ${trendTone(indicator.trend_state)}`}>
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-base font-semibold text-ink">
          {indicator.name} <InfoHint text={indicator.info || indicator.market_impact} />
        </h3>
        <BiasPill value={indicator.bias} />
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <div>
          <div className="text-xs font-semibold uppercase text-muted">Current</div>
          <div className="mt-1 text-lg font-semibold text-ink">{indicator.current_display}</div>
        </div>
        <div>
          <div className="text-xs font-semibold uppercase text-muted">Previous</div>
          <div className="mt-1 text-lg font-semibold text-ink">{indicator.previous_display}</div>
        </div>
        <div>
          <div className="text-xs font-semibold uppercase text-muted">Change</div>
          <div className={`mt-1 text-lg font-semibold ${trendTone(indicator.trend_state)}`}>
            {indicator.change_display}
          </div>
        </div>
      </div>

      <div className="mt-4 grid gap-3 border-t border-line pt-4 md:grid-cols-[1fr_1fr_90px]">
        <div>
          <div className="text-xs font-semibold uppercase text-muted">Trend</div>
          <div className={`mt-1 flex items-center gap-2 text-sm font-semibold ${trendTone(indicator.trend_state)}`}>
            <TrendIcon state={indicator.trend_state} />
            {indicator.trend}
          </div>
          <p className="mt-2 text-sm leading-6 text-muted">{indicator.explanation}</p>
        </div>
        <div>
          <div className="text-xs font-semibold uppercase text-muted">Market Impact</div>
          <div className="mt-1 text-sm font-semibold text-ink">{indicator.impact}</div>
          <p className="mt-2 text-sm leading-6 text-muted">{indicator.market_impact}</p>
        </div>
        <div>
          <div className="text-xs font-semibold uppercase text-muted">Score</div>
          <div className="mt-1 text-xl font-semibold text-ink">{formatNumber(indicator.score)}/100</div>
        </div>
      </div>
    </article>
  );
}

export default async function MacroPage({
  searchParams
}: {
  searchParams: { category?: string };
}) {
  const selected = searchParams.category ?? "liquidity";
  const data = await fetchApi<MacroCategory>(`/macro/${selected}`);
  const indicators = normalizeIndicators(Array.isArray(data.indicators) ? data.indicators : []);
  const drivers = normalizeDrivers(data.drivers, indicators);
  const history = Array.isArray(data.history) ? data.history : [];
  const summary = data.summary ?? data.explanation ?? `${data.name} score is ${formatNumber(data.score)}.`;
  const trend = data.trend ?? trendLabel(trendStateFromScore(Number(data.score)));

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-end justify-between gap-4 border-b border-line pb-4">
        <div>
          <div className="text-xs font-semibold uppercase text-muted">Macro Intelligence</div>
          <h1 className="mt-1 text-2xl font-semibold tracking-normal">{data.name} Intelligence</h1>
        </div>
        <BiasPill value={data.bias} />
      </header>

      <nav className="flex flex-wrap gap-2" aria-label="Macro modules">
        {macroCategories.map(([label, slug]) => (
          <Link
            key={slug}
            href={`/macro?category=${slug}`}
            className={`border px-3 py-2 text-sm ${selected === slug ? "border-ink bg-white text-ink" : "border-line text-muted"}`}
          >
            {label}
          </Link>
        ))}
      </nav>

      <section className="grid gap-3 md:grid-cols-[1.4fr_0.6fr_0.6fr_0.6fr]">
        <Panel className="flex flex-col justify-center">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase text-muted">
            <Activity className="h-4 w-4" aria-hidden="true" />
            What happened
          </div>
          <p className="mt-3 text-lg font-semibold leading-7 text-ink">{summary}</p>
        </Panel>
        <StatCard label="Score" value={`${formatNumber(data.score)}/100`} />
        <StatCard label="Bias" value={data.bias} />
        <StatCard label="Trend" value={trend} />
      </section>

      <section className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
        <Panel>
          <SectionTitle title={`${data.name} Drivers`} />
          <div>
            {drivers.map((driver) => (
              <DriverRow key={driver.name} driver={driver} />
            ))}
          </div>
        </Panel>

        <Panel>
          <SectionTitle
            title="Component Contribution"
            action={<BarChart3 className="h-4 w-4 text-muted" aria-hidden="true" />}
          />
          <ContributionBars drivers={drivers} />
        </Panel>
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        <Panel>
          <SectionTitle title="Score History" />
          <ScoreLine data={history} name={`${data.name} Score`} />
        </Panel>

        <Panel>
          <SectionTitle title="Indicator Trend Chart" />
          <IndicatorTrendChart indicators={indicators} />
        </Panel>
      </section>

      <section className="space-y-3">
        <div className="flex items-center gap-2 text-sm font-semibold uppercase text-ink">
          <Activity className="h-4 w-4" aria-hidden="true" />
          Indicator Intelligence
        </div>
        <div className="grid gap-4">
          {indicators.map((indicator) => (
            <IndicatorCard key={indicator.key} indicator={indicator} />
          ))}
        </div>
      </section>

      <details className="border border-line bg-surface p-4 shadow-terminal">
        <summary className="flex cursor-pointer list-none items-center gap-2 text-sm font-semibold uppercase text-ink">
          <Database className="h-4 w-4 text-muted" aria-hidden="true" />
          Show Advanced Data
        </summary>
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[760px] border-collapse text-sm">
            <thead>
              <tr className="border-b border-line text-left text-xs uppercase text-muted">
                <th className="py-2 pr-4 font-semibold">Indicator</th>
                <th className="py-2 pr-4 font-semibold">FRED Code</th>
                <th className="py-2 pr-4 font-semibold">Current</th>
                <th className="py-2 pr-4 font-semibold">Previous</th>
                <th className="py-2 pr-4 font-semibold">Change %</th>
                <th className="py-2 pr-4 font-semibold">Score</th>
              </tr>
            </thead>
            <tbody>
              {indicators.map((indicator) => (
                <tr key={indicator.key} className="border-b border-line last:border-b-0">
                  <td className="py-2 pr-4 text-ink">{indicator.name}</td>
                  <td className="py-2 pr-4 text-muted">{indicator.code}</td>
                  <td className="py-2 pr-4 text-ink">{formatNumber(indicator.current)}</td>
                  <td className="py-2 pr-4 text-ink">{formatNumber(indicator.previous)}</td>
                  <td className="py-2 pr-4 text-ink">{formatNumber(indicator.change)}</td>
                  <td className="py-2 pr-4 text-ink">{formatNumber(indicator.score)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </div>
  );
}
