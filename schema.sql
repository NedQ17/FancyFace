-- Run this in Supabase SQL Editor to initialize the database

CREATE TABLE IF NOT EXISTS users (
    user_id     BIGINT PRIMARY KEY,
    username    TEXT,
    first_name  TEXT NOT NULL DEFAULT '',
    paid_credits  INTEGER NOT NULL DEFAULT 0,
    free_credits  INTEGER NOT NULL DEFAULT 0,
    total_generated INTEGER NOT NULL DEFAULT 0,
    channel_subscribed BOOLEAN NOT NULL DEFAULT FALSE,
    paywall_shown_at   TIMESTAMPTZ,
    paywall_reminder_sent BOOLEAN NOT NULL DEFAULT FALSE,
    referrer_id BIGINT REFERENCES users(user_id),
    is_blocked  BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS styles (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    emoji       TEXT NOT NULL DEFAULT '',
    prompt      TEXT NOT NULL,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    sort_order  INTEGER NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS photo_sessions (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT NOT NULL,
    photo_count INTEGER NOT NULL,
    prompts     TEXT[] NOT NULL,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS generations (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL REFERENCES users(user_id),
    gen_type        TEXT NOT NULL,
    style_id        INTEGER REFERENCES styles(id),
    session_id      INTEGER REFERENCES photo_sessions(id),
    prompt          TEXT,
    source_file_id  TEXT,
    result_file_ids TEXT[] NOT NULL DEFAULT '{}',
    status          TEXT NOT NULL DEFAULT 'pending',
    was_free        BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS payments (
    id                  SERIAL PRIMARY KEY,
    user_id             BIGINT NOT NULL REFERENCES users(user_id),
    package_id          TEXT NOT NULL,
    credits             INTEGER NOT NULL,
    amount_kopecks      INTEGER NOT NULL,
    status              TEXT NOT NULL DEFAULT 'pending',
    telegram_payment_id TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS referrals (
    id          SERIAL PRIMARY KEY,
    referrer_id BIGINT NOT NULL REFERENCES users(user_id),
    referred_id BIGINT NOT NULL UNIQUE REFERENCES users(user_id),
    credited_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_generations_user_id ON generations(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
