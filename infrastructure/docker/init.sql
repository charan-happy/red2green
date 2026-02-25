CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    webhook_secret TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE repositories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    provider TEXT NOT NULL CHECK (provider IN ('github', 'gitlab', 'bitbucket', 'jenkins')),
    external_id TEXT NOT NULL,
    full_name TEXT NOT NULL,
    default_branch TEXT DEFAULT 'main',
    clone_url TEXT NOT NULL,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(provider, external_id)
);

CREATE TABLE pipeline_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repo_id UUID REFERENCES repositories(id) ON DELETE CASCADE,
    provider TEXT NOT NULL,
    pipeline_id TEXT NOT NULL,
    branch TEXT,
    commit_sha TEXT,
    commit_message TEXT,
    author TEXT,
    status TEXT NOT NULL,
    raw_payload JSONB NOT NULL DEFAULT '{}',
    received_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE heal_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID REFERENCES pipeline_events(id),
    repo_id UUID REFERENCES repositories(id),
    status TEXT NOT NULL DEFAULT 'queued'
        CHECK (status IN ('queued','running','fixing','validating','pr_opened','escalated','resolved','failed')),
    failure_type TEXT,
    root_cause TEXT,
    affected_files TEXT[],
    error_log TEXT,
    fix_attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    fix_branch TEXT,
    pr_url TEXT,
    pr_number INTEGER,
    started_at TIMESTAMPTZ,
    diagnosed_at TIMESTAMPTZ,
    fixed_at TIMESTAMPTZ,
    validated_at TIMESTAMPTZ,
    escalated_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    agent_state JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE fix_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES heal_jobs(id) ON DELETE CASCADE,
    attempt_number INTEGER NOT NULL,
    diagnosis_prompt TEXT,
    diagnosis_response TEXT,
    fix_prompt TEXT,
    fix_response TEXT,
    patch TEXT,
    files_changed JSONB,
    validation_status TEXT CHECK (validation_status IN ('pass', 'fail', 'error')),
    validation_log TEXT,
    validation_duration_ms INTEGER,
    input_tokens INTEGER,
    output_tokens INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE escalations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES heal_jobs(id),
    reason TEXT NOT NULL,
    notified_channels TEXT[],
    notification_sent_at TIMESTAMPTZ,
    acknowledged_by TEXT,
    acknowledged_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE fix_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES heal_jobs(id),
    failure_type TEXT NOT NULL,
    error_signature TEXT NOT NULL,
    fix_summary TEXT NOT NULL,
    patch TEXT NOT NULL,
    embedding vector(1536),
    success_count INTEGER DEFAULT 1,
    failure_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX fix_embeddings_vector_idx ON fix_embeddings
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE TABLE agent_logs (
    id BIGSERIAL PRIMARY KEY,
    job_id UUID REFERENCES heal_jobs(id),
    node_name TEXT NOT NULL,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX heal_jobs_status_idx ON heal_jobs(status);
CREATE INDEX heal_jobs_repo_created_idx ON heal_jobs(repo_id, created_at DESC);
CREATE INDEX agent_logs_job_idx ON agent_logs(job_id, created_at);

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER heal_jobs_updated_at BEFORE UPDATE ON heal_jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
