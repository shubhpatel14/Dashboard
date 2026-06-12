"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { BarChart3, BriefcaseBusiness, Database, Gauge, Globe2, Landmark, LineChart } from "lucide-react";
import clsx from "clsx";
import { assetLabels, assetSlugs, macroCategories } from "@/lib/api";
import { ThemeToggle } from "@/components/theme-toggle";

function NavLink({
  href,
  active,
  children
}: {
  href: string;
  active?: boolean;
  children: React.ReactNode;
}) {
  return (
    <Link
      href={href}
      className={clsx(
        "flex h-8 items-center gap-2 border px-2 text-sm transition-colors",
        active
          ? "border-ink bg-ink text-white dark:bg-terminal dark:text-canvas"
          : "border-transparent text-muted hover:border-line hover:bg-canvas hover:text-ink"
      )}
    >
      {children}
    </Link>
  );
}

export function Sidebar() {
  const [location, setLocation] = useState({ pathname: "", selectedMacro: "liquidity" });

  useEffect(() => {
    function syncLocation() {
      const params = new URLSearchParams(window.location.search);
      setLocation({
        pathname: window.location.pathname,
        selectedMacro: params.get("category") ?? "liquidity"
      });
    }

    syncLocation();
    window.addEventListener("popstate", syncLocation);
    return () => window.removeEventListener("popstate", syncLocation);
  }, []);

  const { pathname, selectedMacro } = location;

  return (
    <aside className="border-r border-line bg-surface p-4">
      <div className="mb-6 flex items-start justify-between gap-3">
        <Link href="/" className="flex min-w-0 items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center border border-ink text-sm font-bold">
            TC
          </div>
          <div className="min-w-0">
            <div className="truncate text-sm font-bold uppercase tracking-normal">Trishula Capital</div>
            <div className="text-xs text-muted">Macro Terminal</div>
          </div>
        </Link>
        <ThemeToggle />
      </div>

      <nav className="space-y-5">
        <div>
          <NavLink href="/" active={pathname === "/"}>
            <BarChart3 className="h-4 w-4" /> Dashboard
          </NavLink>
        </div>

        <div>
          <div className="mb-2 border-t border-line pt-4 text-xs font-semibold uppercase text-muted">Macro Intelligence</div>
          <div className="space-y-1">
            <NavLink href="/macro" active={pathname === "/macro" && selectedMacro === "liquidity"}>
              <Gauge className="h-4 w-4" /> Overview
            </NavLink>
            {macroCategories.map(([label, slug]) => (
              <NavLink key={slug} href={`/macro?category=${slug}`} active={pathname === "/macro" && selectedMacro === slug}>
                {slug === "global_liquidity" ? <Globe2 className="h-4 w-4" /> : <Gauge className="h-4 w-4" />}
                {label === "Labor" ? "Labor Market" : label === "Recession" ? "Recession Monitor" : label}
              </NavLink>
            ))}
          </div>
        </div>

        <div>
          <div className="mb-2 border-t border-line pt-4 text-xs font-semibold uppercase text-muted">
            Market Intelligence
          </div>
          <div className="space-y-1">
            <NavLink href="/" active={pathname === "/"}>
              <LineChart className="h-4 w-4" /> Asset Dashboard
            </NavLink>
            {assetSlugs.map((slug) => (
              <NavLink key={slug} href={`/asset/${slug}`} active={pathname === `/asset/${slug}`}>
                <LineChart className="h-4 w-4" />
                {slug === "bitcoin" ? "Crypto" : assetLabels[slug]}
              </NavLink>
            ))}
          </div>
        </div>

        <div>
          <div className="mb-2 border-t border-line pt-4 text-xs font-semibold uppercase text-muted">
            Institutional Positioning
          </div>
          <NavLink href="/institutional" active={pathname === "/institutional"}>
            <Landmark className="h-4 w-4" /> CFTC Positioning
          </NavLink>
          <NavLink href="/" active={false}>
            <Database className="h-4 w-4" /> Data Sources
          </NavLink>
          <NavLink href="/" active={false}>
            <BriefcaseBusiness className="h-4 w-4" /> Settings
          </NavLink>
        </div>
      </nav>

      <div className="mt-8 border-t border-line pt-4 text-xs text-muted">
        <div className="mb-2 flex items-center gap-2">
          <Database className="h-4 w-4" /> PostgreSQL ready
        </div>
        <div className="flex items-center gap-2">
          <BriefcaseBusiness className="h-4 w-4" /> Cached FastAPI
        </div>
      </div>
    </aside>
  );
}
