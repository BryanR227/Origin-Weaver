-- Run this once against your Tiger database, e.g.:
--   psql "$DATABASE_URL" -f database/schema.sql
-- or paste into any Postgres client connected to your Tiger service.

CREATE TABLE IF NOT EXISTS users (
    id            BIGSERIAL PRIMARY KEY,
    email         TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
