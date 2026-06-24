
CREATE TABLE IF NOT EXISTS macro_snapshots(

    id SERIAL PRIMARY KEY,

    created_at TIMESTAMP DEFAULT NOW(),

    macro_score FLOAT,

    regime TEXT,

    data JSONB

);


CREATE TABLE IF NOT EXISTS asset_snapshots(

    id SERIAL PRIMARY KEY,

    created_at TIMESTAMP DEFAULT NOW(),

    asset TEXT,

    score FLOAT,

    outlook TEXT,

    data JSONB

);


CREATE TABLE IF NOT EXISTS portfolio_snapshots(

    id SERIAL PRIMARY KEY,

    created_at TIMESTAMP DEFAULT NOW(),

    data JSONB

);


CREATE TABLE IF NOT EXISTS economic_surprises(

    id SERIAL PRIMARY KEY,

    category TEXT NOT NULL,

    event_name TEXT NOT NULL,

    actual FLOAT NOT NULL,

    forecast FLOAT NOT NULL,

    previous FLOAT NOT NULL,

    surprise FLOAT NOT NULL,

    score FLOAT NOT NULL,

    bias TEXT NOT NULL,

    release_date DATE NOT NULL,

    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT uq_economic_surprises_release
        UNIQUE(category,event_name,release_date)

);


CREATE INDEX IF NOT EXISTS ix_economic_surprises_latest
ON economic_surprises(category,event_name,release_date DESC);


CREATE UNIQUE INDEX IF NOT EXISTS ux_economic_surprises_release
ON economic_surprises(category,event_name,release_date);

