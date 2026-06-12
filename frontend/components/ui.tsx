import clsx from "clsx";
import { AlertTriangle, Info } from "lucide-react";
import { clampScore, formatNumber, regimeFromScore, toneClass } from "@/lib/format";

export function Panel({
  children,
  className
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section className={clsx("border border-line bg-surface p-4 shadow-terminal transition-colors hover:border-slate-300 dark:hover:border-slate-500", className)}>
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
      <h2 className="text-sm font-semibold uppercase tracking-normal text-ink">{title}</h2>
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
      <div className="text-xs font-medium uppercase tracking-normal text-muted">{label}</div>
      <div className={clsx("mt-2 text-2xl font-semibold", toneClass(value))}>{formatNumber(value)}</div>
      {sub ? <div className="mt-1 text-xs text-muted">{sub}</div> : null}
    </Panel>
  );
}

export function BiasPill({ value }: { value: string | number }) {
  return (
    <span className={clsx("inline-flex items-center border bg-surface px-2 py-1 text-xs font-semibold", toneClass(value))}>
      {String(value || "N/A")}
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
  const rotation = -90 + (value / 100) * 180;
  const regime = regimeFromScore(value);

  return (
    <div className="relative mx-auto flex max-w-[360px] flex-col items-center">
      <div className="relative h-44 w-full overflow-hidden">
        <div className="absolute inset-x-4 top-4 h-72 rounded-full border-[24px] border-line" />
        <div className="absolute left-4 top-4 h-72 w-[calc(100%-2rem)] rounded-full border-[24px] border-transparent border-t-negative border-l-negative" />
        <div className="absolute left-4 top-4 h-72 w-[calc(100%-2rem)] rounded-full border-[24px] border-transparent border-t-neutral" />
        <div className="absolute left-4 top-4 h-72 w-[calc(100%-2rem)] rounded-full border-[24px] border-transparent border-t-positive border-r-positive" />
        <div
          className="absolute bottom-5 left-1/2 h-1 w-32 origin-left bg-ink transition-transform"
          style={{ transform: `rotate(${rotation}deg)` }}
        />
        <div className="absolute bottom-3 left-1/2 h-4 w-4 -translate-x-1/2 rounded-full border border-line bg-surface" />
      </div>
      <div className="text-center">
        <div className={clsx("text-4xl font-semibold tabular-nums", toneClass(value))}>{formatNumber(value)}</div>
        <div className="mt-1 text-xs font-semibold uppercase text-muted">{regime}</div>
      </div>
      <div className="mt-4 grid w-full grid-cols-3 text-center text-[11px] font-semibold uppercase text-muted">
        <span>Risk Off</span>
        <span>Neutral</span>
        <span>Risk On</span>
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
