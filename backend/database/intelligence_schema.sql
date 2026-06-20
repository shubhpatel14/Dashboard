
-- ==========================================
-- MACRO CATEGORY SCORES
-- ==========================================

CREATE TABLE IF NOT EXISTS macro_scores(

    id SERIAL PRIMARY KEY,

    created_at TIMESTAMP DEFAULT NOW(),

    category TEXT,

    score FLOAT,

    bias TEXT,

    trend TEXT,

    data JSONB

);



-- ==========================================
-- INDIVIDUAL INDICATOR INTELLIGENCE
-- ==========================================

CREATE TABLE IF NOT EXISTS indicator_scores(

    id SERIAL PRIMARY KEY,

    created_at TIMESTAMP DEFAULT NOW(),

    indicator TEXT,

    current_value FLOAT,

    previous_value FLOAT,

    change FLOAT,

    percentile FLOAT,

    z_score FLOAT,

    average FLOAT,

    distance_average FLOAT,

    score FLOAT,

    signal TEXT,

    data JSONB

);




-- ==========================================
-- FINAL MACRO STATE HISTORY
-- ==========================================

CREATE TABLE IF NOT EXISTS macro_history(

    id SERIAL PRIMARY KEY,

    created_at TIMESTAMP DEFAULT NOW(),

    macro_score FLOAT,

    regime TEXT,

    liquidity_score FLOAT,

    inflation_score FLOAT,

    growth_score FLOAT,

    rates_score FLOAT,

    labor_score FLOAT,

    credit_score FLOAT,

    sentiment_score FLOAT,

    data JSONB

);



-- ==========================================
-- ASSET MODEL HISTORY
-- ==========================================

CREATE TABLE IF NOT EXISTS asset_scores(

    id SERIAL PRIMARY KEY,

    created_at TIMESTAMP DEFAULT NOW(),

    asset TEXT,

    score FLOAT,

    outlook TEXT,

    bullish_drivers JSONB,

    bearish_drivers JSONB,

    data JSONB

);




-- ==========================================
-- FACTOR ATTRIBUTION HISTORY
-- ==========================================

CREATE TABLE IF NOT EXISTS factor_scores(

    id SERIAL PRIMARY KEY,

    created_at TIMESTAMP DEFAULT NOW(),

    asset TEXT,

    factor TEXT,

    weight FLOAT,

    score FLOAT,

    contribution FLOAT,

    impact TEXT

);




-- ==========================================
-- REGIME HISTORY
-- ==========================================

CREATE TABLE IF NOT EXISTS regime_history(

    id SERIAL PRIMARY KEY,

    created_at TIMESTAMP DEFAULT NOW(),

    regime TEXT,

    confidence FLOAT,

    data JSONB

);



-- ==========================================
-- PORTFOLIO HISTORY
-- ==========================================

CREATE TABLE IF NOT EXISTS portfolio_history(

    id SERIAL PRIMARY KEY,

    created_at TIMESTAMP DEFAULT NOW(),

    allocation JSONB,

    reason JSONB

);


