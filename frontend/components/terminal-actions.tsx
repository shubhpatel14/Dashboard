"use client";

import { useEffect, useMemo, useState } from "react";
import { Bot, Download, Search, X } from "lucide-react";
import { useRouter } from "next/navigation";
import { assetLabels, assetSlugs, macroCategories } from "@/lib/api";

type Action = {
  label: string;
  href: string;
  group: string;
};

export function TerminalActions() {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");

  const actions = useMemo<Action[]>(() => [
    { label: "Dashboard", href: "/", group: "Navigation" },
    ...macroCategories.map(([label, slug]) => ({ label, href: `/macro?category=${slug}`, group: "Macro" })),
    ...assetSlugs.map((slug) => ({ label: assetLabels[slug], href: `/asset/${slug}`, group: "Assets" })),
    { label: "Institutional Positioning", href: "/institutional", group: "System" },
  ], []);

  const filtered = actions.filter((item) => item.label.toLowerCase().includes(query.toLowerCase())).slice(0, 8);

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setOpen(true);
      }
    }

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  function go(href: string) {
    setOpen(false);
    setQuery("");
    router.push(href);
  }

  return (
    <>
      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          onClick={() => setOpen(true)}
          className="inline-flex h-9 min-w-56 items-center gap-2 rounded-lg border border-line bg-surface px-3 text-sm text-muted hover:border-ink hover:text-ink"
        >
          <Search className="h-4 w-4" aria-hidden="true" />
          Search terminal
          <span className="ml-auto text-[10px] font-semibold uppercase">Ctrl K</span>
        </button>
        <button
          type="button"
          onClick={() => window.print()}
          className="inline-flex h-9 items-center gap-2 rounded-lg border border-line bg-surface px-3 text-sm font-semibold text-ink hover:border-ink"
        >
          <Download className="h-4 w-4" aria-hidden="true" />
          Export
        </button>
        <button
          type="button"
          onClick={() => setOpen(true)}
          className="inline-flex h-9 items-center gap-2 rounded-lg border border-line bg-ink px-3 text-sm font-semibold text-white hover:opacity-90 dark:bg-terminal dark:text-canvas"
        >
          <Bot className="h-4 w-4" aria-hidden="true" />
          AI Macro Analyst
        </button>
      </div>

      {open ? (
        <div className="fixed inset-0 z-50 flex items-start justify-center bg-slate-950/40 p-4 pt-[12vh]">
          <div className="w-full max-w-2xl rounded-xl border border-line bg-surface p-3 shadow-2xl">
            <div className="flex items-center gap-2 border-b border-line pb-3">
              <Search className="h-4 w-4 text-muted" aria-hidden="true" />
              <input
                autoFocus
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search CPI, Gold, Liquidity..."
                className="h-9 flex-1 border-0 bg-transparent text-sm text-ink placeholder:text-muted focus:ring-0"
              />
              <button type="button" onClick={() => setOpen(false)} className="rounded-md border border-line p-2 hover:border-ink" aria-label="Close command palette">
                <X className="h-4 w-4" aria-hidden="true" />
              </button>
            </div>
            <div className="mt-2 max-h-80 overflow-y-auto">
              {filtered.map((item) => (
                <button
                  key={`${item.group}-${item.href}`}
                  type="button"
                  onClick={() => go(item.href)}
                  className="flex w-full items-center justify-between rounded-lg px-3 py-2 text-left text-sm hover:bg-canvas"
                >
                  <span className="font-semibold text-ink">{item.label}</span>
                  <span className="text-xs uppercase text-muted">{item.group}</span>
                </button>
              ))}
              {filtered.length === 0 ? <div className="px-3 py-8 text-center text-sm text-muted">No matching terminal command</div> : null}
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
