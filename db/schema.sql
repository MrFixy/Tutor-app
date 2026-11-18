-- AI Engineering Tutor schema.
-- Run manually with: psql $DATABASE_URL -f db/schema.sql
-- SQLAlchemy metadata.create_all() can also create these tables.

CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(64) UNIQUE NOT NULL,
    email           VARCHAR(255) UNIQUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sessions (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at        TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS questions (
    id              SERIAL PRIMARY KEY,
    session_id      INTEGER REFERENCES sessions(id) ON DELETE SET NULL,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    raw_text        TEXT NOT NULL,
    explanation     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS lesson_content (
    id              SERIAL PRIMARY KEY,
    domain          VARCHAR(32) NOT NULL,
    subtopic        VARCHAR(255) NOT NULL,
    language        VARCHAR(32),
    title           VARCHAR(255) NOT NULL,
    body            TEXT NOT NULL,
    "order"         INTEGER NOT NULL DEFAULT 0,
    source_note     VARCHAR(255),
    UNIQUE (domain, subtopic, language)
);

CREATE TABLE IF NOT EXISTS study_plans (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    goal_text       TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS study_plan_items (
    id              SERIAL PRIMARY KEY,
    plan_id         INTEGER NOT NULL REFERENCES study_plans(id) ON DELETE CASCADE,
    domain          VARCHAR(32) NOT NULL DEFAULT 'phases',
    subtopic        VARCHAR(255) NOT NULL,
    "order"         INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS feedback (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER REFERENCES users(id) ON DELETE SET NULL,
    session_id      INTEGER REFERENCES sessions(id) ON DELETE SET NULL,
    category        VARCHAR(16) NOT NULL,
    view            VARCHAR(32),
    severity        VARCHAR(16),
    message         TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_questions_user ON questions(user_id);
CREATE INDEX IF NOT EXISTS idx_study_plans_user ON study_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_category ON feedback(category);
