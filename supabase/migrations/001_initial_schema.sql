-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- USERS TABLE
-- ============================================================
CREATE TABLE public.users (
    id                    UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email                 TEXT NOT NULL UNIQUE,
    full_name             TEXT,
    avatar_url            TEXT,
    elevenlabs_voice_id   TEXT,
    heygen_avatar_id      TEXT,
    default_llm           TEXT NOT NULL DEFAULT 'claude-3.5-sonnet'
                          CHECK (default_llm IN ('claude-3.5-sonnet', 'gpt-4o')),
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX idx_users_email_lower ON public.users (LOWER(email));

-- ============================================================
-- KNOWLEDGE BASE TABLE
-- ============================================================
CREATE TABLE public.knowledge_base (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id       UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    entry_type    TEXT NOT NULL CHECK (entry_type IN (
                    'system_prompt', 'tone_example', 'vocabulary',
                    'instruction', 'hook_template')),
    title         TEXT NOT NULL,
    content       TEXT NOT NULL,
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    priority      INTEGER NOT NULL DEFAULT 0 CHECK (priority >= 0),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_kb_user_id ON public.knowledge_base(user_id);
CREATE INDEX idx_kb_type_active ON public.knowledge_base(entry_type) WHERE is_active = TRUE;

-- ============================================================
-- CONTENT QUEUE TABLE
-- ============================================================
CREATE TABLE public.content_queue (
    id                    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id               UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,

    -- Source
    original_url          TEXT NOT NULL,
    platform              TEXT CHECK (platform IN ('youtube', 'tiktok', 'instagram')),

    -- Status
    status                TEXT NOT NULL DEFAULT 'Pending'
                          CHECK (status IN (
                            'Pending', 'Scraping', 'Scraped',
                            'Transcribing', 'Transcribed',
                            'Script_Generating', 'Script_Generated',
                            'Approved',
                            'Audio_Generating', 'Audio_Generated',
                            'Video_Generating', 'Video_Completed',
                            'Failed')),
    error_message         TEXT,
    retry_count           INTEGER NOT NULL DEFAULT 0,

    -- Scraped metadata
    source_title          TEXT,
    source_description    TEXT,
    source_tags           TEXT[],
    source_view_count     BIGINT,
    thumbnail_url         TEXT,

    -- Transcript
    original_transcript   TEXT,
    transcript_source     TEXT CHECK (transcript_source IN ('captions', 'deepgram', 'whisper')),

    -- Generated content
    generated_script      TEXT,
    script_edited_by_user BOOLEAN NOT NULL DEFAULT FALSE,
    approved_at           TIMESTAMPTZ,

    -- Audio
    audio_url             TEXT,
    audio_duration_sec    DOUBLE PRECISION,

    -- Video
    final_video_url       TEXT,
    heygen_video_id       TEXT,

    -- Generated posting metadata
    generated_title       TEXT,
    generated_description TEXT,
    generated_tags        TEXT[],

    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_cq_user_id ON public.content_queue(user_id);
CREATE INDEX idx_cq_status ON public.content_queue(status);
CREATE INDEX idx_cq_created ON public.content_queue(created_at DESC);
CREATE INDEX idx_cq_pending_approval ON public.content_queue(user_id)
    WHERE status = 'Script_Generated';

-- ============================================================
-- ROW LEVEL SECURITY
-- ============================================================
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knowledge_base ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.content_queue ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_own_data" ON public.users
    FOR ALL USING (auth.uid() = id);
CREATE POLICY "kb_own_data" ON public.knowledge_base
    FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "cq_own_data" ON public.content_queue
    FOR ALL USING (auth.uid() = user_id);

-- ============================================================
-- AUTO updated_at TRIGGER
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated BEFORE UPDATE ON public.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_kb_updated BEFORE UPDATE ON public.knowledge_base
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_cq_updated BEFORE UPDATE ON public.content_queue
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
