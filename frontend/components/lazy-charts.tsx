"use client";

import dynamic from "next/dynamic";
import type { Driver, HistoryPoint, Indicator, InstitutionalResponse } from "@/types/api";

function ChartShell() {
  return <div className="h-64 w-full border border-line bg-canvas" />;
}

export const ScoreLine = dynamic(
  () => import("./charts").then((module) => module.ScoreLine),
  {
    ssr: false,
    loading: ChartShell
  }
) as React.ComponentType<{ data: HistoryPoint[]; name?: string }>;

export const DriverBars = dynamic(
  () => import("./charts").then((module) => module.DriverBars),
  {
    ssr: false,
    loading: ChartShell
  }
) as React.ComponentType<{ drivers: Driver[] }>;

export const IndicatorTrendChart = dynamic(
  () => import("./charts").then((module) => module.IndicatorTrendChart),
  {
    ssr: false,
    loading: ChartShell
  }
) as React.ComponentType<{ indicators: Indicator[] }>;

export const PositioningCharts = dynamic(
  () => import("./charts").then((module) => module.PositioningCharts),
  {
    ssr: false,
    loading: ChartShell
  }
) as React.ComponentType<{ data: InstitutionalResponse }>;
