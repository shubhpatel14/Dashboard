CREATE TABLE IF NOT EXISTS macro_history (
    date DATE PRIMARY KEY,
    liquidity_score NUMERIC(6, 2),
    rates_score NUMERIC(6, 2),
    inflation_score NUMERIC(6, 2),
    growth_score NUMERIC(6, 2),
    macro_score NUMERIC(6, 2)
);

CREATE TABLE IF NOT EXISTS asset_history (
    date DATE NOT NULL,
    asset TEXT NOT NULL,
    score NUMERIC(6, 2),
    outlook TEXT,
    PRIMARY KEY (date, asset)
);

CREATE TABLE IF NOT EXISTS cot_history (
    date DATE NOT NULL,
    asset TEXT NOT NULL,
    long_percent NUMERIC(6, 2),
    short_percent NUMERIC(6, 2),
    net_position BIGINT,
    PRIMARY KEY (date, asset)
);

CREATE INDEX IF NOT EXISTS idx_asset_history_asset_date
    ON asset_history (asset, date DESC);

CREATE INDEX IF NOT EXISTS idx_cot_history_asset_date
    ON cot_history (asset, date DESC);
