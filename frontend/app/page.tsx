import Link from "next/link";
import { ArrowRight, CircleDollarSign, Database, Minus, TrendingDown, TrendingUp } from "lucide-react";
import { assetLabels, assetSlugs, fetchApi } from "@/lib/api";
import { asArray, biasFromScore, clampScore, formatNumber, regimeFromScore, titleCase, toneClass, toNumber } from "@/lib/format";
import { BiasPill, EmptyState, MacroGauge, Panel, ScoreBar, SectionTitle } from "@/components/ui";
import { TerminalActions } from "@/components/terminal-actions";
import type { AssetResponse, HistoryPoint, MacroDashboard } from "@/types/api";

export const dynamic = "force-dynamic";

type AssetRow = {
  slug: string;
  asset: string;
  score: number;
  bias: string;
  trend: string;
  positives: string[];
  negatives: string[];
};

const fallbackMacro: MacroDashboard = {
  success: false,
  data_status: "fallback",
  macro_score: 50,
  regime: "Neutral",
  trend: "Stable",
  recession_risk: "N/A",
  risk_status: "Neutral",
  summary: ["Macro API is temporarily unavailable. Neutral cached fallback is being used."],
  asset_outlooks: {},
  category_scores: {},
  history: [{ date: "Current", score: 50 }]
};

async function getAsset(slug: string): Promise<AssetRow> {
  const fallback: AssetResponse = {
    asset: assetLabels[slug] || titleCase(slug),
    asset_score: 50,
    outlook: "Unavailable",
    drivers: [],
    summary: "Asset model temporarily unavailable.",
    history: []
  };

  const data = await fetchApi<AssetResponse>(`/assets/${slug}`, { fallback });
  const drivers = Array.isArray(data.drivers) ? data.drivers : [];
  const positives = drivers
    .filter((driver) => clampScore(driver.score) >= 55 || String(driver.bias).toLowerCase().includes("bull"))
    .slice(0, 2)
    .map((driver) => `${driver.name} +${formatNumber(driver.score)}`);
  const negatives = drivers
    .filter((driver) => clampScore(driver.score) <= 45 || String(driver.bias).toLowerCase().includes("bear"))
    .slice(0, 2)
    .map((driver) => `${driver.name} ${formatNumber(driver.score)}`);
  const score = clampScore(data.asset_score);

  return {
    slug,
    asset: data.asset || assetLabels[slug] || titleCase(slug),
    score,
    bias: data.outlook || biasFromScore(score),
    trend: drivers[0]?.bias || biasFromScore(score),
    positives,
    negatives
  };
}

function DirectionIcon({ value }: { value: unknown }) {
  const score = clampScore(value);
  if (score < 40) {
    return <TrendingDown className="h-4 w-4 text-negative" aria-hidden="true" />;
  }
  if (score > 60) {
    return <TrendingUp className="h-4 w-4 text-positive" aria-hidden="true" />;
  }
  return <Minus className="h-4 w-4 text-neutral" aria-hidden="true" />;
}

