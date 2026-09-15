-- Phase 0 schema: users, sessions, questions, attempts, mastery_score
-- Run manually with: psql $DATABASE_URL -f db/schema.sql
-- (app/models.py can also create these via SQLAlchemy metadata.create_all())

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
    id                  SERIAL PRIMARY KEY,
    session_id          INTEGER REFERENCES sessions(id) ON DELETE SET NULL,
    user_id             INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    raw_text            TEXT NOT NULL,
    intent_domain       VARCHAR(32),        -- 'stats' | 'coding'
    intent_subtopic     VARCHAR(64),
    intent_confidence   REAL,
    classified_json     JSONB,              -- full raw classifier output
    explanation         TEXT,               -- generated explanation, if any
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS attempts (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question_id     INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    attempt_type    VARCHAR(16) NOT NULL,   -- 'quiz' | 'code'
    submission      TEXT,
    is_correct      BOOLEAN,
    score           REAL,
    feedback        TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS mastery_score (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    domain          VARCHAR(32) NOT NULL,   -- 'stats' | 'coding'
    subtopic        VARCHAR(64) NOT NULL,
    score           REAL NOT NULL DEFAULT 0,      -- rolling mastery 0-1
    attempts_count  INTEGER NOT NULL DEFAULT 0,
    last_updated    TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, domain, subtopic)
);

-- Phase 6 / Week 13: pilot feedback (functional bugs + UI/UX friction),
-- captured from the in-app feedback widget.
CREATE TABLE IF NOT EXISTS feedback (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER REFERENCES users(id) ON DELETE SET NULL,
    session_id      INTEGER REFERENCES sessions(id) ON DELETE SET NULL,
    category        VARCHAR(16) NOT NULL,   -- 'bug' | 'ux_friction' | 'other'
    view            VARCHAR(32),            -- 'chat' | 'practice' | 'progress'
    severity        VARCHAR(16),            -- 'blocker' | 'annoying' | 'minor'
    message         TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_questions_user ON questions(user_id);
CREATE INDEX IF NOT EXISTS idx_attempts_user ON attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_mastery_user ON mastery_score(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_category ON feedback(category);
