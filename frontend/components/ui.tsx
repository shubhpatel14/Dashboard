import clsx from "clsx";
import { Info } from "lucide-react";
import { formatNumber, toneClass } from "@/lib/format";

export function Panel({
  children,
  className
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section className={clsx("border border-line bg-surface p-4 shadow-terminal", className)}>
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
    <span className={clsx("inline-flex items-center border px-2 py-1 text-xs font-semibold", toneClass(value))}>
      {value}
    </span>
  );
}

export function InfoHint({ text }: { text: string }) {
  return (
    <span className="group relative inline-flex align-middle">
      <Info className="h-3.5 w-3.5 text-muted" aria-hidden="true" />
      <span className="pointer-events-none absolute left-0 top-5 z-20 hidden w-72 whitespace-pre-line border border-line bg-white p-2 text-xs font-normal leading-5 text-ink shadow-terminal group-hover:block">
        {text}
      </span>
    </span>
  );
}
