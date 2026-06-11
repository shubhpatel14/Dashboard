import type { Metadata } from "next";
import Link from "next/link";
import {
  BarChart3,
  BriefcaseBusiness,
  CircleDollarSign,
  Database,
  Gauge,
  Globe2,
  Landmark,
  LineChart,
  TrendingUp
} from "lucide-react";
import "./globals.css";
import { assetSlugs, macroCategories } from "@/lib/api";

export const metadata: Metadata = {
  title: "Trishula Capital Terminal",
  description: "Institutional macro intelligence platform"
};

const assetLabels = ["Gold", "Bitcoin", "SP500", "Nasdaq", "Dollar", "Bonds"];

function NavLink({
  href,
  children
}: {
  href: string;
  children: React.ReactNode;
}) {
  return (
    <Link
      href={href}
      className="flex h-8 items-center gap-2 border border-transparent px-2 text-sm text-muted hover:border-line hover:bg-white hover:text-ink"
    >
      {children}
    </Link>
  );
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="terminal-grid">
          <aside className="border-r border-line bg-white p-4">
            <Link href="/" className="mb-6 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center border border-ink text-sm font-bold">
                TC
              </div>
              <div>
                <div className="text-sm font-bold uppercase tracking-normal">Trishula Capital</div>
                <div className="text-xs text-muted">Macro Intelligence Platform</div>
              </div>
            </Link>

            <nav className="space-y-5">
              <div>
                <NavLink href="/">
                  <BarChart3 className="h-4 w-4" /> Dashboard
                </NavLink>
              </div>

              <div>
                <div className="mb-2 border-t border-line pt-4 text-xs font-semibold uppercase text-muted">
                  Macro Intelligence
                </div>
                <div className="space-y-1">
                  {macroCategories.map(([label, slug]) => (
                    <NavLink key={slug} href={`/macro?category=${slug}`}>
                      {slug === "global-liquidity" ? <Globe2 className="h-4 w-4" /> : <Gauge className="h-4 w-4" />}
                      {label}
                    </NavLink>
                  ))}
                </div>
              </div>

              <div>
                <div className="mb-2 border-t border-line pt-4 text-xs font-semibold uppercase text-muted">
                  Asset Intelligence
                </div>
                <div className="space-y-1">
                  {assetSlugs.map((slug, index) => (
                    <NavLink key={slug} href={`/asset/${slug}`}>
                      <LineChart className="h-4 w-4" />
                      {assetLabels[index]}
                    </NavLink>
                  ))}
                </div>
              </div>

              <div>
                <div className="mb-2 border-t border-line pt-4 text-xs font-semibold uppercase text-muted">
                  Institutional Positioning
                </div>
                <NavLink href="/institutional">
                  <Landmark className="h-4 w-4" /> CFTC Positioning
                </NavLink>
              </div>
            </nav>

            <div className="mt-8 border-t border-line pt-4 text-xs text-muted">
              <div className="mb-2 flex items-center gap-2">
                <Database className="h-4 w-4" /> PostgreSQL ready
              </div>
              <div className="flex items-center gap-2">
                <BriefcaseBusiness className="h-4 w-4" /> Redis cached API
              </div>
            </div>
          </aside>

          <main className="min-w-0 p-5">{children}</main>
        </div>
      </body>
    </html>
  );
}
