-- TASK-001: persistence only. Business transitions are implemented in later tasks.

CREATE TABLE IF NOT EXISTS schema_metadata (
    metadata_key TEXT PRIMARY KEY,
    metadata_value TEXT NOT NULL
);

-- Source Vault
CREATE TABLE IF NOT EXISTS source_records (
    source_id TEXT PRIMARY KEY,
    append_receipt_id TEXT NOT NULL UNIQUE,
    source_kind TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS append_receipts (
    receipt_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL UNIQUE REFERENCES source_records(source_id),
    status TEXT NOT NULL CHECK (status IN ('stored', 'duplicate', 'rejected')),
    payload_json TEXT NOT NULL
);

-- Canonical Context
CREATE TABLE IF NOT EXISTS canonical_revisions (
    revision_id TEXT PRIMARY KEY,
    recorded_at TEXT NOT NULL,
    revision_kind TEXT NOT NULL CHECK (revision_kind IN ('seed', 'changeset'))
);

CREATE TABLE IF NOT EXISTS canonical_objects (
    object_id TEXT PRIMARY KEY,
    object_type TEXT NOT NULL CHECK (object_type IN (
        'entity', 'episode', 'assertion', 'relationship', 'state', 'hypothesis',
        'goal', 'commitment', 'decision', 'outcome', 'changeset', 'source'
    )),
    object_revision TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS canonical_evidence_refs (
    object_id TEXT NOT NULL REFERENCES canonical_objects(object_id),
    source_id TEXT NOT NULL REFERENCES source_records(source_id),
    locator_json TEXT NOT NULL,
    stance TEXT NOT NULL CHECK (stance IN ('supports', 'contradicts', 'contextual')),
    claim_ref TEXT NOT NULL,
    PRIMARY KEY (object_id, source_id, locator_json, stance, claim_ref)
);

-- Revision Ledger. TASK-001 establishes storage only; no ChangeSet behavior exists yet.
CREATE TABLE IF NOT EXISTS ledger_records (
    record_id TEXT PRIMARY KEY,
    revision_id TEXT REFERENCES canonical_revisions(revision_id),
    record_type TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

-- Derived Projection. Values are seeded only; projector/read behavior is deferred to TASK-007.
CREATE TABLE IF NOT EXISTS projection_rows (
    view_name TEXT PRIMARY KEY,
    data_revision TEXT NOT NULL REFERENCES canonical_revisions(revision_id),
    view_revision TEXT NOT NULL REFERENCES canonical_revisions(revision_id),
    freshness_status TEXT NOT NULL CHECK (freshness_status IN ('fresh', 'stale', 'updating', 'unavailable')),
    payload_json TEXT NOT NULL
);

-- A1 additive: CoverageWindow storage for answer safety evaluation
-- AS-TASK-001: persistence only. No business trigger or status evaluation.
CREATE TABLE IF NOT EXISTS coverage_windows (
    coverage_window_id TEXT PRIMARY KEY,
    scope_ref TEXT NOT NULL,
    coverage_start TEXT NOT NULL,
    coverage_end TEXT NOT NULL,
    continuity TEXT NOT NULL CHECK (continuity IN ('continuous', 'unknown', 'gapped')),
    gaps_json TEXT NOT NULL,
    export_completeness TEXT NOT NULL CHECK (export_completeness IN ('complete', 'partial', 'unknown'))
);

-- B2 additive: Canonical Episode metadata and explicit Derived summary storage.
-- Business publication, clustering and rebuild policy remain in later B2 tasks.
CREATE TABLE IF NOT EXISTS episodes (
    episode_id TEXT PRIMARY KEY REFERENCES canonical_objects(object_id),
    object_revision TEXT NOT NULL REFERENCES canonical_revisions(revision_id),
    episode_kind TEXT NOT NULL CHECK (episode_kind IN ('synthetic_relationship_event', 'synthetic_project_event')),
    valid_start TEXT NOT NULL,
    valid_end TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    synthetic_profile_id TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS episode_source_refs (
    episode_id TEXT NOT NULL REFERENCES episodes(episode_id),
    source_id TEXT NOT NULL REFERENCES source_records(source_id),
    locator_json TEXT NOT NULL,
    PRIMARY KEY (episode_id, source_id, locator_json)
);

CREATE TABLE IF NOT EXISTS summary_projections (
    projection_id TEXT PRIMARY KEY,
    projection_kind TEXT NOT NULL CHECK (projection_kind IN ('day_summary', 'phase_summary')),
    data_revision TEXT NOT NULL REFERENCES canonical_revisions(revision_id),
    view_revision TEXT NOT NULL REFERENCES canonical_revisions(revision_id),
    freshness_status TEXT NOT NULL CHECK (freshness_status IN ('fresh', 'stale', 'rebuilding', 'unavailable')),
    dependency_json TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    generated_at TEXT NOT NULL,
    generator_policy_id TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS derived_rebuild_receipts (
    receipt_id TEXT PRIMARY KEY,
    projection_id TEXT NOT NULL REFERENCES summary_projections(projection_id),
    data_revision TEXT NOT NULL REFERENCES canonical_revisions(revision_id),
    status TEXT NOT NULL CHECK (status IN ('rebuilt', 'failed')),
    payload_json TEXT NOT NULL
);

-- B3 additive: Canonical Commitment metadata and explicit Derived due-status storage.
-- Business lifecycle and projection policy remain in later B3 tasks.
CREATE TABLE IF NOT EXISTS commitments (
    commitment_id TEXT PRIMARY KEY REFERENCES canonical_objects(object_id),
    object_revision TEXT NOT NULL REFERENCES canonical_revisions(revision_id),
    commitment_kind TEXT NOT NULL CHECK (commitment_kind IN ('synthetic_obligation')),
    responsible_ref TEXT NOT NULL,
    statement_source_id TEXT NOT NULL REFERENCES source_records(source_id),
    statement_locator_json TEXT NOT NULL,
    due_time TEXT NOT NULL,
    valid_start TEXT NOT NULL,
    valid_end TEXT,
    recorded_at TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('open', 'completed', 'cancelled')),
    cancel_reason TEXT,
    review_status TEXT NOT NULL CHECK (review_status IN ('unreviewed', 'user_confirmed')),
    synthetic_profile_id TEXT NOT NULL,
    CHECK (status != 'cancelled' OR (cancel_reason IS NOT NULL AND cancel_reason != ''))
);

CREATE TABLE IF NOT EXISTS due_status_projections (
    projection_id TEXT PRIMARY KEY,
    commitment_id TEXT NOT NULL REFERENCES commitments(commitment_id),
    data_revision TEXT NOT NULL REFERENCES canonical_revisions(revision_id),
    view_revision TEXT NOT NULL REFERENCES canonical_revisions(revision_id),
    freshness_status TEXT NOT NULL CHECK (freshness_status IN ('fresh', 'stale', 'rebuilding', 'unavailable')),
    due_status TEXT NOT NULL CHECK (due_status IN ('upcoming', 'due', 'overdue', 'closed')),
    clock_instant TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    generated_at TEXT NOT NULL,
    generator_policy_id TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS due_rebuild_receipts (
    receipt_id TEXT PRIMARY KEY,
    projection_id TEXT NOT NULL REFERENCES due_status_projections(projection_id),
    data_revision TEXT NOT NULL REFERENCES canonical_revisions(revision_id),
    status TEXT NOT NULL CHECK (status IN ('rebuilt', 'failed')),
    payload_json TEXT NOT NULL
);
