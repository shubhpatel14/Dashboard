import Link from "next/link";
import { ArrowRight, CircleDollarSign, Minus, TrendingDown, TrendingUp } from "lucide-react";
import { assetLabels, assetSlugs, fetchApi } from "@/lib/api";
import { asArray, biasFromScore, clampScore, formatNumber, regimeFromScore, titleCase, toneClass } from "@/lib/format";
import { BiasPill, EmptyState, MacroGauge, Panel, ScoreBar, SectionTitle } from "@/components/ui";
import type { AssetResponse, MacroDashboard } from "@/types/api";

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

async function getAsset(slug: string): Promise<AssetRow> {
  try {
    const data = await fetchApi<AssetResponse>(`/assets/${slug}`);
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
  } catch {
    return {
      slug,
      asset: assetLabels[slug] || titleCase(slug),
      score: 50,
      bias: "Unavailable",
      trend: "N/A",
      positives: [],
      negatives: []
    };
  }
}

function DirectionIcon({ value }: { value: unknown }) {
  const text = String(value).toLowerCase();
  const score = clampScore(value);
  if (text.includes("down") || text.includes("fall") || score < 40) {
    return <TrendingDown className="h-4 w-4 text-negative" aria-hidden="true" />;
  }
  if (text.includes("up") || text.includes("rise") || score > 60) {
    return <TrendingUp className="h-4 w-4 text-positive" aria-hidden="true" />;
  }
  return <Minus className="h-4 w-4 text-neutral" aria-hidden="true" />;
}

export default async function DashboardPage() {
  const macro = await fetchApi<MacroDashboard>("/macro/dashboard");
  const macroScore = clampScore(macro.macro_score);
  const categories = macro.category_scores && typeof macro.category_scores === "object" ? Object.entries(macro.category_scores) : [];
  const summary = asArray<string>(macro.summary);
  const assets = await Promise.all(assetSlugs.map(getAsset));

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-end justify-between gap-4 border-b border-line pb-4">
        <div>
          <div className="text-xs font-semibold uppercase text-muted">Trishula Capital Terminal</div>
          <h1 className="mt-1 text-2xl font-semibold tracking-normal">Executive Macro Overview</h1>
        </div>
        <div className="text-right text-xs text-muted">
          <div>Live FastAPI intelligence</div>
          <div>Decision dashboard</div>
        </div>
      </header>

      <section className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
        <Panel>
          <SectionTitle title="Global Macro Score" />
          <MacroGauge score={macroScore} />
          <div className="mt-5 grid gap-3 sm:grid-cols-3">
            {[
              ["Regime", macro.regime || regimeFromScore(macroScore)],
              ["Trend", macro.trend || "N/A"],
              ["Risk Status", macro.risk_status || macro.recession_risk || "N/A"]
            ].map(([label, value]) => (
              <div key={label} className="border border-line bg-canvas p-3">
                <div className="text-xs font-semibold uppercase text-muted">{label}</div>
                <div className={toneClass(value) + " mt-2 text-sm font-semibold"}>{value}</div>
              </div>
            ))}
          </div>
        </Panel>

        <Panel>
          <SectionTitle title="Macro Brief" />
          <div className="space-y-3">
            {summary.length > 0 ? (
              summary.map((line, index) => (
                <div key={`${line}-${index}`} className="flex items-start gap-3 border-b border-line pb-3 last:border-0">
                  <span className={toneClass(line)}>●</span>
                  <span className="text-sm leading-6 text-ink">{line}</span>
                </div>
              ))
            ) : (
              <EmptyState label="No macro summary returned" />
            )}
          </div>
        </Panel>
      </section>

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
                      <div className="w-20">
                        <ScoreBar score={asset.score} />
                      </div>
                    </div>
                  </td>
                  <td className="py-3 pr-4"><BiasPill value={asset.bias} /></td>
                  <td className="py-3 pr-4 text-muted">{asset.trend}</td>
                  <td className="py-3 pr-4 text-positive">{asset.positives.join(", ") || "N/A"}</td>
                  <td className="py-3 pr-4 text-negative">{asset.negatives.join(", ") || "N/A"}</td>
                  <td className="py-3 text-right">
                    <Link href={`/asset/${asset.slug}`} className="inline-flex h-8 w-8 items-center justify-center border border-line hover:border-ink" title={`Open ${asset.asset}`}>
                      <ArrowRight className="h-4 w-4" aria-hidden="true" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      <Panel>
        <SectionTitle title="Macro Heatmap" />
        <div className="grid gap-2 md:grid-cols-3 xl:grid-cols-5">
          {categories.length > 0 ? (
            categories.map(([name, score]) => {
              const value = clampScore(score);
              return (
                <Link
                  key={name}
                  href={`/macro?category=${name}`}
                  className="border border-line bg-surface p-3 hover:border-ink hover:bg-canvas"
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="text-xs font-semibold uppercase text-muted">{titleCase(name)}</div>
                    <DirectionIcon value={value} />
                  </div>
                  <div className={toneClass(value) + " mt-3 text-2xl font-semibold tabular-nums"}>{formatNumber(value)}</div>
                  <div className="mt-3"><ScoreBar score={value} /></div>
                  <div className="mt-2 text-xs font-semibold uppercase text-muted">{biasFromScore(value)}</div>
                </Link>
              );
            })
          ) : (
            <EmptyState label="No category scores returned" />
          )}
        </div>
      </Panel>
    </div>
  );
}
