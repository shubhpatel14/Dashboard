
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

