import Link from "next/link";
import { ArrowRight, CircleDollarSign } from "lucide-react";
import { fetchApi } from "@/lib/api";
import { formatNumber, toneClass } from "@/lib/format";
import { BiasPill, Panel, SectionTitle, StatCard } from "@/components/ui";
import type { MacroDashboard } from "@/types/api";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const macro = await fetchApi<MacroDashboard>("/macro/dashboard");
  const assets = Object.entries(macro.asset_outlooks).map(([asset, outlook]) => ({
    asset,
    outlook,
    slug: asset.toLowerCase()
  }));

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-end justify-between gap-4 border-b border-line pb-4">
        <div>
          <div className="text-xs font-semibold uppercase text-muted">Trishula Capital Terminal</div>
          <h1 className="mt-1 text-2xl font-semibold tracking-normal">Macro Intelligence Dashboard</h1>
        </div>
        <div className="text-right text-xs text-muted">
          <div>Decision view</div>
          <div>Python analytics via FastAPI</div>
        </div>
      </header>

      <section className="grid gap-3 md:grid-cols-4">
        <StatCard label="Macro Score" value={macro.macro_score} />
        <StatCard label="Market Regime" value={macro.regime} />
        <StatCard label="Trend" value={macro.trend} />
        <StatCard label="Recession Risk" value={macro.recession_risk} />
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.35fr_0.65fr]">
        <Panel>
          <SectionTitle title="Market Outlook" />
          <div className="grid gap-2 md:grid-cols-2 xl:grid-cols-3">
            {assets.map((asset) => (
              <Link
                key={asset.asset}
                href={`/asset/${asset.slug}`}
                className="border border-line p-3 hover:border-ink"
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2 text-sm font-semibold">
                    <CircleDollarSign className="h-4 w-4" />
                    {asset.asset}
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted" />
                </div>
                <div className="mt-3 flex items-end justify-between">
                  <div className="text-sm font-semibold text-muted">Macro bias</div>
                  <BiasPill value={asset.outlook} />
                </div>
              </Link>
            ))}
          </div>
        </Panel>

        <Panel>
          <SectionTitle title="Macro Summary" />
          <div className="space-y-3">
            {macro.summary.map((line) => (
              <div key={line} className="flex items-start justify-between gap-4 border-b border-line pb-3 last:border-0">
                <span className="text-sm text-ink">{line}</span>
                <span className={toneClass(line)}>●</span>
              </div>
            ))}
          </div>
        </Panel>
      </section>

      <Panel>
        <SectionTitle title="Category Scores" />
        <div className="grid gap-2 md:grid-cols-3 xl:grid-cols-6">
          {Object.entries(macro.category_scores).map(([name, score]) => (
            <div key={name} className="border border-line p-3">
              <div className="text-xs font-medium uppercase text-muted">{name}</div>
              <div className={toneClass(score) + " mt-2 text-xl font-semibold"}>{formatNumber(score)}</div>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  );
}
