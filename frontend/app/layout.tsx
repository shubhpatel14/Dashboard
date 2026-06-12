import type { Metadata } from "next";
import { Suspense } from "react";
import "./globals.css";
import { Sidebar } from "@/components/sidebar";

export const metadata: Metadata = {
  title: "Trishula Capital Terminal",
  description: "Institutional macro intelligence platform"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <div className="terminal-grid">
          <Suspense fallback={<aside className="border-r border-line bg-surface p-4" />}>
            <Sidebar />
          </Suspense>
          <main className="min-w-0 p-5">{children}</main>
        </div>
      </body>
    </html>
  );
}
