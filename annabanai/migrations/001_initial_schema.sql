-- AnnabanAI Cognitive Kernel v1 initial SQLite schema.
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS interactions (
    correlation_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    user_id TEXT NOT NULL,
    user_input TEXT NOT NULL,
    ai_output TEXT NOT NULL,
    sentiment_json TEXT NOT NULL,
    provider TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    audit_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS runtime_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    correlation_id TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    UNIQUE(correlation_id, sequence)
);
