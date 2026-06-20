"use client";

import { useState } from "react";
import { Info, X } from "lucide-react";
import { formatLabel, formatNumber } from "@/lib/format";
import type { Indicator } from "@/types/api";

export function IndicatorInfoButton({ indicator }: { indicator: Indicator }) {
  const [open, setOpen] = useState(false);
  const impact = indicator.trend_state === "positive" ? "Risk-on support" : indicator.trend_state === "negative" ? "Risk-off pressure" : "Mixed risk signal";
  const indicatorName = formatLabel(indicator.name);

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="inline-flex h-7 w-7 items-center justify-center rounded-md border border-line bg-surface text-muted hover:border-ink hover:text-ink"
        aria-label={`Open ${indicatorName} explanation`}
        title={`Open ${indicatorName} explanation`}
      >
        <Info className="h-3.5 w-3.5" aria-hidden="true" />
      </button>
      {open ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 p-4" role="dialog" aria-modal="true">
          <div className="max-h-[86vh] w-full max-w-2xl overflow-y-auto rounded-xl border border-line bg-surface p-5 shadow-2xl">
            <div className="flex items-start justify-between gap-4 border-b border-line pb-4">
              <div>
                <div className="text-xs font-semibold text-muted">Indicator Intelligence</div>
                <h2 className="mt-1 text-xl font-semibold text-ink">{indicatorName}</h2>
              </div>
              <button
                type="button"
                onClick={() => setOpen(false)}
                className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-line hover:border-ink"
                aria-label="Close indicator explanation"
              >
                <X className="h-4 w-4" aria-hidden="true" />
              </button>
            </div>

            <div className="mt-4 grid gap-3 sm:grid-cols-3">
              <div className="rounded-lg border border-line bg-canvas p-3">
                <div className="text-xs font-semibold text-muted">Current</div>
                <div className="mt-1 text-lg font-semibold text-ink">{indicator.current_display ?? formatNumber(indicator.current)}</div>
              </div>
              <div className="rounded-lg border border-line bg-canvas p-3">
                <div className="text-xs font-semibold text-muted">Score</div>
                <div className="mt-1 text-lg font-semibold text-ink">{formatNumber(indicator.score)}/100</div>
              </div>
              <div className="rounded-lg border border-line bg-canvas p-3">
                <div className="text-xs font-semibold text-muted">Risk Signal</div>
                <div className="mt-1 text-lg font-semibold text-ink">{impact}</div>
              </div>
            </div>

            <div className="mt-5 space-y-4 text-sm leading-6 text-ink">
              <section>
                <h3 className="text-xs font-semibold text-muted">Meaning</h3>
                <p>{indicator.measures || `${indicatorName} is a macro input used by the scoring model.`}</p>
              </section>
              <section>
                <h3 className="text-xs font-semibold text-muted">Why It Matters</h3>
                <p>{indicator.info || `${indicatorName} can shift policy expectations, yields, USD, liquidity, and risk appetite.`}</p>
              </section>
              <section>
                <h3 className="text-xs font-semibold text-muted">Current Reading Interpretation</h3>
                <p>{indicator.explanation || indicator.market_impact || "Current interpretation is neutral due to limited detail."}</p>
              </section>
              <section>
                <h3 className="text-xs font-semibold text-muted">Market Impact</h3>
                <p>{indicator.market_impact || indicator.impact || "Used as part of the broader macro score."}</p>
              </section>
              <section className="grid gap-2 sm:grid-cols-2">
                <div>
                  <h3 className="text-xs font-semibold text-muted">Formula</h3>
                  <p>Existing scoring engine transform of current, previous, change, direction, and weight where available.</p>
                </div>
                <div>
                  <h3 className="text-xs font-semibold text-muted">Source</h3>
                  <p>{indicator.source || indicator.code || "Internal macro data pipeline"}</p>
                </div>
              </section>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
