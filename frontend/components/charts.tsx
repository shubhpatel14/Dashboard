"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import type { Driver, HistoryPoint, Indicator, InstitutionalResponse } from "@/types/api";
import { clampScore, formatNumber, toNumber } from "@/lib/format";

const grid = "rgb(var(--line))";
const ink = "rgb(var(--ink))";
const muted = "rgb(var(--muted))";
const terminal = "rgb(var(--terminal))";

function scoreColor(score: unknown) {
  const value = clampScore(score);
  if (value < 35) {
    return "#DC2626";
  }
  if (value > 65) {
    return "#16A34A";
  }
  return "#D97706";
}

function chartScore(point: HistoryPoint) {
  return clampScore(point.score ?? point.overall ?? point.macro_score, 50);
}

function movingAverage(values: number[], index: number, window: number) {
  const slice = values.slice(Math.max(0, index - window + 1), index + 1);
  const sum = slice.reduce((total, value) => total + value, 0);
  return Math.round((sum / Math.max(slice.length, 1)) * 100) / 100;
}

function EmptyChart() {
  return (
    <div className="flex h-64 items-center justify-center border border-dashed border-line bg-canvas text-sm text-muted">
      No chart data available
    </div>
  );
}

export function ScoreLine({ data, name = "Score" }: { data: HistoryPoint[]; name?: string }) {
  const scores = Array.isArray(data) ? data.map(chartScore) : [];
  const points = Array.isArray(data)
    ? data.map((point, index) => ({
        date: String(point.date ?? point.Date ?? index + 1),
        score: scores[index],
        ma7: movingAverage(scores, index, 7),
        ma30: movingAverage(scores, index, 30)
      }))
    : [];

  if (points.length === 0) {
    return <EmptyChart />;
  }

  return (
    <div className="h-72">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={points} margin={{ left: 0, right: 16, top: 12, bottom: 0 }}>
          <CartesianGrid stroke={grid} strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="date" tick={{ fill: muted, fontSize: 11 }} tickLine={false} axisLine={{ stroke: grid }} minTickGap={24} />
          <YAxis domain={[0, 100]} tick={{ fill: muted, fontSize: 11 }} tickLine={false} axisLine={false} width={34} />
          <Tooltip
            contentStyle={{ background: "rgb(var(--surface))", border: `1px solid ${grid}`, color: ink }}
            formatter={(value) => [`${formatNumber(Number(value))}/100`, name]}
          />
          <Line type="monotone" dataKey="score" stroke={terminal} strokeWidth={2.5} dot={false} activeDot={{ r: 4 }} name={name} />
          <Line type="monotone" dataKey="ma7" stroke="#16A34A" strokeWidth={1.6} dot={false} name="7D MA" />
          <Line type="monotone" dataKey="ma30" stroke="#D97706" strokeWidth={1.6} dot={false} name="30D MA" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function DriverBars({ drivers }: { drivers: Driver[] }) {
  const rows = Array.isArray(drivers)
    ? drivers.map((driver) => ({
        name: driver.name || "Driver",
        score: clampScore(driver.score),
        contribution: toNumber(driver.contribution, clampScore(driver.score))
      }))
    : [];

  if (rows.length === 0) {
    return <EmptyChart />;
  }

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={rows} layout="vertical" margin={{ left: 16, right: 18, top: 8, bottom: 8 }}>
          <CartesianGrid stroke={grid} strokeDasharray="3 3" horizontal={false} />
          <XAxis type="number" domain={[0, 100]} tick={{ fill: muted, fontSize: 11 }} tickLine={false} axisLine={false} />
          <YAxis type="category" dataKey="name" tick={{ fill: muted, fontSize: 11 }} tickLine={false} axisLine={false} width={110} />
          <Tooltip
            contentStyle={{ background: "rgb(var(--surface))", border: `1px solid ${grid}` }}
            formatter={(value) => [`${formatNumber(Number(value))}`, "Score"]}
          />
          <Bar dataKey="score" radius={[0, 4, 4, 0]} barSize={14}>
            {rows.map((row) => (
              <Cell key={row.name} fill={scoreColor(row.score)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ContributionBars({ indicators }: { indicators: Indicator[] }) {
  const rows = Array.isArray(indicators)
    ? indicators.map((indicator) => {
        const score = clampScore(indicator.score);
        const weight = toNumber(indicator.weight, 10);
        const rawImpact = Number.isFinite(Number(indicator.contribution))
          ? Number(indicator.contribution)
          : Math.round((score - 50) * (weight / 100) * 100) / 100;
        return {
          name: indicator.name || "Indicator",
          impact: rawImpact,
          score
        };
      })
    : [];

  if (rows.length === 0) {
    return <EmptyChart />;
  }

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={rows} layout="vertical" margin={{ left: 18, right: 16, top: 8, bottom: 8 }}>
          <CartesianGrid stroke={grid} strokeDasharray="3 3" horizontal={false} />
          <XAxis type="number" tick={{ fill: muted, fontSize: 11 }} tickLine={false} axisLine={false} />
          <YAxis type="category" dataKey="name" tick={{ fill: muted, fontSize: 10 }} tickLine={false} axisLine={false} width={132} />
          <Tooltip
            contentStyle={{ background: "rgb(var(--surface))", border: `1px solid ${grid}` }}
            formatter={(value) => [`${Number(value) >= 0 ? "+" : ""}${formatNumber(Number(value))} pts`, "Contribution"]}
          />
          <Bar dataKey="impact" radius={[4, 4, 4, 4]} barSize={14}>
            {rows.map((row) => (
              <Cell key={row.name} fill={row.impact < 0 ? "#DC2626" : row.impact > 0 ? "#16A34A" : "#D97706"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function AssetRadar({ drivers }: { drivers: Driver[] }) {
  const rows = Array.isArray(drivers)
    ? drivers.slice(0, 8).map((driver) => ({
        driver: driver.name || "Driver",
        score: clampScore(driver.score)
      }))
    : [];

  if (rows.length < 3) {
    return <EmptyChart />;
  }

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={rows} outerRadius="72%">
          <PolarGrid stroke={grid} />
          <PolarAngleAxis dataKey="driver" tick={{ fill: muted, fontSize: 11 }} />
          <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: muted, fontSize: 10 }} />
          <Radar name="Score" dataKey="score" stroke={terminal} fill={terminal} fillOpacity={0.12} />
          <Tooltip contentStyle={{ background: "rgb(var(--surface))", border: `1px solid ${grid}` }} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function IndicatorTrendChart({ indicators }: { indicators: Indicator[] }) {
  const rows = Array.isArray(indicators)
    ? indicators.slice(0, 8).map((indicator) => ({
        name: indicator.name || "Indicator",
        previous: toNumber(indicator.previous, 0),
        current: toNumber(indicator.current, 0)
      }))
    : [];

  if (rows.length === 0) {
    return <EmptyChart />;
  }

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={rows} margin={{ left: 0, right: 16, top: 12, bottom: 24 }}>
          <CartesianGrid stroke={grid} strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="name" tick={{ fill: muted, fontSize: 10 }} tickLine={false} axisLine={{ stroke: grid }} interval={0} angle={-18} textAnchor="end" height={56} />
          <YAxis tick={{ fill: muted, fontSize: 11 }} tickLine={false} axisLine={false} width={44} />
          <Tooltip contentStyle={{ background: "rgb(var(--surface))", border: `1px solid ${grid}` }} />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Bar dataKey="previous" fill="#94A3B8" radius={[3, 3, 0, 0]} />
          <Bar dataKey="current" fill={terminal} radius={[3, 3, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function PositioningCharts({ data }: { data: InstitutionalResponse }) {
  const history = Array.isArray(data.history)
    ? data.history.map((point, index) => ({
        date: String(point.Date ?? point.date ?? index + 1),
        net: toNumber(point["Net Position"] ?? point.net_position, 0),
        long: toNumber(point["Long Exposure"] ?? point.long_percentage, 0),
        short: toNumber(point["Short Exposure"] ?? point.short_percentage, 0)
      }))
    : [];

  if (history.length === 0) {
    return <EmptyChart />;
  }

  return (
    <div className="h-96">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={history} margin={{ left: 0, right: 16, top: 12, bottom: 0 }}>
          <CartesianGrid stroke={grid} strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="date" tick={{ fill: muted, fontSize: 11 }} tickLine={false} axisLine={{ stroke: grid }} minTickGap={24} />
          <YAxis tick={{ fill: muted, fontSize: 11 }} tickLine={false} axisLine={false} width={46} />
          <Tooltip contentStyle={{ background: "rgb(var(--surface))", border: `1px solid ${grid}` }} />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Line type="monotone" dataKey="net" name="Net Position" stroke={terminal} strokeWidth={2.4} dot={false} />
          <Line type="monotone" dataKey="long" name="Long %" stroke="#16A34A" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="short" name="Short %" stroke="#DC2626" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
