export type HistoryPoint = {
  date: string;
  score?: number;
  [key: string]: string | number | undefined;
};


// ==================================================
// DASHBOARD
// ==================================================

export type MacroBlock = {

  name?: string;

  score: number;

  value?: number;

  bias?: string;

  trend?: string;

  impact?: string;

};


export type MacroDashboard = {

  success?: boolean;

  data_status?: string;


  macro_score: number;

  score?: number;


  core_score?: number;

  surprise_score?: number;

  surprise_events?: any[];


  regime: string;

  risk_regime?: string;


  trend: string;

  recession_risk: string;

  risk_status: string;


  summary: string | string[];


  asset_outlooks: Record<string,string>;



  // OLD FRONTEND SUPPORT
  category_scores: Record<string, MacroBlock>;


  // NEW BACKEND SUPPORT
  categories?: Record<string, MacroBlock>;

  macro_blocks?: Record<string, MacroBlock>;



  // TABLE SUPPORT
  heatmap?: MacroBlock[];

  global_macro_heatmap?: MacroBlock[];



  // SCORE EXPLANATION
  drivers?: MacroDriver[];

  contributions?: MacroDriver[];

  score_breakdown?: MacroDriver[];



  history?: HistoryPoint[];

};



// ==================================================
// MACRO CATEGORY
// ==================================================

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

  explanation: string;


  drivers: MacroDriver[];

  indicators: Indicator[];


  history: HistoryPoint[];

};



// ==================================================
// INDICATORS
// ==================================================

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


  trend_state:

    | "positive"

    | "negative"

    | "neutral"

    | string;



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




// ==================================================
// MACRO DRIVER
// ==================================================

export type MacroDriver = {


  name: string;


  trend?: string;


  trend_state?:

    | "positive"

    | "negative"

    | "neutral"

    | string;



  value?: string;



  score: number;


  core_score?: number;

  surprise_score?: number;

  surprise_events?: any[];



  contribution: number;


  weight?: number;

};




// ==================================================
// ASSETS
// ==================================================

export type AssetResponse = {


  asset: string;


  asset_score: number;


  score: number;


  outlook: string;


  bias: string;


  trend: string;



  explanation: string;


  summary: string;



  drivers: Driver[];


  bullish_drivers:any;


  bearish_drivers:any;



  components:any[];



  history:HistoryPoint[];



  core_score?: number;


  surprise_score?: number;


  surprise_events?: any[];

};




export type Driver = {


  name:string;


  score:number;


  core_score?:number;


  surprise_score?:number;


  surprise_events?:any[];


  contribution:number;


  bias:string;

};




// ==================================================
// INSTITUTIONAL
// ==================================================

export type InstitutionalResponse = {


  asset:string;


  long_percentage:number;


  short_percentage:number;


  net_position:number;


  weekly_change:number;


  four_week_velocity:number;


  bias:string;


  score:number;


  position_percentile:number;



  history:Record<string,string|number>[];



  core_score?:number;


  surprise_score?:number;


  surprise_events?:any[];

};