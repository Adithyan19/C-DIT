-- ============================================================
-- C-DIT Supabase Schema
-- Run this SQL in the Supabase SQL Editor (Dashboard → SQL Editor)
-- ============================================================

-- 1. Sessions table — tracks analysis sessions
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    input_type TEXT NOT NULL CHECK (input_type IN ('image', 'voice', 'text')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Messages table — conversation messages
CREATE TABLE IF NOT EXISTS messages (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('farmer', 'assistant')),
    content TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast message retrieval by session
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);

-- 3. Analysis Results table — stored analysis results
CREATE TABLE IF NOT EXISTS analysis_results (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    disease_label TEXT NOT NULL,
    confidence REAL NOT NULL DEFAULT 0,
    advisory TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analysis_results_session_id ON analysis_results(session_id);

-- 4. Feedback table — farmer feedback
CREATE TABLE IF NOT EXISTS feedback (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    was_helpful BOOLEAN NOT NULL,
    correct_disease TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_feedback_session_id ON feedback(session_id);

-- ============================================================
-- Row Level Security (RLS) — Enable for production
-- For development, we allow all operations with the anon key.
-- ============================================================

ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

-- Allow all operations for the anon role (development only)
CREATE POLICY "Allow all for anon" ON sessions FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for anon" ON messages FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for anon" ON analysis_results FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for anon" ON feedback FOR ALL USING (true) WITH CHECK (true);
