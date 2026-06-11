import { notFound } from "next/navigation";
import { fetchApi, assetSlugs } from "@/lib/api";
import { formatNumber, toneClass } from "@/lib/format";
import { DriverBars, ScoreLine } from "@/components/lazy-charts";
import { BiasPill, Panel, SectionTitle, StatCard } from "@/components/ui";
import type { AssetResponse } from "@/types/api";

export const dynamic = "force-dynamic";

export default async function AssetPage({ params }: { params: { asset: string } }) {
  if (!assetSlugs.includes(params.asset)) {
    notFound();
  }

  const data = await fetchApi<AssetResponse>(`/assets/${params.asset}`);
  const takeaways = data.drivers.slice(0, 3);

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-end justify-between gap-4 border-b border-line pb-4">
        <div>
          <div className="text-xs font-semibold uppercase text-muted">Asset Intelligence</div>
          <h1 className="mt-1 text-2xl font-semibold tracking-normal">{data.asset} Intelligence</h1>
        </div>
        <BiasPill value={data.outlook} />
      </header>

      <section className="grid gap-3 md:grid-cols-3">
        <StatCard label="Score" value={data.asset_score} />
        <StatCard label="Outlook" value={data.outlook} />
        <StatCard label="Drivers" value={data.drivers.length} />
      </section>

      <section className="grid gap-4 xl:grid-cols-[0.8fr_1.2fr]">
        <div className="space-y-4">
          <Panel>
            <SectionTitle title="Key Takeaways" />
            <div className="space-y-3">
              {takeaways.map((driver) => (
                <div key={driver.name} className="flex items-center justify-between gap-4 border-b border-line pb-3 last:border-0">
                  <span className="text-sm">{driver.name}</span>
                  <span className={toneClass(driver.score)}>{driver.bias}</span>
                </div>
              ))}
            </div>
          </Panel>

          <Panel>
            <SectionTitle title="Executive Summary" />
            <p className="text-sm leading-6">{data.summary}</p>
          </Panel>
        </div>

        <Panel>
          <SectionTitle title="Driver Breakdown" />
          <DriverBars drivers={data.drivers} />
        </Panel>
      </section>

      <Panel>
        <SectionTitle title="Score History" />
        <ScoreLine data={data.history} name={`${data.asset} Score`} />
      </Panel>

      <details className="border border-line bg-white p-4">
        <summary className="cursor-pointer text-sm font-semibold uppercase">Advanced Data</summary>
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[720px] text-left text-sm">
            <thead className="border-b border-line text-xs uppercase text-muted">
              <tr>
                <th className="py-2">Driver</th>
                <th className="py-2">Score</th>
                <th className="py-2">Contribution</th>
                <th className="py-2">Bias</th>
              </tr>
            </thead>
            <tbody>
              {data.drivers.map((driver) => (
                <tr key={driver.name} className="border-b border-line">
                  <td className="py-2">{driver.name}</td>
                  <td className="py-2">{formatNumber(driver.score)}</td>
                  <td className="py-2">{formatNumber(driver.contribution)}%</td>
                  <td className="py-2">{driver.bias}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </div>
  );
}
