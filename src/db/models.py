CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS positions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    market_id       TEXT NOT NULL,
    token_id        TEXT NOT NULL,
    question        TEXT NOT NULL,
    side            TEXT NOT NULL CHECK(side IN ('BUY', 'SELL')),
    entry_price     REAL NOT NULL,
    current_price   REAL,
    size            REAL NOT NULL,
    shares          REAL NOT NULL,
    order_id        TEXT,
    status          TEXT NOT NULL DEFAULT 'OPEN'
                        CHECK(status IN ('OPEN', 'CLOSED', 'PENDING', 'CANCELLED')),
    ai_probability  REAL NOT NULL,
    ai_confidence   TEXT NOT NULL,
    ai_reasoning    TEXT,
    prompt_version  TEXT,
    pnl_usd         REAL DEFAULT 0.0,
    pnl_pct         REAL DEFAULT 0.0,
    exit_price      REAL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now')),
    closed_at       TEXT,
    UNIQUE(order_id)
);

CREATE INDEX IF NOT EXISTS idx_positions_status ON positions(status);
CREATE INDEX IF NOT EXISTS idx_positions_market ON positions(market_id);

CREATE TABLE IF NOT EXISTS orders (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        TEXT NOT NULL UNIQUE,
    position_id     INTEGER REFERENCES positions(id),
    market_id       TEXT NOT NULL,
    token_id        TEXT NOT NULL,
    side            TEXT NOT NULL CHECK(side IN ('BUY', 'SELL')),
    order_type      TEXT NOT NULL DEFAULT 'GTC',
    price           REAL NOT NULL,
    size            REAL NOT NULL,
    filled_size     REAL DEFAULT 0.0,
    status          TEXT NOT NULL DEFAULT 'LIVE'
                        CHECK(status IN ('LIVE', 'FILLED', 'PARTIAL', 'CANCELLED', 'EXPIRED')),
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_position ON orders(position_id);

CREATE TABLE IF NOT EXISTS scans (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    markets_scanned INTEGER NOT NULL,
    edges_found     INTEGER NOT NULL DEFAULT 0,
    orders_placed   INTEGER NOT NULL DEFAULT 0,
    errors          INTEGER NOT NULL DEFAULT 0,
    duration_ms     INTEGER,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ai_analyses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    market_id       TEXT NOT NULL,
    question        TEXT NOT NULL,
    market_price    REAL NOT NULL,
    prompt_version  TEXT NOT NULL,
    ai_probability  REAL NOT NULL,
    ai_confidence   TEXT NOT NULL,
    ai_reasoning    TEXT,
    model           TEXT NOT NULL,
    input_tokens    INTEGER,
    output_tokens   INTEGER,
    latency_ms      INTEGER,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_analyses_market ON ai_analyses(market_id);
"""
