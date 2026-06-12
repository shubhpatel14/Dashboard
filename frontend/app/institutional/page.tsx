"use client";

import { useEffect, useMemo, useState } from "react";
import { API_URL, assets } from "@/lib/api";
import { formatNumber, toNumber } from "@/lib/format";
import { PositioningCharts } from "@/components/lazy-charts";
import { BiasPill, ErrorState, Panel, SectionTitle, SkeletonBlock, StatCard } from "@/components/ui";
import type { InstitutionalResponse } from "@/types/api";

const windows = ["1M", "3M", "6M", "1Y", "ALL"];

function slug(value: string) {
  return value.toLowerCase();
}

function filterHistory(data: InstitutionalResponse | null, window: string) {
  if (!data || window === "ALL") {
    return data;
  }

  const sizes: Record<string, number> = { "1M": 4, "3M": 13, "6M": 26, "1Y": 52 };
  return {
    ...data,
    history: Array.isArray(data.history) ? data.history.slice(-sizes[window]) : []
  };
}

export default function InstitutionalPage() {
  const [asset, setAsset] = useState("Gold");
  const [window, setWindow] = useState("6M");
  const [data, setData] = useState<InstitutionalResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    setError("");
    fetch(`${API_URL}/institutional/${slug(asset)}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Positioning request failed: ${response.status}`);
        }
        return response.json();
      })
      .then(setData)
      .catch((caught) => {
        setData(null);
        setError(caught instanceof Error ? caught.message : "Positioning request failed");
      })
      .finally(() => setLoading(false));
  }, [asset]);

  const filtered = useMemo(() => filterHistory(data, window), [data, window]);

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-end justify-between gap-4 border-b border-line pb-4">
        <div>
          <div className="text-xs font-semibold uppercase text-muted">Institutional Positioning</div>
          <h1 className="mt-1 text-2xl font-semibold tracking-normal">CFTC Commitment of Traders</h1>
        </div>
        {data ? <BiasPill value={data.bias || "N/A"} /> : null}
      </header>

      <Panel>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <select
            value={asset}
            onChange={(event) => setAsset(event.target.value)}
            className="h-10 border-line bg-surface text-sm"
          >
            {assets.map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>

          <div className="flex flex-wrap gap-2">
            {windows.map((item) => (
              <button
                key={item}
                onClick={() => setWindow(item)}
                className={`h-9 border px-3 text-sm ${window === item ? "border-ink bg-ink text-white dark:bg-terminal dark:text-canvas" : "border-line bg-surface text-muted hover:border-ink"}`}
              >
                {item}
              </button>
            ))}
          </div>
        </div>
      </Panel>

      {error ? (
        <ErrorState message={error} />
      ) : loading || !filtered ? (
        <SkeletonBlock className="h-48" />
      ) : (
        <>
          <section className="grid gap-3 md:grid-cols-3 xl:grid-cols-6">
            <StatCard label="Long %" value={toNumber(filtered.long_percentage)} />
            <StatCard label="Short %" value={toNumber(filtered.short_percentage)} />
            <StatCard label="Net Position" value={toNumber(filtered.net_position)} />
            <StatCard label="Weekly Change" value={toNumber(filtered.weekly_change)} />
            <StatCard label="4 Week Velocity" value={toNumber(filtered.four_week_velocity)} />
            <StatCard label="Score" value={toNumber(filtered.score)} />
          </section>

          <Panel>
            <SectionTitle title={`${filtered.asset || asset} Positioning Trends`} />
            <PositioningCharts data={filtered} />
          </Panel>

          <Panel>
            <SectionTitle title="Historical Percentile" />
            <div className="flex items-center gap-4">
              <div className="h-3 flex-1 border border-line bg-canvas">
                <div
                  className="h-full bg-ink dark:bg-terminal"
                  style={{ width: `${Math.max(0, Math.min(toNumber(filtered.position_percentile), 100))}%` }}
                />
              </div>
              <div className="w-20 text-right text-sm font-semibold">
                {formatNumber(toNumber(filtered.position_percentile))}%
              </div>
            </div>
          </Panel>
        </>
      )}
    </div>
  );
}
