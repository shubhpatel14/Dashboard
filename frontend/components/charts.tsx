"use client";

import ReactECharts from "echarts-for-react";
import type { Driver, HistoryPoint, Indicator, InstitutionalResponse } from "@/types/api";

export function ScoreLine({ data, name = "Score" }: { data: HistoryPoint[]; name?: string }) {
  const option = {
    grid: { left: 34, right: 12, top: 20, bottom: 30 },
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: data.map((point) => point.date), axisLabel: { fontSize: 10 } },
    yAxis: { type: "value", min: 0, max: 100, splitLine: { lineStyle: { color: "#E5E7EB" } } },
    series: [
      {
        name,
        data: data.map((point) => point.score ?? point.overall ?? point.macro_score ?? 50),
        type: "line",
        smooth: true,
        showSymbol: false,
        lineStyle: { color: "#111827", width: 2 },
        areaStyle: { color: "rgba(17, 24, 39, 0.06)" }
      }
    ]
  };

  return <ReactECharts option={option} style={{ height: 260, width: "100%" }} />;
}

export function DriverBars({ drivers }: { drivers: Driver[] }) {
  const option = {
    grid: { left: 116, right: 18, top: 10, bottom: 20 },
    tooltip: { trigger: "axis" },
    xAxis: { type: "value", min: 0, max: 100, splitLine: { lineStyle: { color: "#E5E7EB" } } },
    yAxis: { type: "category", data: drivers.map((driver) => driver.name), axisLabel: { fontSize: 11 } },
    series: [
      {
        type: "bar",
        data: drivers.map((driver) => driver.score),
        itemStyle: { color: "#111827" },
        barWidth: 12
      }
    ]
  };

  return <ReactECharts option={option} style={{ height: 280, width: "100%" }} />;
}

export function IndicatorTrendChart({ indicators }: { indicators: Indicator[] }) {
  const visible = indicators.slice(0, 6);
  const option = {
    grid: { left: 48, right: 18, top: 24, bottom: 34 },
    tooltip: { trigger: "axis" },
    legend: { bottom: 0, textStyle: { fontSize: 10 } },
    xAxis: { type: "category", data: ["Previous", "Current"], axisLabel: { fontSize: 11 } },
    yAxis: { type: "value", splitLine: { lineStyle: { color: "#E5E7EB" } } },
    series: visible.map((indicator) => ({
      name: indicator.name,
      type: "line",
      smooth: true,
      data: [Number(indicator.previous), Number(indicator.current)],
      lineStyle: {
        width: 2,
        color:
          indicator.trend_state === "positive"
            ? "#16A34A"
            : indicator.trend_state === "negative"
              ? "#DC2626"
              : "#D97706"
      },
      itemStyle: {
        color:
          indicator.trend_state === "positive"
            ? "#16A34A"
            : indicator.trend_state === "negative"
              ? "#DC2626"
              : "#D97706"
      }
    }))
  };

  return <ReactECharts option={option} style={{ height: 320, width: "100%" }} />;
}

export function PositioningCharts({ data }: { data: InstitutionalResponse }) {
  const history = data.history;
  const dates = history.map((point) => point.Date);

  const option = {
    grid: [
      { left: 54, right: 18, top: 24, height: 120 },
      { left: 54, right: 18, top: 196, height: 120 }
    ],
    tooltip: { trigger: "axis" },
    xAxis: [
      { type: "category", data: dates, gridIndex: 0, axisLabel: { fontSize: 10 } },
      { type: "category", data: dates, gridIndex: 1, axisLabel: { fontSize: 10 } }
    ],
    yAxis: [
      { type: "value", gridIndex: 0, splitLine: { lineStyle: { color: "#E5E7EB" } } },
      { type: "value", gridIndex: 1, splitLine: { lineStyle: { color: "#E5E7EB" } } }
    ],
    series: [
      {
        name: "Net Position",
        type: "line",
        xAxisIndex: 0,
        yAxisIndex: 0,
        showSymbol: false,
        data: history.map((point) => point["Net Position"]),
        lineStyle: { color: "#111827", width: 2 }
      },
      {
        name: "Long %",
        type: "line",
        xAxisIndex: 1,
        yAxisIndex: 1,
        showSymbol: false,
        data: history.map((point) => point["Long Exposure"]),
        lineStyle: { color: "#16A34A", width: 2 }
      },
      {
        name: "Short %",
        type: "line",
        xAxisIndex: 1,
        yAxisIndex: 1,
        showSymbol: false,
        data: history.map((point) => point["Short Exposure"]),
        lineStyle: { color: "#DC2626", width: 2 }
      }
    ]
  };

  return <ReactECharts option={option} style={{ height: 360, width: "100%" }} />;
}
