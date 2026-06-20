import clsx from "clsx";
import { AlertTriangle, Info } from "lucide-react";
import { clampScore, formatLabel, formatNumber, regimeFromScore, toneClass } from "@/lib/format";

export function Panel({
  children,
  className
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section className={clsx("rounded-xl border border-line bg-surface p-4 shadow-terminal transition-colors hover:border-slate-300 dark:hover:border-slate-500", className)}>
      {children}
    </section>
  );
}

export function SectionTitle({
  title,
  action
}: {
  title: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="mb-3 flex min-h-8 items-center justify-between gap-4">
      <h2 className="text-sm font-semibold tracking-normal text-ink">{formatLabel(title)}</h2>
      {action}
    </div>
  );
}

export function StatCard({
  label,
  value,
  sub
}: {
  label: string;
  value: string | number;
  sub?: string;
}) {
  return (
    <Panel>
      <div className="text-xs font-medium tracking-normal text-muted">{formatLabel(label)}</div>
      <div className={clsx("mt-2 text-2xl font-semibold tabular-nums", toneClass(value))}>{typeof value === "string" ? formatLabel(value) : formatNumber(value)}</div>
      {sub ? <div className="mt-1 text-xs text-muted">{sub}</div> : null}
    </Panel>
  );
}

export function BiasPill({ value }: { value: string | number }) {
  return (
    <span className={clsx("inline-flex items-center rounded-md border bg-surface px-2 py-1 text-xs font-semibold", toneClass(value))}>
      {typeof value === "string" ? formatLabel(value) : formatNumber(value)}
    </span>
  );
}

export function InfoHint({ text }: { text: string }) {
  return (
    <span className="group relative inline-flex align-middle">
      <Info className="h-3.5 w-3.5 text-muted" aria-hidden="true" />
      <span className="pointer-events-none absolute left-0 top-5 z-20 hidden w-72 whitespace-pre-line border border-line bg-surface p-2 text-xs font-normal leading-5 text-ink shadow-terminal group-hover:block">
        {text}
      </span>
    </span>
  );
}

export function ScoreBar({ score, height = "h-2" }: { score: unknown; height?: string }) {
  const value = clampScore(score);
  const color = value < 35 ? "bg-negative" : value > 65 ? "bg-positive" : "bg-neutral";

  return (
    <div className={clsx("overflow-hidden border border-line bg-canvas", height)}>
      <div className={clsx("h-full", color)} style={{ width: `${value}%` }} />
    </div>
  );
}

export function MacroGauge({ score }: { score: unknown }) {
  const value = clampScore(score);
  const regime = regimeFromScore(value);
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;
  const color = value < 35 ? "stroke-negative" : value > 65 ? "stroke-positive" : "stroke-neutral";

  return (
    <div className="flex items-center gap-5">
      <div className="relative h-36 w-36 shrink-0">
        <svg className="-rotate-90" viewBox="0 0 140 140" aria-hidden="true">
          <circle cx="70" cy="70" r={radius} className="fill-none stroke-line" strokeWidth="14" />
          <circle
            cx="70"
            cy="70"
            r={radius}
            className={clsx("fill-none transition-all", color)}
            strokeWidth="14"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className={clsx("text-3xl font-semibold tabular-nums", toneClass(value))}>{formatNumber(value)}</div>
          <div className="text-[10px] font-semibold text-muted">Score</div>
        </div>
      </div>
      <div className="min-w-0 flex-1">
        <div className="text-xs font-semibold text-muted">Risk Regime</div>
        <div className={clsx("mt-1 text-2xl font-semibold", toneClass(value))}>{regime}</div>
        <div className="mt-4 grid grid-cols-3 gap-2 text-center text-[10px] font-semibold text-muted">
          <span className="rounded-md border border-negative/40 py-1 text-negative">Stress</span>
          <span className="rounded-md border border-neutral/40 py-1 text-neutral">Neutral</span>
          <span className="rounded-md border border-positive/40 py-1 text-positive">Expansion</span>
        </div>
      </div>
    </div>
  );
}

export function EmptyState({ label = "No data available" }: { label?: string }) {
  return (
    <div className="flex min-h-28 items-center justify-center border border-dashed border-line bg-canvas p-4 text-sm text-muted">
      {label}
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex items-start gap-3 border border-negative bg-surface p-4 text-sm text-negative">
      <AlertTriangle className="mt-0.5 h-4 w-4" aria-hidden="true" />
      <span>{message}</span>
    </div>
  );
}

export function SkeletonBlock({ className }: { className?: string }) {
  return <div className={clsx("animate-pulse border border-line bg-surface", className)} />;
}
