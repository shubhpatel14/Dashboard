import { notFound } from "next/navigation";
import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import { assetLabels, assetSlugs, fetchApi } from "@/lib/api";
import { biasFromScore, clampScore, formatLabel, formatNumber, titleCase, toneClass } from "@/lib/format";
import { AssetRadar, DriverBars, ScoreLine } from "@/components/lazy-charts";
import { BiasPill, EmptyState, Panel, ScoreBar, SectionTitle, StatCard } from "@/components/ui";
import type { AssetResponse, Driver } from "@/types/api";

export const dynamic = "force-dynamic";

function normalizeDrivers(drivers: Driver[] | undefined): Driver[] {
  return Array.isArray(drivers)
    ? drivers.map((driver, index) => ({
        name: formatLabel(driver.name || `Driver ${index + 1}`),
        score: clampScore(driver.score),
        contribution: Number.isFinite(Number(driver.contribution)) ? Number(driver.contribution) : clampScore(driver.score),
        bias: driver.bias || biasFromScore(driver.score)
      }))
    : [];
}

function macroExplanation(asset: string, score: number, bullish: Driver[], bearish: Driver[]) {
  const outlook = biasFromScore(score).toLowerCase();
  const supports = bullish.slice(0, 2).map((driver) => driver.name.toLowerCase()).join(" and ");
  const pressures = bearish.slice(0, 2).map((driver) => driver.name.toLowerCase()).join(" and ");

  if (supports && pressures) {
    return `${asset} remains ${outlook} as ${supports} support upside while ${pressures} pressure valuation.`;
  }
  if (supports) {
    return `${asset} screens ${outlook} as ${supports} provide the strongest macro support.`;
  }
  if (pressures) {
    return `${asset} screens ${outlook} as ${pressures} remain the main macro headwinds.`;
  }
  return `${asset} remains ${outlook} with a balanced macro driver set.`;
}

function DriverList({ title, drivers, positive }: { title: string; drivers: Driver[]; positive: boolean }) {
  return (
    <Panel>
      <SectionTitle title={title} />
      <div className="space-y-3">
        {drivers.length > 0 ? (
          drivers.map((driver) => (
            <div key={driver.name} className="flex items-center justify-between gap-3 border-b border-line pb-3 last:border-0">
              <div className="flex min-w-0 items-center gap-2">
                {positive ? <ArrowUpRight className="h-4 w-4 text-positive" /> : <ArrowDownRight className="h-4 w-4 text-negative" />}
                <span className="truncate text-sm font-semibold text-ink">{driver.name}</span>
              </div>
              <span className={positive ? "text-positive" : "text-negative"}>{formatNumber(driver.score)}</span>
            </div>
          ))
        ) : (
          <EmptyState label="No drivers in this group" />
        )}
      </div>
    </Panel>
  );
}

export default async function AssetPage({ params }: { params: { asset: string } }) {
  if (!assetSlugs.includes(params.asset)) {
    notFound();
  }

    const data =
    await fetchApi<AssetResponse>(
    `/assets/${params.asset}`
    );


    const score =
    clampScore(
        data.asset_score ??
        data.score ??
        50
    );


    const drivers =
    normalizeDrivers(
        data.components ??
        []
    );


    const bullish =
    normalizeDrivers(
        data.bullish_drivers ??
        []
    );


    const bearish =
    normalizeDrivers(
        data.bearish_drivers ??
        []
    );
  const assetName = formatLabel(data.asset || assetLabels[params.asset] || titleCase(params.asset));
  const history = Array.isArray(data.history) ? data.history : [];
  const explanation =
    data.explanation ||
    data.summary ||
    macroExplanation(
        assetName,
        score,
        bullish,
        bearish
    );
  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-end justify-between gap-4 border-b border-line pb-4">
        <div>
          <div className="text-xs font-semibold text-muted">Asset Macro Model</div>
          <h1 className="mt-1 text-2xl font-semibold tracking-normal">{assetName} Macro Model</h1>
        </div>
        <BiasPill value={data.outlook || biasFromScore(score)} />
      </header>

      <section className="grid gap-3 md:grid-cols-4">
        <StatCard label="Score" value={`${formatNumber(score)}/100`} />
        <StatCard label="Outlook" value={data.outlook || biasFromScore(score)} />
        <StatCard label="Bullish Drivers" value={bullish.length} />
        <StatCard label="Bearish Drivers" value={bearish.length} />
      </section>

      <Panel>
        <SectionTitle title="Macro Explanation" />
        <p className="max-w-5xl text-lg font-semibold leading-7 text-ink">{explanation}</p>
      </Panel>

      <section className="grid gap-4 xl:grid-cols-2">
        <DriverList title="Bullish Drivers" drivers={bullish} positive />
        <DriverList title="Bearish Drivers" drivers={bearish} positive={false} />
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.05fr_0.95fr]">
        <Panel>
          <SectionTitle title="Component Model" />
          <div className="overflow-x-auto terminal-scrollbar">
            <table className="w-full min-w-[760px] text-left text-sm">
              <thead className="border-b border-line text-xs uppercase text-muted">
                <tr>
                  <th className="py-2 pr-4">Driver</th>
                  <th className="py-2 pr-4">Weight</th>
                  <th className="py-2 pr-4">Current</th>
                  <th className="py-2 pr-4">Change</th>
                  <th className="py-2 pr-4">Score</th>
                  <th className="py-2 pr-4">Impact</th>
                </tr>
              </thead>
              <tbody>
                {drivers.length > 0 ? drivers.map((driver) => (
                  <tr key={driver.name} className="border-b border-line last:border-b-0 hover:bg-canvas">
                    <td className="py-3 pr-4 font-semibold text-ink">{formatLabel(driver.name)}</td>
                    <td className="py-3 pr-4 tabular-nums text-muted">{formatNumber(driver.contribution)}%</td>
                    <td className="py-3 pr-4 text-muted">Model input</td>
                    <td className="py-3 pr-4 text-muted">N/A</td>
                    <td className="py-3 pr-4">
                      <div className="flex items-center gap-3">
                        <span className={`${toneClass(driver.score)} tabular-nums`}>{formatNumber(driver.score)}</span>
                        <div className="w-20"><ScoreBar score={driver.score} /></div>
                      </div>
                    </td>
                    <td className="py-3 pr-4"><BiasPill value={driver.bias} /></td>
                  </tr>
                )) : (
                  <tr>
                    <td colSpan={6} className="py-4"><EmptyState label="No asset drivers returned" /></td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Panel>

        <Panel>
          <SectionTitle title="Asset Driver Radar" />
          <AssetRadar drivers={drivers} />
        </Panel>
      </section>

      <section className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
        <Panel>
          <SectionTitle title="Driver Breakdown" />
          <DriverBars drivers={drivers} />
        </Panel>
        <Panel>
          <SectionTitle title="Score History" />
          <ScoreLine data={history} name={`${assetName} Score`} />
        </Panel>
      </section>
    </div>
  );
}
