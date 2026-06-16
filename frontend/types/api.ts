export type HistoryPoint = {
  date: string;
  score?: number;
  [key: string]: string | number | undefined;
};

export type MacroDashboard = {
  success?: boolean;
  data_status?: string;
  macro_score: number;

  core_score?: number;

  surprise_score?: number;

  surprise_events?: any[];

  regime: string;
  trend: string;
  recession_risk: string;
  risk_status: string;
  summary: string[];
  asset_outlooks: Record<string, string>;
  category_scores: Record<string, number>;
  history?: HistoryPoint[];
};

export type MacroCategory = {
  success?: boolean;
  data_status?: string;
  name: string;
  score: number;

  core_score?: number;

  surprise_score?: number;

  surprise_events?: any[];

  bias: string;
  trend: string;
  summary: string;
  drivers: MacroDriver[];
  indicators: Indicator[];
  explanation: string;
  history: HistoryPoint[];
};

export type Indicator = {
  key: string;
  name: string;
  code: string;
  source: string;
  measures: string;
  score: number;

  core_score?: number;

  surprise_score?: number;

  surprise_events?: any[];

  bias: string;
  current: string | number;
  previous: string | number;
  change: string | number;
  actual?: string | number;
  forecast?: string | number;
  surprise?: string | number;
  trend_change?: string | number;
  trend_score?: number;
  final_score?: number;
  direction_score?: number;
  momentum_score?: number;
  current_display: string;
  previous_display: string;
  change_display: string;
  actual_display?: string;
  forecast_display?: string;
  surprise_display?: string;
  trend: string;
  market_surprise?: string;
  trend_state: "positive" | "negative" | "neutral" | string;
  impact: string;
  market_impact: string;
  last_update: string;
  explanation?: string;
  info?: string;
  weight: number;
  contribution: number;
  release_type?: string;
  percentile?: number;
  z_score?: number;
  distance_from_average?: number;
};

export type MacroDriver = {
  name: string;
  trend: string;
  trend_state: "positive" | "negative" | "neutral" | string;
  value: string;
  score: number;

  core_score?: number;

  surprise_score?: number;

  surprise_events?: any[];

  contribution: number;
  weight: number;
};

export type AssetResponse = {
  asset: string;
  asset_score: number;

  core_score?: number;

  surprise_score?: number;

  surprise_events?: any[];

  outlook: string;
  drivers: Driver[];
  summary: string;
  history: HistoryPoint[];
};

export type Driver = {
  name: string;
  score: number;

  core_score?: number;

  surprise_score?: number;

  surprise_events?: any[];

  contribution: number;
  bias: string;
};

export type InstitutionalResponse = {
  asset: string;
  long_percentage: number;
  short_percentage: number;
  net_position: number;
  weekly_change: number;
  four_week_velocity: number;
  bias: string;
  score: number;

  core_score?: number;

  surprise_score?: number;

  surprise_events?: any[];

  position_percentile: number;
  history: Record<string, string | number>[];
};