function metric(history: HistoryPoint[] | undefined, score: number) {
  const rows = Array.isArray(history) ? history : [];
  const previous = rows.length > 1 ? clampScore(rows[rows.length - 2].score ?? rows[rows.length - 2].overall, score) : score;
  const change = Math.round((score - previous) * 100) / 100;
  const last = rows[rows.length - 1];
  return {
    previous,
    change,
    lastUpdated: String(last?.date ?? new Date().toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" }))
  };
}

function trendWindow(history: HistoryPoint[] | undefined, days: number, score: number) {
  const rows = Array.isArray(history) ? history.slice(-days) : [];
  if (rows.length < 2) {
    return "Stable";
  }
  const first = clampScore(rows[0].score ?? rows[0].overall, score);
  const last = clampScore(rows[rows.length - 1].score ?? rows[rows.length - 1].overall, score);
  if (last - first > 1) {
    return "Improving";
  }
  if (last - first < -1) {
    return "Weakening";
  }
  return "Stable";
}

function DataStatus({ status, updated }: { status?: string; updated: string }) {
  const fallback = status && status !== "connected";
  return (
    <div className="rounded-xl border border-line bg-surface px-3 py-2 text-xs shadow-terminal">
      <div className="flex items-center justify-end gap-2 font-semibold uppercase text-ink">
        <span className={`h-2 w-2 rounded-full ${fallback ? "bg-neutral" : "bg-positive"}`} />
        {fallback ? "Using cached data" : "API Connected"}
      </div>
      <div className="mt-1 text-muted">Last update: {updated}</div>
    </div>
  );
}

function AiMacroBrief({ summary, categories }: { summary: string[]; categories: [string, number][] }) {
  const lookup = new Map(categories.map(([name, score]) => [name.toLowerCase(), clampScore(score)]));
  const rows = [
    ["Inflation", lookup.get("inflation")],
    ["Labor", lookup.get("labor")],
    ["Liquidity", lookup.get("liquidity")],
    ["Growth", lookup.get("growth")],
    ["Market Bias", undefined],
  ] as const;

  return (
    <Panel className="h-full">
      <SectionTitle title="AI Macro Brief" />
      <p className="text-sm leading-6 text-ink">
        {summary[0] || "Macro conditions remain neutral while the terminal waits for fresh data."}
      </p>
      <div className="mt-4 grid gap-2 sm:grid-cols-2">
        {rows.map(([label, score]) => {
          const value = score ?? 50;
          return (
            <div key={label} className="flex items-center justify-between rounded-lg border border-line bg-canvas px-3 py-2">
              <span className="text-xs font-semibold uppercase text-muted">{label}</span>
              <span className={toneClass(value) + " text-sm font-semibold"}>{score === undefined ? biasFromScore(value) : biasFromScore(value)}</span>
            </div>
          );
        })}
      </div>
    </Panel>
  );
}

function MarketPlaybook({
  categories,
  assets
}: {
  categories: [string, number][];
  assets: AssetRow[];
}) {

  const strongest = assets
    .filter(a => a.score >= 55)
    .slice(0,3);

  const weakest = assets
    .filter(a => a.score <=45)
    .slice(0,3);


  const growth =
    categories.find(([n]) => n==="growth")?.[1] ?? 50;

  const inflation =
    categories.find(([n]) => n==="inflation")?.[1] ?? 50;


  let regime="Balanced Macro";

  if(growth>55 && inflation<50)
    regime="Goldilocks Expansion";

  else if(growth<50 && inflation>55)
    regime="Stagflation Risk";

  else if(growth<45 && inflation<45)
    regime="Recession Pressure";

  else if(growth>55 && inflation>55)
    regime="Overheating Economy";


  return (

    <Panel>

      <SectionTitle title="Market Playbook" />

      <div className="grid gap-4 md:grid-cols-3">


        <div>
          <div className="text-xs uppercase text-muted">
            Regime
          </div>

          <div className="mt-2 text-lg font-semibold">
            {regime}
          </div>
        </div>



        <div>

          <div className="text-xs uppercase text-muted">
            Favored Assets
          </div>

          {strongest.length ?

            strongest.map(a=>
              <div 
                key={a.asset}
                className="text-positive font-semibold"
              >
                ↑ {a.asset}
              </div>
            )

            :

            <div className="text-muted">
              No strong winners
            </div>

          }

        </div>



        <div>

          <div className="text-xs uppercase text-muted">
            Under Pressure
          </div>

          {weakest.length ?

            weakest.map(a=>
              <div 
                key={a.asset}
                className="text-negative font-semibold"
              >
                ↓ {a.asset}
              </div>
            )

            :

            <div className="text-muted">
              No major stress
            </div>

          }


        </div>

      </div>

    </Panel>

  );
}

function RegimeTimeline({ score }: { score: number }) {
  const regimes = [
    ["Expansion", score > 65 ? 86 : 42],
    ["Slowdown", score > 40 && score <= 65 ? 88 : 38],
    ["Recession", score <= 35 ? 84 : 22],
    ["Recovery", score > 35 && score <= 50 ? 58 : 24],
  ] as const;

  return (
    <Panel>
      <SectionTitle title="Macro Regime Timeline" />
      <div className="space-y-3">
        {regimes.map(([label, width]) => {
          const current =
            (label === "Expansion" && score > 65) ||
            (label === "Slowdown" && score > 40 && score <= 65) ||
            (label === "Recession" && score <= 35) ||
            (label === "Recovery" && score > 35 && score <= 50);
          return (
            <div key={label} className="grid grid-cols-[92px_1fr_72px] items-center gap-3">
              <div className="text-xs font-semibold uppercase text-muted">{label}</div>
              <div className="h-3 overflow-hidden rounded-full border border-line bg-canvas">
                <div className={current ? "h-full rounded-full bg-ink dark:bg-terminal" : "h-full rounded-full bg-line"} style={{ width: `${width}%` }} />
              </div>
              <div className={current ? "text-xs font-semibold uppercase text-ink" : "text-xs text-muted"}>{current ? "Current" : ""}</div>
            </div>
          );
        })}
      </div>
    </Panel>
  );
}

export default async function DashboardPage() {
  const macro = await fetchApi<MacroDashboard>("/macro/dashboard", { fallback: fallbackMacro });
  const macroScore = clampScore(macro.macro_score);
  const categories = macro.category_scores && typeof macro.category_scores === "object" ? Object.entries(macro.category_scores) : [];
  const summary = asArray<string>(macro.summary);
  const assets = await Promise.all(assetSlugs.map(getAsset));
  const macroMetric = metric(macro.history, macroScore);
  const scoreChange = macroMetric.change >= 0 ? `+${formatNumber(macroMetric.change)}` : formatNumber(macroMetric.change);

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-start justify-between gap-4 border-b border-line pb-4">
        <div>
          <div className="text-xs font-semibold uppercase text-muted">Trishula Capital Terminal</div>
          <h1 className="mt-1 text-2xl font-semibold tracking-normal">Macro Command Center</h1>
        </div>
        <div className="flex flex-wrap items-start justify-end gap-3">
          <TerminalActions />
          <DataStatus status={macro.data_status} updated={macroMetric.lastUpdated} />
        </div>
      </header>

      <section className="grid gap-4 xl:grid-cols-[0.95fr_1.05fr_0.8fr]">
        <Panel>
          <SectionTitle title="Macro Score" />
          <MacroGauge score={macroScore} />
          <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
            <div className="rounded-lg border border-line bg-canvas p-3">
              <div className="text-xs font-semibold uppercase text-muted">Yesterday</div>
              <div className="mt-1 font-semibold text-ink">{formatNumber(macroMetric.previous)}</div>
            </div>
            <div className="rounded-lg border border-line bg-canvas p-3">
              <div className="text-xs font-semibold uppercase text-muted">Change</div>
              <div className={toneClass(macroMetric.change) + " mt-1 flex items-center gap-1 font-semibold"}>
                {scoreChange} {macroMetric.change >= 0 ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
              </div>
            </div>
            <div className="rounded-lg border border-line bg-canvas p-3">
              <div className="text-xs font-semibold uppercase text-muted">7D Trend</div>
              <div className="mt-1 font-semibold text-ink">{trendWindow(macro.history, 7, macroScore)}</div>
            </div>
            <div className="rounded-lg border border-line bg-canvas p-3">
              <div className="text-xs font-semibold uppercase text-muted">30D Trend</div>
              <div className="mt-1 font-semibold text-ink">{trendWindow(macro.history, 30, macroScore)}</div>
            </div>
          </div>
        </Panel>

        <AiMacroBrief summary={summary} categories={categories} />

        <Panel>
          <SectionTitle title="Why Is Score This?" />
          <div className="space-y-3">
            {categories.slice(0, 6).map(([name, score]) => {
              const value = clampScore(score);
              const contribution = Math.round((value - 50) * 10) / 10;
              return (
                <div key={name}>
                  <div className="mb-1 flex items-center justify-between gap-3 text-sm">
                    <span className="font-semibold text-ink">{titleCase(name)}</span>
                    <span className={toneClass(contribution)}>{contribution >= 0 ? "+" : ""}{formatNumber(contribution)} pts</span>
                  </div>
                  <ScoreBar score={value} />
                </div>
              );
            })}
            {categories.length === 0 ? <EmptyState label="No scoring contribution data returned" /> : null}
          </div>
        </Panel>
      </section>

     <MarketPlaybook 
  categories={categories}
  assets={assets}
/>

      <Panel>
        <SectionTitle title="Global Macro Heatmap" action={<Database className="h-4 w-4 text-muted" aria-hidden="true" />} />
        <div className="overflow-x-auto terminal-scrollbar">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead className="border-b border-line text-xs uppercase text-muted">
              <tr>
                <th className="py-2 pr-4">Macro Block</th>
                <th className="py-2 pr-4">Score</th>
                <th className="py-2 pr-4">Trend</th>
                <th className="py-2 pr-4">Impact</th>
              </tr>
            </thead>
            <tbody>
              {categories.length > 0 ? categories.map(([name, score]) => {
                const value = clampScore(score);
                return (
                  <tr key={name} className="border-b border-line last:border-0 hover:bg-canvas">
                    <td className="py-3 pr-4 font-semibold text-ink">{titleCase(name)}</td>
                    <td className="py-3 pr-4">
                      <div className="flex items-center gap-3">
                        <span className={toneClass(value)}>{formatNumber(value)}</span>
                        <div className="w-28"><ScoreBar score={value} /></div>
                      </div>
                    </td>
                    <td className="py-3 pr-4"><DirectionIcon value={value} /></td>
                    <td className="py-3 pr-4"><BiasPill value={biasFromScore(value)} /></td>
                  </tr>
                );
              }) : (
                <tr><td colSpan={4} className="py-4"><EmptyState label="No category scores returned" /></td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>

      <Panel>
        <SectionTitle title="Asset Outlook Matrix" />
        <div className="overflow-x-auto terminal-scrollbar">
          <table className="w-full min-w-[940px] text-left text-sm">
            <thead className="border-b border-line text-xs uppercase text-muted">
              <tr>
                <th className="py-2 pr-4">Asset</th>
                <th className="py-2 pr-4">Score</th>
                <th className="py-2 pr-4">Bias</th>
                <th className="py-2 pr-4">Trend</th>
                <th className="py-2 pr-4">Main positive drivers</th>
                <th className="py-2 pr-4">Main negative drivers</th>
                <th className="py-2" aria-label="Open asset" />
              </tr>
            </thead>
            <tbody>
              {assets.map((asset) => (
                <tr key={asset.slug} className="border-b border-line last:border-b-0 hover:bg-canvas">
                  <td className="py-3 pr-4 font-semibold text-ink">
                    <span className="inline-flex items-center gap-2">
                      <CircleDollarSign className="h-4 w-4 text-muted" />
                      {asset.asset}
                    </span>
                  </td>
                  <td className="py-3 pr-4">
                    <div className="flex min-w-32 items-center gap-3">
                      <span className={toneClass(asset.score)}>{formatNumber(asset.score)}</span>
                      <div className="w-20"><ScoreBar score={asset.score} /></div>
                    </div>
                  </td>
                  <td className="py-3 pr-4"><BiasPill value={asset.bias} /></td>
                  <td className="py-3 pr-4 text-muted">{asset.trend}</td>
                  <td className="py-3 pr-4 text-positive">{asset.positives.join(", ") || "N/A"}</td>
                  <td className="py-3 pr-4 text-negative">{asset.negatives.join(", ") || "N/A"}</td>
                  <td className="py-3 text-right">
                    <Link href={`/asset/${asset.slug}`} className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-line hover:border-ink" title={`Open ${asset.asset}`}>
                      <ArrowRight className="h-4 w-4" aria-hidden="true" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
    </div>
  );
}
